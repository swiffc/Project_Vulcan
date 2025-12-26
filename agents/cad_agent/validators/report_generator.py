"""
Validation Report Generator
===========================
Generates comprehensive validation reports from all validator results.

Phase 25.13 - Report Generation

Outputs:
- JSON reports for integration
- HTML reports for viewing
- CSV exports for data analysis
- Summary statistics
"""

import json
import logging
import io
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum

# PDF Generation imports
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image, HRFlowable
    )
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.report")


# =============================================================================
# REPORT FORMATS
# =============================================================================

class ReportFormat(Enum):
    """Available report formats."""
    JSON = "json"
    HTML = "html"
    CSV = "csv"
    MARKDOWN = "markdown"
    TEXT = "text"


class ReportLevel(Enum):
    """Report detail level."""
    SUMMARY = "summary"       # High-level pass/fail only
    STANDARD = "standard"     # Issues with severity >= WARNING
    DETAILED = "detailed"     # All issues including INFO
    DEBUG = "debug"           # Full debug information


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ValidatorSummary:
    """Summary of a single validator's results."""
    validator_name: str
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    pass_rate: float = 0.0
    status: str = "PASS"


@dataclass
class ReportMetadata:
    """Report metadata."""
    report_id: str = ""
    generated_at: str = ""
    drawing_number: Optional[str] = None
    drawing_revision: Optional[str] = None
    project_name: Optional[str] = None
    validator_version: str = "1.0.0"
    report_level: str = "standard"


@dataclass
class ValidationReport:
    """Complete validation report."""
    metadata: ReportMetadata = field(default_factory=ReportMetadata)
    overall_status: str = "PASS"
    overall_pass_rate: float = 100.0
    total_checks: int = 0
    total_passed: int = 0
    total_failed: int = 0
    total_warnings: int = 0
    total_critical: int = 0
    validator_summaries: List[ValidatorSummary] = field(default_factory=list)
    all_issues: List[Dict] = field(default_factory=list)
    critical_issues: List[Dict] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


# =============================================================================
# REPORT GENERATOR
# =============================================================================

class ReportGenerator:
    """
    Generates validation reports from validator results.

    Phase 25.13 - Features:
    1. Aggregate results from multiple validators
    2. Calculate overall statistics
    3. Generate prioritized issue list
    4. Create recommendations
    5. Export to multiple formats
    6. Include standards references
    """

    def __init__(self):
        self.results: Dict[str, Dict] = {}
        self.report: Optional[ValidationReport] = None

    def add_result(self, validator_name: str, result: Dict[str, Any]):
        """
        Add a validator result to the report.

        Args:
            validator_name: Name of the validator
            result: Validator result dictionary (from to_dict())
        """
        self.results[validator_name] = result

    def generate_report(
        self,
        drawing_number: Optional[str] = None,
        drawing_revision: Optional[str] = None,
        project_name: Optional[str] = None,
        level: ReportLevel = ReportLevel.STANDARD
    ) -> ValidationReport:
        """
        Generate comprehensive validation report.

        Args:
            drawing_number: Drawing number being validated
            drawing_revision: Drawing revision
            project_name: Project name
            level: Report detail level

        Returns:
            Complete validation report
        """
        report = ValidationReport()

        # Set metadata
        report.metadata = ReportMetadata(
            report_id=f"VR-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            generated_at=datetime.now().isoformat(),
            drawing_number=drawing_number,
            drawing_revision=drawing_revision,
            project_name=project_name,
            report_level=level.value,
        )

        # Process each validator result
        for validator_name, result in self.results.items():
            summary = self._create_validator_summary(validator_name, result)
            report.validator_summaries.append(summary)

            # Aggregate totals
            report.total_checks += summary.total_checks
            report.total_passed += summary.passed
            report.total_failed += summary.failed
            report.total_warnings += summary.warnings
            report.total_critical += summary.critical_failures

            # Collect issues based on report level
            issues = result.get("issues", [])
            for issue in issues:
                issue_with_validator = {**issue, "validator": validator_name}

                # Add to all issues based on level
                severity = issue.get("severity", "info")
                if level == ReportLevel.DEBUG:
                    report.all_issues.append(issue_with_validator)
                elif level == ReportLevel.DETAILED:
                    report.all_issues.append(issue_with_validator)
                elif level == ReportLevel.STANDARD:
                    if severity in ["warning", "error", "critical"]:
                        report.all_issues.append(issue_with_validator)
                elif level == ReportLevel.SUMMARY:
                    if severity in ["error", "critical"]:
                        report.all_issues.append(issue_with_validator)

                # Always collect critical issues
                if severity == "critical":
                    report.critical_issues.append(issue_with_validator)

        # Calculate overall statistics
        if report.total_checks > 0:
            report.overall_pass_rate = (report.total_passed / report.total_checks) * 100
        else:
            report.overall_pass_rate = 100.0

        # Determine overall status
        if report.total_critical > 0:
            report.overall_status = "CRITICAL"
        elif report.total_failed > 0:
            report.overall_status = "FAIL"
        elif report.total_warnings > 0:
            report.overall_status = "PASS_WITH_WARNINGS"
        else:
            report.overall_status = "PASS"

        # Sort issues by severity
        severity_order = {"critical": 0, "error": 1, "warning": 2, "info": 3}
        report.all_issues.sort(key=lambda x: severity_order.get(x.get("severity", "info"), 4))

        # Generate recommendations
        report.recommendations = self._generate_recommendations(report)

        self.report = report
        return report

    def _create_validator_summary(
        self,
        validator_name: str,
        result: Dict
    ) -> ValidatorSummary:
        """Create summary for a single validator."""
        total = result.get("total_checks", 0)
        passed = result.get("passed", 0)
        failed = result.get("failed", 0)
        warnings = result.get("warnings", 0)
        critical = result.get("critical_failures", 0)

        pass_rate = (passed / total * 100) if total > 0 else 100.0

        if critical > 0:
            status = "CRITICAL"
        elif failed > 0:
            status = "FAIL"
        elif warnings > 0:
            status = "PASS_WITH_WARNINGS"
        else:
            status = "PASS"

        return ValidatorSummary(
            validator_name=validator_name,
            total_checks=total,
            passed=passed,
            failed=failed,
            warnings=warnings,
            critical_failures=critical,
            pass_rate=pass_rate,
            status=status,
        )

    def _generate_recommendations(self, report: ValidationReport) -> List[str]:
        """Generate prioritized recommendations based on issues."""
        recommendations = []

        # Analyze issue patterns
        issue_types = {}
        standards_referenced = set()

        for issue in report.all_issues:
            check_type = issue.get("check_type", "unknown")
            issue_types[check_type] = issue_types.get(check_type, 0) + 1

            std_ref = issue.get("standard_reference")
            if std_ref:
                standards_referenced.add(std_ref)

        # Generate recommendations based on patterns
        if report.total_critical > 0:
            recommendations.append(
                f"PRIORITY: Address {report.total_critical} critical issue(s) before release"
            )

        # Common issue patterns
        if any("tolerance" in t for t in issue_types):
            recommendations.append(
                "Review tolerance specifications - multiple tolerance-related issues found"
            )

        if any("weld" in t for t in issue_types):
            recommendations.append(
                "Review welding specifications against AWS D1.1 requirements"
            )

        if any("bolt" in t or "fastener" in t for t in issue_types):
            recommendations.append(
                "Verify bolt grades and torque specifications per AISC/RCSC"
            )

        if any("osha" in t.lower() or "handrail" in t or "ladder" in t for t in issue_types):
            recommendations.append(
                "Address OSHA compliance issues before fabrication"
            )

        # Standards to reference
        if standards_referenced:
            recommendations.append(
                f"Reference standards: {', '.join(sorted(standards_referenced))}"
            )

        return recommendations

    def export_json(self, filepath: Optional[str] = None) -> str:
        """
        Export report as JSON.

        Args:
            filepath: Optional file path to write to

        Returns:
            JSON string
        """
        if not self.report:
            raise ValueError("No report generated. Call generate_report() first.")

        # Convert to dict
        report_dict = {
            "metadata": asdict(self.report.metadata),
            "overall_status": self.report.overall_status,
            "overall_pass_rate": round(self.report.overall_pass_rate, 2),
            "statistics": {
                "total_checks": self.report.total_checks,
                "total_passed": self.report.total_passed,
                "total_failed": self.report.total_failed,
                "total_warnings": self.report.total_warnings,
                "total_critical": self.report.total_critical,
            },
            "validator_summaries": [asdict(s) for s in self.report.validator_summaries],
            "critical_issues": self.report.critical_issues,
            "all_issues": self.report.all_issues,
            "recommendations": self.report.recommendations,
        }

        json_str = json.dumps(report_dict, indent=2)

        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_str)

        return json_str

    def export_html(self, filepath: Optional[str] = None) -> str:
        """
        Export report as HTML.

        Args:
            filepath: Optional file path to write to

        Returns:
            HTML string
        """
        if not self.report:
            raise ValueError("No report generated. Call generate_report() first.")

        # Status colors
        status_colors = {
            "PASS": "#28a745",
            "PASS_WITH_WARNINGS": "#ffc107",
            "FAIL": "#dc3545",
            "CRITICAL": "#dc3545",
        }

        severity_colors = {
            "critical": "#dc3545",
            "error": "#dc3545",
            "warning": "#ffc107",
            "info": "#17a2b8",
        }

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Validation Report - {self.report.metadata.drawing_number or 'Unknown'}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        .header {{ border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }}
        .status {{ display: inline-block; padding: 5px 15px; border-radius: 4px; color: white; font-weight: bold; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin: 20px 0; }}
        .stat-box {{ background: #f8f9fa; padding: 15px; border-radius: 4px; text-align: center; }}
        .stat-value {{ font-size: 24px; font-weight: bold; }}
        .stat-label {{ color: #666; font-size: 12px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f8f9fa; }}
        .severity {{ padding: 3px 8px; border-radius: 3px; color: white; font-size: 12px; }}
        .recommendations {{ background: #e7f3ff; padding: 15px; border-radius: 4px; margin: 20px 0; }}
        .recommendations li {{ margin: 5px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Validation Report</h1>
            <p><strong>Drawing:</strong> {self.report.metadata.drawing_number or 'Not specified'}
               Rev {self.report.metadata.drawing_revision or '-'}</p>
            <p><strong>Generated:</strong> {self.report.metadata.generated_at}</p>
            <p><strong>Report ID:</strong> {self.report.metadata.report_id}</p>
            <span class="status" style="background: {status_colors.get(self.report.overall_status, '#666')}">
                {self.report.overall_status}
            </span>
        </div>

        <div class="summary-grid">
            <div class="stat-box">
                <div class="stat-value">{self.report.total_checks}</div>
                <div class="stat-label">Total Checks</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" style="color: #28a745">{self.report.total_passed}</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" style="color: #dc3545">{self.report.total_failed}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" style="color: #ffc107">{self.report.total_warnings}</div>
                <div class="stat-label">Warnings</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{self.report.overall_pass_rate:.1f}%</div>
                <div class="stat-label">Pass Rate</div>
            </div>
        </div>

        <h2>Validator Summary</h2>
        <table>
            <tr>
                <th>Validator</th>
                <th>Status</th>
                <th>Checks</th>
                <th>Passed</th>
                <th>Failed</th>
                <th>Warnings</th>
                <th>Pass Rate</th>
            </tr>
"""

        for summary in self.report.validator_summaries:
            html += f"""            <tr>
                <td>{summary.validator_name}</td>
                <td><span class="status" style="background: {status_colors.get(summary.status, '#666')}; font-size: 12px;">{summary.status}</span></td>
                <td>{summary.total_checks}</td>
                <td>{summary.passed}</td>
                <td>{summary.failed}</td>
                <td>{summary.warnings}</td>
                <td>{summary.pass_rate:.1f}%</td>
            </tr>
"""

        html += """        </table>

        <h2>Issues</h2>
        <table>
            <tr>
                <th>Severity</th>
                <th>Validator</th>
                <th>Check Type</th>
                <th>Message</th>
                <th>Suggestion</th>
                <th>Standard</th>
            </tr>
"""

        for issue in self.report.all_issues:
            severity = issue.get("severity", "info")
            html += f"""            <tr>
                <td><span class="severity" style="background: {severity_colors.get(severity, '#666')}">{severity.upper()}</span></td>
                <td>{issue.get('validator', '-')}</td>
                <td>{issue.get('check_type', '-')}</td>
                <td>{issue.get('message', '-')}</td>
                <td>{issue.get('suggestion', '-') or '-'}</td>
                <td>{issue.get('standard_reference', '-') or '-'}</td>
            </tr>
"""

        html += """        </table>
"""

        if self.report.recommendations:
            html += """
        <div class="recommendations">
            <h3>Recommendations</h3>
            <ul>
"""
            for rec in self.report.recommendations:
                html += f"                <li>{rec}</li>\n"
            html += """            </ul>
        </div>
"""

        html += """    </div>
</body>
</html>
"""

        if filepath:
            with open(filepath, 'w') as f:
                f.write(html)

        return html

    def export_markdown(self, filepath: Optional[str] = None) -> str:
        """
        Export report as Markdown.

        Args:
            filepath: Optional file path to write to

        Returns:
            Markdown string
        """
        if not self.report:
            raise ValueError("No report generated. Call generate_report() first.")

        md = f"""# Validation Report

**Drawing:** {self.report.metadata.drawing_number or 'Not specified'} Rev {self.report.metadata.drawing_revision or '-'}
**Generated:** {self.report.metadata.generated_at}
**Report ID:** {self.report.metadata.report_id}
**Status:** **{self.report.overall_status}**

## Summary

| Metric | Value |
|--------|-------|
| Total Checks | {self.report.total_checks} |
| Passed | {self.report.total_passed} |
| Failed | {self.report.total_failed} |
| Warnings | {self.report.total_warnings} |
| Critical | {self.report.total_critical} |
| Pass Rate | {self.report.overall_pass_rate:.1f}% |

## Validator Results

| Validator | Status | Checks | Passed | Failed | Warnings |
|-----------|--------|--------|--------|--------|----------|
"""

        for s in self.report.validator_summaries:
            md += f"| {s.validator_name} | {s.status} | {s.total_checks} | {s.passed} | {s.failed} | {s.warnings} |\n"

        md += "\n## Issues\n\n"

        if self.report.critical_issues:
            md += "### Critical Issues\n\n"
            for issue in self.report.critical_issues:
                md += f"- **{issue.get('check_type')}**: {issue.get('message')}\n"
                if issue.get('suggestion'):
                    md += f"  - Suggestion: {issue.get('suggestion')}\n"
            md += "\n"

        md += "### All Issues\n\n"
        for issue in self.report.all_issues:
            severity = issue.get('severity', 'info').upper()
            md += f"- [{severity}] **{issue.get('check_type')}**: {issue.get('message')}\n"

        if self.report.recommendations:
            md += "\n## Recommendations\n\n"
            for rec in self.report.recommendations:
                md += f"- {rec}\n"

        if filepath:
            with open(filepath, 'w') as f:
                f.write(md)

        return md

    def export_csv(self, filepath: str) -> None:
        """
        Export issues as CSV.

        Args:
            filepath: File path to write to
        """
        if not self.report:
            raise ValueError("No report generated. Call generate_report() first.")

        import csv

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Severity', 'Validator', 'Check Type', 'Message',
                'Location', 'Suggestion', 'Standard Reference'
            ])

            for issue in self.report.all_issues:
                writer.writerow([
                    issue.get('severity', ''),
                    issue.get('validator', ''),
                    issue.get('check_type', ''),
                    issue.get('message', ''),
                    issue.get('location', ''),
                    issue.get('suggestion', ''),
                    issue.get('standard_reference', ''),
                ])

    def get_summary_dict(self) -> Dict[str, Any]:
        """Get a simple summary dictionary."""
        if not self.report:
            return {}

        return {
            "status": self.report.overall_status,
            "pass_rate": round(self.report.overall_pass_rate, 2),
            "total_checks": self.report.total_checks,
            "passed": self.report.total_passed,
            "failed": self.report.total_failed,
            "warnings": self.report.total_warnings,
            "critical": self.report.total_critical,
            "recommendations": self.report.recommendations,
        }

    def export_pdf(self, filepath: str, include_charts: bool = True) -> bytes:
        """
        Export report as professional PDF document.

        Args:
            filepath: File path to write to
            include_charts: Whether to include pie/bar charts

        Returns:
            PDF bytes
        """
        if not self.report:
            raise ValueError("No report generated. Call generate_report() first.")

        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required for PDF export. Install with: pip install reportlab")

        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        # Get styles
        styles = getSampleStyleSheet()

        # Custom styles
        styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            textColor=colors.HexColor('#1a1a2e')
        ))
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.HexColor('#16213e')
        ))
        styles.add(ParagraphStyle(
            name='StatusPass',
            parent=styles['Normal'],
            fontSize=18,
            textColor=colors.HexColor('#28a745'),
            fontName='Helvetica-Bold'
        ))
        styles.add(ParagraphStyle(
            name='StatusFail',
            parent=styles['Normal'],
            fontSize=18,
            textColor=colors.HexColor('#dc3545'),
            fontName='Helvetica-Bold'
        ))
        styles.add(ParagraphStyle(
            name='StatusWarning',
            parent=styles['Normal'],
            fontSize=18,
            textColor=colors.HexColor('#ffc107'),
            fontName='Helvetica-Bold'
        ))

        # Build document elements
        elements = []

        # === TITLE SECTION ===
        elements.append(Paragraph("VALIDATION REPORT", styles['ReportTitle']))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a1a2e')))
        elements.append(Spacer(1, 12))

        # Metadata table
        meta_data = [
            ['Drawing Number:', self.report.metadata.drawing_number or 'Not Specified'],
            ['Revision:', self.report.metadata.drawing_revision or '-'],
            ['Project:', self.report.metadata.project_name or 'Not Specified'],
            ['Report ID:', self.report.metadata.report_id],
            ['Generated:', self.report.metadata.generated_at],
        ]
        meta_table = Table(meta_data, colWidths=[1.5*inch, 4*inch])
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 20))

        # === OVERALL STATUS ===
        status_style = styles['StatusPass']
        if self.report.overall_status in ['FAIL', 'CRITICAL']:
            status_style = styles['StatusFail']
        elif self.report.overall_status == 'PASS_WITH_WARNINGS':
            status_style = styles['StatusWarning']

        elements.append(Paragraph(f"Overall Status: {self.report.overall_status}", status_style))
        elements.append(Spacer(1, 20))

        # === SUMMARY STATISTICS ===
        elements.append(Paragraph("Summary Statistics", styles['SectionHeader']))

        # Summary stats table
        stats_data = [
            ['Metric', 'Value'],
            ['Total Checks', str(self.report.total_checks)],
            ['Passed', str(self.report.total_passed)],
            ['Failed', str(self.report.total_failed)],
            ['Warnings', str(self.report.total_warnings)],
            ['Critical Issues', str(self.report.total_critical)],
            ['Pass Rate', f"{self.report.overall_pass_rate:.1f}%"],
        ]
        stats_table = Table(stats_data, colWidths=[2*inch, 1.5*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            # Highlight pass rate row
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f5e9') if self.report.overall_pass_rate >= 80 else colors.HexColor('#ffebee')),
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 20))

        # === PIE CHART ===
        if include_charts and self.report.total_checks > 0:
            elements.append(Paragraph("Results Distribution", styles['SectionHeader']))

            drawing = Drawing(400, 200)
            pie = Pie()
            pie.x = 150
            pie.y = 25
            pie.width = 120
            pie.height = 120

            # Data for pie chart
            pie_data = [self.report.total_passed, self.report.total_failed, self.report.total_warnings]
            pie_labels = ['Passed', 'Failed', 'Warnings']
            pie_colors = [colors.HexColor('#28a745'), colors.HexColor('#dc3545'), colors.HexColor('#ffc107')]

            # Filter out zero values
            filtered_data = []
            filtered_labels = []
            filtered_colors = []
            for i, val in enumerate(pie_data):
                if val > 0:
                    filtered_data.append(val)
                    filtered_labels.append(f"{pie_labels[i]}: {val}")
                    filtered_colors.append(pie_colors[i])

            if filtered_data:
                pie.data = filtered_data
                pie.labels = filtered_labels
                pie.slices.strokeWidth = 0.5
                for i, c in enumerate(filtered_colors):
                    pie.slices[i].fillColor = c

                drawing.add(pie)
                elements.append(drawing)
                elements.append(Spacer(1, 20))

        # === VALIDATOR BREAKDOWN ===
        elements.append(Paragraph("Validator Results", styles['SectionHeader']))

        validator_data = [['Validator', 'Status', 'Checks', 'Passed', 'Failed', 'Warnings', 'Pass Rate']]
        for summary in self.report.validator_summaries:
            validator_data.append([
                summary.validator_name[:25],
                summary.status,
                str(summary.total_checks),
                str(summary.passed),
                str(summary.failed),
                str(summary.warnings),
                f"{summary.pass_rate:.0f}%"
            ])

        validator_table = Table(validator_data, colWidths=[1.8*inch, 1*inch, 0.6*inch, 0.6*inch, 0.6*inch, 0.7*inch, 0.7*inch])

        # Table style
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]

        # Color-code status cells
        for i, summary in enumerate(self.report.validator_summaries, start=1):
            if summary.status in ['FAIL', 'CRITICAL']:
                table_style.append(('BACKGROUND', (1, i), (1, i), colors.HexColor('#ffcdd2')))
                table_style.append(('TEXTCOLOR', (1, i), (1, i), colors.HexColor('#c62828')))
            elif summary.status == 'PASS_WITH_WARNINGS':
                table_style.append(('BACKGROUND', (1, i), (1, i), colors.HexColor('#fff9c4')))
            else:
                table_style.append(('BACKGROUND', (1, i), (1, i), colors.HexColor('#c8e6c9')))

        validator_table.setStyle(TableStyle(table_style))
        elements.append(validator_table)
        elements.append(Spacer(1, 20))

        # === CRITICAL ISSUES ===
        if self.report.critical_issues:
            elements.append(Paragraph("Critical Issues (Requires Immediate Attention)", styles['SectionHeader']))

            critical_data = [['Validator', 'Check Type', 'Issue', 'Suggestion']]
            for issue in self.report.critical_issues[:10]:  # Limit to 10
                critical_data.append([
                    issue.get('validator', '-')[:15],
                    issue.get('check_type', '-')[:20],
                    issue.get('message', '-')[:50],
                    (issue.get('suggestion', '-') or '-')[:40]
                ])

            critical_table = Table(critical_data, colWidths=[1*inch, 1.3*inch, 2.5*inch, 2*inch])
            critical_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c62828')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffebee')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(critical_table)
            elements.append(Spacer(1, 20))

        # === ALL ISSUES (Page Break) ===
        if self.report.all_issues:
            elements.append(PageBreak())
            elements.append(Paragraph("All Issues", styles['SectionHeader']))

            # Group issues by severity
            severity_order = ['critical', 'error', 'warning', 'info']
            severity_colors_map = {
                'critical': colors.HexColor('#c62828'),
                'error': colors.HexColor('#d32f2f'),
                'warning': colors.HexColor('#f57c00'),
                'info': colors.HexColor('#1976d2')
            }

            issues_data = [['#', 'Severity', 'Validator', 'Check Type', 'Message']]
            for idx, issue in enumerate(self.report.all_issues[:50], start=1):  # Limit to 50
                issues_data.append([
                    str(idx),
                    issue.get('severity', 'info').upper(),
                    issue.get('validator', '-')[:12],
                    issue.get('check_type', '-')[:18],
                    issue.get('message', '-')[:60]
                ])

            issues_table = Table(issues_data, colWidths=[0.3*inch, 0.7*inch, 0.9*inch, 1.3*inch, 3.8*inch])

            issue_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]

            # Color severity column
            for idx, issue in enumerate(self.report.all_issues[:50], start=1):
                severity = issue.get('severity', 'info')
                if severity in severity_colors_map:
                    issue_style.append(('TEXTCOLOR', (1, idx), (1, idx), severity_colors_map[severity]))
                    issue_style.append(('FONTNAME', (1, idx), (1, idx), 'Helvetica-Bold'))

            issues_table.setStyle(TableStyle(issue_style))
            elements.append(issues_table)

            if len(self.report.all_issues) > 50:
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(
                    f"... and {len(self.report.all_issues) - 50} more issues. See full JSON/CSV export for complete list.",
                    styles['Normal']
                ))

        # === RECOMMENDATIONS ===
        if self.report.recommendations:
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("Recommendations", styles['SectionHeader']))

            for i, rec in enumerate(self.report.recommendations, start=1):
                elements.append(Paragraph(f"{i}. {rec}", styles['Normal']))
                elements.append(Spacer(1, 4))

        # === FOOTER ===
        elements.append(Spacer(1, 30))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(
            f"Generated by Project Vulcan Validation System | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=1)
        ))

        # Build PDF
        doc.build(elements)

        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()

        # Write to file
        if filepath:
            with open(filepath, 'wb') as f:
                f.write(pdf_bytes)
            logger.info(f"PDF report saved to: {filepath}")

        return pdf_bytes

    def export_pdf_summary(self, filepath: str) -> bytes:
        """
        Export a one-page executive summary PDF.

        Args:
            filepath: File path to write to

        Returns:
            PDF bytes
        """
        if not self.report:
            raise ValueError("No report generated. Call generate_report() first.")

        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required for PDF export. Install with: pip install reportlab")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch
        )

        styles = getSampleStyleSheet()
        elements = []

        # Title
        elements.append(Paragraph(
            "VALIDATION SUMMARY",
            ParagraphStyle('Title', parent=styles['Heading1'], fontSize=28, alignment=1)
        ))
        elements.append(Spacer(1, 20))

        # Drawing info
        elements.append(Paragraph(
            f"Drawing: {self.report.metadata.drawing_number or 'N/A'} Rev {self.report.metadata.drawing_revision or '-'}",
            ParagraphStyle('DrawingInfo', parent=styles['Normal'], fontSize=12, alignment=1)
        ))
        elements.append(Spacer(1, 30))

        # Big status indicator
        status_color = colors.HexColor('#28a745')
        if self.report.overall_status in ['FAIL', 'CRITICAL']:
            status_color = colors.HexColor('#dc3545')
        elif self.report.overall_status == 'PASS_WITH_WARNINGS':
            status_color = colors.HexColor('#ffc107')

        elements.append(Paragraph(
            self.report.overall_status,
            ParagraphStyle('BigStatus', parent=styles['Heading1'], fontSize=48, textColor=status_color, alignment=1)
        ))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(
            f"{self.report.overall_pass_rate:.1f}% Pass Rate",
            ParagraphStyle('PassRate', parent=styles['Normal'], fontSize=18, alignment=1)
        ))
        elements.append(Spacer(1, 30))

        # Quick stats
        stats = [
            [str(self.report.total_checks), str(self.report.total_passed), str(self.report.total_failed), str(self.report.total_critical)],
            ['Total Checks', 'Passed', 'Failed', 'Critical']
        ]
        stats_table = Table(stats, colWidths=[1.5*inch]*4)
        stats_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, 0), 24),
            ('FONTSIZE', (0, 1), (-1, 1), 10),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#28a745')),
            ('TEXTCOLOR', (2, 0), (2, 0), colors.HexColor('#dc3545')),
            ('TEXTCOLOR', (3, 0), (3, 0), colors.HexColor('#c62828')),
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 40))

        # Critical issues summary
        if self.report.critical_issues:
            elements.append(Paragraph(
                f"CRITICAL ISSUES: {len(self.report.critical_issues)}",
                ParagraphStyle('CriticalHeader', parent=styles['Heading2'], textColor=colors.HexColor('#c62828'))
            ))
            for issue in self.report.critical_issues[:5]:
                elements.append(Paragraph(
                    f"• {issue.get('message', 'Unknown issue')[:80]}",
                    styles['Normal']
                ))
        else:
            elements.append(Paragraph(
                "No Critical Issues",
                ParagraphStyle('NoIssues', parent=styles['Heading2'], textColor=colors.HexColor('#28a745'))
            ))

        # Build
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        if filepath:
            with open(filepath, 'wb') as f:
                f.write(pdf_bytes)

        return pdf_bytes
