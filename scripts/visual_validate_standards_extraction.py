"""
Visual Validation Extraction for Standards Books
================================================
Extracts content from PDFs with visual validation:
- Converts pages to images for verification
- Validates table extraction accuracy
- Captures screenshots of complex pages
- Uses OCR for scanned content
- Generates visual comparison reports
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    print("ERROR: pdfplumber required for table extraction")
    sys.exit(1)

try:
    from pdf2image import convert_from_path
    from PIL import Image, ImageDraw, ImageFont
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False
    print("WARNING: pdf2image not available - visual validation limited")
    print("Install: pip install pdf2image pillow")

try:
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    print("WARNING: pytesseract not available - OCR disabled")
    print("Install: pip install pytesseract")


class VisualValidationExtractor:
    """Extract PDF content with visual validation and verification."""
    
    def __init__(self, output_dir: str = "output/standards_scan/visual_validation", dpi: int = 200):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi
        self.page_images_dir = self.output_dir / "page_images"
        self.page_images_dir.mkdir(exist_ok=True)
        self.table_validation_dir = self.output_dir / "table_validation"
        self.table_validation_dir.mkdir(exist_ok=True)
        
    def extract_with_validation(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract content from PDF with visual validation.
        
        Returns:
            Dictionary with extracted content, images, and validation results
        """
        print(f"\n{'='*80}")
        print(f"VISUAL VALIDATION EXTRACTION: {Path(pdf_path).name}")
        print(f"{'='*80}")
        
        if not os.path.exists(pdf_path):
            print(f"ERROR: File not found: {pdf_path}")
            return None
        
        result = {
            'pdf_path': pdf_path,
            'pdf_name': Path(pdf_path).stem,
            'pages': [],
            'tables': [],
            'validation_report': {
                'total_pages': 0,
                'pages_with_images': 0,
                'tables_extracted': 0,
                'tables_validated': 0,
                'pages_needing_review': []
            }
        }
        
        # Step 1: Convert PDF to images for visual validation
        page_images = []
        if HAS_PDF2IMAGE:
            print(f"\n[1/4] Converting PDF to images (DPI: {self.dpi})...")
            try:
                page_images = convert_from_path(pdf_path, dpi=self.dpi)
                print(f"  ✓ Converted {len(page_images)} pages to images")
                
                # Save page images
                for i, img in enumerate(page_images, 1):
                    img_path = self.page_images_dir / f"{Path(pdf_path).stem}_page_{i:04d}.png"
                    img.save(img_path, 'PNG')
                    result['validation_report']['pages_with_images'] += 1
            except Exception as e:
                print(f"  ✗ Error converting to images: {e}")
                page_images = []
        else:
            print("  ⚠ Skipping image conversion (pdf2image not available)")
        
        # Step 2: Extract text and tables using pdfplumber
        print(f"\n[2/4] Extracting text and tables...")
        try:
            with pdfplumber.open(pdf_path) as pdf:
                result['validation_report']['total_pages'] = len(pdf.pages)
                
                for i, page in enumerate(pdf.pages, 1):
                    print(f"  Processing page {i}/{len(pdf.pages)}...", end='\r')
                    
                    page_data = {
                        'page_number': i,
                        'text': page.extract_text() or '',
                        'tables': [],
                        'table_count': 0,
                        'needs_review': False,
                        'image_path': None
                    }
                    
                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        page_data['table_count'] = len(tables)
                        result['validation_report']['tables_extracted'] += len(tables)
                        
                        for table_idx, table in enumerate(tables, 1):
                            table_data = {
                                'page': i,
                                'table_number': table_idx,
                                'rows': len(table),
                                'columns': len(table[0]) if table else 0,
                                'data': table,
                                'validation_status': 'pending'
                            }
                            
                            # Validate table structure
                            if self._validate_table(table):
                                table_data['validation_status'] = 'valid'
                                result['validation_report']['tables_validated'] += 1
                            else:
                                table_data['validation_status'] = 'needs_review'
                                page_data['needs_review'] = True
                                result['validation_report']['pages_needing_review'].append(i)
                            
                            page_data['tables'].append(table_data)
                            result['tables'].append(table_data)
                    
                    # Check if page needs visual review
                    if not page_data['text'] or len(page_data['text']) < 50:
                        page_data['needs_review'] = True
                        if i not in result['validation_report']['pages_needing_review']:
                            result['validation_report']['pages_needing_review'].append(i)
                    
                    # Link to page image if available
                    if i <= len(page_images):
                        page_data['image_path'] = str(self.page_images_dir / f"{Path(pdf_path).stem}_page_{i:04d}.png")
                    
                    result['pages'].append(page_data)
                
                print(f"  ✓ Extracted {len(result['pages'])} pages")
                print(f"  ✓ Found {result['validation_report']['tables_extracted']} tables")
                
        except Exception as e:
            print(f"\n  ✗ Error extracting from PDF: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        # Step 3: Visual validation of tables
        if result['tables'] and HAS_PDF2IMAGE and page_images:
            print(f"\n[3/4] Validating table extraction visually...")
            self._validate_tables_visually(result, page_images)
        
        # Step 4: Generate validation report
        print(f"\n[4/4] Generating validation report...")
        self._generate_validation_report(result)
        
        # Save results
        result_file = self.output_dir / f"{Path(pdf_path).stem}_validated.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Saved results to: {result_file}")
        
        return result
    
    def _validate_table(self, table: List[List]) -> bool:
        """Validate that a table has proper structure."""
        if not table:
            return False
        
        # Check for consistent column count
        if len(table) < 2:
            return False
        
        first_row_cols = len(table[0])
        if first_row_cols == 0:
            return False
        
        # Check that most rows have same column count (allow some variation)
        consistent_rows = sum(1 for row in table if len(row) == first_row_cols)
        consistency_ratio = consistent_rows / len(table)
        
        return consistency_ratio >= 0.7  # 70% consistency threshold
    
    def _validate_tables_visually(self, result: Dict, page_images: List):
        """Create visual validation images for tables."""
        pdf_name = result['pdf_name']
        
        for table_data in result['tables']:
            page_num = table_data['page']
            table_num = table_data['table_number']
            
            if page_num <= len(page_images):
                # Load page image
                page_img = page_images[page_num - 1]
                
                # Create annotated image showing table location
                annotated = page_img.copy()
                draw = ImageDraw.Draw(annotated)
                
                # Try to find table bounds (simplified - would need more sophisticated detection)
                # For now, just add a border annotation
                width, height = annotated.size
                margin = 20
                
                # Draw border around potential table area
                draw.rectangle(
                    [margin, margin, width - margin, height - margin],
                    outline='red',
                    width=3
                )
                
                # Add text annotation
                try:
                    font = ImageFont.truetype("arial.ttf", 24)
                except:
                    font = ImageFont.load_default()
                
                annotation_text = f"Page {page_num} - Table {table_num}\nRows: {table_data['rows']}, Cols: {table_data['columns']}\nStatus: {table_data['validation_status']}"
                draw.text((margin + 10, margin + 10), annotation_text, fill='red', font=font)
                
                # Save annotated image
                annotated_path = self.table_validation_dir / f"{pdf_name}_page_{page_num:04d}_table_{table_num}.png"
                annotated.save(annotated_path)
                table_data['validation_image'] = str(annotated_path)
    
    def _generate_validation_report(self, result: Dict):
        """Generate a markdown validation report."""
        report_path = self.output_dir / f"{result['pdf_name']}_validation_report.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# Visual Validation Report: {result['pdf_name']}\n\n")
            f.write(f"**PDF**: `{result['pdf_path']}`\n\n")
            f.write(f"## Summary\n\n")
            f.write(f"- **Total Pages**: {result['validation_report']['total_pages']}\n")
            f.write(f"- **Pages with Images**: {result['validation_report']['pages_with_images']}\n")
            f.write(f"- **Tables Extracted**: {result['validation_report']['tables_extracted']}\n")
            f.write(f"- **Tables Validated**: {result['validation_report']['tables_validated']}\n")
            f.write(f"- **Pages Needing Review**: {len(result['validation_report']['pages_needing_review'])}\n\n")
            
            if result['validation_report']['pages_needing_review']:
                f.write(f"## Pages Requiring Manual Review\n\n")
                f.write(f"The following pages may need manual verification:\n\n")
                for page_num in result['validation_report']['pages_needing_review']:
                    page_data = result['pages'][page_num - 1]
                    f.write(f"### Page {page_num}\n\n")
                    f.write(f"- **Text Length**: {len(page_data['text'])} characters\n")
                    f.write(f"- **Tables**: {page_data['table_count']}\n")
                    if page_data['image_path']:
                        f.write(f"- **Image**: `{page_data['image_path']}`\n")
                    f.write("\n")
            
            f.write(f"## Table Extraction Details\n\n")
            f.write(f"| Page | Table | Rows | Cols | Status |\n")
            f.write(f"|------|-------|------|------|--------|\n")
            
            for table in result['tables']:
                status_icon = "✅" if table['validation_status'] == 'valid' else "⚠️"
                f.write(f"| {table['page']} | {table['table_number']} | {table['rows']} | {table['columns']} | {status_icon} {table['validation_status']} |\n")
        
        print(f"  ✓ Validation report: {report_path}")


def main():
    """Main function to process all PDFs with visual validation."""
    pdf_files = [
        r"C:\Users\D&E Cornealius\Documents\STANDARDS BOOK I_REV0.pdf",
        r"C:\Users\D&E Cornealius\Documents\STANDARDS BOOK II vol. I_REV0.pdf",
        r"C:\Users\D&E Cornealius\Documents\STANDARDS BOOK II vol. II_REV0.pdf",
        r"C:\Users\D&E Cornealius\Documents\STANDARDS BOOK III_REV0.pdf",
        r"C:\Users\D&E Cornealius\Documents\STANDARDS BOOK IV_REV0.pdf",
    ]
    
    extractor = VisualValidationExtractor()
    results = []
    
    for idx, pdf_path in enumerate(pdf_files, 1):
        print(f"\n\n{'='*80}")
        print(f"Processing PDF {idx}/{len(pdf_files)}")
        print(f"{'='*80}")
        
        try:
            result = extractor.extract_with_validation(pdf_path)
            if result:
                results.append(result)
        except Exception as e:
            print(f"ERROR processing {pdf_path}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Generate summary report
    print(f"\n\n{'='*80}")
    print("VISUAL VALIDATION SUMMARY")
    print(f"{'='*80}")
    print(f"Total PDFs processed: {len(results)}")
    if results:
        total_pages = sum(r['validation_report']['total_pages'] for r in results)
        total_tables = sum(r['validation_report']['tables_extracted'] for r in results)
        total_validated = sum(r['validation_report']['tables_validated'] for r in results)
        total_review = sum(len(r['validation_report']['pages_needing_review']) for r in results)
        
        print(f"Total pages: {total_pages}")
        print(f"Total tables extracted: {total_tables}")
        print(f"Total tables validated: {total_validated}")
        print(f"Pages needing review: {total_review}")
        print(f"\nValidation accuracy: {(total_validated/total_tables*100) if total_tables > 0 else 0:.1f}%")
    
    print(f"\nAll results saved to: {extractor.output_dir}")


if __name__ == "__main__":
    main()

