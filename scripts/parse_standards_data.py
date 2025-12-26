"""
Parse and Structure Standards Data
===================================
Parses extracted PDF text and creates structured JSON files for each standards category.
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    HAS_SPACY = True
except:
    HAS_SPACY = False
    print("WARNING: spacy not available - using basic regex parsing")

try:
    from fuzzywuzzy import fuzz
    HAS_FUZZYWUZZY = True
except:
    HAS_FUZZYWUZZY = False

try:
    import pint
    ureg = pint.UnitRegistry()
    HAS_PINT = True
except:
    HAS_PINT = False
    print("WARNING: pint not available - unit conversion disabled")


@dataclass
class StandardPart:
    """Represents a standard part from the books."""
    part_number: str
    description: str
    category: str
    specifications: Dict[str, Any]
    source_book: str
    source_page: int
    notes: Optional[str] = None


@dataclass
class DesignRule:
    """Represents a design rule or formula."""
    rule_id: str
    title: str
    description: str
    formula: Optional[str] = None
    parameters: List[str] = None
    source_book: str = ""
    source_page: int = 0
    category: str = ""


@dataclass
class Specification:
    """Represents a specification or requirement."""
    spec_id: str
    title: str
    requirement: str
    value: Optional[str] = None
    unit: Optional[str] = None
    source_book: str = ""
    source_page: int = 0


class StandardsParser:
    """Parse extracted standards data into structured format."""
    
    def __init__(self, extraction_dir: str = "output/standards_scan"):
        self.extraction_dir = Path(extraction_dir)
        self.output_dir = Path("data/standards/hpc")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Patterns for extraction
        self.part_number_pattern = re.compile(r'[A-Z]+\d+[A-Z]?\d*[-_]?[A-Z0-9]*', re.IGNORECASE)
        self.dimension_pattern = re.compile(r'(\d+\.?\d*)\s*(mm|in|inch|inches|ft|feet|"|\')', re.IGNORECASE)
        self.formula_pattern = re.compile(r'([A-Z][a-z]*\s*=\s*[^=]+)', re.IGNORECASE)
        
    def parse_all_books(self):
        """Parse all extracted standards books."""
        extracted_files = list(self.extraction_dir.glob("*_extracted.txt"))
        
        print(f"\n{'='*80}")
        print(f"PARSING STANDARDS DATA")
        print(f"{'='*80}")
        print(f"Found {len(extracted_files)} extracted files")
        
        all_parts = []
        all_rules = []
        all_specs = []
        
        for file_path in extracted_files:
            print(f"\nProcessing: {file_path.name}")
            book_name = self._extract_book_name(file_path.name)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse content
            parts = self._extract_parts(content, book_name)
            rules = self._extract_design_rules(content, book_name)
            specs = self._extract_specifications(content, book_name)
            
            all_parts.extend(parts)
            all_rules.extend(rules)
            all_specs.extend(specs)
            
            print(f"  ✓ Extracted {len(parts)} parts")
            print(f"  ✓ Extracted {len(rules)} design rules")
            print(f"  ✓ Extracted {len(specs)} specifications")
        
        # Save structured data
        self._save_parts(all_parts)
        self._save_rules(all_rules)
        self._save_specs(all_specs)
        
        # Generate summary
        self._generate_summary(all_parts, all_rules, all_specs)
        
        return {
            'parts': len(all_parts),
            'rules': len(all_rules),
            'specs': len(all_specs)
        }
    
    def _extract_book_name(self, filename: str) -> str:
        """Extract book name from filename."""
        if "BOOK I" in filename:
            return "Standards Book I"
        elif "BOOK II vol. I" in filename:
            return "Standards Book II Vol. I"
        elif "BOOK II vol. II" in filename:
            return "Standards Book II Vol. II"
        elif "BOOK III" in filename:
            return "Standards Book III"
        elif "BOOK IV" in filename:
            return "Standards Book IV"
        return "Unknown"
    
    def _extract_parts(self, content: str, book_name: str) -> List[StandardPart]:
        """Extract standard parts from content."""
        parts = []
        
        # Look for part numbers
        part_numbers = self.part_number_pattern.findall(content)
        
        # Group by context
        lines = content.split('\n')
        current_part = None
        
        for i, line in enumerate(lines):
            # Check for part number
            matches = self.part_number_pattern.findall(line)
            if matches:
                for part_num in matches:
                    # Skip if it's likely not a part number (too short, common words)
                    if len(part_num) < 3 or part_num.upper() in ['THE', 'AND', 'FOR']:
                        continue
                    
                    # Extract description from surrounding lines
                    description = self._extract_description(lines, i, 5)
                    specs = self._extract_specs_from_text(line + " " + description)
                    
                    part = StandardPart(
                        part_number=part_num.upper(),
                        description=description[:200] if description else "",
                        category=self._categorize_part(part_num, description),
                        specifications=specs,
                        source_book=book_name,
                        source_page=self._estimate_page_number(content, i)
                    )
                    parts.append(part)
        
        return parts
    
    def _extract_design_rules(self, content: str, book_name: str) -> List[DesignRule]:
        """Extract design rules and formulas."""
        rules = []
        
        # Look for formulas
        formulas = self.formula_pattern.findall(content)
        
        # Look for rule patterns
        rule_patterns = [
            re.compile(r'(?:shall|must|should|required|minimum|maximum)\s+([^\.]+)', re.IGNORECASE),
            re.compile(r'(?:standard|rule|procedure)\s*:?\s*([^\.]+)', re.IGNORECASE),
        ]
        
        lines = content.split('\n')
        rule_id = 1
        
        for i, line in enumerate(lines):
            # Check for formulas
            if '=' in line and any(op in line for op in ['+', '-', '*', '/', '^']):
                formula = line.strip()
                rule = DesignRule(
                    rule_id=f"RULE-{rule_id:04d}",
                    title=f"Formula from {book_name}",
                    description=formula,
                    formula=formula,
                    source_book=book_name,
                    source_page=self._estimate_page_number(content, i),
                    category="Formula"
                )
                rules.append(rule)
                rule_id += 1
            
            # Check for rule patterns
            for pattern in rule_patterns:
                matches = pattern.findall(line)
                if matches:
                    for match in matches:
                        rule = DesignRule(
                            rule_id=f"RULE-{rule_id:04d}",
                            title=match[:100],
                            description=match,
                            source_book=book_name,
                            source_page=self._estimate_page_number(content, i),
                            category="Requirement"
                        )
                        rules.append(rule)
                        rule_id += 1
        
        return rules
    
    def _extract_specifications(self, content: str, book_name: str) -> List[Specification]:
        """Extract specifications and requirements."""
        specs = []
        
        # Look for specification patterns
        spec_patterns = [
            re.compile(r'(\d+\.?\d*)\s*(mm|in|inch|inches|ft|feet|"|\'|psi|ksi|°F|°C)', re.IGNORECASE),
            re.compile(r'(?:min|max|minimum|maximum)\s*:?\s*(\d+\.?\d*)', re.IGNORECASE),
            re.compile(r'(?:size|diameter|length|width|height|thickness)\s*:?\s*(\d+\.?\d*)', re.IGNORECASE),
        ]
        
        lines = content.split('\n')
        spec_id = 1
        
        for i, line in enumerate(lines):
            # Extract dimensions
            dimensions = self.dimension_pattern.findall(line)
            if dimensions:
                for value, unit in dimensions:
                    spec = Specification(
                        spec_id=f"SPEC-{spec_id:04d}",
                        title=f"Dimension from {book_name}",
                        requirement=line[:200],
                        value=value,
                        unit=unit,
                        source_book=book_name,
                        source_page=self._estimate_page_number(content, i)
                    )
                    specs.append(spec)
                    spec_id += 1
        
        return specs
    
    def _extract_description(self, lines: List[str], index: int, context: int) -> str:
        """Extract description from surrounding lines."""
        start = max(0, index - context)
        end = min(len(lines), index + context + 1)
        return " ".join(lines[start:end])
    
    def _extract_specs_from_text(self, text: str) -> Dict[str, Any]:
        """Extract specifications from text."""
        specs = {}
        
        # Extract dimensions
        dimensions = self.dimension_pattern.findall(text)
        if dimensions:
            specs['dimensions'] = [f"{v} {u}" for v, u in dimensions]
        
        # Extract numbers that might be specifications
        numbers = re.findall(r'\d+\.?\d*', text)
        if numbers:
            specs['numeric_values'] = [float(n) for n in numbers[:10]]  # Limit to 10
        
        return specs
    
    def _categorize_part(self, part_num: str, description: str) -> str:
        """Categorize a part based on number and description."""
        desc_lower = description.lower()
        part_lower = part_num.lower()
        
        if any(word in desc_lower for word in ['mount', 'frame', 'support']):
            return "Structural"
        elif any(word in desc_lower for word in ['fan', 'motor', 'drive']):
            return "Mechanical"
        elif any(word in desc_lower for word in ['header', 'plug', 'nozzle']):
            return "Header"
        elif any(word in desc_lower for word in ['walkway', 'ladder', 'handrail']):
            return "Walkway"
        elif any(word in desc_lower for word in ['tube', 'bundle']):
            return "Tube Bundle"
        else:
            return "General"
    
    def _estimate_page_number(self, content: str, line_index: int) -> int:
        """Estimate page number from line index."""
        # Simple estimation: assume ~50 lines per page
        return (line_index // 50) + 1
    
    def _save_parts(self, parts: List[StandardPart]):
        """Save parts to JSON."""
        output_file = self.output_dir / "hpc_standard_parts.json"
        
        data = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'total_parts': len(parts),
                'source': 'HPC Standards Books I-IV'
            },
            'parts': [asdict(part) for part in parts]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved {len(parts)} parts to: {output_file}")
    
    def _save_rules(self, rules: List[DesignRule]):
        """Save design rules to JSON."""
        output_file = self.output_dir / "hpc_design_rules.json"
        
        data = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'total_rules': len(rules),
                'source': 'HPC Standards Books I-IV'
            },
            'rules': [asdict(rule) for rule in rules]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved {len(rules)} design rules to: {output_file}")
    
    def _save_specs(self, specs: List[Specification]):
        """Save specifications to JSON."""
        output_file = self.output_dir / "hpc_specifications.json"
        
        data = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'total_specs': len(specs),
                'source': 'HPC Standards Books I-IV'
            },
            'specifications': [asdict(spec) for spec in specs]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved {len(specs)} specifications to: {output_file}")
    
    def _generate_summary(self, parts: List[StandardPart], rules: List[DesignRule], specs: List[Specification]):
        """Generate summary report."""
        summary_file = self.output_dir / "extraction_summary.md"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# HPC Standards Extraction Summary\n\n")
            f.write(f"**Generated**: {datetime.now().isoformat()}\n\n")
            f.write(f"## Statistics\n\n")
            f.write(f"- **Total Parts**: {len(parts)}\n")
            f.write(f"- **Total Design Rules**: {len(rules)}\n")
            f.write(f"- **Total Specifications**: {len(specs)}\n\n")
            
            # Category breakdown
            categories = {}
            for part in parts:
                cat = part.category
                categories[cat] = categories.get(cat, 0) + 1
            
            f.write(f"## Parts by Category\n\n")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{cat}**: {count}\n")
        
        print(f"✓ Generated summary: {summary_file}")


def main():
    """Main function."""
    parser = StandardsParser()
    results = parser.parse_all_books()
    
    print(f"\n{'='*80}")
    print("EXTRACTION COMPLETE")
    print(f"{'='*80}")
    print(f"Parts: {results['parts']}")
    print(f"Rules: {results['rules']}")
    print(f"Specs: {results['specs']}")
    print(f"\nData saved to: data/standards/hpc/")


if __name__ == "__main__":
    main()

