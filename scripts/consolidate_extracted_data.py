"""
Phase 5: Consolidation & Indexing

Consolidates related data:
- Merge location tables by configuration
- Group specifications by part type
- Index all extractions for search
"""
import sys
import json
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


class DataConsolidator:
    """Consolidates and indexes extracted data"""
    
    def __init__(self):
        self.location_tables = []
        self.specifications = []
        self.design_rules = []
        self.drawing_references = []
        self.index = []
    
    def load_structured_files(self, structured_dir: Path):
        """Load all structured JSON files"""
        print("Loading structured files...")
        
        json_files = list(structured_dir.rglob('*.json'))
        json_files = [f for f in json_files if f.name not in ['extraction_report.json', 'validation_report.json']]
        
        print(f"Found {len(json_files)} files to consolidate")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                extraction_type = data.get('metadata', {}).get('extraction_type')
                
                if extraction_type == 'location_table':
                    self.location_tables.append(data)
                elif extraction_type == 'specification_table':
                    self.specifications.append(data)
                elif extraction_type == 'design_rule':
                    self.design_rules.append(data)
                elif extraction_type == 'drawing_reference':
                    self.drawing_references.append(data)
                
                # Add to index
                self.index.append({
                    'file': str(json_file.relative_to(structured_dir)),
                    'book': data.get('metadata', {}).get('source_book'),
                    'page': data.get('metadata', {}).get('source_page'),
                    'type': extraction_type,
                    'title': data.get('title')
                })
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
    
    def consolidate_location_tables(self) -> Dict:
        """Consolidate location tables by configuration"""
        print("\nConsolidating location tables...")
        
        consolidated = {
            'metadata': {
                'total_tables': len(self.location_tables),
                'consolidation_date': str(Path(__file__).stat().st_mtime)
            },
            'by_configuration': defaultdict(list),
            'by_type': defaultdict(list)
        }
        
        for table in self.location_tables:
            config = table.get('configuration', {})
            table_type = table.get('table_type', 'unknown')
            
            # Create configuration key
            config_key = f"{config.get('draft_type', 'unknown')}_{config.get('fan_count', 'unknown')}"
            consolidated['by_configuration'][config_key].append(table)
            consolidated['by_type'][table_type].append(table)
        
        # Convert defaultdicts to regular dicts
        consolidated['by_configuration'] = dict(consolidated['by_configuration'])
        consolidated['by_type'] = dict(consolidated['by_type'])
        
        print(f"  Consolidated into {len(consolidated['by_configuration'])} configurations")
        print(f"  Grouped into {len(consolidated['by_type'])} types")
        
        return consolidated
    
    def consolidate_specifications(self) -> Dict:
        """Consolidate specifications by part type"""
        print("\nConsolidating specifications...")
        
        consolidated = {
            'metadata': {
                'total_specifications': len(self.specifications),
                'consolidation_date': str(Path(__file__).stat().st_mtime)
            },
            'by_type': defaultdict(list),
            'by_part_number': defaultdict(list)
        }
        
        for spec_table in self.specifications:
            spec_type = spec_table.get('spec_type', 'unknown')
            consolidated['by_type'][spec_type].append(spec_table)
            
            # Extract part numbers
            specs = spec_table.get('specifications', [])
            for spec in specs:
                part_num = spec.get('part_number')
                if part_num:
                    consolidated['by_part_number'][part_num].append(spec)
        
        # Convert defaultdicts to regular dicts
        consolidated['by_type'] = dict(consolidated['by_type'])
        consolidated['by_part_number'] = dict(consolidated['by_part_number'])
        
        print(f"  Consolidated into {len(consolidated['by_type'])} types")
        print(f"  Found {len(consolidated['by_part_number'])} unique part numbers")
        
        return consolidated
    
    def consolidate_design_rules(self) -> Dict:
        """Consolidate design rules by type"""
        print("\nConsolidating design rules...")
        
        consolidated = {
            'metadata': {
                'total_rules': len(self.design_rules),
                'consolidation_date': str(Path(__file__).stat().st_mtime)
            },
            'by_type': defaultdict(list)
        }
        
        for rule_table in self.design_rules:
            rule_type = rule_table.get('rule_type', 'unknown')
            consolidated['by_type'][rule_type].append(rule_table)
        
        # Convert defaultdict to regular dict
        consolidated['by_type'] = dict(consolidated['by_type'])
        
        print(f"  Consolidated into {len(consolidated['by_type'])} rule types")
        
        return consolidated
    
    def create_index(self) -> Dict:
        """Create searchable index"""
        print("\nCreating searchable index...")
        
        index = {
            'metadata': {
                'total_entries': len(self.index),
                'index_date': str(Path(__file__).stat().st_mtime)
            },
            'entries': self.index,
            'by_book': defaultdict(list),
            'by_type': defaultdict(list),
            'by_page_range': {}
        }
        
        # Group by book
        for entry in self.index:
            book = entry.get('book', 'unknown')
            index['by_book'][book].append(entry)
        
        # Group by type
        for entry in self.index:
            entry_type = entry.get('type', 'unknown')
            index['by_type'][entry_type].append(entry)
        
        # Convert defaultdicts to regular dicts
        index['by_book'] = dict(index['by_book'])
        index['by_type'] = dict(index['by_type'])
        
        print(f"  Created index with {len(self.index)} entries")
        print(f"  Indexed by {len(index['by_book'])} books")
        print(f"  Indexed by {len(index['by_type'])} types")
        
        return index
    
    def save_consolidated_data(self, output_dir: Path):
        """Save all consolidated data"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Consolidate location tables
        location_data = self.consolidate_location_tables()
        with open(output_dir / 'all_location_tables.json', 'w', encoding='utf-8') as f:
            json.dump(location_data, f, indent=2, ensure_ascii=False)
        
        # Consolidate specifications
        spec_data = self.consolidate_specifications()
        with open(output_dir / 'all_specifications.json', 'w', encoding='utf-8') as f:
            json.dump(spec_data, f, indent=2, ensure_ascii=False)
        
        # Consolidate design rules
        rule_data = self.consolidate_design_rules()
        with open(output_dir / 'all_design_rules.json', 'w', encoding='utf-8') as f:
            json.dump(rule_data, f, indent=2, ensure_ascii=False)
        
        # Create index
        index_data = self.create_index()
        with open(output_dir / 'extraction_index.json', 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nConsolidated data saved to: {output_dir}")


def main():
    """Main function"""
    base_dir = Path(__file__).parent.parent
    structured_dir = base_dir / "data" / "standards" / "hpc" / "structured"
    output_dir = base_dir / "data" / "standards" / "hpc" / "consolidated"
    
    print("=" * 80)
    print("Data Consolidation - Phase 5")
    print("=" * 80)
    
    consolidator = DataConsolidator()
    consolidator.load_structured_files(structured_dir)
    consolidator.save_consolidated_data(output_dir)
    
    print("\n" + "=" * 80)
    print("Consolidation Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()

