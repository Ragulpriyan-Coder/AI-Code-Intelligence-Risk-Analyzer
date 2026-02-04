"""
PDF Report Generator using ReportLab.
Generates professional PDF reports from analysis results.
"""
import io
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    HRFlowable,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


# Color scheme (dark theme inspired)
COLORS = {
    "primary": colors.HexColor("#6366f1"),      # Indigo
    "secondary": colors.HexColor("#8b5cf6"),    # Purple
    "success": colors.HexColor("#22c55e"),      # Green
    "warning": colors.HexColor("#f59e0b"),      # Amber
    "danger": colors.HexColor("#ef4444"),       # Red
    "info": colors.HexColor("#06b6d4"),         # Cyan
    "dark": colors.HexColor("#1f2937"),         # Gray 800
    "light": colors.HexColor("#f3f4f6"),        # Gray 100
    "muted": colors.HexColor("#6b7280"),        # Gray 500
}


def get_score_color(score: float) -> colors.Color:
    """Get color based on score value."""
    if score >= 80:
        return COLORS["success"]
    elif score >= 60:
        return COLORS["info"]
    elif score >= 40:
        return COLORS["warning"]
    else:
        return COLORS["danger"]


def get_urgency_color(urgency: str) -> colors.Color:
    """Get color based on urgency level."""
    urgency_colors = {
        "Low": COLORS["success"],
        "Medium": COLORS["warning"],
        "High": colors.HexColor("#f97316"),  # Orange
        "Critical": COLORS["danger"],
    }
    return urgency_colors.get(urgency, COLORS["muted"])


def create_styles() -> Dict[str, ParagraphStyle]:
    """Create custom paragraph styles for the report."""
    base_styles = getSampleStyleSheet()

    custom_styles = {
        "Title": ParagraphStyle(
            "CustomTitle",
            parent=base_styles["Title"],
            fontSize=24,
            textColor=COLORS["primary"],
            spaceAfter=20,
            alignment=TA_CENTER,
        ),
        "Subtitle": ParagraphStyle(
            "CustomSubtitle",
            parent=base_styles["Normal"],
            fontSize=12,
            textColor=COLORS["muted"],
            spaceAfter=30,
            alignment=TA_CENTER,
        ),
        "Heading1": ParagraphStyle(
            "CustomH1",
            parent=base_styles["Heading1"],
            fontSize=18,
            textColor=COLORS["dark"],
            spaceBefore=20,
            spaceAfter=12,
            borderColor=COLORS["primary"],
            borderWidth=0,
            borderPadding=0,
        ),
        "Heading2": ParagraphStyle(
            "CustomH2",
            parent=base_styles["Heading2"],
            fontSize=14,
            textColor=COLORS["secondary"],
            spaceBefore=15,
            spaceAfter=8,
        ),
        "Body": ParagraphStyle(
            "CustomBody",
            parent=base_styles["Normal"],
            fontSize=10,
            textColor=COLORS["dark"],
            spaceAfter=8,
            leading=14,
        ),
        "SmallText": ParagraphStyle(
            "SmallText",
            parent=base_styles["Normal"],
            fontSize=8,
            textColor=COLORS["muted"],
        ),
        "ScoreValue": ParagraphStyle(
            "ScoreValue",
            parent=base_styles["Normal"],
            fontSize=28,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "ScoreLabel": ParagraphStyle(
            "ScoreLabel",
            parent=base_styles["Normal"],
            fontSize=10,
            textColor=COLORS["muted"],
            alignment=TA_CENTER,
        ),
    }

    return custom_styles


def generate_pdf_report(
    repo_name: str,
    scores: Dict[str, Any],
    security_summary: Dict[str, Any],
    maintainability_summary: Dict[str, Any],
    architecture_summary: Dict[str, Any],
    tech_debt: Dict[str, Any],
    llm_explanation: Optional[str] = None,
    analysis_metadata: Optional[Dict[str, Any]] = None
) -> bytes:
    """
    Generate a PDF report from analysis results.

    Args:
        repo_name: Name of the analyzed repository
        scores: Score results
        security_summary: Security analysis summary
        maintainability_summary: Maintainability summary
        architecture_summary: Architecture summary
        tech_debt: Technical debt summary
        llm_explanation: Optional LLM-generated explanation
        analysis_metadata: Optional metadata (files analyzed, duration, etc.)

    Returns:
        PDF file as bytes
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = create_styles()
    story = []

    # ===== TITLE PAGE =====
    story.append(Spacer(1, 1 * inch))
    story.append(Paragraph("Code Analysis Report", styles["Title"]))
    story.append(Paragraph(repo_name, styles["Subtitle"]))

    # Generation timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    story.append(Paragraph(f"Generated: {timestamp}", styles["SmallText"]))
    story.append(Spacer(1, 0.5 * inch))

    # ===== SCORE CARDS =====
    story.append(Paragraph("Executive Summary", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLORS["primary"]))
    story.append(Spacer(1, 0.2 * inch))

    # Create score cards table
    score_data = [
        [
            create_score_cell("Security", scores.get("security_score", 0), styles),
            create_score_cell("Maintainability", scores.get("maintainability_score", 0), styles),
            create_score_cell("Architecture", scores.get("architecture_score", 0), styles),
        ],
    ]

    score_table = Table(score_data, colWidths=[2.3 * inch, 2.3 * inch, 2.3 * inch])
    score_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (0, 0), 1, COLORS["light"]),
        ("BOX", (1, 0), (1, 0), 1, COLORS["light"]),
        ("BOX", (2, 0), (2, 0), 1, COLORS["light"]),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.3 * inch))

    # Tech Debt and Urgency row
    urgency = scores.get("refactor_urgency", "Unknown")
    debt_index = scores.get("tech_debt_index", 0)

    urgency_data = [
        [
            Paragraph(f"<b>Technical Debt Index:</b> {debt_index:.0f}/100", styles["Body"]),
            Paragraph(f"<b>Refactor Urgency:</b> <font color='{get_urgency_color(urgency).hexval()}'>{urgency}</font>", styles["Body"]),
        ]
    ]
    urgency_table = Table(urgency_data, colWidths=[3.5 * inch, 3.5 * inch])
    story.append(urgency_table)
    story.append(Spacer(1, 0.3 * inch))

    # ===== SECURITY SECTION =====
    story.append(Paragraph("Security Analysis", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLORS["danger"]))

    risk_level = security_summary.get("risk_level", "Unknown")
    total_issues = security_summary.get("total_issues", 0)

    story.append(Paragraph(
        f"<b>Risk Level:</b> <font color='{get_urgency_color(risk_level).hexval()}'>{risk_level}</font> | "
        f"<b>Total Issues:</b> {total_issues}",
        styles["Body"]
    ))

    # Severity breakdown
    severity = security_summary.get("severity_breakdown", {})
    if severity:
        severity_text = " | ".join([
            f"Critical: {severity.get('CRITICAL', 0)}",
            f"High: {severity.get('HIGH', 0)}",
            f"Medium: {severity.get('MEDIUM', 0)}",
            f"Low: {severity.get('LOW', 0)}",
        ])
        story.append(Paragraph(severity_text, styles["SmallText"]))

    # Top security issues
    top_issues = security_summary.get("top_issues", [])[:5]
    if top_issues:
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph("Top Security Issues:", styles["Heading2"]))

        issue_data = [["Severity", "Issue", "File"]]
        for issue in top_issues:
            issue_data.append([
                issue.get("severity", ""),
                issue.get("title", "")[:40],
                issue.get("file", "")[:30],
            ])

        issue_table = Table(issue_data, colWidths=[1 * inch, 3 * inch, 2.5 * inch])
        issue_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), COLORS["dark"]),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, COLORS["light"]),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(issue_table)

    story.append(Spacer(1, 0.2 * inch))

    # ===== MAINTAINABILITY SECTION =====
    story.append(Paragraph("Maintainability Analysis", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLORS["info"]))

    avg_complexity = maintainability_summary.get("average_complexity", 0)
    avg_mi = maintainability_summary.get("average_maintainability_index", 0)
    high_complexity = maintainability_summary.get("high_complexity_functions", [])

    maint_data = [
        ["Metric", "Value"],
        ["Average Complexity", f"{avg_complexity:.1f}"],
        ["Maintainability Index", f"{avg_mi:.1f}"],
        ["High Complexity Functions", str(len(high_complexity))],
        ["Files Analyzed", str(maintainability_summary.get("files_analyzed", 0))],
    ]

    maint_table = Table(maint_data, colWidths=[3 * inch, 2 * inch])
    maint_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLORS["dark"]),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, COLORS["light"]),
        ("ALIGN", (1, 1), (1, -1), "CENTER"),
    ]))
    story.append(maint_table)
    story.append(Spacer(1, 0.2 * inch))

    # ===== ARCHITECTURE SECTION =====
    story.append(Paragraph("Architecture Analysis", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLORS["secondary"]))

    arch_data = [
        ["Metric", "Value"],
        ["Total Modules", str(architecture_summary.get("total_modules", 0))],
        ["Total Packages", str(architecture_summary.get("total_packages", 0))],
        ["Modularity Score", f"{architecture_summary.get('modularity_score', 0):.1f}"],
        ["Circular Dependencies", str(architecture_summary.get("circular_dependencies_count", 0))],
        ["Hub Modules", str(len(architecture_summary.get("hub_modules", [])))],
    ]

    arch_table = Table(arch_data, colWidths=[3 * inch, 2 * inch])
    arch_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLORS["dark"]),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, COLORS["light"]),
        ("ALIGN", (1, 1), (1, -1), "CENTER"),
    ]))
    story.append(arch_table)

    # ===== TECHNICAL DEBT SECTION =====
    story.append(PageBreak())
    story.append(Paragraph("Technical Debt & Priorities", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLORS["warning"]))

    story.append(Paragraph(tech_debt.get("summary", ""), styles["Body"]))
    story.append(Spacer(1, 0.1 * inch))

    # Priority items
    priority_items = tech_debt.get("priority_items", [])[:8]
    if priority_items:
        story.append(Paragraph("Priority Items:", styles["Heading2"]))

        priority_data = [["Priority", "Category", "Issue", "Recommendation"]]
        for item in priority_items:
            priority_data.append([
                str(item.get("priority", "")),
                item.get("category", "")[:15],
                item.get("title", "")[:25],
                item.get("recommendation", "")[:35],
            ])

        priority_table = Table(priority_data, colWidths=[0.7 * inch, 1.2 * inch, 2 * inch, 2.6 * inch])
        priority_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), COLORS["dark"]),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, COLORS["light"]),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ]))
        story.append(priority_table)

    # ===== AI INSIGHTS SECTION =====
    if llm_explanation:
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph("AI-Powered Insights", styles["Heading1"]))
        story.append(HRFlowable(width="100%", thickness=1, color=COLORS["primary"]))

        # Convert markdown to simple paragraphs
        for line in llm_explanation.split("\n"):
            line = line.strip()
            if not line:
                story.append(Spacer(1, 0.05 * inch))
            elif line.startswith("## "):
                story.append(Paragraph(line[3:], styles["Heading2"]))
            elif line.startswith("- ") or line.startswith("* "):
                story.append(Paragraph(f"• {line[2:]}", styles["Body"]))
            elif line.startswith("1.") or line.startswith("2.") or line.startswith("3."):
                story.append(Paragraph(line, styles["Body"]))
            elif line.startswith("#"):
                continue  # Skip other headers
            elif line.startswith("---"):
                story.append(HRFlowable(width="50%", thickness=0.5, color=COLORS["light"]))
            else:
                # Clean up markdown formatting
                line = line.replace("**", "").replace("*", "")
                story.append(Paragraph(line, styles["Body"]))

    # ===== FOOTER =====
    story.append(Spacer(1, 0.5 * inch))
    story.append(HRFlowable(width="100%", thickness=1, color=COLORS["light"]))
    story.append(Paragraph(
        "Generated by AI Code Intelligence & Risk Analyzer",
        styles["SmallText"]
    ))

    if analysis_metadata:
        meta_text = f"Files: {analysis_metadata.get('files_analyzed', 0)} | "
        meta_text += f"Lines: {analysis_metadata.get('total_lines', 0)} | "
        meta_text += f"Duration: {analysis_metadata.get('duration', 0):.1f}s"
        story.append(Paragraph(meta_text, styles["SmallText"]))

    # Build PDF
    doc.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes


def create_score_cell(label: str, score: float, styles: Dict) -> List:
    """Create a score cell for the summary table."""
    color = get_score_color(score)

    return [
        Paragraph(f"<font color='{color.hexval()}'><b>{score:.0f}</b></font>", styles["ScoreValue"]),
        Paragraph(label, styles["ScoreLabel"]),
    ]
