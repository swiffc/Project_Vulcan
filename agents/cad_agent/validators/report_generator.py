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
