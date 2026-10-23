import csv
import io
import json
import mimetypes
import os
import re
import time
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

from django.conf import settings

AUDIO_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".m4a",
    ".ogg",
    ".webm",
    ".aac",
    ".flac",
    ".opus",
}

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".csv",
    ".ppt",
    ".pptx",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".txt",
    ".md",
    ".zip",
    ".json",
    ".html",
} | AUDIO_EXTENSIONS

MAX_UPLOAD_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB


def get_chat_files_dir() -> Path:
    path = Path(settings.BASE_DIR) / "public" / "chat_files"
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{max(1, size_bytes)} B"
    kb = size_bytes / 1024.0
    if kb < 1024:
        return f"{kb:.0f} KB" if kb >= 10 else f"{kb:.1f} KB"
    mb = kb / 1024.0
    return f"{mb:.1f} MB"


def sanitize_filename(name: str) -> str:
    base = os.path.basename(name or "attachment")
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", base).strip("._")
    return cleaned or "attachment.bin"


def build_attachment_meta(filename: str, display_name: str = "", role: str = "file") -> dict:
    files_dir = get_chat_files_dir()
    file_path = files_dir / filename
    size_bytes = file_path.stat().st_size if file_path.exists() else 0
    ext = Path(filename).suffix.lstrip(".").upper() or "FILE"
    dot_ext = Path(filename).suffix.lower()
    is_audio = dot_ext in AUDIO_EXTENSIONS
    return {
        "name": display_name or filename,
        "filename": filename,
        "url": f"/workspace/chat/files/{filename}",
        "download_url": f"/workspace/chat/files/{filename}?download=1",
        "ext": ext,
        "kind": "AUDIO" if is_audio else ext,
        "is_audio": is_audio,
        "mime": guess_mime_type(filename),
        "size_bytes": size_bytes,
        "size_display": format_file_size(size_bytes),
        "role": role,
    }



def save_uploaded_chat_files(uploaded_files):
    saved = []
    files_dir = get_chat_files_dir()
    for f in uploaded_files:
        orig_name = getattr(f, "name", "") or "upload"
        ext = Path(orig_name).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type ({ext or 'unknown'}). Allowed: documents (PDF, DOCX, XLSX, CSV, PPTX, TXT), images (PNG, JPG, WEBP), audio (MP3, WAV, M4A, WEBM, OGG, AAC, FLAC), and ZIP."
            )
        if getattr(f, "size", 0) > MAX_UPLOAD_SIZE_BYTES:
            raise ValueError(f"{orig_name} exceeds the 25 MB file size limit.")

        clean_name = sanitize_filename(orig_name)
        unique_filename = f"{int(time.time() * 1000)}_{clean_name}"
        dest_path = files_dir / unique_filename
        with dest_path.open("wb") as out:
            for chunk in f.chunks():
                out.write(chunk)

        saved.append(
            build_attachment_meta(
                filename=unique_filename,
                display_name=orig_name,
                role="upload",
            )
        )
    return saved


def write_docx_file(filename: str, title: str, paragraphs: list[str], role: str = "file") -> dict:
    files_dir = get_chat_files_dir()
    dest = files_dir / filename

    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

    body_xml = []
    if title:
        body_xml.append(
            f'<w:p><w:pPr><w:spacing w:before="120" w:after="240"/></w:pPr><w:r><w:rPr><w:b/><w:color w:val="0F172A"/><w:sz w:val="32"/></w:rPr><w:t xml:space="preserve">{xml_escape(title)}</w:t></w:r></w:p>'
        )
    for para in paragraphs:
        if isinstance(para, (list, tuple)):
            tbl_rows_xml = []
            for r_idx, row in enumerate(para):
                is_head = (r_idx == 0)
                cells_xml = []
                for cell in row:
                    cell_text = xml_escape(str(cell if cell is not None else ""))
                    bg_fill = "F1F5F9" if is_head else ("FFFFFF" if r_idx % 2 == 1 else "F8FAFC")
                    b_tag = "<w:b/>" if is_head else ""
                    color_val = "0F172A" if is_head else "334155"
                    cell_xml = (
                        f'<w:tc>'
                        f'<w:tcPr>'
                        f'<w:shd w:val="clear" w:color="auto" w:fill="{bg_fill}"/>'
                        f'<w:tcMar><w:top w:w="80" w:type="dxa"/><w:bottom w:w="80" w:type="dxa"/><w:left w:w="120" w:type="dxa"/><w:right w:w="120" w:type="dxa"/></w:tcMar>'
                        f'</w:tcPr>'
                        f'<w:p><w:pPr><w:spacing w:after="20" w:before="20"/></w:pPr><w:r><w:rPr>{b_tag}<w:color w:val="{color_val}"/><w:sz w:val="19"/></w:rPr><w:t xml:space="preserve">{cell_text}</w:t></w:r></w:p>'
                        f'</w:tc>'
                    )
                    cells_xml.append(cell_xml)
                tbl_rows_xml.append(f'<w:tr>{"".join(cells_xml)}</w:tr>')

            tbl_borders = (
                '<w:tblBorders>'
                '<w:top w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
                '<w:bottom w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
                '<w:left w:val="none"/>'
                '<w:right w:val="none"/>'
                '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
                '<w:insideV w:val="none"/>'
                '</w:tblBorders>'
            )
            body_xml.append(f'<w:tbl><w:tblPr>{tbl_borders}<w:tblW w:w="5000" w:type="pct"/></w:tblPr>{"".join(tbl_rows_xml)}</w:tbl>')
            body_xml.append('<w:p><w:pPr><w:spacing w:after="100"/></w:pPr></w:p>')
            continue

        text = str(para or "").strip()
        if not text:
            body_xml.append('<w:p><w:pPr><w:spacing w:after="100"/></w:pPr></w:p>')
            continue

        if text in ("--PAGE-BREAK--", "[PAGE BREAK]", "===PAGE==="):
            body_xml.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
            continue

        is_heading = (
            text.startswith("#")
            or text.startswith("ARTICLE ")
            or text.startswith("SECTION ")
            or text.startswith("TEMPLATE ")
            or text.startswith("ROLE ")
            or text.startswith("PAGE ")
            or text.startswith("EMAIL ")
            or (text.isupper() and len(text) < 70 and not text.startswith("—"))
        )
        is_bullet = text.startswith(("—", "•", "-", "*")) or (len(text) > 2 and text[:2].isdigit() and text[2:4] in (". ", ") "))

        if is_heading:
            clean_heading = text.lstrip("# ").strip()
            body_xml.append(
                f'<w:p><w:pPr><w:spacing w:before="240" w:after="80"/></w:pPr><w:r><w:rPr><w:b/><w:color w:val="0F172A"/><w:sz w:val="24"/></w:rPr><w:t xml:space="preserve">{xml_escape(clean_heading)}</w:t></w:r></w:p>'
            )
        elif is_bullet:
            body_xml.append(
                f'<w:p><w:pPr><w:ind w:left="360"/><w:spacing w:after="100"/></w:pPr><w:r><w:rPr><w:color w:val="1E293B"/><w:sz w:val="21"/></w:rPr><w:t xml:space="preserve">{xml_escape(text)}</w:t></w:r></w:p>'
            )
        else:
            body_xml.append(
                f'<w:p><w:pPr><w:spacing w:after="140" w:line="276" w:lineRule="auto"/></w:pPr><w:r><w:rPr><w:color w:val="1E293B"/><w:sz w:val="21"/></w:rPr><w:t xml:space="preserve">{xml_escape(text)}</w:t></w:r></w:p>'
            )

    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {"".join(body_xml)}
  </w:body>
</w:document>"""

    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", document_xml)

    return build_attachment_meta(filename=filename, display_name=filename, role=role)


def _col_letter(idx: int) -> str:
    result = ""
    n = idx + 1
    while n > 0:
        n, rem = divmod(n - 1, 26)
        result = chr(65 + rem) + result
    return result


def write_xlsx_file(
    filename: str,
    sheet_name_or_dict,
    rows: list[list] = None,
    role: str = "file",
) -> dict:
    files_dir = get_chat_files_dir()
    dest = files_dir / filename

    if isinstance(sheet_name_or_dict, dict):
        sheets_map = sheet_name_or_dict
    else:
        sheets_map = {str(sheet_name_or_dict or "Sheet1"): rows or []}

    sheet_items = list(sheets_map.items())

    # Build Content_Types
    sheet_overrides = []
    for idx in range(1, len(sheet_items) + 1):
        sheet_overrides.append(
            f'  <Override PartName="/xl/worksheets/sheet{idx}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
    content_types = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
{chr(10).join(sheet_overrides)}
</Types>"""

    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""

    workbook_sheets = []
    workbook_rels_list = []
    for idx, (s_name, _) in enumerate(sheet_items, start=1):
        safe_title = xml_escape(s_name[:31] or f"Sheet{idx}")
        workbook_sheets.append(f'    <sheet name="{safe_title}" sheetId="{idx}" r:id="rId{idx}"/>')
        workbook_rels_list.append(
            f'  <Relationship Id="rId{idx}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{idx}.xml"/>'
        )

    workbook_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
          xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
{chr(10).join(workbook_sheets)}
  </sheets>
</workbook>"""

    workbook_rels = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
{chr(10).join(workbook_rels_list)}
</Relationships>"""

    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("xl/workbook.xml", workbook_xml)
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels)

        for idx, (_, sheet_rows) in enumerate(sheet_items, start=1):
            sheet_rows_xml = []
            for r_idx, row in enumerate(sheet_rows, start=1):
                cells_xml = []
                for c_idx, val in enumerate(row):
                    cell_ref = f"{_col_letter(c_idx)}{r_idx}"
                    if isinstance(val, (int, float)) and not isinstance(val, bool):
                        cells_xml.append(f'<c r="{cell_ref}"><v>{val}</v></c>')
                    elif isinstance(val, str) and val.startswith("="):
                        formula = xml_escape(val[1:])
                        cells_xml.append(f'<c r="{cell_ref}"><f>{formula}</f></c>')
                    else:
                        text = xml_escape(str(val if val is not None else ""))
                        cells_xml.append(f'<c r="{cell_ref}" t="inlineStr"><is><t>{text}</t></is></c>')
                sheet_rows_xml.append(f'<row r="{r_idx}">{"".join(cells_xml)}</row>')

            sheet_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>
    {"".join(sheet_rows_xml)}
  </sheetData>
</worksheet>"""
            zf.writestr(f"xl/worksheets/sheet{idx}.xml", sheet_xml)

    return build_attachment_meta(filename=filename, display_name=filename, role=role)


def write_pdf_file(
    filename: str,
    title: str,
    lines: list,
    role: str = "file",
    subtitle: str = "",
    meta_tag: str = "",
) -> dict:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        HRFlowable,
        Table,
        TableStyle,
        PageBreak,
    )
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas

    class NumberedCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            num_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.draw_page_number(num_pages)
                canvas.Canvas.showPage(self)
            canvas.Canvas.save(self)

        def draw_page_number(self, page_count):
            self.saveState()
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(44, 32, 568, 32)
            self.drawString(44, 20, "CONFIDENTIAL & PROPRIETARY")
            page_str = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(568, 20, page_str)
            self.restoreState()

    files_dir = get_chat_files_dir()
    dest = files_dir / filename

    doc = SimpleDocTemplate(
        str(dest),
        pagesize=letter,
        leftMargin=44,
        rightMargin=44,
        topMargin=44,
        bottomMargin=48,
    )

    title_style = ParagraphStyle(
        "DocTitle",
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#0B0F19"),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#475569"),
        spaceAfter=10,
    )
    meta_style = ParagraphStyle(
        "DocMeta",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=4,
    )
    heading_style = ParagraphStyle(
        "DocHeading",
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=12,
        spaceAfter=5,
    )
    body_style = ParagraphStyle(
        "DocBody",
        fontName="Helvetica",
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=6,
    )
    bullet_style = ParagraphStyle(
        "DocBullet",
        fontName="Helvetica",
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor("#1E293B"),
        leftIndent=14,
        spaceAfter=4,
    )
    table_header_style = ParagraphStyle(
        "TableHeader",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#0F172A"),
    )
    table_body_style = ParagraphStyle(
        "TableBody",
        fontName="Helvetica",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#334155"),
    )

    story = []

    if meta_tag:
        story.append(Paragraph(xml_escape(meta_tag.upper()), meta_style))

    story.append(Paragraph(xml_escape(title), title_style))

    if subtitle:
        story.append(Paragraph(xml_escape(subtitle), subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=12))

    for item in lines:
        if isinstance(item, (list, tuple)):
            table_data = []
            for r_idx, row in enumerate(item):
                row_cells = []
                for cell in row:
                    cell_text = xml_escape(str(cell if cell is not None else "")).replace("\n", "<br/>")
                    is_head = (r_idx == 0)
                    st = table_header_style if is_head else table_body_style
                    row_cells.append(Paragraph(cell_text, st))
                table_data.append(row_cells)

            t = Table(table_data, colWidths=None, repeatRows=1)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ]))
            story.append(Spacer(1, 4))
            story.append(t)
            story.append(Spacer(1, 6))
            continue

        text = str(item).strip()
        if not text:
            story.append(Spacer(1, 5))
            continue

        if text in ("--PAGE-BREAK--", "[PAGE BREAK]", "===PAGE==="):
            story.append(PageBreak())
            continue

        is_heading = (
            text.isupper()
            or text.startswith("SECTION ")
            or text.startswith("ARTICLE ")
            or text.startswith("PART ")
            or text.startswith("PAGE ")
            or (text.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")) and len(text) < 70 and not text.endswith("."))
        )
        is_bullet = text.startswith(("—", "-", "•", "*")) or (text.startswith(tuple(f"{i}." for i in range(1, 30))) and len(text) >= 70)

        safe_text = xml_escape(text)

        if is_heading:
            clean_heading = safe_text.lstrip("# ").strip()
            story.append(Paragraph(clean_heading, heading_style))
        elif is_bullet:
            clean_bullet = safe_text.lstrip("—•-* ").strip()
            story.append(Paragraph(f"&bull;&nbsp;&nbsp;{clean_bullet}", bullet_style))
        else:
            story.append(Paragraph(safe_text, body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    return build_attachment_meta(filename=filename, display_name=filename, role=role)


def write_csv_file(filename: str, rows: list[list], role: str = "file") -> dict:
    files_dir = get_chat_files_dir()
    dest = files_dir / filename
    with dest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)
    return build_attachment_meta(filename=filename, display_name=filename, role=role)


def write_zip_file(filename: str, files_map: dict[str, str | bytes], role: str = "file") -> dict:
    files_dir = get_chat_files_dir()
    dest = files_dir / filename
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for inner_name, content in files_map.items():
            if isinstance(content, str):
                disk_file = files_dir / content
                if disk_file.exists() and disk_file.is_file():
                    zf.write(disk_file, inner_name)
                else:
                    zf.writestr(inner_name, content.encode("utf-8"))
            elif isinstance(content, bytes):
                zf.writestr(inner_name, content)
    return build_attachment_meta(filename=filename, display_name=filename, role=role)


def write_pptx_file(filename: str, title: str, slides: list[dict], role: str = "file") -> dict:
    files_dir = get_chat_files_dir()
    dest = files_dir / filename

    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
"""
    for i in range(1, len(slides) + 1):
        content_types += f'  <Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>\n'
    content_types += "</Types>"

    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>"""

    pres_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rIdMaster1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
"""
    for i in range(1, len(slides) + 1):
        pres_rels += f'  <Relationship Id="rIdSlide{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>\n'
    pres_rels += "</Relationships>"

    slide_ids = ""
    for i in range(1, len(slides) + 1):
        slide_ids += f'    <p:sldId id="{255 + i}" r:id="rIdSlide{i}"/>\n'

    pres_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst>
    <p:sldMasterId id="2147483648" r:id="rIdMaster1"/>
  </p:sldMasterIdLst>
  <p:sldIdLst>
{slide_ids}  </p:sldIdLst>
  <p:sldSz cx="9144000" cy="5143500"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>"""

    master_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst>
    <p:sldLayoutId id="2147483649" r:id="rIdLayout1"/>
  </p:sldLayoutIdLst>
</p:sldMaster>"""

    master_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rIdLayout1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>"""

    layout_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
             type="blank">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    </p:spTree>
  </p:cSld>
</p:sldLayout>"""

    layout_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rIdMaster" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>"""

    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("ppt/presentation.xml", pres_xml)
        zf.writestr("ppt/_rels/presentation.xml.rels", pres_rels)
        zf.writestr("ppt/slideMasters/slideMaster1.xml", master_xml)
        zf.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", master_rels)
        zf.writestr("ppt/slideLayouts/slideLayout1.xml", layout_xml)
        zf.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", layout_rels)

        for i, s in enumerate(slides, start=1):
            s_title = xml_escape(s.get("title", f"Slide {i}"))
            s_sub = xml_escape(s.get("subtitle", ""))
            bullets = s.get("bullets", [])

            sub_xml = ""
            if s_sub:
                sub_xml = f"""
          <a:p>
            <a:pPr lvl="0"/>
            <a:r>
              <a:rPr lang="en-US" sz="1200" i="1"/>
              <a:t>{s_sub}</a:t>
            </a:r>
          </a:p>"""

            body_xml = ""
            for b in bullets:
                body_xml += f"""
        <a:p>
          <a:pPr lvl="0" marL="288000" indent="-288000">
            <a:buFont typeface="Arial"/>
            <a:buChar char="•"/>
          </a:pPr>
          <a:r>
            <a:rPr lang="en-US" sz="1500"/>
            <a:t>{xml_escape(b)}</a:t>
          </a:r>
        </a:p>"""

            slide_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="2" name="Title"/>
          <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
          <p:nvPr><p:ph type="title"/></p:nvPr>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="685800" y="457200"/><a:ext cx="7772400" cy="914400"/></a:xfrm>
        </p:spPr>
        <p:txBody>
          <a:bodyPr/>
          <a:lstStyle/>
          <a:p>
            <a:r>
              <a:rPr lang="en-US" sz="2400" b="1"/>
              <a:t>{s_title}</a:t>
            </a:r>
          </a:p>
{sub_xml}
        </p:txBody>
      </p:sp>
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="3" name="Content"/>
          <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
          <p:nvPr><p:ph idx="1"/></p:nvPr>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="685800" y="1524000"/><a:ext cx="7772400" cy="3200400"/></a:xfrm>
        </p:spPr>
        <p:txBody>
          <a:bodyPr/>
          <a:lstStyle/>
{body_xml}
        </p:txBody>
      </p:sp>
    </p:spTree>
  </p:cSld>
</p:sld>"""
            zf.writestr(f"ppt/slides/slide{i}.xml", slide_xml)
            slide_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rIdLayout" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>"""
            zf.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", slide_rels)

    return build_attachment_meta(filename=filename, display_name=filename, role=role)


def write_json_file(filename: str, data: dict | list, role: str = "file") -> dict:
    files_dir = get_chat_files_dir()
    dest = files_dir / filename
    with dest.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
    return build_attachment_meta(filename=filename, display_name=filename, role=role)


def write_html_file(filename: str, title: str, html_body: str, role: str = "file") -> dict:
    files_dir = get_chat_files_dir()
    dest = files_dir / filename
    body_stripped = html_body.strip()
    if body_stripped.lower().startswith("<!doctype html") or body_stripped.lower().startswith("<html"):
        full_html = html_body
    else:
        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{xml_escape(title)}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      margin: 0; padding: 40px; background: #0c0b09; color: #f7f4ec; line-height: 1.6;
    }}
    .container {{ max-width: 860px; margin: 0 auto; background: #171612; border: 1px solid #36342e; border-radius: 8px; padding: 36px; box-shadow: 0 10px 25px rgba(0,0,0,0.4); }}
    h1 {{ color: #ffffff; border-bottom: 2px solid #cc4b2c; padding-bottom: 12px; margin-top: 0; font-size: 26px; }}
    h2 {{ color: #e8e3d6; margin-top: 28px; font-size: 19px; }}
    p, li {{ color: #c4beb1; font-size: 15px; }}
    code, pre {{ background: #0c0b09; border: 1px solid #36342e; border-radius: 4px; font-family: monospace; padding: 2px 6px; color: #ff8a65; }}
    pre {{ padding: 16px; overflow-x: auto; }}
    .badge {{ display: inline-block; background: #cc4b2c; color: #fff; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; text-transform: uppercase; margin-bottom: 16px; }}
  </style>
</head>
<body>
  <div class="container">
    <span class="badge">Verified Client Deliverable</span>
    <h1>{xml_escape(title)}</h1>
    {html_body}
  </div>
</body>
</html>"""
    dest.write_text(full_html, encoding="utf-8")
    return build_attachment_meta(filename=filename, display_name=filename, role=role)


def write_png_file(filename: str, title: str, bullets: list[str], subtitle: str = "", role: str = "file") -> dict:
    files_dir = get_chat_files_dir()
    dest = files_dir / filename
    try:
        from PIL import Image, ImageDraw
        w, h = 1200, 750
        img = Image.new("RGB", (w, h), color=(17, 17, 15))
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, w, 8], fill=(204, 75, 44))
        draw.rectangle([40, 40, w - 40, h - 40], fill=(26, 26, 23), outline=(55, 53, 47), width=1)
        draw.rectangle([80, 80, 260, 110], fill=(204, 75, 44))
        draw.text((95, 87), "INFINIAI PRODUCTION", fill=(255, 255, 255))
        draw.text((80, 130), title[:60], fill=(247, 244, 236))
        if subtitle:
            draw.text((80, 180), subtitle[:80], fill=(160, 156, 145))
        y = 230
        for b in bullets[:9]:
            draw.rectangle([80, y + 4, 90, y + 14], fill=(204, 75, 44))
            draw.text((105, y), b[:90], fill=(230, 226, 218))
            y += 45
        draw.line([80, h - 90, w - 80, h - 90], fill=(55, 53, 47), width=1)
        draw.text((80, h - 75), "CONFIDENTIAL & PROPRIETARY · CLIENT DELIVERABLE", fill=(120, 116, 107))
        draw.text((w - 280, h - 75), "VERIFIED ASSET PACK", fill=(204, 75, 44))
        img.save(dest, "PNG", optimize=True)
    except Exception:
        pass
    return build_attachment_meta(filename=filename, display_name=filename, role=role)


def guess_mime_type(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    explicit = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".doc": "application/msword",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xls": "application/vnd.ms-excel",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".csv": "text/csv; charset=utf-8",
        ".txt": "text/plain; charset=utf-8",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".zip": "application/zip",
        ".json": "application/json",
        ".html": "text/html; charset=utf-8",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4",
        ".ogg": "audio/ogg",
        ".opus": "audio/ogg",
        ".webm": "audio/webm",
        ".aac": "audio/aac",
        ".flac": "audio/flac",
    }
    if ext in explicit:
        return explicit[ext]
    guessed, _ = mimetypes.guess_type(filename)
    return guessed or "application/octet-stream"

