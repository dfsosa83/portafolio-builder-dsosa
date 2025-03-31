import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime

def generate_pdf_report(portfolio_value, sharpe, annual_return, 
                      annual_volatility, max_drawdown, cleaned_weights, fig):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, 
                          pagesize=letter,
                          rightMargin=24,
                          leftMargin=24,
                          topMargin=24,
                          bottomMargin=24)
    styles = getSampleStyleSheet()
    elements = []
    
    # ===== Custom Styles =====
    styles.add(ParagraphStyle(
        name='MainTitle',
        fontSize=16,
        leading=18,
        alignment=TA_CENTER,
        spaceAfter=6,
        textColor=colors.HexColor("#2c7da0")
    ))
    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontSize=12,
        textColor=colors.darkblue,
        spaceBefore=12,
        spaceAfter=6,
        alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        name='MetricHeader',
        fontSize=10,
        textColor=colors.darkgrey,
        alignment=TA_RIGHT
    ))

    # ===== Section 1: Header =====
    elements.append(Paragraph("Portfolio Optimization Report", styles['MainTitle']))
    elements.append(Spacer(1, 4))
    elements.append(Image('src/imgs/logo.png', width=1.5*inch, height=0.5*inch, hAlign='CENTER'))
    elements.append(Paragraph(
        f"<font size=9 color='#6c757d'>Generated on: {datetime.now().strftime('%B %d, %Y')}</font>",
        ParagraphStyle(name='DateStyle', alignment=TA_CENTER)
    ))
    elements.append(Spacer(1, 18))

    # ===== Section 2: Two Column Content =====
    col_width = (doc.width - 12) / 2  # 12pt gap between columns
    
    # Left Column: Performance Metrics
    metrics_table = Table([
        [Paragraph("Sharpe Ratio", styles['Normal']), Paragraph(f"{sharpe:.2f}", styles['MetricHeader'])],
        [Paragraph("Annual Return", styles['Normal']), Paragraph(f"{annual_return:.1%}", styles['MetricHeader'])],
        [Paragraph("Volatility", styles['Normal']), Paragraph(f"{annual_volatility:.1%}", styles['MetricHeader'])],
        [Paragraph("Max Drawdown", styles['Normal']), Paragraph(f"{max_drawdown:.1%}", styles['MetricHeader'])]
    ], colWidths=[col_width*0.6, col_width*0.4],
    style=TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 0.5, colors.lightgrey),
        ('LINEBELOW', (0,-1), (-1,-1), 0.5, colors.lightgrey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))

    # Right Column: Asset Allocation
    allocation_data = [[
        Paragraph("Asset", styles['Normal']),
        Paragraph("Weight", styles['Normal']),
        Paragraph("Value", styles['Normal'])
    ]]
    for ticker, weight in cleaned_weights.items():
        if weight > 0.001:
            allocation_data.append([
                Paragraph(ticker, styles['Normal']),
                Paragraph(f"{weight:.1%}", styles['Normal']),
                Paragraph(f"${weight * portfolio_value:,.0f}", styles['Normal'])
            ])

    allocation_table = Table(allocation_data, 
        colWidths=[col_width*0.4, col_width*0.3, col_width*0.3],
        style=TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f8f9fa")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('ALIGN', (1,1), (-1,-1), 'RIGHT')
        ])
    )

    # Combine into two-column layout
    two_col_table = Table([
        [metrics_table, allocation_table]
    ], colWidths=[col_width, col_width],
    style=TableStyle([
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    
    elements.append(Paragraph("Performance Overview", styles['SectionHeader']))
    elements.append(two_col_table)
    elements.append(Spacer(1, 12))

    # ===== Section 3: Full-width Historical Performance =====
    elements.append(Paragraph("Historical Performance", styles['SectionHeader']))
    elements.append(Image(fig, width=doc.width, height=3.5*inch, hAlign='CENTER'))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
