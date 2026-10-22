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


def write_zip_file(filename: str, files_map: dict[str, str | bytes], role: str = "file") -> dict:
    files_dir = get_chat_files_dir()
    dest = files_dir / filename
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for inner_name, content in files_map.items():
            if isinstance(content, str):
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
            bullets = s.get("bullets", [])
            body_xml = ""
            for b in bullets:
                body_xml += f"""
        <a:p>
          <a:pPr lvl="0"/>
          <a:r>
            <a:rPr lang="en-US" sz="1600"/>
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
              <a:rPr lang="en-US" sz="2800" b="1"/>
              <a:t>{s_title}</a:t>
            </a:r>
          </a:p>
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

