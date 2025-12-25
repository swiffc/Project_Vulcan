"""
Natural Language CAD Parser
Converts user descriptions to precise CAD parameters.

Examples:
- "6 inch flange" → {"diameter": 0.1524, "unit": "meters"}
- "quarter inch thick" → {"thickness": 0.00635, "unit": "meters"}
- "100mm diameter, 50mm tall" → {"diameter": 0.1, "height": 0.05, "unit": "meters"}
- "3/8 bolt" → {"diameter": 0.009525, "type": "fastener"}
"""

import re
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from fractions import Fraction


@dataclass
class CADParameter:
    """Parsed CAD parameter with units."""
    value: float
    unit: str  # "meters", "cm", "degrees"
    parameter_type: str  # "diameter", "length", "thickness", "angle"
    confidence: float = 1.0
    original_text: str = ""


class CADNLPParser:
    """Parse natural language into CAD parameters."""
    
    # Common dimension patterns
    PATTERNS = {
        # Fractions: "1/2 inch", "3/8", "1-1/4"
        "fraction": re.compile(
            r"(\d+)?\s*-?\s*(\d+)\s*/\s*(\d+)\s*(inch|in|\")?",
            re.IGNORECASE
        ),
        
        # Decimal with units: "6.5 inches", "100mm", "2.5 cm"
        "decimal_unit": re.compile(
            r"(\d+\.?\d*)\s*(mm|millimeters?|cm|centimeters?|m|meters?|in|inch|inches|ft|feet|'|\")?",
            re.IGNORECASE
        ),
        
        # Named dimensions: "six inches", "quarter inch"
        "written_numbers": re.compile(
            r"(quarter|half|one|two|three|four|five|six|eight|ten|twelve)\s+(inch|mm|cm)",
            re.IGNORECASE
        ),
        
        # Pipe sizes: "6 inch pipe", "2 inch sch 40"
        "pipe_size": re.compile(
            r"(\d+\.?\d*)\s*(?:inch|in|\")\s+(?:pipe|sch|schedule|nps)",
            re.IGNORECASE
        ),
        
        # Angles: "90 degrees", "45°", "30 deg"
        "angle": re.compile(
            r"(\d+\.?\d*)\s*(degrees?|deg|°)",
            re.IGNORECASE
        ),
        
        # Thickness: "1/4 thick", "3mm wall"
        "thickness": re.compile(
            r"(\d+\.?\d*|\d+\s*/\s*\d+)\s*(inch|in|mm)?\s*(thick|thickness|wall|gauge)",
            re.IGNORECASE
        ),
        
        # Diameter: "6 inch OD", "100mm ID", "Ø50"
        "diameter": re.compile(
            r"(?:Ø|dia|diameter|OD|ID|od|id)?\s*(\d+\.?\d*)\s*(mm|inch|in|\")?(?:\s*(?:OD|ID|dia|diameter))?",
            re.IGNORECASE
        ),
    }
    
    # Word to number mapping
    WORD_TO_NUM = {
        "quarter": 0.25,
        "half": 0.5,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "eight": 8,
        "ten": 10,
        "twelve": 12,
    }
    
    def __init__(self, target_software: str = "solidworks"):
        """
        Initialize parser.
        
        Args:
            target_software: "solidworks" (meters) or "inventor" (cm)
        """
        self.target_software = target_software.lower()
        self.target_unit = "meters" if target_software == "solidworks" else "cm"
    
    def parse(self, text: str) -> Dict[str, CADParameter]:
        """
        Parse natural language text into CAD parameters.
        
        Args:
            text: User input like "6 inch flange, 150# rating, 1/4 inch thick"
            
        Returns:
            Dict of parameter_name: CADParameter
            
        Example:
            >>> parser = CADNLPParser("solidworks")
            >>> params = parser.parse("6 inch flange, quarter inch thick")
            >>> params["nominal_size"].value  # 0.1524 (meters)
            >>> params["thickness"].value  # 0.00635 (meters)
        """
        params = {}
        
        # Extract angles
        for match in self.PATTERNS["angle"].finditer(text):
            value = float(match.group(1))
            params["angle"] = CADParameter(
                value=value,
                unit="degrees",
                parameter_type="angle",
                confidence=0.95,
                original_text=match.group(0)
            )
        
        # Extract thickness
        for match in self.PATTERNS["thickness"].finditer(text):
            raw_value = match.group(1)
            unit = match.group(2) or "inch"
            
            value_inches = self._parse_value(raw_value, unit)
            value_target = self._convert_to_target(value_inches, "inch")
            
            params["thickness"] = CADParameter(
                value=value_target,
                unit=self.target_unit,
                parameter_type="thickness",
                confidence=0.9,
                original_text=match.group(0)
            )
        
        # Extract diameter/size
        for match in self.PATTERNS["diameter"].finditer(text):
            value = float(match.group(1))
            unit = match.group(2) or "inch"
            
            value_target = self._convert_to_target(value, unit)
            
            # Determine if OD or ID
            param_name = "diameter"
            if "OD" in match.group(0).upper():
                param_name = "outer_diameter"
            elif "ID" in match.group(0).upper():
                param_name = "inner_diameter"
            
            params[param_name] = CADParameter(
                value=value_target,
                unit=self.target_unit,
                parameter_type="diameter",
                confidence=0.9,
                original_text=match.group(0)
            )
        
        # Extract pipe sizes
        for match in self.PATTERNS["pipe_size"].finditer(text):
            nps = float(match.group(1))
            params["nominal_size"] = CADParameter(
                value=self._convert_to_target(nps, "inch"),
                unit=self.target_unit,
                parameter_type="pipe_size",
                confidence=0.95,
                original_text=match.group(0)
            )
        
        # Extract fractions
        for match in self.PATTERNS["fraction"].finditer(text):
            whole = int(match.group(1)) if match.group(1) else 0
            num = int(match.group(2))
            den = int(match.group(3))
            unit = match.group(4) or "inch"
            
            value_inches = whole + Fraction(num, den)
            value_target = self._convert_to_target(float(value_inches), unit)
            
            # Guess parameter type from context
            param_type = self._guess_parameter_type(match.group(0), text)
            
            params[param_type] = CADParameter(
                value=value_target,
                unit=self.target_unit,
                parameter_type=param_type,
                confidence=0.85,
                original_text=match.group(0)
            )
        
        # Extract decimal dimensions
        for match in self.PATTERNS["decimal_unit"].finditer(text):
            value = float(match.group(1))
            unit = match.group(2) or "inch"
            
            # Skip if already captured
            if any(match.group(0) in p.original_text for p in params.values()):
                continue
            
            value_target = self._convert_to_target(value, unit)
            param_type = self._guess_parameter_type(match.group(0), text)
            
            params[param_type] = CADParameter(
                value=value_target,
                unit=self.target_unit,
                parameter_type=param_type,
                confidence=0.8,
                original_text=match.group(0)
            )
        
        # Extract written numbers
        for match in self.PATTERNS["written_numbers"].finditer(text):
            word = match.group(1).lower()
            unit = match.group(2).lower()
            
            value = self.WORD_TO_NUM.get(word, 0)
            value_target = self._convert_to_target(value, unit)
            
            param_type = self._guess_parameter_type(match.group(0), text)
            
            params[param_type] = CADParameter(
                value=value_target,
                unit=self.target_unit,
                parameter_type=param_type,
                confidence=0.9,
                original_text=match.group(0)
            )
        
        return params
    
    def _parse_value(self, value_str: str, unit: str) -> float:
        """Parse a value string that might be a fraction."""
        if "/" in value_str:
            # Handle fractions: "1-1/4" or "3/8"
            if "-" in value_str:
                whole, frac = value_str.split("-")
                whole_val = float(whole.strip())
                frac_val = float(Fraction(frac.strip()))
                return whole_val + frac_val
            else:
                return float(Fraction(value_str.strip()))
        else:
            return float(value_str)
    
    def _convert_to_target(self, value: float, from_unit: str) -> float:
        """Convert a value to target CAD system units."""
        # Normalize unit name
        from_unit = from_unit.lower().strip('"\'')
        
        # Convert to inches first (common baseline)
        if from_unit in ["in", "inch", "inches", '"']:
            value_inches = value
        elif from_unit in ["mm", "millimeter", "millimeters"]:
            value_inches = value / 25.4
        elif from_unit in ["cm", "centimeter", "centimeters"]:
            value_inches = value / 2.54
        elif from_unit in ["m", "meter", "meters"]:
            value_inches = value / 0.0254
        elif from_unit in ["ft", "feet", "foot", "'"]:
            value_inches = value * 12
        else:
            value_inches = value  # Assume inches
        
        # Convert to target system
        if self.target_software == "solidworks":
            # SolidWorks uses METERS
            return value_inches * 0.0254
        elif self.target_software == "inventor":
            # Inventor uses CENTIMETERS
            return value_inches * 2.54
        else:
            return value_inches
    
    def _guess_parameter_type(self, matched_text: str, full_text: str) -> str:
        """Guess parameter type from context."""
        matched_lower = matched_text.lower()
        full_lower = full_text.lower()
        
        # Check surrounding context
        context_start = max(0, full_lower.find(matched_lower) - 20)
        context_end = min(len(full_lower), full_lower.find(matched_lower) + len(matched_lower) + 20)
        context = full_lower[context_start:context_end]
        
        # Diameter indicators
        if any(word in context for word in ["diameter", "dia", "od", "id", "ø", "size", "nps"]):
            return "diameter"
        
        # Thickness indicators
        if any(word in context for word in ["thick", "wall", "gauge", "t="]):
            return "thickness"
        
        # Length indicators
        if any(word in context for word in ["long", "length", "height", "tall", "l="]):
            return "length"
        
        # Radius
        if any(word in context for word in ["radius", "rad", "r="]):
            return "radius"
        
        # Default to generic dimension
        return "dimension"
    
    def extract_material(self, text: str) -> Optional[str]:
        """Extract material specification from text."""
        materials = {
            # Common materials
            "steel": r"\b(steel|a36|carbon\s*steel)\b",
            "stainless": r"\b(stainless|304|316|ss)\b",
            "aluminum": r"\b(aluminum|aluminium|6061|al)\b",
            "copper": r"\b(copper|cu)\b",
            "brass": r"\b(brass)\b",
            
            # ASTM specs
            "ASTM A105": r"\b(a105|a-105)\b",
            "ASTM A36": r"\b(a36|a-36)\b",
            "ASTM A516": r"\b(a516|sa-516)\b",
            "304 Stainless": r"\b(304|ss304|304ss)\b",
            "316 Stainless": r"\b(316|ss316|316ss)\b",
            "6061-T6": r"\b(6061|6061-t6)\b",
        }
        
        text_lower = text.lower()
        for material, pattern in materials.items():
            if re.search(pattern, text_lower):
                return material
        
        return None
    
    def extract_standard(self, text: str) -> Optional[str]:
        """Extract engineering standard from text."""
        standards = {
            "ASME B16.5": r"\b(b16\.5|b16-5|ansi\s*b16\.5)\b",
            "ASME B16.9": r"\b(b16\.9|b16-9)\b",
            "ASME B31.3": r"\b(b31\.3|b31-3)\b",
            "ASME VIII": r"\b(asme\s*viii|asme\s*8|section\s*viii)\b",
            "AWS D1.1": r"\b(aws\s*d1\.1|d1\.1)\b",
            "AISC": r"\b(aisc)\b",
        }
        
        text_upper = text.upper()
        for standard, pattern in standards.items():
            if re.search(pattern, text_upper):
                return standard
        
        return None
    
    def format_for_cad(self, params: Dict[str, CADParameter]) -> str:
        """Format parsed parameters for CAD tool input."""
        lines = []
        for name, param in params.items():
            lines.append(f"{name}: {param.value:.6f} {param.unit} (from '{param.original_text}')")
        return "\n".join(lines)


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

if __name__ == "__main__":
    # Example 1: SolidWorks flange
    sw_parser = CADNLPParser("solidworks")
    params = sw_parser.parse("6 inch 150# RFWN flange, quarter inch thick, A105 material")
    
    print("SolidWorks Flange:")
    print(sw_parser.format_for_cad(params))
    print(f"Material: {sw_parser.extract_material('A105 material')}")
    print(f"Standard: {sw_parser.extract_standard('ASME B16.5 Class 150')}")
    print()
    
    # Example 2: Inventor bracket
    inv_parser = CADNLPParser("inventor")
    params = inv_parser.parse("100mm x 50mm x 5mm bracket, 45 degree angle, 6061-T6 aluminum")
    
    print("Inventor Bracket:")
    print(inv_parser.format_for_cad(params))
    print(f"Material: {inv_parser.extract_material('6061-T6 aluminum')}")
    print()
    
    # Example 3: Pipe nozzle
    sw_parser2 = CADNLPParser("solidworks")
    params = sw_parser2.parse("2 inch sch 40 pipe nozzle, 8 inch long, 316 stainless")
    
    print("Pipe Nozzle:")
    print(sw_parser2.format_for_cad(params))
