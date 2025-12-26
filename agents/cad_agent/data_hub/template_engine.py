"""
Report Template Engine
======================
Structured output generation with configurable templates.

Features:
- Multiple output formats (HTML, PDF, Markdown, JSON)
- Configurable templates
- Dynamic content sections
- Style customization
"""

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
import base64


class OutputFormat(str, Enum):
    """Supported output formats."""
    HTML = "html"
    PDF = "pdf"
    MARKDOWN = "markdown"
    JSON = "json"
    CSV = "csv"
    TEXT = "text"


class SectionType(str, Enum):
    """Report section types."""
    HEADER = "header"
    SUMMARY = "summary"
    TABLE = "table"
    CHART = "chart"
    LIST = "list"
    DETAIL = "detail"
    FOOTER = "footer"
    CUSTOM = "custom"


@dataclass
class TemplateSection:
    """A section in a report template."""
    id: str
    type: SectionType
    title: Optional[str] = None
    content: Any = None
    style: Dict[str, str] = field(default_factory=dict)
    visible: bool = True
    order: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "content": self.content,
            "style": self.style,
            "visible": self.visible,
            "order": self.order,
        }


@dataclass
class ReportTemplate:
    """A complete report template."""
    id: str
    name: str
    description: str
    format: OutputFormat
    sections: List[TemplateSection] = field(default_factory=list)
    styles: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_section(self, section: TemplateSection):
        """Add a section to the template."""
        self.sections.append(section)
        self.sections.sort(key=lambda s: s.order)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "format": self.format.value,
            "sections": [s.to_dict() for s in self.sections],
            "styles": self.styles,
            "metadata": self.metadata,
        }


class TemplateEngine:
    """
    Template engine for generating structured reports.

    Features:
    - Pre-built templates for common reports
    - Custom template creation
    - Multi-format rendering
    - Style customization
    """

    # Default styles
    DEFAULT_STYLES = {
        "colors": {
            "primary": "#1a73e8",
            "secondary": "#5f6368",
            "success": "#34a853",
            "warning": "#fbbc04",
            "error": "#ea4335",
            "critical": "#d93025",
            "background": "#ffffff",
            "text": "#202124",
        },
        "fonts": {
            "heading": "Arial, sans-serif",
            "body": "Roboto, Arial, sans-serif",
            "mono": "Consolas, monospace",
        },
        "sizes": {
            "h1": "24px",
            "h2": "20px",
            "h3": "16px",
            "body": "14px",
            "small": "12px",
        }
    }

    def __init__(self, templates_dir: Optional[Path] = None):
        """Initialize template engine."""
        self.templates_dir = templates_dir
        self._templates: Dict[str, ReportTemplate] = {}
        self._renderers: Dict[OutputFormat, Callable] = {
            OutputFormat.HTML: self._render_html,
            OutputFormat.MARKDOWN: self._render_markdown,
            OutputFormat.JSON: self._render_json,
            OutputFormat.TEXT: self._render_text,
            OutputFormat.CSV: self._render_csv,
        }

        # Load built-in templates
        self._load_builtin_templates()

    def _load_builtin_templates(self):
        """Load built-in report templates."""
        # Validation Report Template
        validation_template = ReportTemplate(
            id="validation_report",
            name="Validation Report",
            description="Standard validation results report",
            format=OutputFormat.HTML,
            styles=self.DEFAULT_STYLES,
        )
        validation_template.add_section(TemplateSection(
            id="header",
            type=SectionType.HEADER,
            title="Validation Report",
            order=0
        ))
        validation_template.add_section(TemplateSection(
            id="summary",
            type=SectionType.SUMMARY,
            title="Summary",
            order=1
        ))
        validation_template.add_section(TemplateSection(
            id="results_table",
            type=SectionType.TABLE,
            title="Validation Results",
            order=2
        ))
        validation_template.add_section(TemplateSection(
            id="issues_list",
            type=SectionType.LIST,
            title="Issues",
            order=3
        ))
        validation_template.add_section(TemplateSection(
            id="recommendations",
            type=SectionType.LIST,
            title="Recommendations",
            order=4
        ))
        validation_template.add_section(TemplateSection(
            id="footer",
            type=SectionType.FOOTER,
            order=99
        ))
        self._templates["validation_report"] = validation_template

        # BOM Export Template
        bom_template = ReportTemplate(
            id="bom_export",
            name="Bill of Materials",
            description="Standard BOM export format",
            format=OutputFormat.HTML,
            styles=self.DEFAULT_STYLES,
        )
        bom_template.add_section(TemplateSection(
            id="header",
            type=SectionType.HEADER,
            title="Bill of Materials",
            order=0
        ))
        bom_template.add_section(TemplateSection(
            id="assembly_info",
            type=SectionType.DETAIL,
            title="Assembly Information",
            order=1
        ))
        bom_template.add_section(TemplateSection(
            id="bom_table",
            type=SectionType.TABLE,
            title="Parts List",
            order=2
        ))
        bom_template.add_section(TemplateSection(
            id="summary",
            type=SectionType.SUMMARY,
            title="Summary",
            order=3
        ))
        self._templates["bom_export"] = bom_template

        # Executive Summary Template
        exec_summary = ReportTemplate(
            id="executive_summary",
            name="Executive Summary",
            description="One-page executive summary",
            format=OutputFormat.HTML,
            styles=self.DEFAULT_STYLES,
        )
        exec_summary.add_section(TemplateSection(
            id="header",
            type=SectionType.HEADER,
            title="Executive Summary",
            order=0
        ))
        exec_summary.add_section(TemplateSection(
            id="status",
            type=SectionType.SUMMARY,
            title="Overall Status",
            order=1
        ))
        exec_summary.add_section(TemplateSection(
            id="key_metrics",
            type=SectionType.CHART,
            title="Key Metrics",
            order=2
        ))
        exec_summary.add_section(TemplateSection(
            id="critical_issues",
            type=SectionType.LIST,
            title="Critical Issues",
            order=3
        ))
        self._templates["executive_summary"] = exec_summary

    def get_template(self, template_id: str) -> Optional[ReportTemplate]:
        """Get a template by ID."""
        return self._templates.get(template_id)

    def list_templates(self) -> List[Dict[str, str]]:
        """List all available templates."""
        return [
            {"id": t.id, "name": t.name, "description": t.description}
            for t in self._templates.values()
        ]

    def create_template(self, template: ReportTemplate):
        """Register a new template."""
        self._templates[template.id] = template

    # ==================== RENDERING ====================

    def render(self, template_id: str, data: Dict[str, Any],
               format: Optional[OutputFormat] = None) -> str:
        """
        Render a template with data.

        Args:
            template_id: Template to use
            data: Data to populate template
            format: Override template's default format

        Returns:
            Rendered output string
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")

        output_format = format or template.format
        renderer = self._renderers.get(output_format)

        if not renderer:
            raise ValueError(f"Unsupported format: {output_format}")

        return renderer(template, data)

    def _render_html(self, template: ReportTemplate, data: Dict[str, Any]) -> str:
        """Render template as HTML."""
        styles = template.styles or self.DEFAULT_STYLES
        colors = styles.get("colors", self.DEFAULT_STYLES["colors"])

        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"<title>{template.name}</title>",
            "<style>",
            self._generate_css(styles),
            "</style>",
            "</head>",
            "<body>",
            '<div class="report-container">',
        ]

        for section in template.sections:
            if not section.visible:
                continue

            section_data = data.get(section.id, {})
            section_html = self._render_html_section(section, section_data, colors)
            html_parts.append(section_html)

        html_parts.extend([
            "</div>",
            "</body>",
            "</html>",
        ])

        return "\n".join(html_parts)

    def _generate_css(self, styles: Dict[str, Any]) -> str:
        """Generate CSS from styles configuration."""
        colors = styles.get("colors", self.DEFAULT_STYLES["colors"])
        fonts = styles.get("fonts", self.DEFAULT_STYLES["fonts"])
        sizes = styles.get("sizes", self.DEFAULT_STYLES["sizes"])

        return f"""
            body {{
                font-family: {fonts['body']};
                font-size: {sizes['body']};
                color: {colors['text']};
                background-color: {colors['background']};
                margin: 0;
                padding: 20px;
            }}
            .report-container {{
                max-width: 1000px;
                margin: 0 auto;
            }}
            h1 {{ font-size: {sizes['h1']}; color: {colors['primary']}; }}
            h2 {{ font-size: {sizes['h2']}; color: {colors['secondary']}; border-bottom: 1px solid #ddd; padding-bottom: 8px; }}
            h3 {{ font-size: {sizes['h3']}; color: {colors['secondary']}; }}
            .section {{ margin-bottom: 24px; }}
            .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 16px; }}
            .summary-item {{ padding: 16px; border-radius: 8px; background: #f8f9fa; }}
            .summary-value {{ font-size: 24px; font-weight: bold; color: {colors['primary']}; }}
            .summary-label {{ font-size: 12px; color: {colors['secondary']}; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f1f3f4; font-weight: 600; }}
            tr:hover {{ background-color: #f8f9fa; }}
            .severity-critical {{ color: {colors['critical']}; font-weight: bold; }}
            .severity-error {{ color: {colors['error']}; }}
            .severity-warning {{ color: {colors['warning']}; }}
            .severity-info {{ color: {colors['primary']}; }}
            .status-pass {{ color: {colors['success']}; }}
            .status-fail {{ color: {colors['error']}; }}
            ul.issues-list {{ list-style: none; padding: 0; }}
            ul.issues-list li {{ padding: 12px; margin-bottom: 8px; border-left: 4px solid; background: #f8f9fa; }}
            ul.issues-list li.critical {{ border-color: {colors['critical']}; }}
            ul.issues-list li.error {{ border-color: {colors['error']}; }}
            ul.issues-list li.warning {{ border-color: {colors['warning']}; }}
            .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; font-size: {sizes['small']}; color: {colors['secondary']}; }}
        """

    def _render_html_section(self, section: TemplateSection, data: Any, colors: Dict[str, str]) -> str:
        """Render a single section as HTML."""
        if section.type == SectionType.HEADER:
            return self._render_html_header(section, data)
        elif section.type == SectionType.SUMMARY:
            return self._render_html_summary(section, data)
        elif section.type == SectionType.TABLE:
            return self._render_html_table(section, data)
        elif section.type == SectionType.LIST:
            return self._render_html_list(section, data, colors)
        elif section.type == SectionType.DETAIL:
            return self._render_html_detail(section, data)
        elif section.type == SectionType.FOOTER:
            return self._render_html_footer(section, data)
        return ""

    def _render_html_header(self, section: TemplateSection, data: Any) -> str:
        """Render header section."""
        title = data.get("title", section.title or "Report")
        subtitle = data.get("subtitle", "")
        date = data.get("date", datetime.now().strftime("%Y-%m-%d %H:%M"))

        return f"""
        <div class="section header">
            <h1>{title}</h1>
            {f'<p class="subtitle">{subtitle}</p>' if subtitle else ''}
            <p class="date">Generated: {date}</p>
        </div>
        """

    def _render_html_summary(self, section: TemplateSection, data: Any) -> str:
        """Render summary section with metrics."""
        if not data:
            return ""

        html = f'<div class="section summary">'
        if section.title:
            html += f'<h2>{section.title}</h2>'

        html += '<div class="summary-grid">'

        for key, value in data.items():
            if isinstance(value, dict):
                continue  # Skip nested objects
            label = key.replace("_", " ").title()
            html += f"""
            <div class="summary-item">
                <div class="summary-value">{value}</div>
                <div class="summary-label">{label}</div>
            </div>
            """

        html += '</div></div>'
        return html

    def _render_html_table(self, section: TemplateSection, data: Any) -> str:
        """Render table section."""
        if not data:
            return ""

        rows = data.get("rows", data if isinstance(data, list) else [])
        columns = data.get("columns", [])

        if not rows:
            return ""

        # Auto-detect columns from first row
        if not columns and rows:
            columns = list(rows[0].keys())

        html = f'<div class="section table">'
        if section.title:
            html += f'<h2>{section.title}</h2>'

        html += '<table><thead><tr>'
        for col in columns:
            html += f'<th>{col.replace("_", " ").title()}</th>'
        html += '</tr></thead><tbody>'

        for row in rows:
            html += '<tr>'
            for col in columns:
                value = row.get(col, "")
                cell_class = ""
                if col == "status":
                    cell_class = f'class="status-{"pass" if value == "PASS" else "fail"}"'
                elif col == "severity":
                    cell_class = f'class="severity-{value.lower()}"'
                html += f'<td {cell_class}>{value}</td>'
            html += '</tr>'

        html += '</tbody></table></div>'
        return html

    def _render_html_list(self, section: TemplateSection, data: Any, colors: Dict[str, str]) -> str:
        """Render list section."""
        if not data:
            return ""

        items = data.get("items", data if isinstance(data, list) else [])
        if not items:
            return ""

        html = f'<div class="section list">'
        if section.title:
            html += f'<h2>{section.title}</h2>'

        html += '<ul class="issues-list">'

        for item in items:
            if isinstance(item, dict):
                severity = item.get("severity", "info").lower()
                message = item.get("message", str(item))
                suggestion = item.get("suggestion", "")
                html += f'<li class="{severity}"><strong>{message}</strong>'
                if suggestion:
                    html += f'<br><em>Suggestion: {suggestion}</em>'
                html += '</li>'
            else:
                html += f'<li>{item}</li>'

        html += '</ul></div>'
        return html

    def _render_html_detail(self, section: TemplateSection, data: Any) -> str:
        """Render detail section."""
        if not data:
            return ""

        html = f'<div class="section detail">'
        if section.title:
            html += f'<h2>{section.title}</h2>'

        html += '<dl>'
        for key, value in data.items():
            label = key.replace("_", " ").title()
            html += f'<dt><strong>{label}:</strong></dt><dd>{value}</dd>'
        html += '</dl></div>'

        return html

    def _render_html_footer(self, section: TemplateSection, data: Any) -> str:
        """Render footer section."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""
        <div class="footer">
            <p>Generated by Project Vulcan Validation System</p>
            <p>Timestamp: {timestamp}</p>
        </div>
        """

    def _render_markdown(self, template: ReportTemplate, data: Dict[str, Any]) -> str:
        """Render template as Markdown."""
        md_parts = []

        for section in template.sections:
            if not section.visible:
                continue

            section_data = data.get(section.id, {})

            if section.type == SectionType.HEADER:
                title = section_data.get("title", section.title or "Report")
                md_parts.append(f"# {title}\n")
                if "date" in section_data:
                    md_parts.append(f"*Generated: {section_data['date']}*\n")

            elif section.type == SectionType.SUMMARY:
                if section.title:
                    md_parts.append(f"## {section.title}\n")
                for key, value in section_data.items():
                    if not isinstance(value, dict):
                        label = key.replace("_", " ").title()
                        md_parts.append(f"- **{label}:** {value}")
                md_parts.append("")

            elif section.type == SectionType.TABLE:
                if section.title:
                    md_parts.append(f"## {section.title}\n")
                rows = section_data.get("rows", section_data if isinstance(section_data, list) else [])
                if rows:
                    columns = list(rows[0].keys())
                    # Header
                    md_parts.append("| " + " | ".join(c.replace("_", " ").title() for c in columns) + " |")
                    md_parts.append("|" + "|".join(["---"] * len(columns)) + "|")
                    # Rows
                    for row in rows:
                        md_parts.append("| " + " | ".join(str(row.get(c, "")) for c in columns) + " |")
                md_parts.append("")

            elif section.type == SectionType.LIST:
                if section.title:
                    md_parts.append(f"## {section.title}\n")
                items = section_data.get("items", section_data if isinstance(section_data, list) else [])
                for item in items:
                    if isinstance(item, dict):
                        severity = item.get("severity", "").upper()
                        message = item.get("message", str(item))
                        md_parts.append(f"- **[{severity}]** {message}")
                    else:
                        md_parts.append(f"- {item}")
                md_parts.append("")

        md_parts.append("---")
        md_parts.append(f"*Generated by Project Vulcan - {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

        return "\n".join(md_parts)

    def _render_json(self, template: ReportTemplate, data: Dict[str, Any]) -> str:
        """Render template as JSON."""
        output = {
            "template": template.id,
            "generated": datetime.now().isoformat(),
            "sections": {}
        }

        for section in template.sections:
            if section.visible:
                output["sections"][section.id] = data.get(section.id, {})

        return json.dumps(output, indent=2, default=str)

    def _render_text(self, template: ReportTemplate, data: Dict[str, Any]) -> str:
        """Render template as plain text."""
        text_parts = []

        for section in template.sections:
            if not section.visible:
                continue

            section_data = data.get(section.id, {})

            if section.title:
                text_parts.append(f"\n{'=' * 50}")
                text_parts.append(section.title.upper())
                text_parts.append('=' * 50)

            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    if not isinstance(value, (dict, list)):
                        text_parts.append(f"  {key}: {value}")
            elif isinstance(section_data, list):
                for item in section_data:
                    if isinstance(item, dict):
                        text_parts.append(f"  - {item.get('message', str(item))}")
                    else:
                        text_parts.append(f"  - {item}")

        return "\n".join(text_parts)

    def _render_csv(self, template: ReportTemplate, data: Dict[str, Any]) -> str:
        """Render table sections as CSV."""
        csv_lines = []

        for section in template.sections:
            if section.type != SectionType.TABLE or not section.visible:
                continue

            section_data = data.get(section.id, {})
            rows = section_data.get("rows", section_data if isinstance(section_data, list) else [])

            if rows:
                columns = list(rows[0].keys())
                csv_lines.append(",".join(columns))
                for row in rows:
                    values = [str(row.get(c, "")).replace(",", ";") for c in columns]
                    csv_lines.append(",".join(values))

        return "\n".join(csv_lines)
