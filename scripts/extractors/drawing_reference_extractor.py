"""
Drawing Reference Extractor

Extracts drawing lists, references, and part number cross-references
"""
import re
from typing import Dict, List, Optional
from .base_extractor import BaseExtractor


class DrawingReferenceExtractor(BaseExtractor):
    """Extracts drawing references and lists from pages"""
    
    def extract(self, page_data: Dict) -> Optional[Dict]:
        """
        Extract drawing reference data
        
        Args:
            page_data: Dictionary with 'text', 'tables', 'book', 'page'
            
        Returns:
            Extracted drawing reference data or None
        """
        text = page_data.get('text', '')
        tables = page_data.get('tables', [])
        book = page_data.get('book', '')
        page = page_data.get('page', 0)
        
        # Check if this is a drawing reference page
        text_lower = text.lower()
        if not any(kw in text_lower for kw in ['drawing', 'dwg', 'reference', 'ref', 'f 7ref', '7ref']):
            return None
        
        result = {
            'metadata': {
                'source_book': book,
                'source_page': page,
                'extractor': 'DrawingReferenceExtractor',
                'extraction_type': 'drawing_reference'
            },
            'title': self._extract_title(text),
            'references': []
        }
        
        # Determine reference type
        if 'f 7ref' in text_lower or '7ref' in text_lower:
            result['reference_type'] = 'drawing_list'
            result['references'] = self._extract_drawing_list(text, tables)
        elif 'index' in text_lower:
            result['reference_type'] = 'index'
            result['references'] = self._extract_index(text, tables)
        else:
            result['reference_type'] = 'general_reference'
            result['references'] = self._extract_general_references(text, tables)
        
        if not result['references']:
            return None
        
        return result
    
    def _extract_title(self, text: str) -> Optional[str]:
        """Extract page title"""
        lines = text.split('\n')[:5]
        for line in lines:
            if line.strip() and len(line.strip()) > 10:
                return line.strip()[:200]
        return None
    
    def _extract_drawing_list(self, text: str, tables: List) -> List[Dict]:
        """Extract drawing list (F 7REF format)"""
        references = []
        
        # Pattern: F 7REF## Description
        pattern = r'F\s+7REF(\d+)\s+([^\n]+)'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            ref_num = match.group(1)
            description = match.group(2).strip()
            
            references.append({
                'drawing_number': f'F 7REF{ref_num}',
                'reference_number': ref_num,
                'description': description,
                'type': 'drawing_reference'
            })
        
        # Also look for STDBOOK references
        stdbook_pattern = r'STDBOOK\s+7REF(\d+)\s+([^\n]+)'
        stdbook_matches = re.finditer(stdbook_pattern, text, re.IGNORECASE)
        
        for match in stdbook_matches:
            ref_num = match.group(1)
            description = match.group(2).strip()
            
            references.append({
                'drawing_number': f'STDBOOK 7REF{ref_num}',
                'reference_number': ref_num,
                'description': description,
                'type': 'stdbook_reference'
            })
        
        return references
    
    def _extract_index(self, text: str, tables: List) -> List[Dict]:
        """Extract index/reference table"""
        references = []
        
        # Look for table-like structures in text
        # Pattern: Item | Description | Page
        lines = text.split('\n')
        for line in lines:
            # Look for pipe-separated or tab-separated values
            if '|' in line or '\t' in line:
                parts = re.split(r'[|\t]+', line)
                if len(parts) >= 2:
                    item = parts[0].strip()
                    description = parts[1].strip()
                    
                    if item and description:
                        references.append({
                            'item': item,
                            'description': description,
                            'type': 'index_entry'
                        })
        
        return references
    
    def _extract_general_references(self, text: str, tables: List) -> List[Dict]:
        """Extract general references"""
        references = []
        
        # Look for any drawing number patterns
        drawing_pattern = r'([A-Z]+\s*\d+[A-Z]?[-/]?\d*[A-Z]?)\s+([^\n]+)'
        matches = re.finditer(drawing_pattern, text)
        
        for match in matches:
            drawing_num = match.group(1).strip()
            description = match.group(2).strip()
            
            references.append({
                'drawing_number': drawing_num,
                'description': description,
                'type': 'general_reference'
            })
        
        return references

