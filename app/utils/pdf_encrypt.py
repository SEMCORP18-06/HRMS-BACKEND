import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from pypdf import PdfReader, PdfWriter

def get_employee_pdf_password(employee_data: dict) -> str:
    """
    Option 2 Password Standard: First 4 letters of Employee Name (UPPERCASE) + Year of Birth.
    Example: 'John Doe' born in 1995 -> 'JOHN1995'
    """
    raw_name = employee_data.get("name", "EMPLOYEE")
    letters = "".join(c for c in raw_name if c.isalpha()).upper()
    first_4 = letters[:4].ljust(4, "X")
    
    dob = employee_data.get("birthday") or employee_data.get("dob") or "1995-01-01"
    dob_str = str(dob)
    
    # Extract 4-digit year
    year = "1995"
    if "-" in dob_str:
        parts = dob_str.split("-")
        for p in parts:
            if len(p) == 4 and p.isdigit():
                year = p
                break
    elif "/" in dob_str:
        parts = dob_str.split("/")
        for p in parts:
            if len(p) == 4 and p.isdigit():
                year = p
                break
    elif len(dob_str) >= 4 and dob_str[:4].isdigit():
        year = dob_str[:4]
        
    return f"{first_4}{year}"

def generate_salary_breakup_pdf(employee_data: dict, payroll_data: dict, temp_path: str):
    """
    Generates a PDF payslip formatted strictly according to the SEMCORP template with:
    - Company Logo
    - Company Name & Address (ACE Aurum 2, Office No. A-302, Ravet, Pune - 411033)
    - Bold Colored Month Name (Brand Blue #1d4ed8)
    - Bold Colored Salary Figures (Brand Green #15803d)
    - Digitally Approved Document Badge with checkmark
    - Henry Ford Footer Quote
    """
    doc = SimpleDocTemplate(temp_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    
    company_style = ParagraphStyle(
        'Company',
        parent=normal_style,
        fontName='Helvetica-Bold',
        fontSize=13,
        alignment=1, # Center
        spaceAfter=2,
        textColor=colors.HexColor('#0f172a')
    )
    address_style = ParagraphStyle(
        'Address',
        parent=normal_style,
        fontName='Helvetica',
        fontSize=9,
        alignment=1, # Center
        spaceAfter=1,
        textColor=colors.HexColor('#475569')
    )
    title_style = ParagraphStyle(
        'Title',
        parent=normal_style,
        fontName='Helvetica-Bold',
        fontSize=11,
        alignment=1, # Center
        spaceAfter=8,
        textColor=colors.HexColor('#1e293b')
    )
    
    pay_period = payroll_data.get("pay_period", "")
    
    # Locate Logo
    _mailer_dir = os.path.dirname(__file__)
    logo_path = None
    candidates = [
        os.path.abspath(os.path.join(_mailer_dir, "..", "..", "static", "logo.png")),
        os.path.abspath(os.path.join(_mailer_dir, "..", "..", "..", "frontend", "public", "logo.png")),
        os.path.abspath(os.path.join(_mailer_dir, "logo.png")),
    ]
    for c in candidates:
        if os.path.isfile(c):
            logo_path = c
            break

    logo_img = None
    if logo_path:
        try:
            logo_img = Image(logo_path, width=160, height=40)
            logo_img.hAlign = 'CENTER'
        except Exception as e:
            print(f"[PDF] Error loading logo image: {str(e)}")

    # Header Configuration
    month_colored = f'<font color="#1d4ed8"><b>{pay_period}</b></font>'
    header_rows = []
    if logo_img:
        header_rows.append([logo_img])
    header_rows.extend([
        [Paragraph("SEMCORP PROCESS AND VACUUM SYSTEMS PVT LTD", company_style)],
        [Paragraph("ACE Aurum 2, Office No. A-302, Ravet, Pune - 411033", address_style)],
        [Paragraph("PUNE", address_style)],
        [Spacer(1, 4)],
        [Paragraph(f"Salary Slip for the month of {month_colored}", title_style)]
    ])
    
    t_header = Table(header_rows, colWidths=[520])
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
        ["Employee Code", employee_data.get("emp_id") or employee_data.get("employee_code") or "-", "Present Days", str(payroll_data.get("present_days", "-"))],
        ["Designation", employee_data.get("designation") or employee_data.get("role") or "-", "Leaves Taken", str(payroll_data.get("leaves_taken", "-"))],
        ["UAN No", employee_data.get("uan_no") or payroll_data.get("uan_no") or "-", "Leaves Balance", str(payroll_data.get("leaves_balance", "-"))],
        ["ESIC No.", employee_data.get("esic_no") or payroll_data.get("esic_no") or "-", "", ""]
    ]
    t_meta = Table(meta_data, colWidths=[120, 140, 120, 140])
    t_meta.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
        ('FONTNAME', (3,0), (3,-1), 'Helvetica'),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#1e293b')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (3,0), (3,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 5),
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
    if gross_salary == 0.0 and tot_allowance > 0.0:
        gross_salary = tot_allowance
        
    total_deductions = advance + mlwf + pf + esi + pt
    if total_deductions == 0.0 and tot_deduction > 0.0:
        total_deductions = tot_deduction

    net_salary = payroll_data.get("net_salary") or (gross_salary - total_deductions)
    
    gross_colored = f'<font color="#15803d"><b>{format_val(gross_salary)}</b></font>'
    net_colored = f'<font color="#15803d"><b>{format_val(net_salary)}</b></font>'

    fin_cell_style = ParagraphStyle(
        'FinCell',
        parent=normal_style,
        fontName='Helvetica-Bold',
        fontSize=9,
        alignment=2 # Right
    )

    fin_data = [
        ["Allowances", "Amount", "Deductions", "Amount"],
        ["Basic Salary", format_val(basic), "Advance Decucted", format_val(advance)],
        ["HRA", format_val(hra), "MLWF", format_val(mlwf)],
        ["Special Allowance", format_val(special), "PF", format_val(pf)],
        ["Other Allowance", format_val(other), "ESI", format_val(esi)],
        ["Conveyance Allowance", format_val(conveyance), "PT", format_val(pt)],
        ["Reimbursment (others)", format_val(reimbursment), "Net Salary in Hand", Paragraph(net_colored, fin_cell_style)],
        ["Gross Salary", Paragraph(gross_colored, fin_cell_style), "", Paragraph(gross_colored, fin_cell_style)]
    ]
    t_fin = Table(fin_data, colWidths=[160, 100, 160, 100])
    t_fin.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8fafc')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0f172a')),
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

    # Section 3: Digital Approval Badge
    badge_style = ParagraphStyle(
        'Badge',
        parent=normal_style,
        fontName='Helvetica-Bold',
        fontSize=9,
        alignment=1, # Center
        textColor=colors.HexColor('#15803d')
    )
    t_badge = Table([[Paragraph("<b>&#10004; Digitally Approved Document & Verified</b>", badge_style)]], colWidths=[520])
    t_badge.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))

    # Section 4: Footer Quote Configuration
    quote_style = ParagraphStyle(
        'Quote',
        parent=normal_style,
        fontName='Helvetica-Oblique',
        fontSize=8,
        alignment=1, # Center
        textColor=colors.HexColor('#64748b')
    )
    t_footer = Table([[Paragraph("&ldquo;Coming together is the beginning. Keeping together is progress. Working together is success.&rdquo; &mdash; Henry Ford", quote_style)]], colWidths=[520])
    t_footer.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))

    # Master Table Layout
    master_data = [
        [t_header],
        [Spacer(1, 4)],
        [t_meta],
        [Spacer(1, 8)],
        [t_fin],
        [Spacer(1, 10)],
        [t_badge],
        [Spacer(1, 4)],
        [t_footer]
    ]
    t_master = Table(master_data, colWidths=[520])
    t_master.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#0f172a')),
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
