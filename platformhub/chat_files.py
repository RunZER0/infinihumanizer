import csv
import io
import mimetypes
import os
import re
import time
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

from django.conf import settings

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
}

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
    return {
        "name": display_name or filename,
        "filename": filename,
        "url": f"/workspace/chat/files/{filename}",
        "download_url": f"/workspace/chat/files/{filename}?download=1",
        "ext": ext,
        "kind": ext,
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
                f"Unsupported file type ({ext or 'unknown'}). Allowed: PDF, DOCX, XLSX, CSV, PPTX, PNG, JPG, TXT, ZIP."
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
            f'<w:p><w:r><w:rPr><w:b/><w:sz w:val="28"/></w:rPr><w:t>{xml_escape(title)}</w:t></w:r></w:p>'
        )
    for para in paragraphs:
        body_xml.append(
            f'<w:p><w:r><w:rPr><w:sz w:val="22"/></w:rPr><w:t xml:space="preserve">{xml_escape(para)}</w:t></w:r></w:p>'
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


def write_xlsx_file(filename: str, sheet_name: str, rows: list[list], role: str = "file") -> dict:
    files_dir = get_chat_files_dir()
    dest = files_dir / filename

    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>"""

    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""

    workbook_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
          xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="{xml_escape(sheet_name[:31] or 'Sheet1')}" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>"""

    workbook_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>"""

    sheet_rows_xml = []
    for r_idx, row in enumerate(rows, start=1):
        cells_xml = []
        for c_idx, val in enumerate(row):
            cell_ref = f"{_col_letter(c_idx)}{r_idx}"
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                cells_xml.append(f'<c r="{cell_ref}"><v>{val}</v></c>')
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

    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("xl/workbook.xml", workbook_xml)
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)

    return build_attachment_meta(filename=filename, display_name=filename, role=role)


def _pdf_escape(text: str) -> str:
    ascii_text = text.encode("latin-1", "replace").decode("latin-1")
    return ascii_text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def write_pdf_file(filename: str, title: str, lines: list[str], role: str = "file") -> dict:
    files_dir = get_chat_files_dir()
    dest = files_dir / filename

    stream_ops = ["BT", "/F1 13 Tf", "54 740 Td", f"({_pdf_escape(title)}) Tj", "/F1 10 Tf", "0 -22 Td"]
    for line in lines[:42]:
        stream_ops.append(f"({_pdf_escape(line)}) Tj")
        stream_ops.append("0 -15 Td")
    stream_ops.append("ET")
    stream_bytes = "\n".join(stream_ops).encode("latin-1")

    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n",
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
        f"5 0 obj\n<< /Length {len(stream_bytes)} >>\nstream\n".encode("latin-1")
        + stream_bytes
        + b"\nendstream\nendobj\n",
    ]

    buf = io.BytesIO()
    buf.write(b"%PDF-1.4\n")
    offsets = []
    for obj in objects:
        offsets.append(buf.tell())
        buf.write(obj)

    xref_pos = buf.tell()
    buf.write(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
    buf.write(b"0000000000 65535 f \n")
    for off in offsets:
        buf.write(f"{off:010d} 00000 n \n".encode("latin-1"))
    buf.write(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("latin-1")
    )

    dest.write_bytes(buf.getvalue())
    return build_attachment_meta(filename=filename, display_name=filename, role=role)


def write_csv_file(filename: str, rows: list[list], role: str = "file") -> dict:
    files_dir = get_chat_files_dir()
    dest = files_dir / filename
    with dest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)
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
    }
    if ext in explicit:
        return explicit[ext]
    guessed, _ = mimetypes.guess_type(filename)
    return guessed or "application/octet-stream"
