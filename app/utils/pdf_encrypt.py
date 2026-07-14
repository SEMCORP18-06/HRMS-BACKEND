import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from pypdf import PdfReader, PdfWriter

def generate_salary_breakup_pdf(employee_data: dict, payroll_data: dict, temp_path: str):
    """
    Generates a sandboxed salary breakup PDF based strictly on SEMCORP schema layout.
    """
    doc = SimpleDocTemplate(temp_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    
    company_style = ParagraphStyle(
        'Company',
        parent=normal_style,
        fontName='Helvetica-Bold',
        fontSize=12,
        alignment=1, # Center
        spaceAfter=1
    )
    address_style = ParagraphStyle(
        'Address',
        parent=normal_style,
        fontName='Helvetica',
        fontSize=9,
        alignment=1, # Center
        spaceAfter=1
    )
    title_style = ParagraphStyle(
        'Title',
        parent=normal_style,
        fontName='Helvetica-Bold',
        fontSize=11,
        alignment=1, # Center
        spaceAfter=10
    )
    
    pay_period = payroll_data.get("pay_period", "")
    
    # Header Configuration
    header_data = [
        [Paragraph("SEMCORP Process & Vacuum Systems Pvt. Ltd.", company_style)],
        [Paragraph("ACE Aurum 2, Office No. A-302, Ravet", address_style)],
        [Paragraph("Pune - 411033 MH. India.", address_style)],
        [Paragraph(f"Salary Slip for the month of {pay_period}", title_style)]
    ]
    t_header = Table(header_data, colWidths=[520])
    t_header.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 1),
    ]))

    # Formatter for values
    def format_val(val):
        if val is None or val == 0 or val == 0.0:
            return "-"
        try:
            val_float = float(val)
            if val_float == 0.0:
                return "-"
            return f"{val_float:,.2f}"
        except Exception:
            return "-"

    # Section 1: Employee Metadata Block
    meta_data = [
        ["Employee Name", employee_data.get("name", "-"), "", ""],
        ["Employee Code", employee_data.get("emp_id", "-"), "Present Days", str(payroll_data.get("present_days", "-"))],
        ["Designation", employee_data.get("designation", "-"), "Leaves Taken", str(payroll_data.get("leaves_taken", "-"))],
        ["UAN No", employee_data.get("uan_no", "-"), "Leaves Balance", str(payroll_data.get("leaves_balance", "-"))],
        ["ESIC No.", employee_data.get("esic_no", "-"), "", ""]
    ]
    t_meta = Table(meta_data, colWidths=[120, 140, 120, 140])
    t_meta.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica'),
        ('FONTNAME', (1,0), (1,-1), 'Helvetica-Bold'),
        ('FONTNAME', (3,0), (3,-1), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (3,0), (3,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 4),
        ('SPAN', (1,0), (3,0)),
        ('SPAN', (1,4), (3,4))
    ]))

    # Section 2: Financial Grid
    basic = payroll_data.get("basic_salary", 0.0)
    hra = payroll_data.get("hra", 0.0)
    special = payroll_data.get("special_allowance", 0.0)
    other = payroll_data.get("other_allowance", 0.0)
    conveyance = payroll_data.get("conveyance_allowance", 0.0)
    reimbursment = payroll_data.get("reimbursment", 0.0)
    
    advance = payroll_data.get("advance_decucted", 0.0)
    mlwf = payroll_data.get("mlwf", 0.0)
    pf = payroll_data.get("pf", 0.0)
    esi = payroll_data.get("esi", 0.0)
    pt = payroll_data.get("pt", 0.0)
    
    tot_allowance = payroll_data.get("allowances", 0.0)
    if tot_allowance > 0.0 and (hra + special + other + conveyance + reimbursment) == 0.0:
        other = tot_allowance - basic
        
    tot_deduction = payroll_data.get("deductions", 0.0)
    if tot_deduction > 0.0 and (advance + mlwf + pf + esi + pt) == 0.0:
        pt = tot_deduction

    gross_salary = basic + hra + special + other + conveyance + reimbursment
    total_deductions = advance + mlwf + pf + esi + pt
    net_salary = gross_salary - total_deductions
    
    fin_data = [
        ["Allowances", "Amount", "Deductions", "Amount"],
        ["Basic Salary", format_val(basic), "Advance Decucted", format_val(advance)],
        ["HRA", format_val(hra), "MLWF", format_val(mlwf)],
        ["Special Allowance", format_val(special), "PF", format_val(pf)],
        ["Other Allowance", format_val(other), "ESI", format_val(esi)],
        ["Conveyance Allowance", format_val(conveyance), "PT", format_val(pt)],
        ["Reimbursment", format_val(reimbursment), "Net Salary in Hand", format_val(net_salary)],
        ["Gross Salary", format_val(gross_salary), "", format_val(gross_salary)]
    ]
    t_fin = Table(fin_data, colWidths=[160, 100, 160, 100])
    t_fin.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('ALIGN', (2,0), (2,0), 'LEFT'),
        ('ALIGN', (3,0), (3,0), 'RIGHT'),
        
        ('ALIGN', (0,1), (0,-1), 'LEFT'),
        ('ALIGN', (1,1), (1,-1), 'RIGHT'),
        ('ALIGN', (2,1), (2,-1), 'LEFT'),
        ('ALIGN', (3,1), (3,-1), 'RIGHT'),
        
        ('FONTNAME', (0,-1), (1,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,-1), (3,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,-2), (3,-2), 'Helvetica-Bold'),
        
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))

    # Footer Configuration
    footer_style = ParagraphStyle(
        'Footer',
        parent=normal_style,
        fontName='Helvetica',
        fontSize=8,
        alignment=1, # Center
        spaceBefore=10
    )
    t_footer = Table([[Paragraph("( This is Computer generated document. Does not required signature )", footer_style)]], colWidths=[520])
    t_footer.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))

    # Master Table
    master_data = [
        [t_header],
        [Spacer(1, 5)],
        [t_meta],
        [Spacer(1, 10)],
        [t_fin],
        [Spacer(1, 15)],
        [t_footer]
    ]
    t_master = Table(master_data, colWidths=[520])
    t_master.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('PADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER')
    ]))
    
    story.append(t_master)
    doc.build(story)

def encrypt_pdf_aes(input_pdf_path: str, output_pdf_path: str, password: str):
    """
    Encrypts a generated PDF file using AES-256 encryption.
    """
    if not os.path.exists(input_pdf_path):
        raise FileNotFoundError(f"Source PDF file not found: {input_pdf_path}")
        
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()
    
    # Copy pages
    for page in reader.pages:
        writer.add_page(page)
        
    # Encrypt the writer object with AES-256
    writer.encrypt(user_password=password, owner_password=None, algorithm="AES-256")
    
    # Save the encrypted PDF
    with open(output_pdf_path, "wb") as f_out:
        writer.write(f_out)
        
    # Clean up unencrypted file
    try:
        os.remove(input_pdf_path)
    except OSError:
        pass
