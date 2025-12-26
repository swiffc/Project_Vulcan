"""
Location Table Extractor

Extracts location tables (like lifting lug locations, tube support spacing)
"""
import re
from typing import Dict, List, Optional
from .base_extractor import BaseExtractor


class LocationTableExtractor(BaseExtractor):
    """Extracts location tables from pages"""
    
    def extract(self, page_data: Dict) -> Optional[Dict]:
        """
        Extract location table data
        
        Args:
            page_data: Dictionary with 'text', 'tables', 'book', 'page'
            
        Returns:
            Extracted location data or None
        """
        text = page_data.get('text', '')
        tables = page_data.get('tables', [])
        book = page_data.get('book', '')
        page = page_data.get('page', 0)
        
        # Check if this is a location table page
        text_lower = text.lower()
        if not ('location' in text_lower or 'spacing' in text_lower or 'lug' in text_lower):
            return None
        
        result = {
            'metadata': {
                'source_book': book,
                'source_page': page,
                'extractor': 'LocationTableExtractor',
                'extraction_type': 'location_table'
            },
            'title': self._extract_title(text),
            'locations': []
        }
        
        # Determine table type
        if 'lifting lug' in text_lower and 'tube support' in text_lower:
            result['table_type'] = 'tube_support_lifting_lug'
            result['locations'] = self._extract_tube_support_lug_table(text, tables)
        elif 'lifting lug' in text_lower:
            result['table_type'] = 'lifting_lug_location'
            result['locations'] = self._extract_lifting_lug_table(text, tables)
        elif 'spacing' in text_lower:
            result['table_type'] = 'spacing_table'
            result['locations'] = self._extract_spacing_table(text, tables)
        else:
            result['table_type'] = 'general_location'
            result['locations'] = self._extract_general_location_table(text, tables)
        
        # Extract configuration info
        result['configuration'] = self._extract_configuration(text)
        
        # Extract requirements/notes
        result['requirements'] = self._extract_requirements(text)
        
        if not result['locations']:
            return None
        
        return result
    
    def _extract_title(self, text: str) -> Optional[str]:
        """Extract page title"""
        lines = text.split('\n')[:5]
        for line in lines:
            if line.strip() and len(line.strip()) > 10:
                return line.strip()[:200]
        return None
    
    def _extract_configuration(self, text: str) -> Dict:
        """Extract configuration information (fan count, draft type, etc.)"""
        config = {}
        text_lower = text.lower()
        
        # Fan count
        if 'one fan' in text_lower or '1 fan' in text_lower:
            config['fan_count'] = 1
        elif 'two fan' in text_lower or '2 fan' in text_lower:
            config['fan_count'] = 2
        elif 'three fan' in text_lower or '3 fan' in text_lower:
            config['fan_count'] = 3
        
        # Draft type
        if 'induced draft' in text_lower or 'nd' in text_lower:
            config['draft_type'] = 'induced_draft'
        elif 'forced draft' in text_lower or 'fd' in text_lower:
            config['draft_type'] = 'forced_draft'
        
        return config
    
    def _extract_requirements(self, text: str) -> Dict:
        """Extract requirements and notes"""
        requirements = {}
        
        # Look for maximum spacing
        spacing_match = re.search(r'max.*?spacing.*?(\d+[\'"]?\s*-?\s*\d+[\'"]?)', text, re.IGNORECASE)
        if spacing_match:
            spacing_str = spacing_match.group(1)
            spacing_ft = self.parse_dimension(spacing_str)
            if spacing_ft:
                requirements['max_spacing_ft'] = spacing_ft
        
        # Extract notes
        note_pattern = r'(\d+\.\s+[^\n]+)'
        notes = re.findall(note_pattern, text)
        if notes:
            requirements['notes'] = [n.strip() for n in notes[:5]]
        
        return requirements
    
    def _extract_tube_support_lug_table(self, text: str, tables: List) -> List[Dict]:
        """Extract tube support spacing and lifting lug location table"""
        locations = []
        
        # Look for table data in text
        # Pattern: tube length, supports, lug location
        pattern = r"(\d+)'\s+(\d+)\s+([\d'\"-]+)"
        matches = re.finditer(pattern, text)
        
        for match in matches:
            tube_length = int(match.group(1))
            num_supports = int(match.group(2))
            lug_location_str = match.group(3)
            lug_location = self.parse_dimension(lug_location_str)
            
            if lug_location:
                locations.append({
                    'tube_length_ft': tube_length,
                    'num_supports': num_supports,
                    'lug_location_from_cl_ft': lug_location,
                    'lug_quantity': 1  # Default
                })
        
        # Also try to parse from tables if available
        if tables:
            for table in tables:
                if len(table) > 1:  # Has header + data rows
                    for row in table[1:]:  # Skip header
                        if len(row) >= 3:
                            try:
                                tube_length_str = str(row[0]).strip()
                                lug_location_str = str(row[-1]).strip()
                                
                                # Parse tube length
                                tube_length = self._parse_tube_length(tube_length_str)
                                lug_location = self.parse_dimension(lug_location_str)
                                
                                if tube_length and lug_location:
                                    locations.append({
                                        'tube_length_ft': tube_length,
                                        'lug_location_from_cl_ft': lug_location,
                                        'lug_quantity': 1
                                    })
                            except:
                                continue
        
        return locations
    
    def _extract_lifting_lug_table(self, text: str, tables: List) -> List[Dict]:
        """Extract simple lifting lug location table"""
        locations = []
        
        # Pattern for tube length -> location mapping
        pattern = r"(\d+)['-]0\s+([\d'\"-]+)"
        matches = re.finditer(pattern, text)
        
        for match in matches:
            tube_length = int(match.group(1))
            location_str = match.group(2)
            location = self.parse_dimension(location_str)
            
            if location:
                locations.append({
                    'tube_length_ft': tube_length,
                    'lug_location_from_end_ft': location
                })
        
        return locations
    
    def _extract_spacing_table(self, text: str, tables: List) -> List[Dict]:
        """Extract spacing table"""
        locations = []
        
        # Similar to lifting lug table but for spacing
        pattern = r"(\d+)['-]0\s+([\d'\"-]+)"
        matches = re.finditer(pattern, text)
        
        for match in matches:
            dimension = int(match.group(1))
            spacing_str = match.group(2)
            spacing = self.parse_dimension(spacing_str)
            
            if spacing:
                locations.append({
                    'dimension_ft': dimension,
                    'spacing_ft': spacing
                })
        
        return locations
    
    def _extract_general_location_table(self, text: str, tables: List) -> List[Dict]:
        """Extract general location table"""
        # Fallback for other location tables
        return self._extract_lifting_lug_table(text, tables)
    
    def _parse_tube_length(self, length_str: str) -> Optional[float]:
        """Parse tube length string"""
        if not length_str:
            return None
        
        # Handle "6'-0" format
        if "'" in length_str:
            feet_part = length_str.split("'")[0]
            try:
                return float(feet_part)
            except:
                return None
        
        # Try direct float
        try:
            return float(length_str)
        except:
            return None

