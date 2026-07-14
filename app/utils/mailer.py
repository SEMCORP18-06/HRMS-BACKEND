import smtplib
import datetime
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.header import Header
import os
from dotenv import load_dotenv

load_dotenv(override=True)

SMTP_HOST = os.getenv("SMTP_HOST", "").strip()
SMTP_PORT_STR = os.getenv("SMTP_PORT", "587").strip()
SMTP_PORT = int(SMTP_PORT_STR) if SMTP_PORT_STR.isdigit() else 587
SMTP_USER = os.getenv("SMTP_USER", "").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").strip()
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "hr@company.com").strip()

def safe_print(msg):
    try:
        print(msg)
    except Exception:
        try:
            print(str(msg).encode('ascii', 'ignore').decode('ascii'))
        except Exception:
            pass

def verify_smtp_connection():
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASSWORD:
        safe_print("[MAILER] Warning: SMTP configuration is missing. Operating in MOCK mode.")
        return True
    
    safe_print(f"[MAILER] Verifying SMTP connection to {SMTP_HOST}:{SMTP_PORT} for user {SMTP_USER}...")
    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.quit()
        safe_print("[MAILER] SMTP connection verified successfully! Credentials are valid.")
        return True
    except Exception as e:
        import sys
        safe_print(f"\nCRITICAL: SMTP Authentication failed on initialization for {SMTP_USER}!")
        safe_print(f"CRITICAL ERROR DETAIL: {str(e)}")
        safe_print("CRITICAL: Halting the mail service immediately to prevent consecutive failed login lockouts.\n")
        sys.exit(1)

# Verify credentials immediately upon initialization
verify_smtp_connection()

# ── Locate SEMCO logo on disk once at module startup ────────────────────────
_LOGO_PATH = None
try:
    _mailer_dir = os.path.dirname(__file__)
    _candidates = [
        # backend/static/logo.png (copied)
        os.path.join(_mailer_dir, "..", "..", "static", "logo.png"),
        # frontend/public/logo.png (source)
        os.path.join(_mailer_dir, "..", "..", "..", "frontend", "public", "logo.png"),
        # same directory as mailer
        os.path.join(_mailer_dir, "logo.png"),
    ]
    for _c in _candidates:
        _abs = os.path.abspath(_c)
        if os.path.isfile(_abs):
            _LOGO_PATH = _abs
            break
except Exception:
    pass

# Use a logs folder in backend root or local dir
MOCK_EMAIL_LOG = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "mock_emails.log"))

_EMAIL_BRAND_HEADER = ""
_EMAIL_BRAND_FOOTER = ""

def _build_brand_blocks():
    global _EMAIL_BRAND_HEADER, _EMAIL_BRAND_FOOTER
    
    # We reference the logo via cid:logo_image to keep the email body small and prevent Gmail clipping
    logo_tag = '<img src="cid:logo_image" alt="SEMCO Groups" style="height:64px; width:auto; display:block; margin:0 auto 0 0; border-radius:10px;" />'

    _EMAIL_BRAND_HEADER = f"""
<table width="100%" cellpadding="0" cellspacing="0" style="background:linear-gradient(135deg,#15803d 0%,#1d4ed8 100%);padding:0;margin:0 0 0 0;">
  <tr>
    <td style="padding:20px 36px 16px 36px;">
      {logo_tag}
    </td>
    <td style="padding:20px 36px 16px 0;text-align:right;vertical-align:middle;">
      <span style="font-size:12px;color:rgba(255,255,255,0.7);font-weight:600;letter-spacing:0.5px;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
        HR OPERATIONS
      </span>
    </td>
  </tr>
</table>
"""

    footer_logo = '<img src="cid:logo_image" alt="SEMCO Groups" style="height:32px; width:auto; display:inline-block; vertical-align:middle; border-radius:6px; margin-right:8px;" />'

    _EMAIL_BRAND_FOOTER = f"""
<table width="100%" cellpadding="0" cellspacing="0" style="border-top:1px solid #e5e7eb; margin-top:32px;">
  <tr>
    <td style="padding:18px 36px; text-align:center; background:#f8fafc;">
      {footer_logo}
      <span style="font-size:11px; color:#94a3b8; font-family:'Helvetica Neue',Helvetica,Arial,sans-serif; vertical-align:middle;">
        &copy; {datetime.datetime.now().year} SEMCO Groups HR Operations &nbsp;&middot;&nbsp; This is an automated message, please do not reply directly.
      </span>
    </td>
  </tr>
</table>
"""

_build_brand_blocks()


def _inject_brand_into_body(html_body: str) -> str:
    """Inject SEMCO branded header and footer into an HTML email body."""
    import re

    header_html = _EMAIL_BRAND_HEADER
    footer_html = _EMAIL_BRAND_FOOTER

    # Wrap in a centered 640px container if not already done by a template
    # We inject right after <body ...> and right before </body>
    def body_open_repl(match):
        attrs = match.group(1) or ""
        return f'<body {attrs}>\n<table width="100%" cellpadding="0" cellspacing="0" style="background:#f3f4f6;padding:0;margin:0;"><tr><td><table width="640" cellpadding="0" cellspacing="0" align="center" style="max-width:640px;margin:0 auto;background:#ffffff;border-radius:0 0 12px 12px;overflow:hidden;">\n<tr><td>{header_html}</td></tr>\n<tr><td style="padding:0;">'

    html_body = re.sub(r'<body([^>]*)>', body_open_repl, html_body, count=1, flags=re.IGNORECASE)

    # Inject footer before </body>
    html_body = re.sub(
        r'</body>',
        f'{footer_html}</td></tr></table></td></tr></table></body>',
        html_body, count=1, flags=re.IGNORECASE
    )

    return html_body


def apply_email_styles(html_body: str) -> str:
    # If the email is not HTML, wrap it in standard HTML structure
    if not ("<html" in html_body.lower() or "<body" in html_body.lower() or "<div" in html_body.lower()):
        # Convert plain line breaks to html breaks
        html_body = f"<html><body>{html_body.replace(chr(10), '<br>')}</body></html>"

    font_family = "'Helvetica Neue', Helvetica, 'Open Sans', Arial, sans-serif"
    body_styles = f"font-family: {font_family}; font-size: 15px; line-height: 1.5; color: #1e293b;"
    heading_styles = f"font-family: {font_family}; font-size: 22px; line-height: 1.4; color: #0f172a;"
    footer_styles = f"font-family: {font_family}; font-size: 11px; line-height: 1.5; color: #94a3b8;"

    style_block = f"""
    <style>
      body, p, td, div, span, li, a {{
        font-family: {font_family} !important;
        font-size: 15px;
        line-height: 1.5;
      }}
      h1, h2, h3, h4, h5, h6 {{
        font-family: {font_family} !important;
        font-size: 22px;
        line-height: 1.4;
      }}
      .footer, .preheader, [class*="footer"], footer, td.footer, div.footer, p.footer {{
        font-size: 11px;
        line-height: 1.5;
      }}
      @media only screen and (max-width: 640px) {{
        table[width="640"] {{ width: 100% !important; }}
      }}
    </style>
    """

    if "</head>" in html_body.lower():
        html_body = html_body.replace("</head>", f"{style_block}</head>")
    elif "<html>" in html_body.lower():
        html_body = html_body.replace("<html>", f"<html><head>{style_block}</head>")
    else:
        html_body = f"<html><head>{style_block}</head><body>{html_body}</body></html>"

    import re

    def merge_styles(tag, attrs, default_style):
        style_match = re.search(r'style="([^"]*)"', attrs, re.IGNORECASE)
        if style_match:
            custom_style = style_match.group(1).strip()
            base = default_style.strip()
            if base and not base.endswith(';'):
                base += ';'
            combined = f"{base} {custom_style}"
            new_attrs = re.sub(r'style="[^"]*"', f'style="{combined}"', attrs, flags=re.IGNORECASE)
            return f"<{tag} {new_attrs}>"
        else:
            attrs_str = attrs.strip()
            if attrs_str:
                return f"<{tag} style=\"{default_style}\" {attrs_str}>"
            else:
                return f"<{tag} style=\"{default_style}\">"

    def body_repl(match):
        attrs = match.group(1) or ""
        return merge_styles("body", attrs, body_styles)

    html_body = re.sub(r"<body([^>]*)>", body_repl, html_body, flags=re.IGNORECASE)

    for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        def tag_repl(match, current_tag=tag):
            attrs = match.group(1) or ""
            return merge_styles(current_tag, attrs, heading_styles)
        html_body = re.sub(f"<{tag}([^>]*)>", tag_repl, html_body, flags=re.IGNORECASE)

    def p_repl(match):
        attrs = match.group(1) or ""
        return merge_styles("p", attrs, body_styles)
    html_body = re.sub(r"<p([^>]*)>", p_repl, html_body, flags=re.IGNORECASE)

    def footer_repl(match):
        attrs = match.group(1) or ""
        return merge_styles("footer", attrs, footer_styles)
    html_body = re.sub(r"<footer([^>]*)>", footer_repl, html_body, flags=re.IGNORECASE)

    # Inject branded header and footer into every email
    html_body = _inject_brand_into_body(html_body)

    return html_body


def send_email(to_email: str, subject: str, body: str, attachment_path: str = None, attachment_name: str = None, inline_images: list = None):
    """
    Sends an email using SMTP if credentials are configured, or logs it to mock_emails.log.
    Supports comma-separated recipients by sending separate individual transactions.
    """
    recipients = [r.strip() for r in to_email.split(',') if r.strip()]
    if not recipients:
        return False

    body = apply_email_styles(body)

    # Check if SMTP is configured
    if SMTP_HOST and SMTP_USER and SMTP_PASSWORD:
        try:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=5)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)

            for recipient in recipients:
                # Use 'related' to embed inline image attachments correctly
                msg = MIMEMultipart('related')
                msg['From'] = f"HR SEMCO Groups <{SENDER_EMAIL}>"
                msg['To'] = recipient
                msg['Subject'] = Header(subject, 'utf-8')

                msg_alternative = MIMEMultipart('alternative')
                msg.attach(msg_alternative)

                # Attach HTML text body
                msg_html = MIMEText(body, 'html', 'utf-8')
                msg_alternative.attach(msg_html)

                # Attach inline logo
                if _LOGO_PATH and os.path.exists(_LOGO_PATH):
                    try:
                        with open(_LOGO_PATH, 'rb') as f:
                            logo_data = f.read()
                        msg_logo = MIMEImage(logo_data)
                        msg_logo.add_header('Content-ID', '<logo_image>')
                        msg_logo.add_header('Content-Disposition', 'inline', filename='logo.png')
                        msg.attach(msg_logo)
                    except Exception as e:
                        safe_print(f"[MAILER] Error attaching inline logo: {str(e)}")

                # Attach other inline images if any
                if inline_images:
                    for img in inline_images:
                        try:
                            msg_img = MIMEImage(img["data"])
                            msg_img.add_header('Content-ID', f"<{img['content_id']}>")
                            msg_img.add_header('Content-Disposition', 'inline', filename=img.get('filename', 'image.png'))
                            msg.attach(msg_img)
                        except Exception as img_err:
                            safe_print(f"[MAILER] Error attaching inline image: {str(img_err)}")

                # Attach standard document attachments if any
                if attachment_path and os.path.exists(attachment_path):
                    try:
                        with open(attachment_path, "rb") as f:
                            part = MIMEApplication(f.read(), Name=attachment_name or os.path.basename(attachment_path))
                        part['Content-Disposition'] = f'attachment; filename="{attachment_name or os.path.basename(attachment_path)}"'
                        msg.attach(part)
                    except Exception as e:
                        safe_print(f"[MAILER] Error attaching file: {str(e)}")

                server.sendmail(SENDER_EMAIL, recipient, msg.as_string())
                safe_print(f"[MAILER] Real email sent to {recipient}: {subject}")

            server.quit()
            return True
        except Exception as e:
            safe_print(f"[MAILER] Failed to send real email: {str(e)}")
            # Fallback to logging

    # Mock fallback
    for recipient in recipients:
        log_msg = f"\n{'='*50}\n"
        log_msg += f"DATE: {datetime.datetime.now().isoformat()}\n"
        log_msg += f"TO: {recipient}\n"
        log_msg += f"FROM: HR SEMCO Groups <{SENDER_EMAIL}>\n"
        log_msg += f"SUBJECT: {subject}\n"
        log_msg += f"BODY:\n{body}\n"
        if attachment_path:
            log_msg += f"ATTACHMENT: {attachment_name or os.path.basename(attachment_path)} (Path: {attachment_path}, Encrypted: Yes)\n"
        log_msg += f"{'='*50}\n"

        try:
            with open(MOCK_EMAIL_LOG, "a", encoding="utf-8") as f_log:
                f_log.write(log_msg)
        except Exception as e:
            safe_print(f"[MAILER] Error writing to mock log: {str(e)}")

        safe_print(f"[MAILER - MOCK] Logged email to {recipient}: {subject}")
    return True
