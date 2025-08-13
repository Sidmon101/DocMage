# pdf_generator.py
import re
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm


ACCENT = colors.HexColor("#007bff")  # Match your site's primary blue


def _build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        textColor=colors.black,
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name="Meta",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name="Section",
        parent=styles["Heading2"],
        textColor=ACCENT,
        fontSize=14,
        spaceBefore=12,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name="Body",
        parent=styles["Normal"],
        fontSize=11,
        leading=15
    ))
    styles.add(ParagraphStyle(
        name="TableCell",
        parent=styles["Normal"],
        fontSize=10,
        leading=14
    ))
    styles.add(ParagraphStyle(
        name="TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=colors.white
    ))
    return styles


def _header_footer(canvas, doc, title, tool_name):
    canvas.saveState()

    # Top accent line
    canvas.setStrokeColor(ACCENT)
    canvas.setLineWidth(0.8)
    canvas.line(15*mm, 287*mm, 195*mm, 287*mm)

    # Tool name at the very top (accent color)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.setFillColor(ACCENT)
    canvas.drawString(15*mm, 292*mm, str(tool_name)[:90])

    # Title just beneath (black)
    canvas.setFillColor(colors.black)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(15*mm, 289*mm, str(title)[:90])

    # Footer with timestamp and page
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.grey)
    canvas.drawString(15*mm, 12*mm, f"Generated: {now}")
    canvas.drawRightString(195*mm, 12*mm, f"Page {doc.page}")

    canvas.restoreState()


def _split_points(summary: str):
    """
    Robust sentence splitter for bullet points (dedup preserves order).
    Splits on period/question/exclamation followed by whitespace.
    """
    parts = []
    for piece in (summary or "").splitlines():
        piece = piece.strip()
        if not piece:
            continue
        # FIX: use true lookbehind (no HTML escaping)
        chunks = re.split(r'(?<=[\.?!])\s+', piece)
        parts.extend([c.strip().rstrip(".") for c in chunks if c.strip()])
    seen, out = set(), []
    for p in parts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def _make_table(rows, col_widths, styles, header_bg=ACCENT):
    """
    Helper to build a well-styled table with a colored header and zebra striping.
    `rows` should include the header row first.
    """
    table = Table(rows, colWidths=col_widths)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.Color(0.96, 0.96, 0.96)]),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
        ("INNERGRID", (0, 1), (-1, -1), 0.25, colors.lightgrey),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def generate_summary_pdf(
    title,
    summary,
    output_path,
    category=None,
    highlights=None,
    tool_name="Document Analyzer",
    paragraphs=None,   # Optional: list[str] for Overview section
    bullets=None       # Optional: list[str] for Key Points section
):
    """
    Builds a professional PDF with:
      • Header: Tool name (top), Title; Footer: timestamp & page number
      • Overview (paragraphs): uses `paragraphs` if provided; else falls back to full `summary`
      • Key Highlights (table): two-column (Field / Value) — optional
      • Key Points (table at the end): numbered list in a 2-column table ("#", "Key Point")

    Returns: output_path (str)
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=18*mm,
        leftMargin=18*mm,
        topMargin=22*mm,
        bottomMargin=18*mm
    )

    styles = _build_styles()
    elements = []

    # Title
    elements.append(Paragraph(str(title), styles["ReportTitle"]))

    # Meta line
    meta_bits = []
    if category:
        meta_bits.append(f"<b>Category:</b> {category}")
    meta_bits.append(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    elements.append(Paragraph(" &nbsp; | &nbsp; ".join(meta_bits), styles["Meta"]))
    elements.append(Spacer(1, 6))

    # -------------------------
    # Overview (paragraph mode)
    # -------------------------
    elements.append(Paragraph("Overview", styles["Section"]))
    if paragraphs and isinstance(paragraphs, (list, tuple)) and any(str(p).strip() for p in paragraphs):
        for para in paragraphs:
            if para and str(para).strip():
                elements.append(Paragraph(str(para).strip(), styles["Body"]))
                elements.append(Spacer(1, 4))
    else:
        if summary and str(summary).strip():
            elements.append(Paragraph(str(summary).strip(), styles["Body"]))
        else:
            elements.append(Paragraph("No overview available.", styles["Body"]))

    elements.append(Spacer(1, 10))

    # -------------------------
    # Highlights (table mode)
    # -------------------------
    if highlights and isinstance(highlights, dict) and len(highlights) > 0:
        elements.append(Paragraph("Key Highlights", styles["Section"]))

        # Table rows with Paragraph cells for proper wrapping
        rows = [
            [Paragraph("<b>Field</b>", styles["TableHeader"]),
             Paragraph("<b>Value</b>", styles["TableHeader"])]
        ]
        for key, value in highlights.items():
            # Normalize values to string
            if isinstance(value, (list, tuple)):
                value = ", ".join([str(v) for v in value])
            key_disp = str(key).replace("_", " ")
            rows.append([
                Paragraph(key_disp, styles["TableCell"]),
                Paragraph(str(value), styles["TableCell"])
            ])

        table = _make_table(rows, [55*mm, 117*mm], styles)
        elements.append(table)

    elements.append(Spacer(1, 12))

    # -------------------------------------------------
    # Key Points — as a TABLE at the very end (last)
    # -------------------------------------------------
    # Use provided bullets or derive from summary
    if bullets and isinstance(bullets, (list, tuple)) and any(str(b).strip() for b in bullets):
        key_points = [str(b).strip() for b in bullets if str(b).strip()]
    else:
        key_points = _split_points(summary or "")

    elements.append(Paragraph("Key Points", styles["Section"]))
    if key_points:
        # Build a 2-column table with numbering
        kp_rows = [
            [Paragraph("<b>#</b>", styles["TableHeader"]),
             Paragraph("<b>Key Point</b>", styles["TableHeader"])]
        ]
        for idx, point in enumerate(key_points, start=1):
            kp_rows.append([
                Paragraph(str(idx), styles["TableCell"]),
                Paragraph(point, styles["TableCell"])
            ])

        kp_table = _make_table(kp_rows, [15*mm, 157*mm], styles)
        elements.append(kp_table)
    else:
        elements.append(Paragraph("No key points available.", styles["Body"]))

    # Header/Footer decorator with tool name
    def _decorate(canvas, doc_):
        _header_footer(canvas, doc_, title=str(title), tool_name=str(tool_name))

    doc.build(elements, onFirstPage=_decorate, onLaterPages=_decorate)
    return output_path
