import html
import os
import shutil
from PIL import Image
from playwright.sync_api import sync_playwright
from platformhub.engaging_posters_data import ENGAGING_POSTERS


def build_html(p: dict) -> str:
    t = p["theme"]
    is_dark = t.get("is_dark", True)

    sticker_border = "rgba(0,0,0,0.1)" if not is_dark else "rgba(255,255,255,0.2)"
    sticker_shadow = "0 18px 40px rgba(0,0,0,0.12)" if not is_dark else "0 24px 50px rgba(0,0,0,0.7)"
    swipe_color = "#71717a" if is_dark else "#78716c"

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@600;700&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 1080px;
    height: 1920px;
    background: {t["bg"]};
    color: {t["text"]};
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    position: relative;
    overflow: hidden;
    padding: 110px 80px 120px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .glow-1 {{
    position: absolute;
    top: -160px;
    right: -160px;
    width: 750px;
    height: 750px;
    background: radial-gradient(circle, {t["glow1"]} 0%, rgba(0,0,0,0) 70%);
    filter: blur(85px);
    pointer-events: none;
  }}
  .glow-2 {{
    position: absolute;
    bottom: 260px;
    left: -200px;
    width: 820px;
    height: 820px;
    background: radial-gradient(circle, {t["glow2"]} 0%, rgba(0,0,0,0) 70%);
    filter: blur(95px);
    pointer-events: none;
  }}
  .top-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
    z-index: 2;
  }}
  .brand {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 26px;
    font-weight: 700;
    letter-spacing: 4px;
    color: {t["text"]};
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .brand-dot {{
    width: 14px;
    height: 14px;
    background: {t["accent"]};
    border-radius: 50%;
    box-shadow: 0 0 16px {t["accent"]};
  }}
  .tag-badge {{
    background: {t["badge_bg"]};
    border: 1px solid {t["badge_border"]};
    backdrop-filter: blur(16px);
    padding: 14px 26px;
    border-radius: 100px;
    font-size: 19px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: {t["badge_text"]};
  }}
  .main-content {{
    position: relative;
    z-index: 2;
    display: flex;
    flex-direction: column;
    gap: 40px;
  }}
  .eyebrow-hook {{
    font-family: 'Space Grotesk', sans-serif;
    color: {t["eyebrow"]};
    font-size: 26px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
  }}
  .headline {{
    font-size: 70px;
    font-weight: 900;
    line-height: 1.08;
    letter-spacing: -0.04em;
    color: {t["text"]};
  }}
  .headline span {{
    background: {t["headline_grad"]};
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .outcome-card {{
    background: {t["card_bg"]};
    border: 1px solid {t["card_border"]};
    backdrop-filter: blur(32px);
    border-radius: 32px;
    padding: 48px;
    box-shadow: 0 30px 60px rgba(0, 0, 0, 0.45);
  }}
  .outcome-card p {{
    font-size: 31px;
    line-height: 1.48;
    color: {t["text"]};
    font-weight: 500;
  }}
  .outcome-meta {{
    display: flex;
    gap: 28px;
    margin-top: 32px;
    padding-top: 28px;
    border-top: 1px solid rgba(255, 255, 255, 0.12);
    flex-wrap: wrap;
  }}
  .meta-pill {{
    font-size: 21px;
    font-weight: 700;
    color: {t["text_muted"]};
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .meta-pill b {{
    color: {t["text"]};
  }}
  .bottom-cta {{
    position: relative;
    z-index: 2;
    display: flex;
    flex-direction: column;
    gap: 20px;
    align-items: center;
  }}
  .story-link-sticker {{
    width: 100%;
    background: {t["sticker_bg"]};
    color: {t["sticker_text"]};
    padding: 34px 40px;
    border-radius: 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: {sticker_shadow}, 0 0 0 1px {sticker_border};
  }}
  .sticker-left {{
    display: flex;
    align-items: center;
    gap: 22px;
  }}
  .sticker-icon {{
    width: 56px;
    height: 56px;
    background: {t["sticker_accent"]};
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    font-size: 26px;
    flex-shrink: 0;
  }}
  .sticker-text {{
    display: flex;
    flex-direction: column;
    gap: 4px;
  }}
  .sticker-label {{
    font-size: 15px;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    opacity: 0.7;
  }}
  .sticker-url {{
    font-size: 25px;
    font-weight: 800;
    letter-spacing: -0.01em;
  }}
  .sticker-arrow {{
    font-size: 36px;
    font-weight: 900;
    color: {t["sticker_accent"]};
  }}
  .swipe-note {{
    font-size: 19px;
    letter-spacing: 2px;
    font-weight: 700;
    text-transform: uppercase;
    color: {swipe_color};
  }}
</style>
</head>
<body>
  <div class="glow-1"></div>
  <div class="glow-2"></div>

  <div class="top-bar">
    <div class="brand">
      <div class="brand-dot"></div>
      INFINIAI
    </div>
    <div class="tag-badge">{html.escape(p["tag_badge"])}</div>
  </div>

  <div class="main-content">
    <div class="eyebrow-hook">{html.escape(p["eyebrow"])}</div>
    <h1 class="headline">{html.escape(p["headline_pre"])}<span>{html.escape(p["headline_span"])}</span>{html.escape(p["headline_post"])}</h1>

    <div class="outcome-card">
      <p>{html.escape(p["outcome"])}</p>
      <div class="outcome-meta">
        <div class="meta-pill">Turnaround: <b>{html.escape(p["turnaround"])}</b></div>
        <div class="meta-pill">Deliverable: <b>{html.escape(p["deliverable"])}</b></div>
      </div>
    </div>
  </div>

  <div class="bottom-cta">
    <div class="story-link-sticker">
      <div class="sticker-left">
        <div class="sticker-icon">↗</div>
        <div class="sticker-text">
          <span class="sticker-label">Direct Intake &amp; Scoping</span>
          <span class="sticker-url">{html.escape(p["contact_display"])}</span>
        </div>
      </div>
      <div class="sticker-arrow">→</div>
    </div>
    <div class="swipe-note">Tap link or visit site to submit project</div>
  </div>
</body>
</html>"""


def generate_all_engaging():
    static_dir = os.path.abspath("static/posters")
    public_dir = os.path.abspath("public/posters")
    html_dir = os.path.abspath("static/posters_html")
    os.makedirs(static_dir, exist_ok=True)
    os.makedirs(public_dir, exist_ok=True)
    os.makedirs(html_dir, exist_ok=True)

    print(f"Generating HTML layouts for {len(ENGAGING_POSTERS)} social story posters...")
    for p in ENGAGING_POSTERS:
        html_code = build_html(p)
        filename = f"poster_{p['number']}.html"
        with open(os.path.join(html_dir, filename), "w", encoding="utf-8") as f:
            f.write(html_code)

    print("Launching Chromium to render 1080x1920 social image posters...")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)

        for p in ENGAGING_POSTERS:
            num = p["number"]
            html_path = os.path.join(html_dir, f"poster_{num}.html").replace("\\", "/")
            png_static = os.path.join(static_dir, f"poster_{num}.png")
            png_public = os.path.join(public_dir, f"poster_{num}.png")
            jpg_static = os.path.join(static_dir, f"poster_{num}.jpg")
            jpg_public = os.path.join(public_dir, f"poster_{num}.jpg")

            page.goto(f"file:///{html_path}")
            # Wait for Google Fonts to settle
            page.wait_for_timeout(300)
            page.screenshot(path=png_static)
            shutil.copyfile(png_static, png_public)

            with Image.open(png_static) as img:
                rgb_im = img.convert("RGB")
                rgb_im.save(jpg_static, format="JPEG", quality=95)
                rgb_im.save(jpg_public, format="JPEG", quality=95)

            print(f"Rendered engaging story image poster_{num}.png & poster_{num}.jpg")

        browser.close()

    print(f"Completed rendering all {len(ENGAGING_POSTERS)} engaging social story images!")


if __name__ == "__main__":
    generate_all_engaging()
