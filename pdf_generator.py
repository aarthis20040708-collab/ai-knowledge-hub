import io
import re
import html
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT

def sanitize_unicode(text: str) -> str:
    """Normalizes special unicode characters into PDF-safe equivalents."""
    replacements = {
        '\u2011': '-',  # Non-breaking hyphen
        '\u2012': '-',
        '\u2013': '-',  # En-dash
        '\u2014': '--', # Em-dash
        '\u2018': "'",  # Left single quote
        '\u2019': "'",  # Right single quote
        '\u201c': '"',  # Left double quote
        '\u201d': '"',  # Right double quote
        '\u2022': '&bull;', # Bullet
        '\u2026': '...', # Ellipsis
        '\u00a0': ' ',  # Non-breaking space
    }
    for char, rep in replacements.items():
        text = text.replace(char, rep)
    
    # Remove unsupported emojis or non-ascii/latin symbols that cause font issues
    text = re.sub(r'[^\x00-\x7F\u00A0-\u00FF]', '', text)
    return text


def clean_line_for_reportlab(line_str: str) -> str:
    """Safely converts markdown formatting to ReportLab XML tags and fixes self-closing tags."""
    text = sanitize_unicode(line_str)

    # 1. Clean markdown tables: remove leading and trailing pipes
    if text.startswith("|") and text.endswith("|"):
        cells = [c.strip() for c in text.strip("|").split("|") if c.strip()]
        text = " &nbsp;|&nbsp; ".join(cells)

    # 2. Fix unclosed <br> tags to <br/>
    text = re.sub(r'<br\s*>', '<br/>', text, flags=re.IGNORECASE)

    # 3. Escape raw ampersands not part of an existing entity
    text = re.sub(r'&(?!amp;|lt;|gt;|quot;|bull;|nbsp;|#\d+;)', '&amp;', text)

    # 4. Convert markdown bold, italics, code
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = re.sub(r'`(.*?)`', r'<font face="Courier">\1</font>', text)

    return text


def safe_paragraph(raw_text: str, style: ParagraphStyle) -> Paragraph:
    """Creates a ReportLab Paragraph with a guaranteed fallback if markup fails."""
    formatted_text = clean_line_for_reportlab(raw_text)
    try:
        return Paragraph(formatted_text, style)
    except Exception:
        # Fallback: Strip all tags and escape everything
        plain = re.sub(r'<[^>]+>', '', raw_text)
        plain = html.escape(sanitize_unicode(plain))
        return Paragraph(plain, style)


def generate_pdf_report(title: str, content: str, workspace_name: str = "General", author: str = "AI Assistant") -> io.BytesIO:
    """
    Generates a beautifully formatted, crash-proof PDF report in-memory.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E293B'),
        alignment=TA_LEFT,
        spaceAfter=6
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=10
    )

    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=10,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#334155'),
        leftIndent=14,
        spaceAfter=3
    )

    story = []

    # Title & Header
    story.append(safe_paragraph(title, title_style))
    date_str = datetime.now().strftime("%B %d, %Y - %I:%M %p")
    meta_text = f"<b>Workspace:</b> {workspace_name} &nbsp;|&nbsp; <b>Author:</b> {author} &nbsp;|&nbsp; <b>Date:</b> {date_str}"
    story.append(safe_paragraph(meta_text, meta_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3B82F6"), spaceAfter=12))

    # Process content line by line
    lines = content.split('\n')
    for line in lines:
        line_str = line.strip()
        if not line_str:
            story.append(Spacer(1, 4))
            continue

        # Skip markdown horizontal rules or separator lines
        if re.match(r'^[\|\-\+\s]{3,}$', line_str):
            continue

        # Headings
        if line_str.startswith("### "):
            story.append(safe_paragraph(line_str[4:], h2_style))
        elif line_str.startswith("## "):
            story.append(safe_paragraph(line_str[3:], h2_style))
        elif line_str.startswith("# "):
            story.append(safe_paragraph(line_str[2:], title_style))
        # Bullets
        elif line_str.startswith("- ") or line_str.startswith("* ") or line_str.startswith("• "):
            bullet_content = line_str[2:]
            story.append(safe_paragraph(f"&bull; {bullet_content}", bullet_style))
        elif re.match(r'^\d+\.\s', line_str):
            num_match = re.match(r'^(\d+\.)\s*(.*)', line_str)
            if num_match:
                prefix, text_part = num_match.groups()
                story.append(safe_paragraph(f"<b>{prefix}</b> {text_part}", bullet_style))
            else:
                story.append(safe_paragraph(line_str, body_style))
        else:
            story.append(safe_paragraph(line_str, body_style))

    # Build document
    doc.build(story)
    buffer.seek(0)
    return buffer
