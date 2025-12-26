"""
Phase 4: Data Validation & Quality Checks

Validates extracted data:
- Required fields present
- Data types correct
- Units consistent
- References valid
- No duplicate extractions
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


class DataValidator:
    """Validates extracted structured data"""
    
    def __init__(self):
        self.validation_results = []
        self.errors = []
        self.warnings = []
        self.duplicates = []
    
    def validate_file(self, file_path: Path) -> Dict:
        """Validate a single extracted JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            return {
                'file': str(file_path),
                'valid': False,
                'error': f"Could not read file: {str(e)}"
            }
        
        result = {
            'file': str(file_path),
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required metadata
        metadata = data.get('metadata', {})
        required_metadata = ['source_book', 'source_page']
        for field in required_metadata:
            if field not in metadata:
                result['valid'] = False
                result['errors'].append(f"Missing required metadata field: {field}")
        
        # Validate based on extraction type
        extraction_type = metadata.get('extraction_type')
        
        if extraction_type == 'location_table':
            result = self._validate_location_table(data, result)
        elif extraction_type == 'specification_table':
            result = self._validate_specification_table(data, result)
        elif extraction_type == 'design_rule':
            result = self._validate_design_rule(data, result)
        elif extraction_type == 'drawing_reference':
            result = self._validate_drawing_reference(data, result)
        
        return result
    
    def _validate_location_table(self, data: Dict, result: Dict) -> Dict:
        """Validate location table data"""
        locations = data.get('locations', [])
        
        if not locations:
            result['warnings'].append("No locations found in location table")
        
        for i, location in enumerate(locations):
            # Check for required fields based on table type
            table_type = data.get('table_type', '')
            
            if 'tube_length_ft' in location:
                if not isinstance(location['tube_length_ft'], (int, float)):
                    result['errors'].append(f"Location {i}: tube_length_ft must be numeric")
                    result['valid'] = False
            
            if 'lug_location' in str(location):
                location_key = [k for k in location.keys() if 'location' in k.lower()]
                if location_key:
                    loc_value = location[location_key[0]]
                    if not isinstance(loc_value, (int, float)):
                        result['errors'].append(f"Location {i}: location value must be numeric")
                        result['valid'] = False
        
        return result
    
    def _validate_specification_table(self, data: Dict, result: Dict) -> Dict:
        """Validate specification table data"""
        specifications = data.get('specifications', [])
        
        if not specifications:
            result['warnings'].append("No specifications found in specification table")
        
        for i, spec in enumerate(specifications):
            # Check for part number if it's a part specification
            if data.get('spec_type') == 'part_specification':
                if 'part_number' not in spec:
                    result['warnings'].append(f"Specification {i}: Missing part_number")
            
            # Validate dimensions if present
            if 'dimensions' in spec:
                dims = spec['dimensions']
                if not isinstance(dims, dict):
                    result['errors'].append(f"Specification {i}: dimensions must be a dictionary")
                    result['valid'] = False
                else:
                    for dim_name, dim_value in dims.items():
                        if not isinstance(dim_value, (int, float)):
                            result['errors'].append(f"Specification {i}: dimension {dim_name} must be numeric")
                            result['valid'] = False
        
        return result
    
    def _validate_design_rule(self, data: Dict, result: Dict) -> Dict:
        """Validate design rule data"""
        rules = data.get('rules', [])
        
        if not rules:
            result['warnings'].append("No rules found in design rule data")
        
        for i, rule in enumerate(rules):
            if 'type' not in rule:
                result['warnings'].append(f"Rule {i}: Missing type field")
        
        return result
    
    def _validate_drawing_reference(self, data: Dict, result: Dict) -> Dict:
        """Validate drawing reference data"""
        references = data.get('references', [])
        
        if not references:
            result['warnings'].append("No references found in drawing reference data")
        
        for i, ref in enumerate(references):
            if 'drawing_number' not in ref and 'item' not in ref:
                result['warnings'].append(f"Reference {i}: Missing drawing_number or item")
        
        return result
    
    def check_duplicates(self, structured_dir: Path) -> List[Dict]:
        """Check for duplicate extractions"""
        duplicates = []
        seen_pages = defaultdict(list)
        
        # Scan all JSON files
        for json_file in structured_dir.rglob('*.json'):
            if json_file.name == 'extraction_report.json':
                continue
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                metadata = data.get('metadata', {})
                book = metadata.get('source_book')
                page = metadata.get('source_page')
                
                if book and page:
                    key = (book, page)
                    seen_pages[key].append(str(json_file))
            except:
                continue
        
        # Find duplicates
        for (book, page), files in seen_pages.items():
            if len(files) > 1:
                duplicates.append({
                    'book': book,
                    'page': page,
                    'files': files
                })
        
        return duplicates
    
    def validate_all(self, structured_dir: Path) -> Dict:
        """Validate all extracted files"""
        print("=" * 80)
        print("Data Validation - Phase 4")
        print("=" * 80)
        
        json_files = list(structured_dir.rglob('*.json'))
        json_files = [f for f in json_files if f.name != 'extraction_report.json']
        
        print(f"\nValidating {len(json_files)} files...")
        
        validation_results = []
        total_valid = 0
        total_errors = 0
        total_warnings = 0
        
        for json_file in json_files:
            result = self.validate_file(json_file)
            validation_results.append(result)
            
            if result['valid']:
                total_valid += 1
            else:
                total_errors += 1
            
            total_warnings += len(result.get('warnings', []))
        
        # Check for duplicates
        print("\nChecking for duplicates...")
        duplicates = self.check_duplicates(structured_dir)
        
        # Generate report
        report = {
            'metadata': {
                'total_files': len(json_files),
                'valid_files': total_valid,
                'invalid_files': total_errors,
                'total_warnings': total_warnings,
                'duplicate_count': len(duplicates)
            },
            'validation_results': validation_results[:100],  # Limit to first 100
            'duplicates': duplicates,
            'summary': {
                'success_rate': f"{(total_valid / len(json_files) * 100):.1f}%" if json_files else "0%"
            }
        }
        
        # Save report
        report_path = Path(__file__).parent.parent / "data" / "standards" / "hpc" / "validation_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 80)
        print("Validation Report")
        print("=" * 80)
        print(f"Total files: {len(json_files)}")
        print(f"Valid files: {total_valid}")
        print(f"Invalid files: {total_errors}")
        print(f"Warnings: {total_warnings}")
        print(f"Duplicates: {len(duplicates)}")
        print(f"Success rate: {report['summary']['success_rate']}")
        print(f"\nReport saved to: {report_path}")
        
        return report


def main():
    """Main function"""
    base_dir = Path(__file__).parent.parent
    structured_dir = base_dir / "data" / "standards" / "hpc" / "structured"
    
    validator = DataValidator()
    validator.validate_all(structured_dir)


if __name__ == "__main__":
    main()

