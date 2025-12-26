"""
Specification Table Extractor

Extracts part specifications, dimensions, materials, etc.
"""
import re
from typing import Dict, List, Optional
from .base_extractor import BaseExtractor


class SpecificationTableExtractor(BaseExtractor):
    """Extracts specification tables from pages"""
    
    def extract(self, page_data: Dict) -> Optional[Dict]:
        """
        Extract specification table data
        
        Args:
            page_data: Dictionary with 'text', 'tables', 'book', 'page'
            
        Returns:
            Extracted specification data or None
        """
        text = page_data.get('text', '')
        tables = page_data.get('tables', [])
        book = page_data.get('book', '')
        page = page_data.get('page', 0)
        
        # Check if this is a specification table page
        text_lower = text.lower()
        if not any(kw in text_lower for kw in ['specification', 'dimension', 'part', 'material', 'coating']):
            return None
        
        result = {
            'metadata': {
                'source_book': book,
                'source_page': page,
                'extractor': 'SpecificationTableExtractor',
                'extraction_type': 'specification_table'
            },
            'title': self._extract_title(text),
            'specifications': []
        }
        
        # Determine specification type
        if 'part' in text_lower and ('dimension' in text_lower or 'size' in text_lower):
            result['spec_type'] = 'part_specification'
            result['specifications'] = self._extract_part_specifications(text, tables)
        elif 'material' in text_lower or 'coating' in text_lower:
            result['spec_type'] = 'material_specification'
            result['specifications'] = self._extract_material_specifications(text, tables)
        else:
            result['spec_type'] = 'general_specification'
            result['specifications'] = self._extract_general_specifications(text, tables)
        
        if not result['specifications']:
            return None
        
        return result
    
    def _extract_title(self, text: str) -> Optional[str]:
        """Extract page title"""
        lines = text.split('\n')[:5]
        for line in lines:
            if line.strip() and len(line.strip()) > 10:
                return line.strip()[:200]
        return None
    
    def _extract_part_specifications(self, text: str, tables: List) -> List[Dict]:
        """Extract part specifications with dimensions"""
        specs = []
        
        # Look for part number patterns (W708, W709, etc.)
        part_pattern = r'([WOP]\d+)\s*\(?([^)]+)\)?\s*([\d'"/\s-]+)'
        matches = re.finditer(part_pattern, text, re.IGNORECASE)
        
        for match in matches:
            part_num = match.group(1).strip()
            description = match.group(2).strip() if match.group(2) else None
            dims_str = match.group(3).strip() if match.group(3) else None
            
            spec = {
                'part_number': part_num,
                'description': description
            }
            
            # Parse dimensions
            if dims_str:
                dims = self._parse_dimensions(dims_str)
                if dims:
                    spec['dimensions'] = dims
            
            # Look for block out dimensions
            block_out = self._extract_block_out_dimensions(text, part_num)
            if block_out:
                spec['block_out_dimensions'] = block_out
            
            specs.append(spec)
        
        # Also parse from tables
        if tables:
            for table in tables:
                if len(table) > 1:
                    # Try to identify header row
                    header_row = table[0]
                    part_col = None
                    dim_cols = []
                    
                    for i, cell in enumerate(header_row):
                        cell_lower = str(cell).lower()
                        if 'part' in cell_lower or 'number' in cell_lower:
                            part_col = i
                        elif 'dimension' in cell_lower or 'size' in cell_lower or 'thickness' in cell_lower or 'width' in cell_lower:
                            dim_cols.append(i)
                    
                    # Extract data rows
                    for row in table[1:]:
                        if part_col is not None and len(row) > part_col:
                            part_num = str(row[part_col]).strip()
                            if part_num and re.match(r'[WOP]\d+', part_num, re.IGNORECASE):
                                spec = {'part_number': part_num}
                                
                                # Extract dimensions
                                dims = {}
                                for col_idx in dim_cols:
                                    if col_idx < len(row):
                                        dim_value = self.parse_dimension(str(row[col_idx]))
                                        if dim_value:
                                            header_cell = str(header_row[col_idx]).lower()
                                            dim_name = self._extract_dimension_name(header_cell)
                                            dims[dim_name] = dim_value
                                
                                if dims:
                                    spec['dimensions'] = dims
                                
                                specs.append(spec)
        
        return specs
    
    def _extract_material_specifications(self, text: str, tables: List) -> List[Dict]:
        """Extract material/coating specifications"""
        specs = []
        
        # Look for material patterns
        material_pattern = r'(material|coating|paint)[:\s]+([^\n]+)'
        matches = re.finditer(material_pattern, text, re.IGNORECASE)
        
        for match in matches:
            spec_type = match.group(1).lower()
            spec_value = match.group(2).strip()
            
            specs.append({
                'type': spec_type,
                'value': spec_value
            })
        
        return specs
    
    def _extract_general_specifications(self, text: str, tables: List) -> List[Dict]:
        """Extract general specifications"""
        # Fallback to part specifications
        return self._extract_part_specifications(text, tables)
    
    def _parse_dimensions(self, dims_str: str) -> Optional[Dict]:
        """Parse dimension string into dictionary"""
        if not dims_str:
            return None
        
        dims = {}
        
        # Pattern: "3/4 X 5 1/2" or "0.75 X 5.5"
        pattern = r'([\d./\s-]+)\s*[xX×]\s*([\d./\s-]+)'
        match = re.search(pattern, dims_str)
        if match:
            dim1 = self.parse_dimension(match.group(1))
            dim2 = self.parse_dimension(match.group(2))
            if dim1 and dim2:
                dims['thickness_in'] = dim1
                dims['width_in'] = dim2
                return dims
        
        # Try individual dimensions
        dim_values = re.findall(r'[\d./\s-]+', dims_str)
        if len(dim_values) >= 2:
            dim1 = self.parse_dimension(dim_values[0])
            dim2 = self.parse_dimension(dim_values[1])
            if dim1 and dim2:
                dims['dimension_1_in'] = dim1
                dims['dimension_2_in'] = dim2
                return dims
        
        return None
    
    def _extract_block_out_dimensions(self, text: str, part_num: str) -> Optional[Dict]:
        """Extract block out dimensions for a part"""
        # Look for block out table near the part number
        block_out_pattern = rf'{re.escape(part_num)}[^\n]*\n[^\n]*([\d'"/\s-]+)\s+([\d'"/\s-]+)\s+([\d'"/\s-]+)'
        match = re.search(block_out_pattern, text, re.IGNORECASE)
        
        if match:
            a = self.parse_dimension(match.group(1))
            b = self.parse_dimension(match.group(2))
            c = self.parse_dimension(match.group(3))
            
            if a and b and c:
                return {
                    'A_in': a,
                    'B_in': b,
                    'C_in': c
                }
        
        return None
    
    def _extract_dimension_name(self, header: str) -> str:
        """Extract dimension name from header cell"""
        header_lower = header.lower()
        
        if 'thickness' in header_lower or 'thick' in header_lower:
            return 'thickness_in'
        elif 'width' in header_lower:
            return 'width_in'
        elif 'length' in header_lower:
            return 'length_in'
        elif 'diameter' in header_lower or 'dia' in header_lower:
            return 'diameter_in'
        else:
            return 'dimension_in'

