from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4

from app.services.dashboard_service import generate_dashboard_insights
from sqlalchemy.orm import Session
from app.models.control import Control
import os


def generate_compliance_report(db: Session, tenant_id: str, file_path: str):
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    normal_style = styles["Normal"]

    # Title
    elements.append(Paragraph("Compliance Risk Report", title_style))
    elements.append(Spacer(1, 0.3 * inch))

    # Summary Metrics
    controls = db.query(Control).filter(Control.tenant_id == tenant_id).all()
    total = len(controls)
    high = len([c for c in controls if c.control_risk_level == "HIGH"])
    medium = len([c for c in controls if c.control_risk_level == "MEDIUM"])
    low = len([c for c in controls if c.control_risk_level == "LOW"])

    avg_risk = sum(c.control_failure_prob or 0 for c in controls) / total if total else 0
    audit_readiness = 1 - avg_risk

    elements.append(Paragraph(f"Tenant: {tenant_id}", normal_style))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"Audit Readiness: {audit_readiness*100:.2f}%", normal_style))
    elements.append(Paragraph(f"Average Risk: {avg_risk*100:.2f}%", normal_style))
    elements.append(Paragraph(f"Total Controls: {total}", normal_style))
    elements.append(Spacer(1, 0.3 * inch))

    # Risk Distribution Table
    data = [
        ["Risk Level", "Count"],
        ["HIGH", high],
        ["MEDIUM", medium],
        ["LOW", low],
    ]

    table = Table(data, colWidths=[2 * inch, 1 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ]))

    elements.append(Paragraph("Risk Distribution", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(table)
    elements.append(Spacer(1, 0.4 * inch))

    # High Risk Controls
    elements.append(Paragraph("High Risk Controls", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    high_controls = [
        c for c in controls if c.control_risk_level == "HIGH"
    ]

    high_data = [["Control ID", "Failure Probability"]]

    for c in high_controls:
        high_data.append([
            c.id,
            f"{(c.control_failure_prob or 0)*100:.2f}%"
        ])

    high_table = Table(high_data, colWidths=[2 * inch, 2 * inch])
    high_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(high_table)
    elements.append(Spacer(1, 0.4 * inch))

    # Insights
    elements.append(Paragraph("Risk Insights", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    insights = generate_dashboard_insights(db, tenant_id)

    for insight in insights:
        elements.append(Paragraph(f"- {insight}", normal_style))
        elements.append(Spacer(1, 0.1 * inch))

    doc.build(elements)
