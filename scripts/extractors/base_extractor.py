"""
Base Extractor Class

Provides common functionality for all extractors
"""
import json
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any


class BaseExtractor(ABC):
    """Base class for all data extractors"""
    
    def __init__(self):
        self.extracted_data = []
        self.errors = []
    
    @abstractmethod
    def extract(self, page_data: Dict) -> Optional[Dict]:
        """
        Extract structured data from a page
        
        Args:
            page_data: Dictionary containing page text, tables, metadata
            
        Returns:
            Extracted data dictionary or None if extraction fails
        """
        pass
    
    def validate(self, data: Dict) -> bool:
        """
        Validate extracted data
        
        Args:
            data: Extracted data dictionary
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(data, dict):
            return False
        
        # Check for required metadata
        required_fields = ['source_book', 'source_page']
        for field in required_fields:
            if field not in data:
                return False
        
        return True
    
    def save(self, data: Dict, output_dir: Path, filename: str):
        """
        Save extracted data to JSON file
        
        Args:
            data: Extracted data dictionary
            output_dir: Output directory
            filename: Output filename
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def parse_dimension(self, dim_str: str) -> Optional[float]:
        """
        Parse dimension string to float (inches)
        
        Handles formats like:
        - "2-7/8" -> 2.875
        - "5'-9\"" -> 5.75
        - "3.5" -> 3.5
        
        Args:
            dim_str: Dimension string
            
        Returns:
            Float value in inches or None if parsing fails
        """
        if not dim_str or not isinstance(dim_str, str):
            return None
        
        dim_str = dim_str.strip()
        
        # Handle feet-inches format: "5'-9\""
        if "'" in dim_str:
            parts = dim_str.split("'")
            feet = float(parts[0]) if parts[0] else 0
            inches = 0
            if len(parts) > 1 and parts[1]:
                inch_part = parts[1].replace('"', '').strip()
                if inch_part:
                    # Handle fraction in inches
                    if '-' in inch_part:
                        whole, frac = inch_part.split('-', 1)
                        whole = float(whole) if whole else 0
                        if '/' in frac:
                            num, den = frac.split('/')
                            frac_val = float(num) / float(den)
                            inches = whole + frac_val
                        else:
                            inches = whole
                    else:
                        inches = float(inch_part)
            return feet * 12 + inches
        
        # Handle fraction format: "2-7/8"
        if '-' in dim_str and '/' in dim_str:
            parts = dim_str.split('-')
            whole = float(parts[0]) if parts[0] else 0
            if len(parts) > 1 and '/' in parts[1]:
                num, den = parts[1].split('/')
                frac = float(num) / float(den)
                return whole + frac
            return whole
        
        # Try direct float conversion
        try:
            return float(dim_str)
        except ValueError:
            return None
    
    def extract_tables_from_text(self, text: str) -> List[List[List[str]]]:
        """
        Extract table data from text (simplified parser)
        
        Args:
            text: Page text content
            
        Returns:
            List of tables (each table is a list of rows)
        """
        # This is a simplified parser - in production, use pdfplumber tables
        tables = []
        
        # Look for table markers
        table_pattern = r'Table \d+:(.*?)(?=Table \d+:|$)'
        matches = re.finditer(table_pattern, text, re.DOTALL)
        
        for match in matches:
            table_text = match.group(1)
            rows = []
            for line in table_text.split('\n'):
                if line.strip():
                    # Try to parse as list representation
                    if line.startswith('[') and line.endswith(']'):
                        try:
                            row = eval(line)  # Simple eval for list representation
                            if isinstance(row, list):
                                rows.append([str(cell) if cell is not None else '' for cell in row])
                        except:
                            pass
            if rows:
                tables.append(rows)
        
        return tables

