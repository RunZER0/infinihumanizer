import html
import os
import shutil
from PIL import Image
from playwright.sync_api import sync_playwright
from platformhub.engaging_posters_data import ENGAGING_POSTERS


def build_html(p: dict) -> str:
    style = p.get("style", "ink-obsidian")
    base_dir = os.path.abspath("static/posters/backgrounds").replace("\\", "/")

    if style == "photo-dark":
        bg_file = p.get("bg_image", "bg_executive_desk.jpg")
        bg_url = f"file:///{base_dir}/{bg_file}"
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
    position: relative;
    overflow: hidden;
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    color: #faf8f2;
    padding: 110px 80px 110px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: #11110f;
  }}
  .bg-photo {{
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: 0;
  }}
  .bg-overlay {{
    position: absolute;
    inset: 0;
    background: linear-gradient(180deg, rgba(17, 17, 15, 0.72) 0%, rgba(17, 17, 15, 0.88) 48%, rgba(17, 17, 15, 0.98) 100%);
    z-index: 1;
  }}
  .terracotta-glow {{
    position: absolute;
    top: 220px;
    right: -120px;
    width: 700px;
    height: 700px;
    background: radial-gradient(circle, rgba(200, 65, 50, 0.35) 0%, rgba(0,0,0,0) 70%);
    filter: blur(85px);
    z-index: 2;
    pointer-events: none;
  }}
  .content-z {{
    position: relative;
    z-index: 3;
  }}
  .top-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .brand {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 26px;
    font-weight: 700;
    letter-spacing: 4px;
    color: #faf8f2;
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .brand-dot {{
    width: 14px;
    height: 14px;
    background: #c84132;
    border-radius: 50%;
    box-shadow: 0 0 16px #c84132;
  }}
  .tag-badge {{
    background: rgba(200, 65, 50, 0.18);
    border: 1px solid rgba(200, 65, 50, 0.45);
    backdrop-filter: blur(16px);
    padding: 14px 26px;
    border-radius: 100px;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #e46b5d;
  }}
  .main-block {{
    display: flex;
    flex-direction: column;
    gap: 36px;
  }}
  .eyebrow {{
    font-family: 'Space Grotesk', sans-serif;
    color: #e46b5d;
    font-size: 24px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
  }}
  .headline {{
    font-size: 72px;
    font-weight: 900;
    line-height: 1.08;
    letter-spacing: -0.04em;
    color: #ffffff;
  }}
  .headline span {{
    color: #e46b5d;
  }}
  .outcome-card {{
    background: rgba(25, 24, 21, 0.82);
    border: 1px solid rgba(200, 65, 50, 0.3);
    backdrop-filter: blur(32px);
    border-radius: 30px;
    padding: 44px;
    box-shadow: 0 30px 60px rgba(0, 0, 0, 0.6);
  }}
  .outcome-card p {{
    font-size: 30px;
    line-height: 1.48;
    color: #f1eee6;
    font-weight: 500;
  }}
  .outcome-meta {{
    display: flex;
    gap: 32px;
    margin-top: 28px;
    padding-top: 26px;
    border-top: 1px solid rgba(255, 255, 255, 0.12);
  }}
  .meta-pill {{
    font-size: 20px;
    font-weight: 700;
    color: #9a9488;
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .meta-pill b {{
    color: #faf8f2;
  }}
  .story-link-sticker {{
    width: 100%;
    background: #faf8f2;
    color: #11110f;
    padding: 34px 40px;
    border-radius: 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 24px 50px rgba(0,0,0,0.7), 0 0 0 1px rgba(255,255,255,0.2);
  }}
  .sticker-left {{
    display: flex;
    align-items: center;
    gap: 22px;
  }}
  .sticker-icon {{
    width: 56px;
    height: 56px;
    background: #c84132;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    font-size: 26px;
    flex-shrink: 0;
  }}
  .sticker-label {{
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #68645c;
  }}
  .sticker-url {{
    font-size: 25px;
    font-weight: 800;
    color: #11110f;
    letter-spacing: -0.01em;
  }}
  .sticker-arrow {{
    font-size: 34px;
    font-weight: 900;
    color: #c84132;
  }}
  .swipe-note {{
    font-size: 18px;
    letter-spacing: 2px;
    font-weight: 700;
    text-transform: uppercase;
    color: #8d877b;
    text-align: center;
    margin-top: 18px;
  }}
</style>
</head>
<body>
  <img class="bg-photo" src="{bg_url}">
  <div class="bg-overlay"></div>
  <div class="terracotta-glow"></div>

  <div class="top-bar content-z">
    <div class="brand">
      <div class="brand-dot"></div>
      INFINIAI
    </div>
    <div class="tag-badge">{html.escape(p["tag_badge"])}</div>
  </div>

  <div class="main-block content-z">
    <div class="eyebrow">{html.escape(p["eyebrow"])}</div>
    <h1 class="headline">{html.escape(p["headline_pre"])}<span>{html.escape(p["headline_span"])}</span>{html.escape(p["headline_post"])}</h1>
    <div class="outcome-card">
      <p>{html.escape(p["outcome"])}</p>
      <div class="outcome-meta">
        <div class="meta-pill">Speed: <b>{html.escape(p["turnaround"])}</b></div>
        <div class="meta-pill">Deliverable: <b>{html.escape(p["deliverable"])}</b></div>
      </div>
    </div>
  </div>

  <div class="bottom-block content-z">
    <div class="story-link-sticker">
      <div class="sticker-left">
        <div class="sticker-icon">↗</div>
        <div>
          <div class="sticker-label">Direct Intake &amp; Scoping</div>
          <div class="sticker-url">{html.escape(p["contact_display"])}</div>
        </div>
      </div>
      <div class="sticker-arrow">→</div>
    </div>
    <div class="swipe-note">Tap link or visit site to submit project</div>
  </div>
</body>
</html>"""

    elif style == "editorial-paper":
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
    position: relative;
    overflow: hidden;
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    color: #171612;
    padding: 110px 80px 110px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: #faf8f2;
  }}
  .paper-frame {{
    position: absolute;
    inset: 40px;
    border: 1px solid #cfc9bc;
    pointer-events: none;
    z-index: 1;
  }}
  .content-z {{
    position: relative;
    z-index: 2;
  }}
  .top-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .brand {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 26px;
    font-weight: 700;
    letter-spacing: 4px;
    color: #171612;
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .brand-dot {{
    width: 14px;
    height: 14px;
    background: #c84132;
    border-radius: 50%;
  }}
  .tag-badge {{
    background: rgba(200, 65, 50, 0.1);
    border: 1px solid rgba(200, 65, 50, 0.35);
    padding: 14px 26px;
    border-radius: 100px;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #c84132;
  }}
  .main-block {{
    display: flex;
    flex-direction: column;
    gap: 36px;
  }}
  .eyebrow {{
    font-family: 'Space Grotesk', sans-serif;
    color: #c84132;
    font-size: 24px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
  }}
  .headline {{
    font-size: 72px;
    font-weight: 900;
    line-height: 1.08;
    letter-spacing: -0.04em;
    color: #171612;
  }}
  .headline span {{
    color: #c84132;
  }}
  .outcome-card {{
    background: #ffffff;
    border: 1px solid #cfc9bc;
    border-radius: 30px;
    padding: 44px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.05);
  }}
  .outcome-card p {{
    font-size: 30px;
    line-height: 1.48;
    color: #171612;
    font-weight: 500;
  }}
  .outcome-meta {{
    display: flex;
    gap: 32px;
    margin-top: 28px;
    padding-top: 26px;
    border-top: 1px solid #cfc9bc;
  }}
  .meta-pill {{
    font-size: 20px;
    font-weight: 700;
    color: #68645c;
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .meta-pill b {{
    color: #171612;
  }}
  .story-link-sticker {{
    width: 100%;
    background: #11110f;
    color: #faf8f2;
    padding: 34px 40px;
    border-radius: 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 20px 40px rgba(0,0,0,0.18);
  }}
  .sticker-left {{
    display: flex;
    align-items: center;
    gap: 22px;
  }}
  .sticker-icon {{
    width: 56px;
    height: 56px;
    background: #c84132;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    font-size: 26px;
    flex-shrink: 0;
  }}
  .sticker-label {{
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #9a9488;
  }}
  .sticker-url {{
    font-size: 25px;
    font-weight: 800;
    color: #faf8f2;
    letter-spacing: -0.01em;
  }}
  .sticker-arrow {{
    font-size: 34px;
    font-weight: 900;
    color: #e46b5d;
  }}
  .swipe-note {{
    font-size: 18px;
    letter-spacing: 2px;
    font-weight: 700;
    text-transform: uppercase;
    color: #68645c;
    text-align: center;
    margin-top: 18px;
  }}
</style>
</head>
<body>
  <div class="paper-frame"></div>

  <div class="top-bar content-z">
    <div class="brand">
      <div class="brand-dot"></div>
      INFINIAI
    </div>
    <div class="tag-badge">{html.escape(p["tag_badge"])}</div>
  </div>

  <div class="main-block content-z">
    <div class="eyebrow">{html.escape(p["eyebrow"])}</div>
    <h1 class="headline">{html.escape(p["headline_pre"])}<span>{html.escape(p["headline_span"])}</span>{html.escape(p["headline_post"])}</h1>
    <div class="outcome-card">
      <p>{html.escape(p["outcome"])}</p>
      <div class="outcome-meta">
        <div class="meta-pill">Speed: <b>{html.escape(p["turnaround"])}</b></div>
        <div class="meta-pill">Deliverable: <b>{html.escape(p["deliverable"])}</b></div>
      </div>
    </div>
  </div>

  <div class="bottom-block content-z">
    <div class="story-link-sticker">
      <div class="sticker-left">
        <div class="sticker-icon">↗</div>
        <div>
          <div class="sticker-label">Direct Intake &amp; Scoping</div>
          <div class="sticker-url">{html.escape(p["contact_display"])}</div>
        </div>
      </div>
      <div class="sticker-arrow">→</div>
    </div>
    <div class="swipe-note">Tap link or visit site to submit project</div>
  </div>
</body>
</html>"""

    else:
        # ink-obsidian
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
    position: relative;
    overflow: hidden;
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    color: #faf8f2;
    padding: 110px 80px 110px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: #11110f;
  }}
  .glow-1 {{
    position: absolute;
    top: -150px;
    right: -120px;
    width: 750px;
    height: 750px;
    background: radial-gradient(circle, rgba(200, 65, 50, 0.32) 0%, rgba(0,0,0,0) 70%);
    filter: blur(85px);
    z-index: 1;
    pointer-events: none;
  }}
  .glow-2 {{
    position: absolute;
    bottom: 240px;
    left: -180px;
    width: 800px;
    height: 800px;
    background: radial-gradient(circle, rgba(169, 50, 37, 0.22) 0%, rgba(0,0,0,0) 70%);
    filter: blur(95px);
    z-index: 1;
    pointer-events: none;
  }}
  .content-z {{
    position: relative;
    z-index: 2;
  }}
  .top-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .brand {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 26px;
    font-weight: 700;
    letter-spacing: 4px;
    color: #faf8f2;
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .brand-dot {{
    width: 14px;
    height: 14px;
    background: #c84132;
    border-radius: 50%;
    box-shadow: 0 0 16px #c84132;
  }}
  .tag-badge {{
    background: rgba(200, 65, 50, 0.16);
    border: 1px solid rgba(200, 65, 50, 0.4);
    backdrop-filter: blur(16px);
    padding: 14px 26px;
    border-radius: 100px;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #e46b5d;
  }}
  .main-block {{
    display: flex;
    flex-direction: column;
    gap: 36px;
  }}
  .eyebrow {{
    font-family: 'Space Grotesk', sans-serif;
    color: #e46b5d;
    font-size: 24px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
  }}
  .headline {{
    font-size: 72px;
    font-weight: 900;
    line-height: 1.08;
    letter-spacing: -0.04em;
    color: #ffffff;
  }}
  .headline span {{
    color: #e46b5d;
  }}
  .outcome-card {{
    background: rgba(25, 24, 21, 0.85);
    border: 1px solid rgba(200, 65, 50, 0.28);
    backdrop-filter: blur(32px);
    border-radius: 30px;
    padding: 44px;
    box-shadow: 0 30px 60px rgba(0, 0, 0, 0.55);
  }}
  .outcome-card p {{
    font-size: 30px;
    line-height: 1.48;
    color: #f1eee6;
    font-weight: 500;
  }}
  .outcome-meta {{
    display: flex;
    gap: 32px;
    margin-top: 28px;
    padding-top: 26px;
    border-top: 1px solid rgba(255, 255, 255, 0.12);
  }}
  .meta-pill {{
    font-size: 20px;
    font-weight: 700;
    color: #9a9488;
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .meta-pill b {{
    color: #faf8f2;
  }}
  .story-link-sticker {{
    width: 100%;
    background: #faf8f2;
    color: #11110f;
    padding: 34px 40px;
    border-radius: 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 24px 50px rgba(0,0,0,0.7), 0 0 0 1px rgba(255,255,255,0.2);
  }}
  .sticker-left {{
    display: flex;
    align-items: center;
    gap: 22px;
  }}
  .sticker-icon {{
    width: 56px;
    height: 56px;
    background: #c84132;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    font-size: 26px;
    flex-shrink: 0;
  }}
  .sticker-label {{
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #68645c;
  }}
  .sticker-url {{
    font-size: 25px;
    font-weight: 800;
    color: #11110f;
    letter-spacing: -0.01em;
  }}
  .sticker-arrow {{
    font-size: 34px;
    font-weight: 900;
    color: #c84132;
  }}
  .swipe-note {{
    font-size: 18px;
    letter-spacing: 2px;
    font-weight: 700;
    text-transform: uppercase;
    color: #8d877b;
    text-align: center;
    margin-top: 18px;
  }}
</style>
</head>
<body>
  <div class="glow-1"></div>
  <div class="glow-2"></div>

  <div class="top-bar content-z">
    <div class="brand">
      <div class="brand-dot"></div>
      INFINIAI
    </div>
    <div class="tag-badge">{html.escape(p["tag_badge"])}</div>
  </div>

  <div class="main-block content-z">
    <div class="eyebrow">{html.escape(p["eyebrow"])}</div>
    <h1 class="headline">{html.escape(p["headline_pre"])}<span>{html.escape(p["headline_span"])}</span>{html.escape(p["headline_post"])}</h1>
    <div class="outcome-card">
      <p>{html.escape(p["outcome"])}</p>
      <div class="outcome-meta">
        <div class="meta-pill">Speed: <b>{html.escape(p["turnaround"])}</b></div>
        <div class="meta-pill">Deliverable: <b>{html.escape(p["deliverable"])}</b></div>
      </div>
    </div>
  </div>

  <div class="bottom-block content-z">
    <div class="story-link-sticker">
      <div class="sticker-left">
        <div class="sticker-icon">↗</div>
        <div>
          <div class="sticker-label">Direct Intake &amp; Scoping</div>
          <div class="sticker-url">{html.escape(p["contact_display"])}</div>
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

    print(f"Generating HTML layouts for {len(ENGAGING_POSTERS)} social story posters (Brand-aligned)...")
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
            page.wait_for_timeout(300)
            page.screenshot(path=png_static)
            shutil.copyfile(png_static, png_public)

            with Image.open(png_static) as img:
                rgb_im = img.convert("RGB")
                rgb_im.save(jpg_static, format="JPEG", quality=95)
                rgb_im.save(jpg_public, format="JPEG", quality=95)

            print(f"Rendered [{p.get('style')}] poster_{num}.png & poster_{num}.jpg")

        browser.close()

    print(f"Completed rendering all {len(ENGAGING_POSTERS)} site-themed image posters!")


if __name__ == "__main__":
    generate_all_engaging()
