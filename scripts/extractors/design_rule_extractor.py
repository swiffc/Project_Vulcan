"""
Design Rule Extractor

Extracts formulas, calculations, design procedures, and rules
"""
import re
from typing import Dict, List, Optional
from .base_extractor import BaseExtractor


class DesignRuleExtractor(BaseExtractor):
    """Extracts design rules, formulas, and procedures from pages"""
    
    def extract(self, page_data: Dict) -> Optional[Dict]:
        """
        Extract design rule data
        
        Args:
            page_data: Dictionary with 'text', 'tables', 'book', 'page'
            
        Returns:
            Extracted design rule data or None
        """
        text = page_data.get('text', '')
        tables = page_data.get('tables', [])
        book = page_data.get('book', '')
        page = page_data.get('page', 0)
        
        # Check if this is a design rule page
        text_lower = text.lower()
        if not any(kw in text_lower for kw in ['formula', 'calculation', 'rule', 'procedure', 'how to', 'design']):
            return None
        
        result = {
            'metadata': {
                'source_book': book,
                'source_page': page,
                'extractor': 'DesignRuleExtractor',
                'extraction_type': 'design_rule'
            },
            'title': self._extract_title(text),
            'rules': []
        }
        
        # Determine rule type
        if 'formula' in text_lower or 'calculation' in text_lower:
            result['rule_type'] = 'formula_calculation'
            result['rules'] = self._extract_formulas(text)
        elif 'how to' in text_lower or 'procedure' in text_lower or 'step' in text_lower:
            result['rule_type'] = 'procedure'
            result['rules'] = self._extract_procedures(text)
        else:
            result['rule_type'] = 'general_rule'
            result['rules'] = self._extract_general_rules(text)
        
        if not result['rules']:
            return None
        
        return result
    
    def _extract_title(self, text: str) -> Optional[str]:
        """Extract page title"""
        lines = text.split('\n')[:5]
        for line in lines:
            if line.strip() and len(line.strip()) > 10:
                return line.strip()[:200]
        return None
    
    def _extract_formulas(self, text: str) -> List[Dict]:
        """Extract mathematical formulas and calculations"""
        formulas = []
        
        # Look for formula patterns
        # Pattern: Variable = expression
        formula_pattern = r'([A-Z][A-Za-z0-9_]*)\s*=\s*([^\n]+)'
        matches = re.finditer(formula_pattern, text)
        
        for match in matches:
            variable = match.group(1).strip()
            expression = match.group(2).strip()
            
            formulas.append({
                'variable': variable,
                'expression': expression,
                'type': 'formula'
            })
        
        # Look for calculation examples
        calc_pattern = r'(\d+\.?\d*)\s*([+\-*/×÷])\s*(\d+\.?\d*)\s*=\s*(\d+\.?\d*)'
        calc_matches = re.finditer(calc_pattern, text)
        
        for match in calc_matches:
            formulas.append({
                'calculation': f"{match.group(1)} {match.group(2)} {match.group(3)} = {match.group(4)}",
                'type': 'calculation'
            })
        
        return formulas
    
    def _extract_procedures(self, text: str) -> List[Dict]:
        """Extract step-by-step procedures"""
        procedures = []
        
        # Look for numbered steps
        step_pattern = r'(?:Step\s+)?(\d+)\.\s+([^\n]+)'
        matches = re.finditer(step_pattern, text, re.IGNORECASE)
        
        for match in matches:
            step_num = int(match.group(1))
            step_text = match.group(2).strip()
            
            procedures.append({
                'step_number': step_num,
                'description': step_text,
                'type': 'procedure_step'
            })
        
        # Look for "How to" sections
        how_to_pattern = r'how\s+to\s+([^\n:]+)[:\s]+([^\n]+)'
        how_matches = re.finditer(how_to_pattern, text, re.IGNORECASE)
        
        for match in how_matches:
            procedures.append({
                'procedure': match.group(1).strip(),
                'description': match.group(2).strip(),
                'type': 'how_to'
            })
        
        return procedures
    
    def _extract_general_rules(self, text: str) -> List[Dict]:
        """Extract general design rules and requirements"""
        rules = []
        
        # Look for requirement statements
        requirement_pattern = r'(shall|must|should|required|minimum|maximum)\s+([^\n.]+)'
        matches = re.finditer(requirement_pattern, text, re.IGNORECASE)
        
        for match in matches:
            requirement_type = match.group(1).lower()
            requirement_text = match.group(2).strip()
            
            rules.append({
                'requirement_type': requirement_type,
                'description': requirement_text,
                'type': 'requirement'
            })
        
        # Look for configuration rules
        config_pattern = r'if\s+([^\n,]+),\s+then\s+([^\n.]+)'
        config_matches = re.finditer(config_pattern, text, re.IGNORECASE)
        
        for match in config_matches:
            rules.append({
                'condition': match.group(1).strip(),
                'action': match.group(2).strip(),
                'type': 'conditional_rule'
            })
        
        return rules

