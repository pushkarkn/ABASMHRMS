import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from datetime import date

def generate_leave_request_pdf(request_data, action):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        doc = SimpleDocTemplate(tmp_file.name, pagesize=letter, topMargin=1*inch, bottomMargin=1*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
        styles = getSampleStyleSheet()

        # Modify existing styles instead of adding new ones
        styles['Title'].fontSize = 20
        styles['Title'].alignment = 1
        styles['Title'].spaceAfter = 0.2*inch
        styles['Title'].color = colors.HexColor("#e6e6fa")
        styles['Title'].fontName = "Helvetica-Bold"

        styles['Heading2'].fontSize = 14
        styles['Heading2'].spaceAfter = 0.1*inch

        styles['Normal'].fontSize = 11
        styles['Normal'].spaceAfter = 0.1*inch

        elements = []

        # Function to create a boxed section
        def create_boxed_section(title, content):
            data = [[Paragraph(title, styles['Heading2'])]] + [[Paragraph(item, styles['Normal'])] for item in content]
            t = Table(data, colWidths=[7.5*inch], rowHeights=[0.50*inch]*len(data))
            t.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#9E9E9E")),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E0E0E0")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#424242")),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 2),
                ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
            ]))
            return t

        # Title
        elements.append(Paragraph("Leave Request Form", styles['Title']))
        elements.append(Spacer(1, 0.2*inch))

        # Employee Information section (table)
        data = [
            ["Name", "Employee ID", "Job Title"],
            [request_data['Name'], request_data['Employee ID'], request_data['Job Title']],
            ["Leave Request Days", "Dates of Absence", "Type of Leave"],
            [str(request_data['Leave Days']), f"From {request_data['From']} To {request_data['To']}", request_data['Leave Type']]
        ]
        table = Table(data, colWidths=[2.5*inch, 2.5*inch, 2.5*inch], rowHeights=[0.45*inch]*len(data))
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#9E9E9E")),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E0E0E0")),  # First row background
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor("#E0E0E0")),  # Third row background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#424242")),
            ('TEXTCOLOR', (0, 2), (-1, 2), colors.HexColor("#424242")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 2), (-1, 2), 10),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
            ('FONTNAME', (0, 3), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, 1), 10),
            ('FONTSIZE', (0, 3), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))

        # Reason for Leave section (boxed)
        elements.append(create_boxed_section("Reason for Leave", [request_data['Reason']]))
        elements.append(Spacer(1, 0.2*inch))

        # Employee Signature section (boxed)
        elements.append(create_boxed_section("Employee Signature", [
            "I understand that this request is subject to approval by my employer.",
            "Signature: ______________________________       Date: ______________________________",
        ]))
        elements.append(Spacer(1, 0.2*inch))

        # HR Department section (boxed)
        elements.append(create_boxed_section("HR Department", [
            "Signature: ______________________________       Date: ______________________________",
        ]))
        elements.append(Spacer(1, 0.2*inch))

        # Manager Approval section (boxed)
        decision_text = "Approved" if action == 'Approve' else "Denied"
        decision_color = colors.green if action == 'Approve' else colors.red
        elements.append(create_boxed_section("Manager Approval", [
            f"Decision: <font color='{decision_color}'>{decision_text}</font>",
            "Signature: ______________________________       Date: ______________________________",
        ]))

        doc.build(elements)
        return tmp_file.name

def sick_leave_request_html(request_data, action):
    # This function is no longer needed, but keep it for backwards compatibility
    # You can call generate_leave_request_pdf directly instead
    return generate_leave_request_pdf(request_data, action)




import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
from datetime import datetime

def generate_contract_pdf(agreements, first_party, second_party, date_of_contract):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        doc = SimpleDocTemplate(
            tmp_file.name,
            pagesize=letter,
            topMargin=1*inch,
            bottomMargin=1*inch,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch
        )
        styles = getSampleStyleSheet()
        elements = []

        # Custom styles
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor("#000000"),
            alignment=1,
            spaceAfter=0.5*inch,
            fontName='Helvetica-Bold'
        )

        header_style = ParagraphStyle(
            'Header',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor("#000000"),
            spaceAfter=0.3*inch,
            fontName='Helvetica-Bold'
        )

        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=0.15*inch,
            leading=14,  # Increased line spacing
            fontName='Helvetica'
        )

        # Title
        elements.append(Paragraph("EMPLOYMENT CONTRACT", title_style))
        elements.append(Spacer(1, 0.2*inch))

        # Header Information
        header_text = f"""
        This Employment Contract is entered into on <b>{date_of_contract.strftime('%B %d, %Y')}</b>, by and between:

        <b>{first_party}</b>, hereinafter referred to as the "Employer",

        and

        <b>{second_party}</b>, hereinafter referred to as the "Employee".

        The Employer and Employee are collectively referred to as the "Parties".
        """

        elements.append(Paragraph(header_text, normal_style))
        elements.append(Spacer(1, 0.3*inch))

        # Agreements (Terms and Conditions)
        terms_text = "<br/>".join([f"{i}. {agreement['content']}" for i, agreement in enumerate(agreements, 1)])
        terms_conditions = f"""
        <b>TERMS AND CONDITIONS:</b><br/>
        {terms_text}
        """
        terms_conditions_paragraph = Paragraph(terms_conditions, normal_style)
        terms_conditions_paragraph.keepWithNext = True
        elements.append(terms_conditions_paragraph)

        for i, agreement in enumerate(agreements, 1):
            if i < len(agreements):
                elements.append(Spacer(1, 0.1*inch))  # Add space between agreements

        elements.append(Spacer(1, 0.5*inch))  # Additional space after terms

        # Signature block
        elements.append(Paragraph("IN WITNESS WHEREOF, the Parties have executed this Contract as of the date first above written.", normal_style))
        elements.append(Spacer(1, 0.2*inch))

        signature_table = Table([
            ["EMPLOYER:", "EMPLOYEE:"],
            [f"Name: {first_party}", f"Name: {second_party}"],
            ["Signature: _________________", "Signature: _________________"],
            ["Date: _____________________", "Date: _____________________"],
        ], colWidths=[3*inch, 3*inch])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        elements.append(signature_table)

        doc.build(elements)
        return tmp_file.name