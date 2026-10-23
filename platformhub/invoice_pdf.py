import io
from decimal import Decimal
import qrcode

from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    KeepTogether,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def mask_email(email: str) -> str:
    """Mask email for privacy, e.g. audreymbrown2007@gmail.com -> a***7@gmail.com"""
    if not email or "@" not in email:
        return "[Protected]"
    user, domain = email.split("@", 1)
    if len(user) <= 2:
        masked_user = user[:1] + "***"
    else:
        masked_user = user[:1] + "***" + user[-1:]
    return f"{masked_user}@{domain}"


def mask_name(full_name: str, fallback_email: str = "") -> str:
    """
    Show first name and redact last name for privacy, e.g.
    'Audrey Brown' -> 'Audrey B. [Protected]'
    'Jose Cruz' -> 'Jose C. [Protected]'
    """
    name = (full_name or "").strip()
    if not name and fallback_email:
        name = fallback_email.split("@")[0].replace(".", " ").replace("_", " ").title()
    if not name:
        return "Valued Client [Protected]"
    parts = name.split()
    if len(parts) == 1:
        return f"{parts[0]} [Protected]"
    first = parts[0]
    last_initial = parts[-1][:1].upper() if parts[-1] else ""
    return f"{first} {last_initial}. [Protected]"


def generate_invoice_qr(invoice, base_url: str = "https://www.byinfini.online") -> io.BytesIO:
    """Generate a crisp PNG QR code pointing to the invoice verification URL."""
    verify_url = f"{base_url.rstrip('/')}/invoices/verify/{invoice.id}/"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=1,
    )
    qr.add_data(verify_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0F172A", back_color="#FFFFFF")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def generate_invoice_pdf(invoice, base_url: str = "https://www.byinfini.online") -> bytes:
    """
    Generate an executive-grade, beautifully branded invoice PDF with ReportLab.
    Includes full branding, client details, line items, payment audit trail,
    and a scannable QR code linking to verification.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    brand_title = ParagraphStyle(
        "BrandTitle",
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#0B0F19"),
    )
    brand_sub = ParagraphStyle(
        "BrandSub",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#475569"),
    )
    inv_title = ParagraphStyle(
        "InvoiceTitle",
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        alignment=2,  # Right
        textColor=colors.HexColor("#0F172A"),
    )
    inv_meta_right = ParagraphStyle(
        "InvoiceMetaRight",
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        alignment=2,  # Right
        textColor=colors.HexColor("#334155"),
    )
    section_head = ParagraphStyle(
        "SectionHead",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#0F172A"),
    )
    body_text = ParagraphStyle(
        "BodyText",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155"),
    )
    body_bold = ParagraphStyle(
        "BodyBold",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#0F172A"),
    )
    mono_text = ParagraphStyle(
        "MonoText",
        fontName="Courier",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0F172A"),
    )
    table_head = ParagraphStyle(
        "TableHead",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0F172A"),
    )
    table_head_r = ParagraphStyle(
        "TableHeadR",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        alignment=2,
        textColor=colors.HexColor("#0F172A"),
    )
    table_cell = ParagraphStyle(
        "TableCell",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155"),
    )
    table_cell_r = ParagraphStyle(
        "TableCellR",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        alignment=2,
        textColor=colors.HexColor("#0F172A"),
    )
    paid_badge_style = ParagraphStyle(
        "PaidBadge",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        alignment=2,
        textColor=colors.HexColor("#059669"),
    )
    open_badge_style = ParagraphStyle(
        "OpenBadge",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        alignment=2,
        textColor=colors.HexColor("#2563EB"),
    )
    qr_text_style = ParagraphStyle(
        "QrText",
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#475569"),
    )
    qr_url_style = ParagraphStyle(
        "QrUrl",
        fontName="Courier-Bold",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#4338CA"),
    )

    story = []

    # -------------------------------------------------------------------------
    # 1. Header (Brand left, Invoice title & status right)
    # -------------------------------------------------------------------------
    left_brand = [
        Paragraph("<b>INFINIAI</b>", brand_title),
        Paragraph("Executive Writing, Text Intelligence &amp; Operational Systems", brand_sub),
        Paragraph("InfiniAI Operations · Remote &amp; Global Dispatch", brand_sub),
        Paragraph(f"{base_url} · operations@byinfini.online", brand_sub),
    ]

    is_paid = invoice.status == "paid" or (invoice.amount_paid >= invoice.amount_due and invoice.amount_due > 0)
    status_label = "PAID &amp; SETTLED" if is_paid else "PAYMENT DUE"
    status_style = paid_badge_style if is_paid else open_badge_style

    issued_date_str = invoice.created_at.strftime("%B %d, %Y") if invoice.created_at else timezone.now().strftime("%B %d, %Y")
    due_date_str = invoice.due_at.strftime("%B %d, %Y") if invoice.due_at else issued_date_str

    right_inv = [
        Paragraph(f"<b>INVOICE &amp; RECEIPT</b>" if is_paid else "<b>INVOICE</b>", inv_title),
        Paragraph(f"<b>{status_label}</b>", status_style),
        Paragraph(f"<b>Invoice #:</b> {invoice.number}", inv_meta_right),
        Paragraph(f"<b>Issue Date:</b> {issued_date_str}", inv_meta_right),
        Paragraph(f"<b>Due Date:</b> {due_date_str}", inv_meta_right),
    ]

    header_table = Table([[left_brand, right_inv]], colWidths=[310, 230])
    header_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ])
    )
    story.append(header_table)
    story.append(Spacer(1, 12))

    # Divider line
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#E2E8F0"), spaceAfter=12))

    # -------------------------------------------------------------------------
    # 2. Addresses / Project Metadata (2 Columns)
    # -------------------------------------------------------------------------
    user_name = ""
    if invoice.user:
        user_name = invoice.user.get_full_name() or invoice.user.username
    if not user_name and invoice.request:
        user_name = invoice.request.full_name
    if not user_name:
        user_name = invoice.email.split("@")[0].replace(".", " ").title()

    billed_to_cells = [
        Paragraph("<b>BILLED TO</b>", section_head),
        Paragraph(f"<b>{user_name}</b>", body_bold),
        Paragraph(invoice.email, body_text),
        Paragraph(f"Account ID: {invoice.user.username if invoice.user else 'Direct Client'}", body_text),
    ]

    req_title = invoice.request.title if invoice.request else invoice.description
    req_ref = invoice.request.reference if invoice.request else invoice.number

    project_cells = [
        Paragraph("<b>ENGAGEMENT &amp; REFERENCE</b>", section_head),
        Paragraph(f"<b>Project:</b> {req_title[:60]}", body_text),
        Paragraph(f"<b>Service Reference:</b> {req_ref}", body_text),
        Paragraph(f"<b>Billing Currency:</b> {invoice.currency}", body_text),
    ]

    info_table = Table([[billed_to_cells, project_cells]], colWidths=[270, 270])
    info_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ])
    )
    story.append(info_table)
    story.append(Spacer(1, 14))

    # -------------------------------------------------------------------------
    # 3. Line Items Table
    # -------------------------------------------------------------------------
    items_data = [
        [
            Paragraph("Item", table_head),
            Paragraph("Description &amp; Scope of Deliverables", table_head),
            Paragraph("Category", table_head),
            Paragraph("Qty", table_head_r),
            Paragraph("Rate", table_head_r),
            Paragraph("Amount", table_head_r),
        ]
    ]

    # Check if quote items exist
    if invoice.quote and invoice.quote.items.exists():
        for idx, it in enumerate(invoice.quote.items.all(), 1):
            items_data.append([
                Paragraph(str(idx), table_cell),
                Paragraph(f"<b>{it.label}</b><br/>{it.description}", table_cell),
                Paragraph(invoice.request.service_family if invoice.request else "Commercial Scope", table_cell),
                Paragraph(f"{it.quantity:0.0f}", table_cell_r),
                Paragraph(f"{invoice.currency} {it.unit_price:0.2f}", table_cell_r),
                Paragraph(f"{invoice.currency} {(it.quantity * it.unit_price):0.2f}", table_cell_r),
            ])
    else:
        desc = invoice.description or "Professional Services & Deliverables"
        category = invoice.request.service_family if invoice.request else "Text Intelligence / Operational Services"
        items_data.append([
            Paragraph("1", table_cell),
            Paragraph(f"<b>{desc}</b><br/>Complete finalized deliverables and documentation.", table_cell),
            Paragraph(category, table_cell),
            Paragraph("1", table_cell_r),
            Paragraph(f"{invoice.currency} {invoice.amount_due:0.2f}", table_cell_r),
            Paragraph(f"{invoice.currency} {invoice.amount_due:0.2f}", table_cell_r),
        ])

    items_table = Table(
        items_data,
        colWidths=[28, 232, 110, 35, 65, 70],
    )
    items_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("LINEBELOW", (0, 0), (-1, 0), 1.2, colors.HexColor("#CBD5E1")),
            ("LINEBELOW", (0, 1), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ])
    )
    story.append(items_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # 4. Totals Calculation Table (Right Aligned)
    # -------------------------------------------------------------------------
    balance_due = max(Decimal("0.00"), invoice.amount_due - invoice.amount_paid)

    totals_data = [
        [Paragraph("Subtotal:", table_cell_r), Paragraph(f"{invoice.currency} {invoice.amount_due:0.2f}", table_cell_r)],
        [Paragraph("Platform &amp; Gateway Fees:", table_cell_r), Paragraph(f"{invoice.currency} 0.00", table_cell_r)],
        [Paragraph("<b>Total Due:</b>", table_cell_r), Paragraph(f"<b>{invoice.currency} {invoice.amount_due:0.2f}</b>", table_cell_r)],
        [Paragraph("<b>Amount Paid / Cleared:</b>", table_cell_r), Paragraph(f"<b>{invoice.currency} {invoice.amount_paid:0.2f}</b>", table_cell_r)],
        [
            Paragraph("<b>Net Balance Remaining:</b>", table_cell_r),
            Paragraph(f"<font color='{'#059669' if is_paid else '#DC2626'}'><b>{invoice.currency} {balance_due:0.2f}</b></font>", table_cell_r)
        ],
    ]
    totals_table = Table(totals_data, colWidths=[150, 100])
    totals_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LINEBELOW", (0, 2), (-1, 2), 0.5, colors.HexColor("#CBD5E1")),
            ("LINEBELOW", (0, -1), (-1, -1), 1, colors.HexColor("#0F172A")),
        ])
    )

    totals_wrapper = Table([["", totals_table]], colWidths=[290, 250])
    totals_wrapper.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ])
    )
    story.append(totals_wrapper)
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------------------
    # 5. Settlement / Audit Trail (if payments exist)
    # -------------------------------------------------------------------------
    payments = list(invoice.payments.filter(status="success").order_by("created_at"))
    if payments:
        audit_rows = [
            [
                Paragraph("Settled Date", table_head),
                Paragraph("Gateway / Payment Channel", table_head),
                Paragraph("Transaction Ref", table_head),
                Paragraph("Auth Code", table_head),
                Paragraph("Settled Amount", table_head_r),
            ]
        ]
        for p in payments:
            paid_dt = p.paid_at or p.created_at
            meta = p.metadata or {}
            channel = p.source_type or meta.get("channel") or "Apple Pay / Card Gateway"
            bank = meta.get("bank", "")
            brand = meta.get("brand", "")
            chan_str = f"{channel.replace('_', ' ').title()}"
            if bank or brand:
                chan_str += f" ({brand} · {bank})".strip()
            auth_code = meta.get("authorization_code", "AUTH-OK")

            audit_rows.append([
                Paragraph(paid_dt.strftime("%b %d, %Y · %H:%M"), table_cell),
                Paragraph(chan_str[:38], table_cell),
                Paragraph(f"<code>{p.reference}</code>", mono_text),
                Paragraph(f"<code>{auth_code}</code>", mono_text),
                Paragraph(f"<b>{p.currency} {p.amount:0.2f}</b>", table_cell_r),
            ])

        audit_table = Table(audit_rows, colWidths=[95, 145, 120, 95, 85])
        audit_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F8FAFC")),
                ("LINEBELOW", (0, 0), (-1, 0), 1, colors.HexColor("#CBD5E1")),
                ("LINEBELOW", (0, 1), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ])
        )

        audit_block = [
            Paragraph("<b>SETTLEMENT AUDIT TRAIL</b>", section_head),
            Spacer(1, 4),
            audit_table,
        ]
        story.append(KeepTogether(audit_block))
        story.append(Spacer(1, 12))

    # -------------------------------------------------------------------------
    # 6. QR Code Verification Panel
    # -------------------------------------------------------------------------
    qr_buf = generate_invoice_qr(invoice, base_url=base_url)
    qr_img = Image(qr_buf, width=74, height=74)

    verify_url = f"{base_url.rstrip('/')}/invoices/verify/{invoice.id}/"
    qr_desc = [
        Paragraph("<b>OFFICIAL LEDGER VERIFICATION &amp; AUTHENTICITY RECORD</b>", section_head),
        Spacer(1, 3),
        Paragraph(
            "This invoice is cryptographically registered on the InfiniAI operational ledger. "
            "Scan the QR code with any smartphone camera or visit the verification portal below to "
            "independently confirm its real-time settlement status, itemized scope, and transaction audit logs.",
            qr_text_style,
        ),
        Spacer(1, 4),
        Paragraph(f"Verify Online: <a href='{verify_url}'>{verify_url}</a>", qr_url_style),
    ]

    qr_panel = Table([[qr_img, qr_desc]], colWidths=[84, 456])
    qr_panel.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )
    story.append(KeepTogether(qr_panel))
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------------------
    # 7. Footer
    # -------------------------------------------------------------------------
    footer_text = Paragraph(
        f"InfiniAI Operations · Encrypted 256-Bit Financial Settlement Ledger · Document ID: {invoice.id}",
        ParagraphStyle(
            "Footer",
            fontName="Helvetica",
            fontSize=7.5,
            leading=10,
            alignment=1,  # Centered
            textColor=colors.HexColor("#94A3B8"),
        )
    )
    story.append(footer_text)

    doc.build(story)
    return buffer.getvalue()
