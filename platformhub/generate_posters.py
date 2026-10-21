import html
import os
from platformhub.posters_data import POSTERS


def wrap_text(text: str, max_chars: int = 34) -> list[str]:
    words = text.split()
    lines = []
    curr = []
    curr_len = 0
    for w in words:
        if curr_len + len(w) + 1 <= max_chars:
            curr.append(w)
            curr_len += len(w) + 1
        else:
            if curr:
                lines.append(" ".join(curr))
            curr = [w]
            curr_len = len(w)
    if curr:
        lines.append(" ".join(curr))
    return lines


def build_svg(p: dict) -> str:
    theme = p["theme"]
    if theme == "dark":
        bg = "#11110f"
        fg = "#faf8f2"
        muted = "#9a9488"
        card_bg = "#191815"
        border = "#2e2b26"
        accent = "#c84132"
        pill_bg = "#23211d"
        pill_fg = "#faf8f2"
    else:
        bg = "#faf8f2"
        fg = "#11110f"
        muted = "#666157"
        card_bg = "#f1eee6"
        border = "#cfc9bc"
        accent = "#c84132"
        pill_bg = "#e5e1d7"
        pill_fg = "#11110f"

    h_lines = wrap_text(p["headline"], max_chars=28)
    b_lines = wrap_text(p["body"], max_chars=44)

    y_headline = 520
    h_tspans = "".join(
        f'<tspan x="120" y="{y_headline + i * 72}">{html.escape(line)}</tspan>'
        for i, line in enumerate(h_lines)
    )

    y_divider = y_headline + len(h_lines) * 72 + 25
    y_body = y_divider + 60
    b_tspans = "".join(
        f'<tspan x="120" y="{y_body + i * 46}">{html.escape(line)}</tspan>'
        for i, line in enumerate(b_lines)
    )

    y_specs = y_body + len(b_lines) * 46 + 80

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" width="1080" height="1920">
  <defs>
    <style>
      .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
      .sans {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
    </style>
  </defs>

  <!-- Solid Minimalist Background -->
  <rect width="1080" height="1920" fill="{bg}"/>

  <!-- Architectural Frame -->
  <rect x="60" y="60" width="960" height="1800" fill="none" stroke="{border}" stroke-width="1.5"/>
  <rect x="68" y="68" width="944" height="1784" fill="none" stroke="{border}" stroke-width="0.5" opacity="0.6"/>

  <!-- Top Metadata Bar -->
  <text x="120" y="160" class="mono" font-size="16" font-weight="700" letter-spacing="3" fill="{accent}">INFINIAI · SERVICE SPECIFICATION</text>
  <text x="960" y="160" text-anchor="end" class="mono" font-size="20" font-weight="700" letter-spacing="2" fill="{muted}">{p["number"]} / 20</text>
  <line x1="120" y1="200" x2="960" y2="200" stroke="{border}" stroke-width="1.5"/>

  <!-- Service Badge -->
  <rect x="120" y="250" width="420" height="46" rx="4" fill="{pill_bg}"/>
  <text x="140" y="280" class="mono" font-size="14" font-weight="700" letter-spacing="1.5" fill="{pill_fg}">{html.escape(p["family"].upper())} · {html.escape(p["service_name"].upper())}</text>

  <!-- One Full Sentence Headline -->
  <text class="sans" font-size="52" font-weight="800" fill="{fg}">
    {h_tspans}
  </text>

  <!-- Terracotta Hairline -->
  <line x1="120" y1="{y_divider}" x2="340" y2="{y_divider}" stroke="{accent}" stroke-width="3.5"/>

  <!-- Flat Declarative Body -->
  <text class="sans" font-size="26" font-weight="400" fill="{muted}">
    {b_tspans}
  </text>

  <!-- Concrete Specifications Panel -->
  <g transform="translate(120, {y_specs})">
    <rect x="0" y="0" width="840" height="230" rx="6" fill="{card_bg}" stroke="{border}" stroke-width="1.5"/>

    <text x="45" y="60" class="mono" font-size="13" font-weight="700" letter-spacing="2" fill="{muted}">TURNAROUND</text>
    <text x="45" y="105" class="sans" font-size="30" font-weight="700" fill="{fg}">{html.escape(p["turnaround"])}</text>

    <line x1="280" y1="35" x2="280" y2="195" stroke="{border}" stroke-width="1"/>

    <text x="325" y="60" class="mono" font-size="13" font-weight="700" letter-spacing="2" fill="{muted}">DELIVERABLE</text>
    <text x="325" y="105" class="sans" font-size="30" font-weight="700" fill="{fg}">{html.escape(p["format"])}</text>

    <line x1="570" y1="35" x2="570" y2="195" stroke="{border}" stroke-width="1"/>

    <text x="615" y="60" class="mono" font-size="13" font-weight="700" letter-spacing="2" fill="{muted}">BASE PRICING</text>
    <text x="615" y="105" class="sans" font-size="30" font-weight="700" fill="{accent}">{html.escape(p["base_rate"])}</text>

    <line x1="45" y1="145" x2="795" y2="145" stroke="{border}" stroke-width="0.8" stroke-dasharray="4 4"/>
    <text x="45" y="188" class="mono" font-size="15" fill="{muted}">Catalog code: {html.escape(p["service_code"])}</text>
  </g>

  <!-- Required Contact Bar Leading to /consultation/ -->
  <g transform="translate(120, 1530)">
    <rect x="0" y="0" width="840" height="150" rx="6" fill="{pill_bg}" stroke="{border}" stroke-width="1.5"/>
    <circle cx="50" cy="75" r="9" fill="{accent}"/>
    <text x="80" y="65" class="mono" font-size="13" letter-spacing="2" font-weight="700" fill="{muted}">DIRECT INTAKE &amp; SCOPING</text>
    <text x="80" y="108" class="sans" font-size="23" font-weight="700" fill="{fg}">{html.escape(p["contact_display"])}</text>
  </g>

  <!-- Bottom Brand Rules -->
  <line x1="120" y1="1750" x2="960" y2="1750" stroke="{border}" stroke-width="1"/>
  <text x="120" y="1800" class="mono" font-size="14" letter-spacing="2" fill="{muted}">WWW.BYINFINI.ONLINE</text>
  <text x="960" y="1800" text-anchor="end" class="mono" font-size="14" letter-spacing="2" fill="{muted}">INTERNAL DESK &amp; CHAT BILLED DIRECTLY</text>
</svg>"""


def generate_all():
    os.makedirs("static/posters", exist_ok=True)
    os.makedirs("public/posters", exist_ok=True)

    for p in POSTERS:
        svg = build_svg(p)
        filename = f"poster_{p['number']}.svg"
        with open(os.path.join("static", "posters", filename), "w", encoding="utf-8") as f:
            f.write(svg)
        with open(os.path.join("public", "posters", filename), "w", encoding="utf-8") as f:
            f.write(svg)
        p["svg_filename"] = filename
        p["svg_path"] = f"/static/posters/{filename}"

    print(f"Generated {len(POSTERS)} minimalist SVG posters.")


if __name__ == "__main__":
    generate_all()
