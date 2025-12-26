"""
Phase 1: Page Classification System

Classifies each page of the Standards Books by type based on:
- Title/header text patterns
- Table structure
- Content keywords
- Drawing references
"""
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from collections import Counter

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Page type keywords
LOCATION_TABLE_KEYWORDS = [
    'location', 'loc', 'spacing', 'lug', 'support', 'tube support',
    'lifting lug', 'fan spacing', 'mount location', 'centerline',
    'distance', 'position', 'placement'
]

SPECIFICATION_TABLE_KEYWORDS = [
    'specification', 'spec', 'dimension', 'part', 'standard part',
    'material', 'coating', 'thickness', 'width', 'length', 'diameter',
    'block out', 'size', 'weight', 'quantity'
]

DESIGN_RULE_KEYWORDS = [
    'formula', 'calculation', 'rule', 'procedure', 'design',
    'sizing', 'configuration', 'requirement', 'standard',
    'method', 'how to', 'step'
]

DRAWING_REFERENCE_KEYWORDS = [
    'drawing', 'dwg', 'reference', 'ref', 'index', 'list',
    'f 7ref', '7ref', 'stdbook', 'drawing number'
]

TEXT_PROCEDURE_KEYWORDS = [
    'note', 'instruction', 'procedure', 'check', 'verify',
    'requirement', 'shall', 'must', 'should'
]


class PageClassifier:
    """Classifies pages by type based on content analysis"""
    
    def __init__(self):
        self.classifications = []
    
    def classify_page(self, book: str, page_num: int, text: str, tables: List) -> Dict:
        """
        Classify a single page
        
        Args:
            book: Book name
            page_num: Page number
            text: Page text content
            tables: List of tables on page
            
        Returns:
            Classification dictionary
        """
        text_lower = text.lower()
        
        # Extract title/header (first few lines)
        lines = text.split('\n')[:10]
        title = ' '.join(lines[:3]).strip()
        
        # Count keywords
        location_score = sum(1 for kw in LOCATION_TABLE_KEYWORDS if kw in text_lower)
        spec_score = sum(1 for kw in SPECIFICATION_TABLE_KEYWORDS if kw in text_lower)
        design_score = sum(1 for kw in DESIGN_RULE_KEYWORDS if kw in text_lower)
        drawing_score = sum(1 for kw in DRAWING_REFERENCE_KEYWORDS if kw in text_lower)
        text_score = sum(1 for kw in TEXT_PROCEDURE_KEYWORDS if kw in text_lower)
        
        # Determine page type
        page_type = 'text_procedure'  # default
        subtype = None
        
        # Check for location tables
        if location_score > 0 and len(tables) > 0:
            if 'lifting lug' in text_lower and 'location' in text_lower:
                page_type = 'location_table'
                subtype = 'lifting_lug_location'
            elif 'tube support' in text_lower:
                page_type = 'location_table'
                subtype = 'tube_support_lifting_lug'
            elif 'spacing' in text_lower and 'location' in text_lower:
                page_type = 'location_table'
                subtype = 'spacing_location'
            elif location_score >= 2:
                page_type = 'location_table'
                subtype = 'general_location'
        
        # Check for specification tables
        elif spec_score > 0 and len(tables) > 0:
            if 'part' in text_lower and ('dimension' in text_lower or 'size' in text_lower):
                page_type = 'specification_table'
                subtype = 'part_specification'
            elif 'material' in text_lower or 'coating' in text_lower:
                page_type = 'specification_table'
                subtype = 'material_specification'
            elif spec_score >= 2:
                page_type = 'specification_table'
                subtype = 'general_specification'
        
        # Check for design rules
        elif design_score > 0:
            if 'formula' in text_lower or 'calculation' in text_lower:
                page_type = 'design_rule'
                subtype = 'formula_calculation'
            elif 'how to' in text_lower or 'procedure' in text_lower:
                page_type = 'design_rule'
                subtype = 'procedure'
            elif design_score >= 2:
                page_type = 'design_rule'
                subtype = 'general_rule'
        
        # Check for drawing references
        elif drawing_score > 0:
            if 'f 7ref' in text_lower or '7ref' in text_lower:
                page_type = 'drawing_reference'
                subtype = 'drawing_list'
            elif 'index' in text_lower or 'list' in text_lower:
                page_type = 'drawing_reference'
                subtype = 'reference_table'
            elif drawing_score >= 2:
                page_type = 'drawing_reference'
                subtype = 'general_reference'
        
        # Extract keywords for indexing
        all_keywords = []
        for kw_list in [LOCATION_TABLE_KEYWORDS, SPECIFICATION_TABLE_KEYWORDS, 
                       DESIGN_RULE_KEYWORDS, DRAWING_REFERENCE_KEYWORDS]:
            all_keywords.extend([kw for kw in kw_list if kw in text_lower])
        
        classification = {
            'book': book,
            'page': page_num,
            'type': page_type,
            'subtype': subtype,
            'title': title[:200] if title else None,
            'has_table': len(tables) > 0,
            'table_count': len(tables),
            'keywords': list(set(all_keywords[:10])),  # Top 10 unique keywords
            'scores': {
                'location': location_score,
                'specification': spec_score,
                'design_rule': design_score,
                'drawing_reference': drawing_score,
                'text_procedure': text_score
            }
        }
        
        return classification
    
    def classify_from_extracted_files(self, output_dir: Path) -> List[Dict]:
        """
        Classify all pages from extracted text files
        
        Args:
            output_dir: Directory containing extracted text files
            
        Returns:
            List of classifications
        """
        extracted_files = [
            'STANDARDS BOOK I_REV0_extracted.txt',
            'STANDARDS BOOK II vol. I_REV0_extracted.txt',
            'STANDARDS BOOK II vol. II_REV0_extracted.txt',
            'STANDARDS BOOK III_REV0_extracted.txt',
            'STANDARDS BOOK IV_REV0_extracted.txt',
        ]
        
        classifications = []
        
        for filename in extracted_files:
            filepath = output_dir / filename
            if not filepath.exists():
                print(f"Warning: File not found: {filepath}")
                continue
            
            print(f"Classifying pages from: {filename}")
            book_name = filename.replace('_extracted.txt', '')
            
            # Parse the extracted file
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split by page markers
            page_pattern = r'={60,}\s*PAGE\s+(\d+)\s*={60,}'
            pages = re.split(page_pattern, content)
            
            current_page = None
            current_text = []
            current_tables = []
            
            for i, section in enumerate(pages):
                if i == 0:
                    # Skip header
                    continue
                
                if section.isdigit():
                    # Save previous page if exists
                    if current_page is not None and current_text:
                        text = '\n'.join(current_text)
                        classification = self.classify_page(
                            book_name, current_page, text, current_tables
                        )
                        classifications.append(classification)
                    
                    # Start new page
                    current_page = int(section)
                    current_text = []
                    current_tables = []
                else:
                    # Extract tables from section
                    table_section = re.search(r'--- TABLES ON PAGE \d+ ---(.*?)(?=\n\n|\Z)', section, re.DOTALL)
                    if table_section:
                        # Parse table data (simplified - actual tables are in raw format)
                        table_lines = table_section.group(1).strip().split('\n')
                        # Count table markers
                        table_count = len([l for l in table_lines if l.startswith('Table ')])
                        current_tables = [{}] * table_count  # Placeholder
                    
                    # Add text (excluding table section)
                    text_section = re.sub(r'--- TABLES ON PAGE \d+ ---.*', '', section, flags=re.DOTALL)
                    current_text.append(text_section)
            
            # Save last page
            if current_page is not None and current_text:
                text = '\n'.join(current_text)
                classification = self.classify_page(
                    book_name, current_page, text, current_tables
                )
                classifications.append(classification)
            
            print(f"  Classified {len([c for c in classifications if c['book'] == book_name])} pages")
        
        return classifications
    
    def save_classifications(self, classifications: List[Dict], output_path: Path):
        """Save classifications to JSON file"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'total_pages': len(classifications),
                    'extracted_date': str(Path(__file__).stat().st_mtime),
                    'classifier_version': '1.0'
                },
                'classifications': classifications
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved {len(classifications)} classifications to: {output_path}")
        
        # Print summary
        type_counts = Counter(c['type'] for c in classifications)
        print("\nClassification Summary:")
        for page_type, count in type_counts.most_common():
            print(f"  {page_type}: {count}")


def main():
    """Main function"""
    output_dir = Path(__file__).parent.parent / "output" / "standards_scan"
    output_path = Path(__file__).parent.parent / "data" / "standards" / "hpc" / "page_classification.json"
    
    print("=" * 80)
    print("Page Classification System - Phase 1")
    print("=" * 80)
    
    classifier = PageClassifier()
    classifications = classifier.classify_from_extracted_files(output_dir)
    classifier.save_classifications(classifications, output_path)
    
    print("\n" + "=" * 80)
    print("Classification Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()

