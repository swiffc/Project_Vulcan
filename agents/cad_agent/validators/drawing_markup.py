"""
Drawing Markup Generator
=========================
Generate SVG markup overlays for validation issues on engineering drawings.

Phase 25 - Drawing Markup System

Features:
- SVG-based markup generation
- Cloud/balloon callouts for issues
- Color-coded severity indicators
- Leader lines to issue locations
- Legend generation
- Export to SVG or PNG
"""

import io
import math
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import xml.etree.ElementTree as ET

logger = logging.getLogger("vulcan.drawing_markup")


# =============================================================================
# DATA CLASSES
# =============================================================================

class MarkupSeverity(Enum):
    """Markup severity levels with colors."""
    CRITICAL = ("critical", "#c62828", "#ffcdd2")  # Dark red, light red
    ERROR = ("error", "#d32f2f", "#ffebee")
    WARNING = ("warning", "#f57c00", "#fff3e0")
    INFO = ("info", "#1976d2", "#e3f2fd")
    NOTE = ("note", "#388e3c", "#e8f5e9")


class MarkupType(Enum):
    """Types of markup annotations."""
    CLOUD = "cloud"
    BALLOON = "balloon"
    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    ARROW = "arrow"
    TEXT = "text"
    LEADER = "leader"
    DIMENSION_CHECK = "dimension_check"
    TOLERANCE_FLAG = "tolerance_flag"


@dataclass
class MarkupLocation:
    """Location coordinates for markup."""
    x: float
    y: float
    x2: Optional[float] = None  # For rectangles/leaders
    y2: Optional[float] = None


@dataclass
class MarkupItem:
    """Single markup annotation."""
    id: str
    markup_type: MarkupType
    severity: MarkupSeverity
    location: MarkupLocation
    message: str
    detail: str = ""
    check_type: str = ""
    standard_ref: str = ""
    balloon_number: Optional[int] = None


@dataclass
class DrawingMarkup:
    """Complete drawing markup document."""
    drawing_number: str = ""
    revision: str = ""
    width: float = 1100  # Default B-size (11x17)
    height: float = 850
    scale: float = 1.0
    markups: List[MarkupItem] = field(default_factory=list)
    title: str = "Validation Markup"
    generated_at: str = ""


# =============================================================================
# MARKUP GENERATOR
# =============================================================================

class DrawingMarkupGenerator:
    """
    Generate SVG markup overlays for engineering drawings.

    Features:
    - Cloud callouts (revision-style)
    - Numbered balloons
    - Leader lines
    - Color-coded severity
    - Legend generation
    """

    # Severity colors
    COLORS = {
        MarkupSeverity.CRITICAL: {"fill": "#ffcdd2", "stroke": "#c62828", "text": "#b71c1c"},
        MarkupSeverity.ERROR: {"fill": "#ffebee", "stroke": "#d32f2f", "text": "#c62828"},
        MarkupSeverity.WARNING: {"fill": "#fff3e0", "stroke": "#f57c00", "text": "#e65100"},
        MarkupSeverity.INFO: {"fill": "#e3f2fd", "stroke": "#1976d2", "text": "#0d47a1"},
        MarkupSeverity.NOTE: {"fill": "#e8f5e9", "stroke": "#388e3c", "text": "#1b5e20"},
    }

    def __init__(self):
        self.markup = DrawingMarkup()
        self.balloon_counter = 1

    def set_drawing_info(
        self,
        drawing_number: str,
        revision: str = "",
        width: float = 1100,
        height: float = 850
    ):
        """Set drawing information."""
        self.markup.drawing_number = drawing_number
        self.markup.revision = revision
        self.markup.width = width
        self.markup.height = height

    def add_markup(
        self,
        markup_type: MarkupType,
        severity: MarkupSeverity,
        x: float,
        y: float,
        message: str,
        detail: str = "",
        check_type: str = "",
        standard_ref: str = "",
        x2: Optional[float] = None,
        y2: Optional[float] = None,
    ) -> str:
        """
        Add a markup annotation.

        Args:
            markup_type: Type of markup (cloud, balloon, etc.)
            severity: Severity level
            x, y: Primary location
            message: Short message
            detail: Detailed description
            check_type: Type of validation check
            standard_ref: Reference standard
            x2, y2: Secondary location (for rectangles/leaders)

        Returns:
            Markup ID
        """
        markup_id = f"M{len(self.markup.markups) + 1:03d}"

        balloon_num = None
        if markup_type in [MarkupType.BALLOON, MarkupType.CLOUD]:
            balloon_num = self.balloon_counter
            self.balloon_counter += 1

        item = MarkupItem(
            id=markup_id,
            markup_type=markup_type,
            severity=severity,
            location=MarkupLocation(x=x, y=y, x2=x2, y2=y2),
            message=message,
            detail=detail,
            check_type=check_type,
            standard_ref=standard_ref,
            balloon_number=balloon_num,
        )

        self.markup.markups.append(item)
        return markup_id

    def add_from_validation_issues(self, issues: List[Dict[str, Any]]):
        """
        Add markups from validation issue list.

        Args:
            issues: List of validation issue dicts with fields:
                - severity: str
                - message: str
                - location: dict with x, y (optional)
                - check_type: str
                - suggestion: str
                - standard_reference: str
        """
        for issue in issues:
            severity_str = issue.get("severity", "info").lower()
            severity_map = {
                "critical": MarkupSeverity.CRITICAL,
                "error": MarkupSeverity.ERROR,
                "warning": MarkupSeverity.WARNING,
                "info": MarkupSeverity.INFO,
            }
            severity = severity_map.get(severity_str, MarkupSeverity.INFO)

            # Get location (use default if not provided)
            loc = issue.get("location", {})
            x = loc.get("x", 100 + len(self.markup.markups) * 50)
            y = loc.get("y", 100 + len(self.markup.markups) * 30)

            markup_type = MarkupType.BALLOON
            if severity == MarkupSeverity.CRITICAL:
                markup_type = MarkupType.CLOUD

            self.add_markup(
                markup_type=markup_type,
                severity=severity,
                x=x,
                y=y,
                message=issue.get("message", ""),
                detail=issue.get("suggestion", ""),
                check_type=issue.get("check_type", ""),
                standard_ref=issue.get("standard_reference", ""),
            )

    def generate_svg(self, include_legend: bool = True) -> str:
        """
        Generate SVG markup document.

        Args:
            include_legend: Include legend/key

        Returns:
            SVG string
        """
        self.markup.generated_at = datetime.now().isoformat()

        # Create SVG root
        svg = ET.Element('svg', {
            'xmlns': 'http://www.w3.org/2000/svg',
            'width': str(self.markup.width),
            'height': str(self.markup.height),
            'viewBox': f'0 0 {self.markup.width} {self.markup.height}',
        })

        # Add styles
        style = ET.SubElement(svg, 'style')
        style.text = self._generate_styles()

        # Add defs for markers
        defs = ET.SubElement(svg, 'defs')
        self._add_marker_defs(defs)

        # Title
        title = ET.SubElement(svg, 'title')
        title.text = f"Validation Markup - {self.markup.drawing_number}"

        # Background (transparent)
        # ET.SubElement(svg, 'rect', {'width': '100%', 'height': '100%', 'fill': 'none'})

        # Group for markups
        markup_group = ET.SubElement(svg, 'g', {'id': 'markups'})

        # Add each markup
        for item in self.markup.markups:
            self._render_markup(markup_group, item)

        # Add legend if requested
        if include_legend and self.markup.markups:
            self._render_legend(svg)

        # Add header info
        self._render_header(svg)

        # Convert to string
        return ET.tostring(svg, encoding='unicode', method='xml')

    def _generate_styles(self) -> str:
        """Generate CSS styles for SVG."""
        return """
            .markup-text { font-family: Arial, sans-serif; font-size: 10px; }
            .balloon-text { font-family: Arial, sans-serif; font-size: 12px; font-weight: bold; }
            .legend-text { font-family: Arial, sans-serif; font-size: 10px; }
            .header-text { font-family: Arial, sans-serif; font-size: 12px; }
            .title-text { font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; }
            .cloud { fill-opacity: 0.7; }
            .balloon { fill-opacity: 0.9; }
        """

    def _add_marker_defs(self, defs: ET.Element):
        """Add SVG marker definitions (arrows, etc.)."""
        # Arrow marker
        marker = ET.SubElement(defs, 'marker', {
            'id': 'arrow',
            'markerWidth': '10',
            'markerHeight': '7',
            'refX': '9',
            'refY': '3.5',
            'orient': 'auto',
        })
        ET.SubElement(marker, 'polygon', {
            'points': '0 0, 10 3.5, 0 7',
            'fill': '#333',
        })

        # Cloud pattern
        for severity in MarkupSeverity:
            colors = self.COLORS[severity]
            pattern_id = f"cloud-{severity.value[0]}"
            # Could add gradient or pattern here

    def _render_markup(self, parent: ET.Element, item: MarkupItem):
        """Render a single markup item."""
        colors = self.COLORS[item.severity]

        if item.markup_type == MarkupType.CLOUD:
            self._render_cloud(parent, item, colors)
        elif item.markup_type == MarkupType.BALLOON:
            self._render_balloon(parent, item, colors)
        elif item.markup_type == MarkupType.RECTANGLE:
            self._render_rectangle(parent, item, colors)
        elif item.markup_type == MarkupType.ARROW:
            self._render_arrow(parent, item, colors)
        elif item.markup_type == MarkupType.LEADER:
            self._render_leader(parent, item, colors)

    def _render_cloud(self, parent: ET.Element, item: MarkupItem, colors: Dict):
        """Render a cloud/revision callout."""
        x, y = item.location.x, item.location.y

        # Cloud shape using path with bumps
        cloud_width = 80
        cloud_height = 40

        # Create cloud path with bumpy edges
        bumps = 8
        path_d = self._create_cloud_path(x, y, cloud_width, cloud_height, bumps)

        cloud = ET.SubElement(parent, 'path', {
            'd': path_d,
            'fill': colors['fill'],
            'stroke': colors['stroke'],
            'stroke-width': '2',
            'class': 'cloud',
        })

        # Balloon number
        if item.balloon_number:
            ET.SubElement(parent, 'text', {
                'x': str(x + cloud_width/2),
                'y': str(y + cloud_height/2 + 4),
                'text-anchor': 'middle',
                'class': 'balloon-text',
                'fill': colors['text'],
            }).text = str(item.balloon_number)

    def _create_cloud_path(self, x: float, y: float, w: float, h: float, bumps: int) -> str:
        """Create SVG path for cloud shape."""
        # Simplified cloud using overlapping circles
        cx = x + w/2
        cy = y + h/2
        rx = w/2
        ry = h/2

        # Create bumpy ellipse
        points = []
        for i in range(bumps * 2):
            angle = (i / (bumps * 2)) * 2 * math.pi
            bump = 1 + 0.15 * math.sin(i * 3)  # Variation
            px = cx + rx * bump * math.cos(angle)
            py = cy + ry * bump * math.sin(angle)
            points.append((px, py))

        # Build path
        path = f"M {points[0][0]:.1f} {points[0][1]:.1f}"
        for i in range(1, len(points)):
            # Quadratic curve for smooth bumps
            mx = (points[i-1][0] + points[i][0]) / 2
            my = (points[i-1][1] + points[i][1]) / 2
            path += f" Q {points[i-1][0]:.1f} {points[i-1][1]:.1f} {mx:.1f} {my:.1f}"
        path += " Z"

        return path

    def _render_balloon(self, parent: ET.Element, item: MarkupItem, colors: Dict):
        """Render a numbered balloon callout."""
        x, y = item.location.x, item.location.y
        radius = 15

        # Circle
        ET.SubElement(parent, 'circle', {
            'cx': str(x),
            'cy': str(y),
            'r': str(radius),
            'fill': colors['fill'],
            'stroke': colors['stroke'],
            'stroke-width': '2',
            'class': 'balloon',
        })

        # Number
        if item.balloon_number:
            ET.SubElement(parent, 'text', {
                'x': str(x),
                'y': str(y + 4),
                'text-anchor': 'middle',
                'class': 'balloon-text',
                'fill': colors['text'],
            }).text = str(item.balloon_number)

    def _render_rectangle(self, parent: ET.Element, item: MarkupItem, colors: Dict):
        """Render a rectangle highlight."""
        x, y = item.location.x, item.location.y
        x2 = item.location.x2 or x + 50
        y2 = item.location.y2 or y + 30

        ET.SubElement(parent, 'rect', {
            'x': str(min(x, x2)),
            'y': str(min(y, y2)),
            'width': str(abs(x2 - x)),
            'height': str(abs(y2 - y)),
            'fill': colors['fill'],
            'fill-opacity': '0.3',
            'stroke': colors['stroke'],
            'stroke-width': '2',
            'stroke-dasharray': '5,3',
        })

    def _render_arrow(self, parent: ET.Element, item: MarkupItem, colors: Dict):
        """Render an arrow."""
        x, y = item.location.x, item.location.y
        x2 = item.location.x2 or x + 50
        y2 = item.location.y2 or y

        ET.SubElement(parent, 'line', {
            'x1': str(x),
            'y1': str(y),
            'x2': str(x2),
            'y2': str(y2),
            'stroke': colors['stroke'],
            'stroke-width': '2',
            'marker-end': 'url(#arrow)',
        })

    def _render_leader(self, parent: ET.Element, item: MarkupItem, colors: Dict):
        """Render a leader line with text."""
        x, y = item.location.x, item.location.y
        x2 = item.location.x2 or x + 80
        y2 = item.location.y2 or y - 30

        # Leader line
        ET.SubElement(parent, 'polyline', {
            'points': f"{x},{y} {x+20},{y2} {x2},{y2}",
            'fill': 'none',
            'stroke': colors['stroke'],
            'stroke-width': '1.5',
        })

        # Text box
        text_width = len(item.message) * 6 + 10
        ET.SubElement(parent, 'rect', {
            'x': str(x2),
            'y': str(y2 - 12),
            'width': str(text_width),
            'height': '20',
            'fill': colors['fill'],
            'stroke': colors['stroke'],
            'stroke-width': '1',
        })

        ET.SubElement(parent, 'text', {
            'x': str(x2 + 5),
            'y': str(y2 + 3),
            'class': 'markup-text',
            'fill': colors['text'],
        }).text = item.message[:40]

    def _render_legend(self, svg: ET.Element):
        """Render legend/key."""
        # Count by severity
        severity_counts = {}
        for item in self.markup.markups:
            sev = item.severity
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        legend_x = self.markup.width - 180
        legend_y = self.markup.height - 120

        # Legend box
        legend_group = ET.SubElement(svg, 'g', {'id': 'legend'})

        ET.SubElement(legend_group, 'rect', {
            'x': str(legend_x - 10),
            'y': str(legend_y - 25),
            'width': '170',
            'height': str(25 + len(severity_counts) * 20),
            'fill': 'white',
            'stroke': '#333',
            'stroke-width': '1',
        })

        ET.SubElement(legend_group, 'text', {
            'x': str(legend_x),
            'y': str(legend_y - 8),
            'class': 'title-text',
        }).text = "MARKUP KEY"

        y_offset = legend_y + 10
        for severity, count in sorted(severity_counts.items(), key=lambda x: x[0].value[0]):
            colors = self.COLORS[severity]

            # Color swatch
            ET.SubElement(legend_group, 'rect', {
                'x': str(legend_x),
                'y': str(y_offset - 10),
                'width': '15',
                'height': '15',
                'fill': colors['fill'],
                'stroke': colors['stroke'],
                'stroke-width': '1',
            })

            # Label
            ET.SubElement(legend_group, 'text', {
                'x': str(legend_x + 22),
                'y': str(y_offset),
                'class': 'legend-text',
            }).text = f"{severity.value[0].upper()}: {count}"

            y_offset += 20

    def _render_header(self, svg: ET.Element):
        """Render header information."""
        header_group = ET.SubElement(svg, 'g', {'id': 'header'})

        ET.SubElement(header_group, 'text', {
            'x': '10',
            'y': '20',
            'class': 'title-text',
        }).text = f"VALIDATION MARKUP - {self.markup.drawing_number} Rev {self.markup.revision}"

        ET.SubElement(header_group, 'text', {
            'x': '10',
            'y': '35',
            'class': 'header-text',
            'fill': '#666',
        }).text = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        ET.SubElement(header_group, 'text', {
            'x': '10',
            'y': '50',
            'class': 'header-text',
            'fill': '#666',
        }).text = f"Total Issues: {len(self.markup.markups)}"

    def get_issue_table(self) -> List[Dict]:
        """Get tabular list of all markups with details."""
        return [
            {
                "number": item.balloon_number,
                "id": item.id,
                "severity": item.severity.value[0],
                "type": item.markup_type.value,
                "message": item.message,
                "detail": item.detail,
                "check_type": item.check_type,
                "standard_ref": item.standard_ref,
                "location": {"x": item.location.x, "y": item.location.y},
            }
            for item in self.markup.markups
        ]

    def export_svg(self, filepath: Optional[str] = None) -> Tuple[str, bytes]:
        """
        Export markup as SVG file.

        Args:
            filepath: Optional file path

        Returns:
            Tuple of (filename, svg_bytes)
        """
        svg_str = self.generate_svg()
        svg_bytes = svg_str.encode('utf-8')

        filename = f"markup_{self.markup.drawing_number or 'drawing'}.svg"

        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(svg_str)

        return filename, svg_bytes

    def clear(self):
        """Clear all markups."""
        self.markup.markups.clear()
        self.balloon_counter = 1
