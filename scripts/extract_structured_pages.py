"""
Phase 3: Page-by-Page Processing Script

Main orchestrator that:
1. Loads page classification
2. Routes each page to appropriate extractor
3. Validates extracted data
4. Saves structured JSON per page/category
5. Generates extraction report
"""
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.extractors import (
    LocationTableExtractor,
    SpecificationTableExtractor,
    DesignRuleExtractor,
    DrawingReferenceExtractor
)


class StructuredPageExtractor:
    """Main orchestrator for structured page extraction"""
    
    def __init__(self):
        self.extractors = {
            'location_table': LocationTableExtractor(),
            'specification_table': SpecificationTableExtractor(),
            'design_rule': DesignRuleExtractor(),
            'drawing_reference': DrawingReferenceExtractor(),
        }
        self.extraction_stats = defaultdict(int)
        self.errors = []
    
    def load_classifications(self, classification_file: Path) -> List[Dict]:
        """Load page classifications"""
        if not classification_file.exists():
            print(f"Error: Classification file not found: {classification_file}")
            print("Please run scripts/classify_standards_pages.py first")
            return []
        
        with open(classification_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get('classifications', [])
    
    def load_page_content(self, output_dir: Path, book: str, page_num: int) -> Optional[Dict]:
        """Load page content from extracted text file"""
        # Find the extracted file for this book
        # Map book names from classification to actual filenames
        book_to_file = {
            'STANDARDS BOOK I_REV0': 'STANDARDS BOOK I_REV0_extracted.txt',
            'STANDARDS BOOK II vol. I_REV0': 'STANDARDS BOOK II vol. I_REV0_extracted.txt',
            'STANDARDS BOOK II vol. II_REV0': 'STANDARDS BOOK II vol. II_REV0_extracted.txt',
            'STANDARDS BOOK III_REV0': 'STANDARDS BOOK III_REV0_extracted.txt',
            'STANDARDS BOOK IV_REV0': 'STANDARDS BOOK IV_REV0_extracted.txt',
        }
        
        filename = book_to_file.get(book)
        if not filename:
            # Fallback: try to construct filename
            filename = book.replace(' ', '_') + '_extracted.txt'
        
        filepath = output_dir / filename
        
        if not filepath.exists():
            return None
        
        # Read and parse the file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the specific page
        page_pattern = rf'={60,}\s*PAGE\s+{page_num}\s*={60,}'
        match = re.search(page_pattern, content)
        
        if not match:
            return None
        
        # Extract page content
        start_pos = match.end()
        next_page_match = re.search(rf'={60,}\s*PAGE\s+{page_num + 1}\s*={60,}', content[start_pos:])
        
        if next_page_match:
            page_text = content[start_pos:start_pos + next_page_match.start()]
        else:
            page_text = content[start_pos:]
        
        # Extract tables
        tables = []
        table_section = re.search(r'--- TABLES ON PAGE \d+ ---(.*?)(?=\n\n|\Z)', page_text, re.DOTALL)
        if table_section:
            # Parse table data
            table_lines = table_section.group(1).strip().split('\n')
            current_table = []
            for line in table_lines:
                if line.startswith('Table '):
                    if current_table:
                        tables.append(current_table)
                    current_table = []
                elif line.strip() and (line.startswith('[') or line.startswith("'")):
                    # Try to parse as table row
                    try:
                        # Simple parsing - in production use proper table parser
                        if line.startswith('[') and line.endswith(']'):
                            row = eval(line)  # Simple eval for list representation
                            if isinstance(row, list):
                                current_table.append([str(cell) if cell is not None else '' for cell in row])
                    except:
                        pass
            if current_table:
                tables.append(current_table)
        
        return {
            'book': book,
            'page': page_num,
            'text': page_text,
            'tables': tables
        }
    
    def extract_page(self, classification: Dict, output_dir: Path) -> Optional[Dict]:
        """Extract structured data from a single page"""
        page_type = classification.get('type')
        book = classification.get('book')
        page_num = classification.get('page')
        
        # Load page content
        page_data = self.load_page_content(output_dir, book, page_num)
        if not page_data:
            self.errors.append(f"Could not load page {page_num} from {book}")
            return None
        
        # Route to appropriate extractor
        extractor = self.extractors.get(page_type)
        if not extractor:
            # No extractor for this type, skip
            return None
        
        try:
            extracted_data = extractor.extract(page_data)
            if extracted_data and extractor.validate(extracted_data):
                self.extraction_stats[page_type] += 1
                return extracted_data
            else:
                self.errors.append(f"Extraction failed or validation failed for {book} page {page_num}")
                return None
        except Exception as e:
            self.errors.append(f"Error extracting {book} page {page_num}: {str(e)}")
            return None
    
    def save_extracted_data(self, extracted_data: Dict, output_base: Path, classification: Dict):
        """Save extracted data to appropriate directory"""
        page_type = classification.get('type')
        book = classification.get('book')
        page_num = classification.get('page')
        
        # Create output directory for this type
        type_dir = output_base / 'structured' / page_type.replace('_', '-')
        type_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename
        book_safe = book.replace(' ', '_').replace('/', '_')
        filename = f"page_{page_num}_{book_safe}_{extracted_data.get('metadata', {}).get('extraction_type', 'data')}.json"
        
        # Save
        with open(type_dir / filename, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, indent=2, ensure_ascii=False)
    
    def process_all_pages(self, classification_file: Path, output_dir: Path, output_base: Path):
        """Process all classified pages"""
        print("=" * 80)
        print("Structured Page Extraction - Phase 3")
        print("=" * 80)
        
        # Load classifications
        print("\nLoading page classifications...")
        classifications = self.load_classifications(classification_file)
        print(f"Loaded {len(classifications)} page classifications")
        
        # Filter to pages with extractors
        extractable_types = set(self.extractors.keys())
        extractable_pages = [c for c in classifications if c.get('type') in extractable_types]
        print(f"Found {len(extractable_pages)} pages with extractable types")
        
        # Process each page
        print("\nProcessing pages...")
        total_extracted = 0
        
        for i, classification in enumerate(extractable_pages, 1):
            if i % 50 == 0:
                print(f"  Processed {i}/{len(extractable_pages)} pages...")
            
            extracted_data = self.extract_page(classification, output_dir)
            
            if extracted_data:
                self.save_extracted_data(extracted_data, output_base, classification)
                total_extracted += 1
        
        # Generate report
        self.generate_report(output_base, total_extracted, len(extractable_pages))
    
    def generate_report(self, output_base: Path, total_extracted: int, total_pages: int):
        """Generate extraction report"""
        report = {
            'metadata': {
                'total_pages_processed': total_pages,
                'total_extracted': total_extracted,
                'success_rate': f"{(total_extracted / total_pages * 100):.1f}%" if total_pages > 0 else "0%"
            },
            'statistics_by_type': dict(self.extraction_stats),
            'errors': self.errors[:100],  # Limit to first 100 errors
            'error_count': len(self.errors)
        }
        
        report_path = output_base / 'structured' / 'extraction_report.json'
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 80)
        print("Extraction Report")
        print("=" * 80)
        print(f"Total pages processed: {total_pages}")
        print(f"Total extracted: {total_extracted}")
        print(f"Success rate: {report['metadata']['success_rate']}")
        print(f"\nExtractions by type:")
        for page_type, count in self.extraction_stats.items():
            print(f"  {page_type}: {count}")
        print(f"\nErrors: {len(self.errors)}")
        print(f"\nReport saved to: {report_path}")


def main():
    """Main function"""
    base_dir = Path(__file__).parent.parent
    classification_file = base_dir / "data" / "standards" / "hpc" / "page_classification.json"
    output_dir = base_dir / "output" / "standards_scan"
    output_base = base_dir / "data" / "standards" / "hpc"
    
    extractor = StructuredPageExtractor()
    extractor.process_all_pages(classification_file, output_dir, output_base)


if __name__ == "__main__":
    main()

