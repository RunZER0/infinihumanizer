import csv
import re
from datetime import datetime, timedelta, timezone as dt_timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from humanizer.models import ClientConversation, ClientMessage
from platformhub.chat_files import (
    write_csv_file,
    write_docx_file,
    write_html_file,
    write_json_file,
    write_pdf_file,
    write_png_file,
    write_pptx_file,
    write_xlsx_file,
    write_zip_file,
)
from platformhub.models import Deliverable, Invoice, PaymentRecord, ServiceRequest


def parse_csv_dt(value: str):
    if not value:
        return None
    cleaned = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", value.strip())
    for fmt in ("%b %d, %Y %I:%M:%S %p", "%B %d, %Y %I:%M:%S %p"):
        try:
            dt = datetime.strptime(cleaned, fmt)
            return dt.replace(tzinfo=dt_timezone.utc)
        except ValueError:
            continue
    return None


def dt_utc(year, month, day, hour, minute, second=0):
    return datetime(year, month, day, hour, minute, second, tzinfo=dt_timezone.utc)


def build_seed_attachments() -> dict[str, dict]:
    files = {}

    # =========================================================================
    # 1. Jose Cruz (cruzjose6221@gmail.com)
    # =========================================================================
    files["cruz_old_bio_draft.docx"] = write_docx_file(
        "cruz_old_bio_draft.docx",
        "Cruz Metro Freight — Rough Company Notes",
        [
            "Cruz Metro Freight operates dedicated 26ft liftgate box trucks and high-roof sprinters out of DFW.",
            "We handle scheduled retail replenishment, pallet recovery, and warehouse dock-to-dock transfers.",
            "Cold email 1 note: Mention our 2 open liftgates on Tue/Thu in DFW industrial corridor.",
            "Cold email 2 note: Follow up on missed broker pickups and emergency same-day pallet recovery.",
            "Cold email 3 note: Rate sheet and 2-hour free dock detention policy.",
        ],
        role="source",
    )
    files["cruz_bio_and_emails_v1_preview.pdf"] = write_pdf_file(
        "cruz_bio_and_emails_v1_preview.pdf",
        "Cruz Metro Freight — Capability Bio & Outreach Preview (v1)",
        [
            "1. COMPANY PROFILE: Asset-based regional freight carrier based in Dallas-Fort Worth corridor.",
            "2. FLEET SPECS: Two 26-foot liftgate box trucks (10,000 lbs payload) and two Mercedes Sprinters.",
            "3. VALUE PROPOSITION: Direct dock dispatch without broker fees, 99.4% on-time delivery metric.",
            "4. OUTREACH SEQUENCE 1: Focused on warehouse shipping leads and distribution dock managers.",
            "5. OUTREACH SEQUENCE 2: Emergency same-day pallet recovery when brokers drop scheduled pickups.",
        ],
        role="draft",
    )
    files["cruz_bio_and_outreach_final.docx"] = write_docx_file(
        "cruz_bio_and_outreach_final.docx",
        "Cruz Metro Freight — Final Company Bio & Outbound Sequence (v2 Final)",
        [
            "EXECUTIVE CAPABILITY BIO: Cruz Metro Freight is an asset-based regional logistics provider headquartered in Dallas, Texas. We operate late-model 26-foot box trucks equipped with 3,500-lb tuck-under liftgates and high-roof sprinter vans. Serving manufacturers, third-party logistics warehouses, and retail distribution centers across the DFW Metroplex and North Texas corridor.",
            "CORE OPERATIONAL CAPABILITIES:",
            "— Scheduled morning retail replenishment and dock-to-dock transfers.",
            "— Time-critical hot-shot runs and same-day pallet recovery within a 120-mile radius.",
            "— Liftgate delivery with pallet jack assistance for facilities without dedicated loading bays.",
            "— Direct dispatcher communication with real-time GPS tracking and instant electronic PODs.",
            "OUTREACH SEQUENCE 1 (Cold Warehouse Dock Intro):",
            "Subject: Open Tue/Thu liftgate capacity in DFW industrial parks",
            "Hi {{First_Name}}, we run two dedicated 26ft liftgate box trucks through Arlington and Grand Prairie on Tuesday and Thursday mornings. If your primary freight broker ever scrambles to cover regional pallet drops, we keep backup capacity reserved for local industrial shippers. We include a 2-hour free dock window and flat metro zone pricing.",
            "OUTREACH SEQUENCE 2 (Missed Pickup Hot-Shot):",
            "Subject: Backup box-truck capacity for missed DFW dock pickups",
            "Hi {{First_Name}}, checking in because warehouse shipping supervisors usually have 2-3 loads a week where a broker misses an afternoon pickup window. When that happens, your dock gets clogged. We can dispatch a liftgate truck to your facility within 90 minutes.",
            "OUTREACH SEQUENCE 3 (Clear Flat-Rate Structure):",
            "Subject: Flat metro zone rates — Cruz Metro Freight (DFW)",
            "Here is our standard DFW metro rate matrix effective November 1, 2026. Transparent pricing, no surprise detention charges.",
        ],
        role="deliverable",
    )
    files["cruz_freight_rates_card.png"] = write_png_file(
        "cruz_freight_rates_card.png",
        "Cruz Metro Freight — 2026 DFW Metro Rate Card",
        [
            "Metro Core (0–25 miles): $175 Flat / $25 per additional pallet",
            "Outer Metro (25–50 miles): $285 Flat / $35 per additional pallet",
            "Liftgate Service: Included on all scheduled retail drops",
            "Free Dock Detention: 2 full hours included per stop",
            "Same-Day Hotshot Dispatch: $95 rush fee / 90-min response",
            "Direct Dispatcher Hotline: (214) 555-0194",
        ],
        subtitle="Asset-Based Box-Truck & Sprinter Logistics · Dallas-Fort Worth Corridor",
        role="deliverable",
    )

    # =========================================================================
    # 2. Audrey Brown (audreymbrown2007@gmail.com)
    # =========================================================================
    files["audrey_current_site_screenshots.pdf"] = write_pdf_file(
        "audrey_current_site_screenshots.pdf",
        "Studio Brown — Current Squarespace Booking Funnel Audit",
        [
            "Audit capture of current Squarespace homepage and intake flow.",
            "Problem 1: Headline is generic ('Visual storytelling for modern life') with no location context.",
            "Problem 2: Booking button routes to a 14-question form before showing any package rates.",
            "Problem 3: Dropdown selection mixes commercial day rates with personal portrait sessions.",
            "Recommendation: Separate commercial inquiries from studio sessions; cut intake to 5 fields.",
        ],
        role="source",
    )
    files["audrey_homepage_booking_audit.pdf"] = write_pdf_file(
        "audrey_homepage_booking_audit.pdf",
        "Studio Brown — Homepage & Booking Flow Copy Audit Report",
        [
            "EXECUTIVE SUMMARY: Studio Brown's current intake funnel loses 68% of visitors at the intake step.",
            "1. HERO SECTION: Reposition to 'Editorial Portraiture & Commercial Brand Campaigns in Austin'.",
            "2. PRICING ANCHOR: Add starting package rates ($450 / $950 / $2,200) directly on the Services tab.",
            "3. STREAMLINED INTAKE: Reduce 14 fields to 5 essentials: Name, Date, Service Tier, Phone, Concept.",
            "4. EXPECTATIONS CHECKLIST: Add transparent delivery timelines (10 business days) and deposit terms.",
        ],
        role="deliverable",
    )
    files["audrey_wireframe_notes.docx"] = write_docx_file(
        "audrey_wireframe_notes.docx",
        "Studio Brown — 3-Page Wireframe Notes & Sitemap",
        [
            "Page 1: Homepage — Hero headline, portfolio reel, client trust strip, package preview, FAQs.",
            "Page 2: Services & Rates — 3 clearly defined packages (Essential, Studio Session, Campaign).",
            "Page 3: Booking & Availability — 5-field inquiry form, calendar embed, booking policy.",
        ],
        role="source",
    )
    files["audrey_3page_website_copy_v1.docx"] = write_docx_file(
        "audrey_3page_website_copy_v1.docx",
        "Studio Brown — 3-Page Website Copy Deck (v1 Draft)",
        [
            "PAGE 1: HOMEPAGE HERO",
            "Headline: Editorial photography crafted for brands and individuals with distinct vision.",
            "Subhead: Based in East Austin. Natural light studio sessions, on-location campaigns, and brand lookbooks.",
            "PAGE 2: SERVICES TIERS (Starter / Signature / Full Production)",
            "PAGE 3: BOOKING CALENDAR INTAKE & POLICIES",
        ],
        role="draft",
    )
    files["audrey_3page_website_copy_final.docx"] = write_docx_file(
        "audrey_3page_website_copy_final.docx",
        "Studio Brown — 3-Page Website Copy Deck (v2 Final)",
        [
            "PAGE 1: HOMEPAGE (FINAL)",
            "Headline: Editorial portraits & brand campaigns that feel authentic, modern, and enduring.",
            "Subhead: Natural light studio in East Austin. Available for on-location brand commissions worldwide.",
            "Trust Strip: Featured in Austin Monthly, Kinfolk, Rangefinder, and Architectural Digest.",
            "PAGE 2: SERVICES & PACKAGES (FINAL NAMING PER AUDREY)",
            "— Tier 1: Essential Session ($450) · 60 minutes studio time, 15 retouched images, 7-day turnaround.",
            "— Tier 2: Studio Session ($950) · 2.5 hours, 2 wardrobe looks, 35 retouched images, commercial license.",
            "— Tier 3: Full Day Campaign ($2,200) · Full studio + location, creative direction, 75 selects, raw archive.",
            "PAGE 3: BOOKING INTAKE & SCHEDULING (MON–FRI HOURS)",
            "Intake fields: Your Name, Email & Phone, Preferred Shoot Date, Package Selection, Creative Vision.",
            "Policy: 50% retainer secures the studio calendar. Rescheduling permitted with 48 hours notice.",
        ],
        role="deliverable",
    )
    files["audrey_studio_brown_website_prototype.html"] = write_html_file(
        "audrey_studio_brown_website_prototype.html",
        "Studio Brown · East Austin Editorial & Portrait Photography",
        """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Studio Brown · Editorial & Portrait Photography (Austin, TX)</title>
  <style>
    :root {
      --bg: #11100e;
      --card-bg: #1c1a16;
      --border: #33302a;
      --accent: #d4a373;
      --accent-hover: #e3b88c;
      --text: #f7f4ec;
      --text-muted: #a6a092;
      --coral: #cc4b2c;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; }
    header { border-bottom: 1px solid var(--border); padding: 20px 40px; display: flex; justify-content: space-between; align-items: center; background: rgba(17, 16, 14, 0.95); position: sticky; top: 0; z-index: 100; backdrop-filter: blur(10px); }
    .brand { font-size: 20px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: var(--text); }
    .brand span { color: var(--accent); }
    nav { display: flex; gap: 8px; }
    .nav-btn { background: transparent; border: 1px solid transparent; color: var(--text-muted); padding: 8px 18px; border-radius: 20px; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s; }
    .nav-btn:hover { color: var(--text); background: var(--card-bg); }
    .nav-btn.active { color: #fff; background: var(--card-bg); border-color: var(--accent); }
    .container { max-width: 1080px; margin: 0 auto; padding: 50px 24px; }
    .tab-content { display: none; }
    .tab-content.active { display: block; animation: fadeIn 0.3s ease; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
    .hero { text-align: center; padding: 60px 0 40px; max-width: 780px; margin: 0 auto; }
    .badge { display: inline-block; background: rgba(212, 163, 115, 0.15); color: var(--accent); border: 1px solid rgba(212, 163, 115, 0.3); padding: 4px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 20px; }
    .hero h1 { font-size: 42px; line-height: 1.2; font-weight: 700; margin-bottom: 20px; color: #fff; }
    .hero p { font-size: 18px; color: var(--text-muted); margin-bottom: 32px; }
    .btn-group { display: flex; gap: 16px; justify-content: center; }
    .btn-primary { background: var(--accent); color: #11100e; font-weight: 600; padding: 14px 28px; border-radius: 6px; border: none; cursor: pointer; text-decoration: none; font-size: 15px; transition: background 0.2s; }
    .btn-primary:hover { background: var(--accent-hover); }
    .btn-secondary { background: transparent; color: var(--text); border: 1px solid var(--border); font-weight: 600; padding: 14px 28px; border-radius: 6px; cursor: pointer; text-decoration: none; font-size: 15px; }
    .btn-secondary:hover { background: var(--card-bg); border-color: var(--accent); }
    .trust-strip { display: flex; justify-content: center; gap: 40px; padding: 30px 0; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); margin: 50px 0; font-size: 13px; text-transform: uppercase; letter-spacing: 1.5px; color: var(--text-muted); flex-wrap: wrap; }
    .trust-strip strong { color: var(--text); }
    .grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; margin-top: 30px; }
    .pricing-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 32px; display: flex; flex-direction: column; justify-content: space-between; position: relative; }
    .pricing-card.featured { border-color: var(--accent); box-shadow: 0 0 30px rgba(212, 163, 115, 0.12); }
    .featured-badge { position: absolute; top: -12px; right: 24px; background: var(--accent); color: #11100e; font-size: 11px; font-weight: 700; text-transform: uppercase; padding: 3px 10px; border-radius: 12px; letter-spacing: 1px; }
    .card-title { font-size: 22px; font-weight: 700; color: #fff; margin-bottom: 8px; }
    .card-price { font-size: 36px; font-weight: 800; color: var(--accent); margin-bottom: 16px; }
    .card-price span { font-size: 14px; font-weight: 400; color: var(--text-muted); }
    .card-desc { font-size: 14px; color: var(--text-muted); margin-bottom: 24px; min-height: 42px; }
    .features-list { list-style: none; margin-bottom: 30px; }
    .features-list li { font-size: 14px; color: var(--text); padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; align-items: center; gap: 10px; }
    .features-list li::before { content: "✓"; color: var(--accent); font-weight: bold; }
    .form-box { max-width: 640px; margin: 0 auto; background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 40px; }
    .form-group { margin-bottom: 20px; }
    .form-label { display: block; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; color: var(--text); }
    .form-control { width: 100%; background: #11100e; border: 1px solid var(--border); border-radius: 6px; padding: 12px 16px; color: #fff; font-size: 15px; }
    .form-control:focus { outline: none; border-color: var(--accent); }
    .form-note { font-size: 12px; color: var(--text-muted); margin-top: 6px; }
    .alert-box { background: rgba(204, 75, 44, 0.12); border: 1px solid var(--coral); border-radius: 6px; padding: 16px; margin-bottom: 24px; font-size: 13px; color: #f4c2b7; }
    .success-modal { display: none; background: rgba(212, 163, 115, 0.15); border: 1px solid var(--accent); border-radius: 8px; padding: 24px; text-align: center; margin-top: 24px; }
  </style>
</head>
<body>
  <header>
    <div class="brand">Studio <span>Brown</span></div>
    <nav>
      <button class="nav-btn active" onclick="switchTab('home')">Home</button>
      <button class="nav-btn" onclick="switchTab('services')">Services & Packages</button>
      <button class="nav-btn" onclick="switchTab('booking')">Booking & Availability</button>
    </nav>
  </header>
  <div class="container">
    <div id="tab-home" class="tab-content active">
      <section class="hero">
        <span class="badge">East Austin · Natural Light Studio</span>
        <h1>Editorial portraits & brand campaigns that feel authentic, modern, and enduring.</h1>
        <p>Specializing in commercial brand lookbooks, executive editorial profiles, and intimate creative portraiture. Based in Austin with worldwide travel availability.</p>
        <div class="btn-group">
          <button class="btn-primary" onclick="switchTab('booking')">Check Studio Availability</button>
          <button class="btn-secondary" onclick="switchTab('services')">Explore 2026 Rates</button>
        </div>
      </section>
      <div class="trust-strip">
        <span>Featured in <strong>Austin Monthly</strong></span>
        <span>·</span>
        <span><strong>Kinfolk</strong> Magazine</span>
        <span>·</span>
        <span><strong>Rangefinder</strong> Award Winner</span>
        <span>·</span>
        <span><strong>Architectural Digest</strong> Features</span>
      </div>
      <div style="background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 32px; text-align: center;">
        <h3 style="color: #fff; margin-bottom: 12px; font-size: 20px;">The Studio Brown Experience</h3>
        <p style="color: var(--text-muted); max-width: 680px; margin: 0 auto;">"Working with Audrey was the easiest commercial shoot our creative agency had all year. Zero awkward posing, immaculate natural window lighting, and our gallery arrived 3 days ahead of schedule."</p>
        <div style="margin-top: 16px; font-size: 13px; font-weight: 600; color: var(--accent);">— Sarah L., Creative Director, Kinship Goods</div>
      </div>
    </div>
    <div id="tab-services" class="tab-content">
      <div style="text-align: center; max-width: 680px; margin: 0 auto 30px;">
        <span class="badge">Transparent Investment</span>
        <h2 style="font-size: 32px; color: #fff; margin-bottom: 12px;">Curated Session Tiers</h2>
        <p style="color: var(--text-muted);">Every session includes high-resolution master delivery, commercial usage rights, and private online proofing gallery with full print release.</p>
      </div>
      <div class="grid-3">
        <div class="pricing-card">
          <div>
            <div class="card-title">Essential Session</div>
            <div class="card-price">$450 <span>flat</span></div>
            <div class="card-desc">Designed for artists, founders, and professionals who need a tight, editorial portfolio refresh.</div>
            <ul class="features-list">
              <li>60 minutes private studio time</li>
              <li>15 hand-retouched high-res master files</li>
              <li>1 wardrobe look in natural light</li>
              <li>Fast 7-business-day delivery turnaround</li>
              <li>Private online proofing gallery</li>
            </ul>
          </div>
          <button class="btn-secondary" style="width: 100%; text-align: center;" onclick="selectTier('Essential Session ($450)')">Select Essential</button>
        </div>
        <div class="pricing-card featured">
          <span class="featured-badge">Most Popular</span>
          <div>
            <div class="card-title">Studio Session</div>
            <div class="card-price">$950 <span>flat</span></div>
            <div class="card-desc">Our signature comprehensive session for executive portraits, brand lookbooks, and personal editorial narratives.</div>
            <ul class="features-list">
              <li>2.5 hours studio + courtyard space</li>
              <li>35 hand-retouched high-res master files</li>
              <li>Up to 3 wardrobe looks & mood transitions</li>
              <li>Commercial & editorial licensing included</li>
              <li>Priority 5-day delivery turnaround</li>
              <li>Full resolution raw archive access</li>
            </ul>
          </div>
          <button class="btn-primary" style="width: 100%; text-align: center;" onclick="selectTier('Studio Session ($950)')">Select Studio Session</button>
        </div>
        <div class="pricing-card">
          <div>
            <div class="card-title">Full Day Campaign</div>
            <div class="card-price">$2,200 <span>flat</span></div>
            <div class="card-desc">Full commercial production for brand launches, apparel lookbooks, and editorial magazine spreads.</div>
            <ul class="features-list">
              <li>Full 6-hour studio + on-location block</li>
              <li>75 hand-retouched campaign hero selects</li>
              <li>Creative direction & custom moodboarding</li>
              <li>Unlimited wardrobe & product transitions</li>
              <li>Full commercial buyout & billboard license</li>
              <li>Dedicated lighting assistant on set</li>
            </ul>
          </div>
          <button class="btn-secondary" style="width: 100%; text-align: center;" onclick="selectTier('Full Day Campaign ($2,200)')">Select Campaign</button>
        </div>
      </div>
    </div>
    <div id="tab-booking" class="tab-content">
      <div class="form-box">
        <h2 style="font-size: 26px; color: #fff; margin-bottom: 8px; text-align: center;">Reserve Your Session</h2>
        <p style="color: var(--text-muted); font-size: 14px; text-align: center; margin-bottom: 24px;">Complete our streamlined 5-field inquiry to reserve your preferred date on our East Austin studio calendar.</p>
        <div class="alert-box">
          <strong>Studio Policy:</strong> A 50% deposit secures your date on the calendar. Studio sessions run Monday through Friday. Rescheduling permitted with 48 hours advance notice.
        </div>
        <form id="booking-form" onsubmit="handleBookingSubmit(event)">
          <div class="form-group">
            <label class="form-label">Full Legal Name *</label>
            <input type="text" id="b-name" class="form-control" required placeholder="e.g. Clara Henderson">
          </div>
          <div class="form-group">
            <label class="form-label">Email & Direct Phone *</label>
            <input type="text" id="b-contact" class="form-control" required placeholder="name@example.com · (512) 555-0192">
          </div>
          <div class="form-group">
            <label class="form-label">Preferred Session Date *</label>
            <input type="date" id="b-date" class="form-control" required min="2026-11-01">
            <div class="form-note">Studio open Mon–Fri, 9:00 AM – 4:00 PM for optimal natural window light.</div>
          </div>
          <div class="form-group">
            <label class="form-label">Selected Package Tier *</label>
            <select id="b-tier" class="form-control" required>
              <option value="">Select a package tier...</option>
              <option value="Essential Session ($450)">Essential Session ($450)</option>
              <option value="Studio Session ($950)" selected>Studio Session ($950) — Most Popular</option>
              <option value="Full Day Campaign ($2,200)">Full Day Campaign ($2,200)</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Creative Vision & Wardrobe Notes</label>
            <textarea id="b-notes" class="form-control" rows="3" placeholder="Tell us about the vibe, intended usage, and wardrobe concepts..."></textarea>
          </div>
          <button type="submit" class="btn-primary" style="width: 100%; font-size: 16px; padding: 16px;">Confirm Date & Request Retainer Link</button>
        </form>
        <div id="booking-success" class="success-modal">
          <h3 style="color: var(--accent); margin-bottom: 8px;">🎉 Reservation Hold Requested!</h3>
          <p style="color: var(--text); font-size: 14px;" id="success-summary">We have tentatively reserved your date on the East Austin studio calendar. A 50% deposit checkout link will be sent to your email.</p>
          <button class="btn-secondary" style="margin-top: 16px; padding: 8px 18px; font-size: 13px;" onclick="switchTab('home')">Return to Studio Home</button>
        </div>
      </div>
    </div>
  </div>
  <script>
    function switchTab(tabId) {
      document.querySelectorAll('.tab-content').forEach(function(el) { el.classList.remove('active'); });
      document.querySelectorAll('.nav-btn').forEach(function(el) { el.classList.remove('active'); });
      const target = document.getElementById('tab-' + tabId);
      if (target) target.classList.add('active');
      const btns = document.querySelectorAll('.nav-btn');
      if (tabId === 'home') btns[0].classList.add('active');
      if (tabId === 'services') btns[1].classList.add('active');
      if (tabId === 'booking') btns[2].classList.add('active');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    function selectTier(tierName) {
      switchTab('booking');
      const select = document.getElementById('b-tier');
      if (select) select.value = tierName;
    }
    function handleBookingSubmit(e) {
      e.preventDefault();
      const name = document.getElementById('b-name').value;
      const tier = document.getElementById('b-tier').value;
      const date = document.getElementById('b-date').value;
      document.getElementById('booking-form').style.display = 'none';
      const successModal = document.getElementById('booking-success');
      successModal.style.display = 'block';
      document.getElementById('success-summary').textContent =
        "Thank you, " + name + "! Your calendar hold for " + tier + " on " + date + " is created. Retainer deposit link generated.";
    }
  </script>
</body>
</html>""",
        role="deliverable",
    )
    files["audrey_booking_flow_wireframe_diagram.png"] = write_png_file(
        "audrey_booking_flow_wireframe_diagram.png",
        "Studio Brown — Optimized 3-Step Booking Funnel",
        [
            "Step 1: Homepage positioning & transparent package pricing ($450 / $950 / $2,200)",
            "Step 2: Simplified 5-question intake form with automatic date availability check",
            "Step 3: Automated deposit checkout via encrypted Paystack portal & instant calendar invite",
            "Result: Projected 42% reduction in drop-offs and zero unvetted inquiry back-and-forth",
            "Client Handover: Complete Figma wireframe and Squarespace CSS copy deck",
        ],
        subtitle="UX Architecture & Copy Blueprint · Studio Brown East Austin",
        role="deliverable",
    )

    # =========================================================================
    # 3. Keegan Chin (kchin444@gmail.com)
    # =========================================================================
    files["keegan_raw_sku_list.xlsx"] = write_xlsx_file(
        "keegan_raw_sku_list.xlsx",
        "Raw_SKU_Import",
        [
            ["SKU", "Item Description", "Supplier FOB (USD)", "Carton Units", "CBM / Carton", "HTS Code", "Tariff %", "Current Retail"],
            ["KC-101", "Precision Gooseneck Kettle 1.2L Matte Black", 8.40, 12, 0.068, "7323.93.00", "10.9%", 34.00],
            ["KC-102", "Conical Burr Hand Grinder Brushed Aluminum", 14.20, 20, 0.055, "8210.00.00", "3.7%", 58.00],
            ["KC-103", "Micro-Timer Digital Espresso Scale USB-C", 6.15, 30, 0.042, "8423.81.00", "4.5%", 29.00],
            ["KC-104", "Double-Wall Insulated Borosilicate Glasses (2pk)", 3.80, 24, 0.082, "7013.42.00", "6.0%", 24.00],
            ["KC-105", "Ceramic Pour-Over Dripper Size 02 White", 2.90, 36, 0.048, "6911.10.00", "6.5%", 18.00],
            ["KC-106", "Barista Tamping Mat Silicone 8x6", 1.45, 50, 0.035, "3924.10.00", "3.4%", 12.00],
            ["KC-107", "Cold Brew Extraction Pitcher 1.5L Tritan", 5.20, 16, 0.062, "3924.10.00", "3.4%", 28.00],
            ["KC-108", "WDT Espresso Needle Distribution Tool", 2.10, 60, 0.028, "8205.59.00", "3.7%", 16.00],
        ],
        role="source",
    )
    files["keegan_freight_duty_rates.pdf"] = write_pdf_file(
        "keegan_freight_duty_rates.pdf",
        "Trans-Pacific LCL Ocean Freight & Customs Broker Rate Sheet",
        [
            "Port of Origin: Shenzhen / Yantian to Port of Los Angeles (POLA).",
            "Ocean Freight Rate: $185.00 per CBM (includes bunker adjustment and terminal handling).",
            "Port Drayage & Deconsolidation: $140.00 flat entry fee + $18.50 per pallet.",
            "Customs Clearance Broker Fee: $125.00 flat per entry filing.",
            "Tariff Notes: Section 301 List 3 tariffs apply to HTS 7323 stainless items (7.5% additional).",
        ],
        role="source",
    )
    files["keegan_sku_margin_calculator_v1.xlsx"] = write_xlsx_file(
        "keegan_sku_margin_calculator_v1.xlsx",
        "Margin_Calculator_v1",
        [
            ["SKU", "Item Description", "FOB", "Ocean/Unit", "Duty/Unit", "Landed", "Retail", "Margin %", "Reorder Level"],
            ["KC-101", "Precision Kettle", 8.40, 1.05, 0.92, 10.37, 34.00, "69.5%", 180],
            ["KC-102", "Burr Grinder", 14.20, 0.51, 0.53, 15.24, 58.00, "73.7%", 120],
            ["KC-103", "Digital Scale", 6.15, 0.26, 0.28, 6.69, 29.00, "76.9%", 250],
            ["KC-104", "Glass Mugs 2pk", 3.80, 0.63, 0.23, 4.66, 24.00, "80.6%", 300],
        ],
        role="draft",
    )
    files["keegan_sku_margin_calculator_v2_locked.xlsx"] = write_xlsx_file(
        "keegan_sku_margin_calculator_v2_locked.xlsx",
        {
            "Landed_Cost_&_Margin_Model": [
                ["SKU", "Item Description", "Supplier FOB", "Allocated Ocean", "Customs Duty", "Landed Cost", "Wholesale (2.1x)", "MSRP Retail", "Gross Margin", "45-Day Reorder"],
                ["KC-101", "Precision Kettle 1.2L", 8.40, 1.05, 0.92, "=C2+D2+E2", "=F2*2.1", 34.00, "=(H2-F2)/H2", 180],
                ["KC-102", "Burr Hand Grinder", 14.20, 0.51, 0.53, "=C3+D3+E3", "=F3*2.1", 58.00, "=(H3-F3)/H3", 120],
                ["KC-103", "Espresso Scale USB-C", 6.15, 0.26, 0.28, "=C4+D4+E4", "=F4*2.1", 29.00, "=(H4-F4)/H4", 250],
                ["KC-104", "Glass Mug 2pk", 3.80, 0.63, 0.23, "=C5+D5+E5", "=F5*2.1", 24.00, "=(H5-F5)/H5", 300],
                ["KC-105", "Ceramic Dripper 02", 2.90, 0.25, 0.19, "=C6+D6+E6", "=F6*2.1", 18.00, "=(H6-F6)/H6", 220],
                ["KC-106", "Silicone Tamping Mat", 1.45, 0.13, 0.05, "=C7+D7+E7", "=F7*2.1", 12.00, "=(H7-F7)/H7", 400],
                ["KC-107", "Cold Brew Pitcher", 5.20, 0.72, 0.18, "=C8+D8+E8", "=F8*2.1", 28.00, "=(H8-F8)/H8", 150],
                ["KC-108", "WDT Needle Tool", 2.10, 0.09, 0.08, "=C9+D9+E9", "=F9*2.1", 16.00, "=(H9-F9)/H9", 350],
                ["TOTALS / AVG", "Catalog Summary", "=SUM(C2:C9)", "=SUM(D2:D9)", "=SUM(E2:E9)", "=SUM(F2:F9)", "=AVERAGE(G2:G9)", "=SUM(H2:H9)", "=AVERAGE(I2:I9)", "=SUM(J2:J9)"],
            ],
            "Freight_&_Customs_Reference": [
                ["Route / Tariff Code", "Classification Name", "Base Rate (USD)", "Unit Basis", "Notes"],
                ["Yantian to POLA", "Ocean LCL Freight Rate", 185.00, "Per CBM", "Includes BAF and terminal handling"],
                ["HTS 7323.93.00", "Stainless Steel Hollowware", "10.9%", "Ad Valorem", "Includes Section 301 List 3 addition"],
                ["HTS 8210.00.00", "Hand-Operated Mechanical Grinder", "3.7%", "Ad Valorem", "Base duty rate"],
                ["HTS 8423.81.00", "Digital Scale Electronic", "4.5%", "Ad Valorem", "USB-C rechargeable micro-timer"],
                ["POLA Drayage", "Deconsolidation & Transfer", 140.00, "Entry Flat", "Plus $18.50 per pallet handling"],
            ]
        },
        role="deliverable",
    )
    files["keegan_warehouse_sku_handbook.pdf"] = write_pdf_file(
        "keegan_warehouse_sku_handbook.pdf",
        "Warehouse Receiving & Landed Cost Entry SOP — Chin Specialty Goods",
        [
            "SECTION 1: RECEIVING CONTAINERS & LCL PALLETS",
            "1. Inspect ocean bills of lading against supplier pack lists before signing drayage interchange receipts.",
            "2. Count master cartons by SKU code and record broken seal exceptions within 24 hours.",
            "SECTION 2: UPDATING THE SPREADSHEET MODEL",
            "3. Enter invoice totals in cell C2 (Ocean Freight) and C3 (Customs Broker Total).",
            "4. Formulas in columns F through I dynamically distribute landed cost per item based on carton volume.",
            "5. If gross margin falls below 65%, review wholesale multiplier before publishing retail catalog changes.",
        ],
        role="deliverable",
    )

    # =========================================================================
    # 4. Liza Iza (vickyizad@gmail.com)
    # =========================================================================
    files["liza_vendor_packet_draft.docx"] = write_docx_file(
        "liza_vendor_packet_draft.docx",
        "Liza Facilities Maintenance — Vendor Onboarding Notes",
        [
            "Need formal W-9, Certificate of Insurance, and ACH direct deposit forms.",
            "Rate schedule needs commercial pricing for 4-building medical plaza RFP.",
            "Turnaround requirements: 48-hour standard commercial crew vs same-day priority.",
        ],
        role="source",
    )
    files["liza_vendor_packet_clean.pdf"] = write_pdf_file(
        "liza_vendor_packet_clean.pdf",
        "Vendor Onboarding Packet & Compliance Manual — Liza Facility Services",
        [
            "1. VENDOR COMPLIANCE REQUIREMENTS: Valid W-9, $1M General Liability COI naming Liza Facilities LLC.",
            "2. DISPATCH SLA: Priority work orders require on-site crew arrival within 120 minutes of dispatch.",
            "3. BILLING SCHEDULE: Invoices submitted by Friday 5pm clear on Net-15 terms via automated ACH.",
            "4. SAFETY GUIDELINES: OSHA compliant PPE required on all medical and commercial client properties.",
        ],
        role="deliverable",
    )
    files["liza_rate_card_final.xlsx"] = write_xlsx_file(
        "liza_rate_card_final.xlsx",
        "Commercial_Rate_Card",
        [
            ["Service Classification", "Response SLA", "Base Rate (USD)", "Per Sq Ft / Unit", "Weekend / After-Hours"],
            ["Standard Commercial Maintenance", "48 Hours", 450.00, 0.12, 125.00],
            ["High-Frequency Medical Disinfection", "24 Hours", 650.00, 0.18, 175.00],
            ["Emergency Mechanical / HVAC Response", "Same Day (2h)", 850.00, "Custom T&M", 250.00],
            ["Monthly Retainer Contract (4 Visits)", "Scheduled", 1600.00, 0.09, 0.00],
            ["Quarterly Deep Scrub & Floor Polish", "Scheduled", 1250.00, 0.15, 75.00],
        ],
        role="deliverable",
    )
    files["liza_15p_service_proposal_messy.docx"] = write_docx_file(
        "liza_15p_service_proposal_messy.docx",
        "Tampa Bay Medical Plaza RFP Response — 15 Pages (Rough Scramble)",
        [
            "Section 1: Company Profile & Executive Bio (rough unformatted text).",
            "Section 2: Scope of Work for 4 Multi-Tenant Medical Buildings (48,000 sq ft total).",
            "Section 3: Staffing matrix, green chemical certifications, and pricing breakdown.",
        ],
        role="source",
    )
    files["liza_15p_service_proposal_v1.docx"] = write_docx_file(
        "liza_15p_service_proposal_v1.docx",
        "Commercial Facility Maintenance Proposal — Formatted Draft (v1)",
        [
            "Standardized RFP response layout, structured SLA tables, and executive summary for medical plaza review.",
        ],
        role="draft",
    )
    files["liza_15p_service_proposal_final.pdf"] = write_pdf_file(
        "liza_15p_service_proposal_final.pdf",
        "Commercial Facility Maintenance Proposal — Tampa Medical Plaza (v2 Final)",
        [
            "EXECUTIVE SUMMARY: Liza Facility Services delivers commercial-grade sanitation and maintenance across 48,000 sq ft.",
            "SECTION 1: CLINICAL ENVIRONMENT DISINFECTION PROTOCOLS (CDC & OSHA COMPLIANT)",
            "SECTION 2: 4-BUILDING PREVENTIVE MAINTENANCE MATRIX (DAILY, WEEKLY, QUARTERLY)",
            "SECTION 3: CREW DEPLOYMENT & SUPERVISOR ESCALATION CHAIN",
            "SECTION 4: FIXED-FEE COMMERCIAL RATE STRUCTURE & DEDICATED ON-SITE STORAGE",
            "SECTION 5: CLIENT TESTIMONIALS, CERTIFICATE OF INSURANCE, AND AUTHORIZED SIGNATURE BLOCK",
        ],
        role="deliverable",
    )

    # =========================================================================
    # 5. Drako Santa Ana (drako.santaana.glz@gmail.com)
    # =========================================================================
    files["drako_old_resume_2023.pdf"] = write_pdf_file(
        "drako_old_resume_2023.pdf",
        "Drako Santa Ana — Resume (Outdated 2021 Version)",
        [
            "Drako Santa Ana — Material Handler & Forklift Driver.",
            "Sunbelt Distribution (2019–2021): Operated sit-down forklift, unloaded freight trailers.",
            "Note: Missing 3 years as Night Shift Dock Supervisor managing 14 handlers.",
        ],
        role="source",
    )
    files["drako_2024_2026_warehouse_notes.docx"] = write_docx_file(
        "drako_2024_2026_warehouse_notes.docx",
        "Drako's Notes on Actual Work Experience (2022–Present)",
        [
            "Promoted to Night Shift Dock Supervisor in early 2023.",
            "Manage 14 material handlers, 6 reach trucks, 4 order pickers across 120,000 sq ft.",
            "Hit 99.8% shipping accuracy on outbound retail freight for 18 consecutive months.",
            "Zero OSHA recordable injuries across 540 consecutive shifts.",
            "Trained team on new RF barcode scanning system that cut dock turn time by 22 minutes.",
        ],
        role="source",
    )
    files["drako_resume_and_linkedin_v1.docx"] = write_docx_file(
        "drako_resume_and_linkedin_v1.docx",
        "Drako Santa Ana — Operations Supervisor Resume (v1 Draft)",
        [
            "Target Title: Logistics & Warehouse Operations Supervisor.",
            "Executive summary highlighting 14-person shift leadership and 99.8% shipping accuracy.",
        ],
        role="draft",
    )
    files["drako_resume_and_linkedin_final.pdf"] = write_pdf_file(
        "drako_resume_and_linkedin_final.pdf",
        "Drako Santa Ana — Professional Operations Resume & LinkedIn Profile (Final)",
        [
            "DRAKO SANTA ANA · WAREHOUSE & DOCK OPERATIONS SUPERVISOR",
            "PROFESSIONAL PROFILE: Results-driven warehouse operations supervisor with 6+ years of progressive supply chain leadership. Proven track record managing 14-person shifts, optimizing cross-dock pallet turn times, and enforcing strict OSHA safety protocols across 120,000 sq ft distribution facilities.",
            "CORE COMPETENCIES:",
            "— Cross-Dock Logistics & Outbound Freight Scheduling",
            "— WMS Systems (SAP / Manhattan Associates) & RF Barcode Scanning",
            "— Inventory Reconciliation, Cycle Counts, and Pallet Put-Away Optimization",
            "— Team Leadership, Safety Training, and Equipment Certification",
            "EXPERIENCE: Night Shift Operations Supervisor, Sunbelt Distribution (2023–Present)",
            "— Directed nightly cross-dock operations for 30+ regional freight trailers.",
            "— Sustained 99.8% picking and shipping accuracy across 450,000 outbound cases.",
            "— Achieved 540 consecutive shifts with zero OSHA-recordable safety incidents.",
            "LINKEDIN HEADLINE & SUMMARY PACK INCLUDED.",
        ],
        role="deliverable",
    )

    # =========================================================================
    # 6. Estella Williams (estellawilliams06@gmail.com)
    # =========================================================================
    files["estella_october_newsletter_draft.docx"] = write_docx_file(
        "estella_october_newsletter_draft.docx",
        "Estella Williams — Leadership Update Draft (October)",
        [
            "Rough draft of Q3 recap for company all-hands and investor circular.",
            "Needs executive tone, crisp numbers on customer retention, and clear strategic goals.",
        ],
        role="source",
    )
    files["estella_october_newsletter_refined.docx"] = write_docx_file(
        "estella_october_newsletter_refined.docx",
        "Estella Williams — Refined Q3 Leadership Memo (Final)",
        [
            "Polished executive memo with key metrics: 94% gross revenue retention, 18% ARR growth.",
        ],
        role="deliverable",
    )
    files["estella_rough_role_notes.docx"] = write_docx_file(
        "estella_rough_role_notes.docx",
        "Rough Onboarding Notes for 4 Key Operations Hires",
        [
            "Roles: Lead Logistics Dispatcher, Customer Operations Associate, Billing Specialist, Account Exec.",
            "Need 30-60-90 day benchmarks and operational KPIs for each hire.",
        ],
        role="source",
    )
    files["estella_4role_onboarding_sops_v1.docx"] = write_docx_file(
        "estella_4role_onboarding_sops_v1.docx",
        "4-Role Operations Onboarding SOPs (v1 Draft)",
        [
            "Draft onboarding frameworks and 30-60-90 day ramp schedules for all 4 positions.",
        ],
        role="draft",
    )
    files["estella_4role_onboarding_sops_final.pdf"] = write_pdf_file(
        "estella_4role_onboarding_sops_final.pdf",
        "Executive Operations Onboarding SOP Manual (4 Key Roles) — Final",
        [
            "ROLE 1: Lead Logistics Dispatcher — Fleet routing, driver comms, 30-day KPI benchmarks.",
            "ROLE 2: Customer Operations Associate — Escalations, SLA management, ticketing workflows.",
            "ROLE 3: Billing & Accounts Specialist — Invoice generation, payment reconciliations, collections.",
            "ROLE 4: Account Executive — Pipeline qualification, contract negotiation, handoff SOPs.",
        ],
        role="deliverable",
    )
    files["estella_q4_board_deck_rough_bullets.docx"] = write_docx_file(
        "estella_q4_board_deck_rough_bullets.docx",
        "Q4 Board Deck — Unformatted Bullet Dump (40 Pages)",
        [
            "Raw bullets on Q3 financials, ARR expansion, churn breakdown, and 2027 hiring plan.",
            "Need condensed into a powerful 16-slide presentation and 2-page briefing memo.",
        ],
        role="source",
    )
    files["estella_q4_executive_investor_deck_v1.docx"] = write_docx_file(
        "estella_q4_executive_investor_deck_v1.docx",
        "Q4 Board Deck Slide Outline & Speaker Script (v1 Draft)",
        [
            "16-slide narrative outline structured for Series A/B board members.",
        ],
        role="draft",
    )
    files["estella_q4_board_briefing_memo_final.docx"] = write_docx_file(
        "estella_q4_board_briefing_memo_final.docx",
        "Q4 Executive Board Briefing Memo — Estella Williams (Final)",
        [
            "EXECUTIVE BRIEFING: Key milestones from Q3, runway extension, and core strategic priorities for Q4 2026.",
        ],
        role="deliverable",
    )
    files["estella_q4_investor_deck_slide_copy_final.pdf"] = write_pdf_file(
        "estella_q4_investor_deck_slide_copy_final.pdf",
        "Q4 Board Deck — Slide Copy & Executive Visual Layouts",
        [
            "Slide 1: Title & Executive Overview",
            "Slide 2: Q3 Performance Snapshot ($4.2M ARR, 114% Net Expansion)",
            "Slide 3: Customer Retention & Cohort Health",
            "Slide 4: Product Roadmap & Enterprise Features",
            "Slide 5: Unit Economics & CAC Payback Efficiency",
            "Slide 6: 2027 Headcount & Operations Roadmap",
        ],
        role="deliverable",
    )
    # 16-Slide Executive Board & Investor Presentation Deck (.pptx)
    files["estella_q4_executive_investor_deck_final.pptx"] = write_pptx_file(
        "estella_q4_executive_investor_deck_final.pptx",
        "Q4 2026 Executive Investor Update — Estella Williams",
        [
            {"title": "InfiniAI Logistics Platform", "subtitle": "Q4 2026 Executive Investor Update · Board Briefing", "bullets": ["Presented by Estella Williams, Founder & CEO", "Confidential Board of Directors Review · October 2026"]},
            {"title": "Executive Summary & Q3 Highlights", "subtitle": "Accelerating Enterprise Terminal Adoption", "bullets": ["$4.2M Current Annual Recurring Revenue (+18% QoQ expansion)", "114% Net Revenue Retention across mid-market enterprise carrier tier", "Gross margin expanded to 77.2% through automated infrastructure scaling", "Net monthly burn reduced to $94K with 18.2-month cash runway"]},
            {"title": "Financial Trajectory & ARR Bridge", "subtitle": "Q1 2026 Actuals to FY 2027 Projections", "bullets": ["Q1 Actuals: $2.8M ARR across 180 active terminals", "Q2 Actuals: $3.4M ARR with 28 new carrier fleet logos", "Q3 Actuals: $4.2M ARR driven by $420K organic expansion", "Q4 2026 Target: $5.1M ARR (92% visibility on pipeline contracts)", "FY 2027 Plan: $7.8M ARR with positive operating cash flow by Q3"]},
            {"title": "Net Revenue Retention & Cohort Health", "subtitle": "Zero Enterprise Logo Churn Across 6 Consecutive Quarters", "bullets": ["Gross Revenue Retention: 96.4% across all contract vintages", "Net Expansion Rate: 114% driven by dockdoor volume tier upgrades", "Cohort health shows full CAC payback achieved within 7.2 months of go-live", "Average terminal usage increased from 42 trailers/day to 74 trailers/day"]},
            {"title": "Gross Margin & Infrastructure Efficiency", "subtitle": "COGS Optimization Strategy", "bullets": ["Cloud hosting cost per terminal declined from $142 to $84/month", "Automated OCR bill of lading processing cut manual audit labor by 64%", "Gross margin path: 74% (Q1) -> 76% (Q2) -> 77% (Q3) -> 81% (Target FY27)", "Fixed vs variable margin cushion absorbs regional freight volume swings"]},
            {"title": "Unit Economics & Customer Acquisition", "subtitle": "17.5x LTV/CAC Ratio", "bullets": ["Blended Customer Acquisition Cost (CAC): $480 per terminal", "Average Revenue Per Account (ARPU): $507/month ($6,084 annual)", "Customer Lifetime Value (LTV): $8,450 based on 4-year retention curve", "CAC payback period sustained at under 8 months across all sales channels"]},
            {"title": "Product Roadmap & Enterprise Moat", "subtitle": "Core Platform Enhancements", "bullets": ["Live: Geofenced trailer arrival check-in with multilingual driver SMS", "In Pilot: Real-time bi-directional EDI connectors for SAP TMS and Blue Yonder", "Q1 2027: Predictive dock detention warning engine (patent pending)", "Enterprise single sign-on (SSO) and SOC-2 Type II audit report delivered"]},
            {"title": "Mid-Market Logistics Traction", "subtitle": "Asset-Based Carrier Adoption", "bullets": ["65 live freight terminals across Midwest, Texas, and Pacific Northwest", "Key win: Apex Cold Storage expanded from 3 to 14 facilities in Q3", "Average customer detention fee savings: $14,800 per terminal per month", "Frontline dispatcher satisfaction score: 4.9/5 across 840 active operators"]},
            {"title": "Sales Pipeline & Territory Velocity", "subtitle": "Weighted Pipeline of $1.8M ARR", "bullets": ["65 qualified opportunities in active sales evaluation stages", "Average enterprise sales cycle compressed from 64 to 38 days", "Inbound demo conversion rate: 38% from organic search and industry referrals", "Channel partner distribution agreements signed with 2 major TMS consultancies"]},
            {"title": "Security, Governance & Compliance", "subtitle": "Enterprise Trust Infrastructure", "bullets": ["SOC-2 Type II report completed with zero material exceptions", "End-to-end 256-bit AES data encryption in transit and at rest", "Quarterly penetration tests executed by independent third-party auditor", "Automated role-based access control (RBAC) with granular audit logs"]},
            {"title": "Carrier Fleet Tier Economics", "subtitle": "Performance by Fleet Size Category", "bullets": ["Tier 1 (5–20 Trucks): 38 fleets · $750/mo avg · 98% retention", "Tier 2 (21–50 Trucks): 21 fleets · $1,650/mo avg · 118% net expansion", "Tier 3 (50+ Trucks): 6 fleets · $3,200/mo avg · 140% net expansion", "Focus on Tier 2 expansion generates highest net contribution margin"]},
            {"title": "2027 Headcount & Organization Plan", "subtitle": "Targeted Operational Scaling", "bullets": ["Current Headcount: 14 FTEs (Engineering 7, Sales/CS 5, G&A 2)", "Key Q1 Hires: VP of Enterprise Sales, Staff Distributed Systems Engineer", "Operational SOPs finalized for 4 core support & dispatch roles", "Hiring plan gated strictly on achieving $4.8M ARR milestone"]},
            {"title": "Cash Flow & Runway Analysis", "subtitle": "18.2 Months of Cash Runway", "bullets": ["Ending Cash Balance as of Sept 30, 2026: $4.42M", "Average Net Monthly Burn: $94,000 (down from $138,000 in Q1)", "Current runway extends through April 2028 without additional capital", "Optionality to reach cash flow breakeven with 15% ARR growth"]},
            {"title": "Cap Table & Bridge Financing", "subtitle": "Capital Structure Summary", "bullets": ["Founders & Common Stock: 68.4% fully diluted", "Series Seed Investors: 18.2% (SAFE notes converted)", "Unallocated Option Pool: 13.4% reserved for key technical hires", "Bridge Financing: $150K strategic working capital tranche settled Oct 2026"]},
            {"title": "Strategic Priorities for Q1 2027", "subtitle": "Execution Milestones", "bullets": ["Scale enterprise terminal count from 65 to 110 facilities", "Complete SAP PartnerEdge certification for direct marketplace listing", "Launch automated driver detention compensation dispute module", "Target ARR: $5.6M with gross margin surpassing 79%"]},
            {"title": "Board Resolution & Next Steps", "subtitle": "Items for Board Vote", "bullets": ["Approval of 2027 Annual Operating Plan and Gated Headcount Budget", "Authorization of expanded 15% equity incentive pool for engineering leads", "Scheduling of Q1 Board Meeting for Thursday, February 18, 2027", "Direct Contact: Estella Williams (estella@infiniai.online)"]},
        ],
        role="deliverable",
    )
    # Multi-Sheet Financial Projections, Unit Economics & Cap Table (.xlsx)
    files["estella_q4_financial_model.xlsx"] = write_xlsx_file(
        "estella_q4_financial_model.xlsx",
        {
            "ARR_&_P&L_Forecast": [
                ["Financial Metric ($k)", "Q1 2026", "Q2 2026", "Q3 2026", "Q4 2026 (Est)", "FY 2026 Total", "FY 2027 Plan"],
                ["Active Enterprise Terminals", 180, 220, 270, 330, "=D2", 520],
                ["Annual Recurring Revenue (ARR)", 2800, 3400, 4200, 5100, "=D3", 7800],
                ["Gross Subscription Revenue", "=B3/4", "=C3/4", "=D3/4", "=E3/4", "=SUM(B4:E4)", "=G3"],
                ["Cloud Infrastructure COGS", 182, 204, 238, 280, "=SUM(B5:E5)", 380],
                ["Customer Support & Onboarding", 90, 110, 130, 160, "=SUM(B6:E6)", 240],
                ["Total Cost of Goods Sold", "=B5+B6", "=C5+C6", "=D5+D6", "=E5+E6", "=SUM(B7:E7)", "=G5+G6"],
                ["Gross Profit", "=B4-B7", "=C4-C7", "=D4-D7", "=E4-E7", "=SUM(B8:E8)", "=G4-G7"],
                ["Gross Margin %", "=B8/B4", "=C8/C4", "=D8/D4", "=E8/E4", "=F8/F4", "=G8/G4"],
                ["R&D Engineering OpEx", 260, 275, 290, 310, "=SUM(B10:E10)", 420],
                ["Sales & Marketing OpEx", 160, 180, 210, 240, "=SUM(B11:E11)", 350],
                ["General & Administrative OpEx", 85, 90, 95, 105, "=SUM(B12:E12)", 150],
                ["Total Operating Expenses", "=B10+B11+B12", "=C10+C11+C12", "=D10+D11+D12", "=E10+E11+E12", "=SUM(B13:E13)", "=G10+G11+G12"],
                ["Net Operating Income (Burn)", "=B8-B13", "=C8-C13", "=D8-D13", "=E8-E13", "=SUM(B14:E14)", "=G8-G13"],
                ["Ending Cash Balance", 6200, 5500, 4900, 4420, "=E15", 7500],
            ],
            "Unit_Economics": [
                ["KPI Metric", "Q1 Actuals", "Q2 Actuals", "Q3 Actuals", "Q4 Target", "Benchmark Target"],
                ["Customer Acquisition Cost (CAC)", 520.00, 495.00, 480.00, 460.00, 650.00],
                ["Average Revenue Per Unit (ARPU / Mo)", 480.00, 495.00, 507.00, 520.00, 400.00],
                ["Customer Lifetime Value (LTV)", 7200.00, 7800.00, 8450.00, 8900.00, 5500.00],
                ["LTV / CAC Ratio", "=C4/C2", "=D4/D2", "=E4/E2", "=F4/F2", "=G4/G2"],
                ["Net Revenue Retention (NRR)", "108%", "111%", "114%", "116%", "110%"],
                ["CAC Payback Period (Months)", 7.8, 7.5, 7.2, 6.9, 12.0],
            ],
            "Cap_Table_&_Runway": [
                ["Shareholder Entity", "Share Class", "Share Count", "Fully Diluted %", "Investment ($)"],
                ["Estella Williams (Founder & CEO)", "Common", 5472000, "=C2/SUM(C2:C5)", "Sweat Equity"],
                ["Founding Engineering Team", "Common", 1368000, "=C3/SUM(C2:C5)", "Sweat Equity"],
                ["Series Seed Institutional Syndicate", "Preferred Series Seed", 1820000, "=C4/SUM(C2:C5)", 2500000],
                ["Unallocated Employee Option Pool", "Options Reserved", 1340000, "=C5/SUM(C2:C5)", "Pool Reserve"],
                ["Total Fully Diluted Capitalization", "All Classes", "=SUM(C2:C5)", "=SUM(D2:D5)", 2500000],
            ]
        },
        role="deliverable",
    )
    # Complete Board Pack ZIP containing PPTX, XLSX, and DOCX
    files["estella_q4_executive_board_pack.zip"] = write_zip_file(
        "estella_q4_executive_board_pack.zip",
        {
            "Estella_Williams_Q4_Executive_Investor_Deck.pptx": "estella_q4_executive_investor_deck_final.pptx",
            "Estella_Williams_Q4_Financial_Model.xlsx": "estella_q4_financial_model.xlsx",
            "Estella_Williams_Q4_Board_Briefing_Memo.docx": "estella_q4_board_briefing_memo_final.docx",
            "README_BOARD_PACK.txt": "Estella Williams — Q4 Executive Board Package\nIncludes: 16-Slide Board Deck (.pptx), Cap Table & Projections (.xlsx), Briefing Memo (.docx).\nAll assets verified and approved for Q4 Board Review.",
        },
        role="deliverable",
    )

    # =========================================================================
    # 7. Kaylee Cabreros (kayleecabreros@gmail.com)
    # =========================================================================
    files["kaylee_shopify_product_descriptions.xlsx"] = write_xlsx_file(
        "kaylee_shopify_product_descriptions.xlsx",
        "Skincare_Catalog_Copy",
        [
            ["SKU", "Product Name", "Hero Benefit", "Sensory Description", "Full Ingredients", "How to Use Ritual", "Meta Title & Description"],
            ["KC-SK01", "Midnight Botanical Nectar Serum", "Deep Cellular Hydration", "Silky lightweight oil with subtle chamomile and damask rose aroma.", "Jojoba, Rosehip, Squalane, Blue Tansy, Vitamin E", "Warm 3 drops between palms and gently press onto damp skin before bedtime.", "Midnight Botanical Serum | Clean Sensory Skincare"],
            ["KC-SK02", "Ceramide Barrier Restoration Cream", "Lipid Barrier Defense", "Velvety whipped cloud texture that melts instantly without tackiness.", "Ceramides NP/AP/EOP, Colloidal Oat, Niacinamide", "Massage dime-sized amount morning and night after serum application.", "Ceramide Barrier Cream | Calming Daily Moisture"],
            ["KC-SK03", "Exfoliating Fruit Enzyme Glow Polish", "Radiant Pore Refinement", "Gentle micro-crystals infused with fermented papaya and pineapple enzymes.", "Papaya Enzyme, Rice Powder, Aloe Barbadensis, Glycerin", "Use 2x weekly on damp skin. Gently buff in circular motions for 60 seconds.", "Fruit Enzyme Face Polish | Gentle Exfoliating Ritual"],
            ["KC-SK04", "Hydra-Firm Copper Peptide Mist", "Instant Plumping Refresh", "Ultra-fine hydrating dew with botanical minerals and multi-peptides.", "Copper Tripeptide-1, Rose Hydrosol, Hyaluronic Acid", "Mist generously throughout the day over makeup or on clean skin.", "Copper Peptide Hydrating Mist | Dewy Firming Spray"],
        ],
        role="deliverable",
    )
    files["kaylee_welcome_emails_draft.docx"] = write_docx_file(
        "kaylee_welcome_emails_draft.docx",
        "Kaylee Skincare — Welcome Flow Rough Notes",
        [
            "Email 1: Welcome to the brand + 15% discount code.",
            "Email 2: Our botanical sourcing story and founder message.",
            "Email 3: How to build your 3-step morning ritual.",
        ],
        role="source",
    )
    files["kaylee_welcome_emails_final.docx"] = write_docx_file(
        "kaylee_welcome_emails_final.docx",
        "Kaylee Skincare — 4-Part Welcome & Ritual Email Sequence (Final)",
        [
            "EMAIL 1: Welcome to the sanctuary (15% off + rituals guide).",
            "EMAIL 2: Why we cold-press our botanical oils (The story behind the serum).",
            "EMAIL 3: Skin barrier 101: Stop stripping your acid mantle.",
            "EMAIL 4: Join the VIP loyalty circle & exclusive small-batch drops.",
        ],
        role="deliverable",
    )

    # =========================================================================
    # 8. Dennis Kiragu (dkiragu97@gmail.com)
    # =========================================================================
    files["dennis_old_expense_sheet.xlsx"] = write_xlsx_file(
        "dennis_old_expense_sheet.xlsx",
        "Corridor_Expenses_Raw",
        [
            ["Trip Date", "Truck Reg", "Route", "Fuel Expense (KES)", "Toll Gate", "Driver Allowance", "Mileage"],
            ["2026-09-04", "KDC 482B", "Mombasa to Nairobi", 42500, 3200, 5000, 485],
            ["2026-09-08", "KDD 109F", "Nairobi to Eldoret", 36000, 1800, 4500, 310],
            ["2026-09-12", "KDC 482B", "Nairobi to Mombasa", 41200, 3200, 5000, 485],
        ],
        role="source",
    )
    files["dennis_q3_corridor_reconciliation_final.xlsx"] = write_xlsx_file(
        "dennis_q3_corridor_reconciliation_final.xlsx",
        "Corridor_Reconciliation_Q3",
        [
            ["Corridor Segment", "Total Trips", "Total Miles", "Fuel Expense (USD)", "KES Converted", "Toll Surcharges", "Net Margin %"],
            ["Mombasa – Nairobi (Southern Corridor)", 24, 11640, 7840.00, 1019200, 768.00, "28.4%"],
            ["Nairobi – Eldoret – Malaba (Western Corridor)", 18, 5580, 4920.00, 639600, 324.00, "31.2%"],
            ["Nairobi Metro Delivery Shuttle", 45, 3150, 2180.00, 283400, 0.00, "38.6%"],
        ],
        role="deliverable",
    )
    files["dennis_12month_cashflow_tracker_final.xlsx"] = write_xlsx_file(
        "dennis_12month_cashflow_tracker_final.xlsx",
        {
            "12_Month_Cash_Flow": [
                ["Category", "Jan 2026", "Feb 2026", "Mar 2026", "Apr 2026", "May 2026", "Jun 2026", "Jul 2026", "Aug 2026", "Sep 2026", "Oct 2026", "Nov 2026", "Dec 2026", "Full Year Total"],
                ["Gross Freight Revenue (USD)", 28500, 31200, 34800, 32100, 36400, 39500, 42100, 41800, 44200, 46000, 48500, 52000, "=SUM(B2:M2)"],
                ["Diesel Fuel Burn (USD)", 8400, 9100, 10200, 9500, 10800, 11600, 12400, 12200, 12900, 13400, 14200, 15100, "=SUM(B3:M3)"],
                ["Toll & Weighbridge Fees", 1200, 1300, 1450, 1350, 1500, 1650, 1750, 1700, 1850, 1900, 2050, 2200, "=SUM(B4:M4)"],
                ["Driver Allowances & Per Diem", 3200, 3400, 3800, 3500, 4000, 4300, 4600, 4500, 4800, 5000, 5300, 5700, "=SUM(B5:M5)"],
                ["Truck Maintenance & Spares", 2400, 1800, 3100, 2200, 2600, 3400, 2800, 3900, 3100, 2900, 3600, 4100, "=SUM(B6:M6)"],
                ["Total Operating Expense", "=SUM(B3:B6)", "=SUM(C3:C6)", "=SUM(D3:D6)", "=SUM(E3:E6)", "=SUM(F3:F6)", "=SUM(G3:G6)", "=SUM(H3:H6)", "=SUM(I3:I6)", "=SUM(J3:J6)", "=SUM(K3:K6)", "=SUM(L3:L6)", "=SUM(M3:M6)", "=SUM(N3:N6)"],
                ["Net Operating Margin (USD)", "=B2-B7", "=C2-C7", "=D2-D7", "=E2-E7", "=F2-F7", "=G2-G7", "=H2-H7", "=I2-I7", "=J2-J7", "=K2-K7", "=L2-L7", "=M2-M7", "=N2-N7"],
                ["Operating Margin %", "=B8/B2", "=C8/C2", "=D8/D2", "=E8/E2", "=F8/F2", "=G8/G2", "=H8/H2", "=I8/I2", "=J8/J2", "=K8/K2", "=L8/L2", "=M8/M2", "=N8/N2"],
            ],
            "Corridor_Segments": [
                ["Segment", "Round Trips / Mo", "Avg Miles", "Avg KES Fuel / Trip", "Avg Toll KES", "Net Revenue USD"],
                ["Mombasa - Nairobi (Southern)", 18, 608, 42500, 3200, 18400],
                ["Nairobi - Eldoret - Malaba", 12, 480, 36000, 1800, 14200],
                ["Nairobi Metro Shuttles", 35, 120, 8500, 0, 9600],
            ]
        },
        role="deliverable",
    )

    # =========================================================================
    # 9. Alexa Quintero (uzbekquintero@gmail.com)
    # =========================================================================
    files["alexa_pitch_rough_bullets.docx"] = write_docx_file(
        "alexa_pitch_rough_bullets.docx",
        "Alexa Quintero — 10-Slide Pitch Outline & Mentor Feedback",
        [
            "Slide 1: Problem statement — Field service companies waste 14 hrs/week on paper dispatch.",
            "Slide 2: Solution — Automated dispatch & electronic signoff on mobile.",
            "Slide 3: Market Size — $8.2B TAM in North American trade logistics.",
            "Slide 4: Traction — 28 pilot contractors, $14K MRR, zero churn in 90 days.",
            "Mentors say: Sharpen unit economics and customer acquisition playbook.",
        ],
        role="source",
    )
    files["alexa_competitor_rates.xlsx"] = write_xlsx_file(
        "alexa_competitor_rates.xlsx",
        "Competitor_Analysis",
        [
            ["Competitor", "Price / Seat / Mo", "Setup Fee", "Mobile Offline Mode", "Electronic Signatures"],
            ["ServiceTitan", 249.00, 1500.00, "Limited", "Yes"],
            ["Jobber", 99.00, 0.00, "No", "Yes"],
            ["Housecall Pro", 129.00, 0.00, "No", "Yes"],
            ["Our Solution", 79.00, 0.00, "Full Offline", "Instant"],
        ],
        role="source",
    )
    files["alexa_pitch_deck_structure_v1.pdf"] = write_pdf_file(
        "alexa_pitch_deck_structure_v1.pdf",
        "Angel Pitch Deck Architecture (10 Slides) — v1 Review",
        [
            "Slide 1: Executive Title & The 10-Second Hook",
            "Slide 2: The Operational Pain of Disconnected Field Crews",
            "Slide 3: Product Demo: Real-Time Mobile Dispatch & Invoicing",
            "Slide 4: TAM / SAM / SOM ($8.2B North American Service Fleets)",
            "Slide 5: Traction: 28 Paid Pilots, $14.2K MRR, 100% Logo Retention",
        ],
        role="draft",
    )
    # DIVERSE DELIVERABLE: Real OpenXML PPTX presentation
    files["alexa_10slide_investor_pitch.pptx"] = write_pptx_file(
        "alexa_10slide_investor_pitch.pptx",
        "Alexa Quintero — Angel Investor Presentation (10 Slides)",
        [
            {"title": "FieldPulse: Automated Mobile Dispatch for Trade Fleets", "bullets": ["Presented by Alexa Quintero, Founder & CEO", "Targeting the $8.2B North American Trade & Field Services Market"]},
            {"title": "The Problem: Broken Field Communication", "bullets": ["Field technicians spend 2.4 hours daily on manual paper logs", "Dispatchers scramble across phone calls, whiteboards, and text threads", "Lost invoices and uncollected change orders bleed 8% of trade contractor margins"]},
            {"title": "The Solution: Real-Time Mobile Workflows", "bullets": ["One-tap dispatch with GPS turn-by-turn routing", "Offline mobile sign-off with instant photo attachments", "Automated customer invoicing and integrated payment collection"]},
            {"title": "Market Opportunity: $8.2B TAM", "bullets": ["1.2 million independent trade and field service businesses in the US & Canada", "$8.2B Serviceable Available Market across plumbing, electrical, and HVAC fleets", "Initial beachhead: 15,000 plumbing & HVAC fleets with 5-25 service vans"]},
            {"title": "Product Architecture & Moat", "bullets": ["Native offline-first mobile sync engine", "Direct two-way accounting sync into QuickBooks and Xero", "Zero onboarding friction: operational within 24 hours of setup"]},
            {"title": "Traction & Early Unit Economics", "bullets": ["28 paid pilot contractors signed in first 90 days", "$14,200 Monthly Recurring Revenue ($507 average fleet ARPU)", "Zero logo churn since launch with 4.9/5 mobile app rating"]},
            {"title": "Go-To-Market Strategy", "bullets": ["Direct local trade association partnerships and wholesale supplier distributor tie-ins", "Performance SEO focused on state contractor licensing lookup pages", "Low-friction 14-day free trial converting at 38% to paid annual tiers"]},
            {"title": "Competitive Matrix", "bullets": ["Incumbents charge $1,500+ setup fees and require 6-week onboarding cycles", "Legacy tools lack reliable offline caching when technicians work in basements", "FieldPulse delivers 3x faster time-to-value at 50% lower total cost of ownership"]},
            {"title": "Financial Projections (3-Year Target)", "bullets": ["Year 1: 180 Fleets · $1.1M ARR · Gross Margin 82%", "Year 2: 650 Fleets · $3.9M ARR · Cash flow breakeven at Month 18", "Year 3: 2,100 Fleets · $12.8M ARR · 4.2x LTV/CAC ratio"]},
            {"title": "The Ask: $750,000 Pre-Seed Round", "bullets": ["65% dedicated to engineering & offline sync hardening", "25% to initial customer acquisition and trade show sponsorships", "10% working capital and reserve runway"]},
        ],
        role="deliverable",
    )
    files["alexa_unit_economics_model.xlsx"] = write_xlsx_file(
        "alexa_unit_economics_model.xlsx",
        "Unit_Economics",
        [
            ["Metric", "Pilot Actuals", "Month 6 Target", "Month 12 Target", "Industry Benchmark"],
            ["Customer Acquisition Cost (CAC)", 340.00, 420.00, 480.00, 850.00],
            ["Average Revenue Per User (ARPU)", 507.00, 525.00, 550.00, 400.00],
            ["Customer Lifetime Value (LTV)", 6084.00, 7350.00, 8250.00, 4800.00],
            ["LTV / CAC Ratio", "17.9x", "17.5x", "17.2x", "5.6x"],
            ["Payback Period (Months)", 0.67, 0.80, 0.87, 2.10],
        ],
        role="deliverable",
    )

    # =========================================================================
    # 10. Cami Kurtz (cami.kurtz@icloud.com)
    # =========================================================================
    files["cami_raw_call_transcripts_18p.docx"] = write_docx_file(
        "cami_raw_call_transcripts_18p.docx",
        "Raw Leadership Interview Transcripts (18 Pages)",
        [
            "Interview 1: Chief Technology Officer on sprint delivery silos and cross-team bottlenecks.",
            "Interview 2: VP of Product on roadmapping disconnect with regional sales leaders.",
            "Interview 3: VP of People on manager burnout and onboarding retention issues.",
        ],
        role="source",
    )
    files["cami_call_action_sheet_v1.pdf"] = write_pdf_file(
        "cami_call_action_sheet_v1.pdf",
        "Executive Discovery Synthesis & Priority Actions (v1 Draft)",
        [
            "Key Findings: 3 core friction points across leadership tiers.",
            "Proposed 6-week modular executive alignment workshops.",
        ],
        role="draft",
    )
    files["cami_call_action_sheet_final.pdf"] = write_pdf_file(
        "cami_call_action_sheet_final.pdf",
        "Executive Leadership Action Sheet & Workshop Roadmap — Cami Kurtz (Final)",
        [
            "EXECUTIVE SYNTHESIS: Diagnostic findings from 18 pages of C-suite interviews.",
            "THEME 1: ENGINEERING & PRODUCT ALIGNMENT — Transition to quarterly shared OKRs.",
            "THEME 2: SALES FEEDBACK LOOP — Institute bi-weekly roadmap priority forums.",
            "THEME 3: MANAGER RETENTION & BURNOUT — Establish structured peer coaching circles.",
            "RECOMMENDED WORKSHOP SCHEDULE: 4 half-day intensive modular sessions with clear deliverables.",
        ],
        role="deliverable",
    )

    # =========================================================================
    # 11. Victor Mawira / ValdaceAI (valdaceai@gmail.com)
    # =========================================================================
    files["victor_service_page_1_draft.docx"] = write_docx_file(
        "victor_service_page_1_draft.docx",
        "ValdaceAI System Specifications & Calibration Notes",
        [
            "Notes on system prompt temperature, lexical diversity settings, and few-shot calibration.",
        ],
        role="source",
    )
    # DIVERSE DELIVERABLE: Real JSON config blueprint
    files["valdace_ai_tone_calibration_blueprint.json"] = write_json_file(
        "valdace_ai_tone_calibration_blueprint.json",
        {
            "engine": "InfiniAI-Humanizer-v3",
            "version": "3.4.1",
            "timestamp": "2026-09-29T14:28:44Z",
            "parameters": {
                "temperature": 0.72,
                "top_p": 0.89,
                "frequency_penalty": 0.35,
                "presence_penalty": 0.28,
                "lexical_variation_target": 0.68,
                "sentence_length_variance": "high",
            },
            "heuristics": {
                "ban_cliches": ["in today's fast-paced world", "delve into", "testament to", "revolutionize"],
                "allow_idioms": True,
                "human_hesitation_markers": ["honestly", "actually", "to be fair", "let me double check"],
                "active_voice_enforcement": 0.85,
            },
            "calibration_benchmarks": {
                "turnitin_ai_score_max": 0.04,
                "gptzero_ai_score_max": 0.03,
                "copy_leaks_probability": 0.02,
                "readability_flesch_kincaid_grade": 9.4,
            },
        },
        role="deliverable",
    )

    # =========================================================================
    # 12. Azael Orozco (orozcoazael815@gmail.com)
    # =========================================================================
    files["orozco_roofing_rough_notes.docx"] = write_docx_file(
        "orozco_roofing_rough_notes.docx",
        "Azael Roofing — Rough Website Content & Job History",
        [
            "Family owned roofing contractor in McAllen & Brownsville since 2012.",
            "Expanding from shingle repairs to commercial flat roofs (TPO, PVC, and Standing Seam Metal).",
            "Need professional website copy that builds trust with commercial building owners.",
        ],
        role="source",
    )
    files["orozco_site_copy_and_estimate_v1.docx"] = write_docx_file(
        "orozco_site_copy_and_estimate_v1.docx",
        "Orozco Commercial Roofing — Website Copy & Bid Estimate (v1)",
        [
            "Homepage copy, commercial systems overview, and free roof assessment CTA.",
        ],
        role="draft",
    )
    files["orozco_site_copy_and_estimate_final.docx"] = write_docx_file(
        "orozco_site_copy_and_estimate_final.docx",
        "Orozco Commercial & Residential Roofing — Final Copy Deck (v2)",
        [
            "HOMEPAGE: South Texas Commercial Flat Roofing & Storm Restoration Specialists.",
            "SERVICES BREAKDOWN: Single-Ply TPO Membranes, Standing Seam Architectural Metal, Shingle Replacement.",
            "COMMERCIAL WARRANTIES: 20-Year NDL (No Dollar Limit) Manufacturer Backed Warranties.",
            "ESTIMATE INTAKE: Simple 4-step emergency inspection request for commercial facility managers.",
        ],
        role="deliverable",
    )
    files["orozco_estimate_sheet.xlsx"] = write_xlsx_file(
        "orozco_estimate_sheet.xlsx",
        {
            "Commercial_Bid_Estimator": [
                ["Roof Section", "System Type", "Area (Sq Ft)", "Tear-Off ($/Sq)", "Membrane ($/Sq)", "Labor ($/Sq)", "Section Total ($)"],
                ["Main Warehouse Deck", "60-mil TPO Single-Ply", 18500, 85.00, 240.00, 115.00, "=(C2/100)*(D2+E2+F2)"],
                ["Front Office Mansard", "24-Gauge Standing Seam Metal", 3200, 110.00, 385.00, 160.00, "=(C3/100)*(D3+E3+F3)"],
                ["Loading Dock Overhang", "EPDM Ballasted Membrane", 2400, 75.00, 195.00, 95.00, "=(C4/100)*(D4+E4+F4)"],
                ["Total Roof Footprint", "All Commercial Sections", "=SUM(C2:C4)", "=AVERAGE(D2:D4)", "=AVERAGE(E2:E4)", "=AVERAGE(F2:F4)", "=SUM(G2:G4)"],
                ["Sales Tax / Material Surcharge (8.25%)", "", "", "", "", "", "=G5*0.0825"],
                ["Manufacturer 20-Yr NDL Warranty Inspection", "", "", "", "", "", 2850.00],
                ["TOTAL PROPOSED BID PRICE", "Client Firm Fixed Price", "", "", "", "", "=G5+G6+G7"],
            ],
            "Manufacturer_Warranty_Matrix": [
                ["Membrane Thickness", "Manufacturer", "Warranty Term", "Wind Uplift Rating", "Inspection Fee"],
                ["60-mil TPO", "Carlisle SynTec", "20-Year NDL", "FM 1-90 Approved", 1200.00],
                ["80-mil TPO", "Firestone Building Products", "25-Year NDL", "FM 1-120 Approved", 1500.00],
                ["24-Gauge Metal", "Berridge Architectural", "30-Year Finish", "Class 4 Impact", 950.00],
            ]
        },
        role="deliverable",
    )
    files["orozco_roofing_website_prototype.html"] = write_html_file(
        "orozco_roofing_website_prototype.html",
        "Orozco Commercial & Residential Roofing · South Texas",
        """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Orozco Roofing · Commercial Flat Roofs & Storm Restoration</title>
  <style>
    :root {
      --bg: #0f172a;
      --card-bg: #1e293b;
      --border: #334155;
      --accent: #f97316;
      --accent-hover: #ea580c;
      --text: #f8fafc;
      --text-muted: #94a3b8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; }
    header { background: rgba(15, 23, 42, 0.95); border-bottom: 1px solid var(--border); padding: 18px 40px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 100; backdrop-filter: blur(8px); }
    .brand { font-size: 22px; font-weight: 800; letter-spacing: 1px; color: #fff; }
    .brand span { color: var(--accent); }
    nav { display: flex; gap: 8px; }
    .nav-btn { background: transparent; border: 1px solid transparent; color: var(--text-muted); padding: 8px 16px; border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
    .nav-btn:hover { color: #fff; background: var(--card-bg); }
    .nav-btn.active { color: #fff; background: var(--card-bg); border-color: var(--accent); }
    .container { max-width: 1080px; margin: 0 auto; padding: 40px 24px; }
    .tab-content { display: none; }
    .tab-content.active { display: block; animation: fadeIn 0.3s ease; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
    .emergency-bar { background: var(--accent); color: #fff; text-align: center; padding: 10px; font-weight: 700; font-size: 14px; letter-spacing: 0.5px; }
    .hero { text-align: center; padding: 50px 0 30px; }
    .badge { display: inline-block; background: rgba(249, 115, 22, 0.15); color: var(--accent); border: 1px solid rgba(249, 115, 22, 0.3); padding: 4px 14px; border-radius: 20px; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 16px; }
    h1 { font-size: 40px; font-weight: 800; color: #fff; line-height: 1.2; margin-bottom: 16px; }
    .hero p { font-size: 18px; color: var(--text-muted); max-width: 750px; margin: 0 auto 30px; }
    .btn-primary { background: var(--accent); color: #fff; font-weight: 700; padding: 14px 28px; border-radius: 6px; border: none; cursor: pointer; font-size: 15px; text-decoration: none; display: inline-block; }
    .btn-primary:hover { background: var(--accent-hover); }
    .grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; margin-top: 30px; }
    .feature-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 28px; }
    .feature-card h3 { color: #fff; font-size: 20px; margin-bottom: 10px; }
    .calc-box { background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 36px; max-width: 680px; margin: 0 auto; }
    .form-group { margin-bottom: 20px; }
    .form-label { display: block; font-size: 13px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; color: var(--text); }
    .form-control { width: 100%; background: #0f172a; border: 1px solid var(--border); border-radius: 6px; padding: 12px 16px; color: #fff; font-size: 15px; }
    .calc-result { background: rgba(249, 115, 22, 0.1); border: 1px solid var(--accent); border-radius: 8px; padding: 24px; margin-top: 24px; text-align: center; }
  </style>
</head>
<body>
  <div class="emergency-bar">🚨 24/7 Commercial Emergency Roof Dispatch (McAllen & Brownsville): (956) 555-ROOF</div>
  <header>
    <div class="brand">OROZCO <span>ROOFING</span></div>
    <nav>
      <button class="nav-btn active" onclick="switchTab('commercial')">Commercial Systems</button>
      <button class="nav-btn" onclick="switchTab('residential')">Residential</button>
      <button class="nav-btn" onclick="switchTab('calculator')">Instant Bid Calculator</button>
    </nav>
  </header>
  <div class="container">
    <div id="tab-commercial" class="tab-content active">
      <div class="hero">
        <span class="badge">South Texas Certified Commercial Installer</span>
        <h1>Engineered Flat Roof Systems & 20-Year NDL Manufacturer Warranties</h1>
        <p>Specializing in single-ply TPO, EPDM, and architectural standing seam metal roofs for warehouses, distribution centers, and commercial retail plazas across the Rio Grande Valley.</p>
        <button class="btn-primary" onclick="switchTab('calculator')">Calculate Project Estimate</button>
      </div>
      <div class="grid-3">
        <div class="feature-card">
          <h3>Single-Ply TPO Membranes</h3>
          <p style="color: var(--text-muted); font-size: 14px;">60-mil and 80-mil heat-welded thermoplastic polyolefin. Reflects 87% of solar UV radiation, cutting warehouse HVAC cooling loads by up to 28% in South Texas heat.</p>
        </div>
        <div class="feature-card">
          <h3>24-Gauge Standing Seam Metal</h3>
          <p style="color: var(--text-muted); font-size: 14px;">Concealed-fastener architectural metal with Kynar 500 finish. Class 4 hail resistance and engineered to withstand 140+ mph coastal hurricane wind uplift.</p>
        </div>
        <div class="feature-card">
          <h3>20-Year NDL Warranties</h3>
          <p style="color: var(--text-muted); font-size: 14px;">Direct manufacturer backed No Dollar Limit warranties from Carlisle SynTec and Firestone Building Products covering 100% of material and labor.</p>
        </div>
      </div>
    </div>
    <div id="tab-residential" class="tab-content">
      <div class="hero">
        <span class="badge">Residential Storm Restoration</span>
        <h1>South Texas Architectural Shingle & Metal Roof Replacements</h1>
        <p>Comprehensive insurance claim assistance, rapid storm tarping, and complete architectural tear-offs completed in 24 to 48 hours.</p>
      </div>
      <div class="grid-3">
        <div class="feature-card">
          <h3>Wind & Hail Damage Assessments</h3>
          <p style="color: var(--text-muted); font-size: 14px;">Drone aerial imaging and certified hail impact documentation accepted by all major Texas home insurance adjusters.</p>
        </div>
        <div class="feature-card">
          <h3>Lifetime Architectural Shingles</h3>
          <p style="color: var(--text-muted); font-size: 14px;">130 mph wind-rated architectural laminate shingles with Scotchgard algae protection and 50-year manufacturer warranty.</p>
        </div>
        <div class="feature-card">
          <h3>Emergency 2-Hour Tarping</h3>
          <p style="color: var(--text-muted); font-size: 14px;">Immediate weatherproofing response across Hidalgo and Cameron counties following severe Gulf storms.</p>
        </div>
      </div>
    </div>
    <div id="tab-calculator" class="tab-content">
      <div class="calc-box">
        <h2 style="color: #fff; margin-bottom: 8px; text-align: center;">Commercial Roof Estimate Calculator</h2>
        <p style="color: var(--text-muted); font-size: 14px; text-align: center; margin-bottom: 24px;">Generate an instant commercial flat roof budgetary estimate based on your square footage and membrane specification.</p>
        <div class="form-group">
          <label class="form-label">Total Roof Footprint (Square Feet)</label>
          <input type="number" id="sqft" class="form-control" value="18500" step="500" min="1000" oninput="runEstimate()">
        </div>
        <div class="form-group">
          <label class="form-label">Membrane & System Type</label>
          <select id="sys-type" class="form-control" onchange="runEstimate()">
            <option value="4.40">60-mil TPO Single-Ply Membrane ($4.40 / sq ft installed)</option>
            <option value="6.55">24-Gauge Architectural Standing Seam ($6.55 / sq ft installed)</option>
            <option value="3.65">EPDM Ballasted Rubber Membrane ($3.65 / sq ft installed)</option>
            <option value="5.20">80-mil Heavy Duty TPO Membrane ($5.20 / sq ft installed)</option>
          </select>
        </div>
        <div class="calc-result">
          <div style="font-size: 13px; text-transform: uppercase; color: var(--text-muted); letter-spacing: 1px;">Budgetary Project Range</div>
          <div style="font-size: 38px; font-weight: 800; color: var(--accent); margin: 8px 0;" id="est-total">$81,400.00</div>
          <p style="font-size: 13px; color: var(--text-muted);">Includes existing tear-off, 2" polyiso insulation board, membrane, perimeter flashings, and labor.</p>
        </div>
        <button class="btn-primary" style="width: 100%; margin-top: 20px;" onclick="alert('Inspection requested! Our commercial estimator will call within 60 minutes.')">Request Official On-Site Core Sampling & Bid</button>
      </div>
    </div>
  </div>
  <script>
    function switchTab(tabId) {
      document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
      document.getElementById('tab-' + tabId).classList.add('active');
      const btns = document.querySelectorAll('.nav-btn');
      if (tabId === 'commercial') btns[0].classList.add('active');
      if (tabId === 'residential') btns[1].classList.add('active');
      if (tabId === 'calculator') btns[2].classList.add('active');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    function runEstimate() {
      const sqft = parseFloat(document.getElementById('sqft').value) || 0;
      const rate = parseFloat(document.getElementById('sys-type').value) || 4.40;
      const total = sqft * rate;
      document.getElementById('est-total').textContent = '$' + total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
  </script>
</body>
</html>""",
        role="deliverable",
    )

    # =========================================================================
    # 13. Jack Johnson (jackjohnson0533@gmail.com)
    # =========================================================================
    # REALISTIC MULTI-ROW CSV: 65 rows of authentic HubSpot CRM data
    crm_rows = [
        ["Deal ID", "Company Name", "Contact Name", "Stage", "Territory", "MRR (USD)", "Days In Stage", "Lead Source", "Owner"],
    ]
    companies = [
        ("Apex Cold Storage", "Midwest", 3800, "Inbound Demo"),
        ("Vanguard Parts Logistics", "Southeast", 5200, "Outbound SDR"),
        ("Harbor Marine Freight", "West Coast", 2900, "Referral"),
        ("Redwood Distribution", "Northwest", 4100, "Trade Show"),
        ("Prairie Grain Transport", "Central", 3200, "Cold Call"),
        ("Keystone 3PL Solutions", "Northeast", 6400, "Content Download"),
        ("Lone Star Freightways", "Texas", 4800, "Outbound SDR"),
        ("Buckeye Supply Chain", "Midwest", 3500, "Partner"),
        ("Chesapeake Dock Services", "Mid-Atlantic", 2700, "Website Form"),
        ("Cascade Industrial Cargo", "Northwest", 5900, "Outbound SDR"),
    ]
    owners = ["Dave Miller", "Sarah Jenkins", "Marcus Vance", "Elena Rostova"]
    stages = ["Discovery", "Technical Scoping", "Security & Legal Review", "Proposal Sent", "Contract Sent"]
    deal_counter = 101
    for loop in range(6):
        for comp, terr, base_mrr, src in companies:
            stage = stages[(deal_counter * 3) % len(stages)]
            days = 4 + (deal_counter * 7) % 35
            mrr = base_mrr + ((deal_counter % 5) * 250)
            owner = owners[deal_counter % len(owners)]
            crm_rows.append([f"DL-{deal_counter}", f"{comp} #{loop+1}" if loop > 0 else comp, f"Contact {deal_counter}", stage, terr, mrr, days, src, owner])
            deal_counter += 1

    files["johnson_hubspot_export.csv"] = write_csv_file(
        "johnson_hubspot_export.csv",
        crm_rows,
        role="source",
    )
    files["johnson_crm_pipeline_export_clean.csv"] = write_csv_file(
        "johnson_crm_pipeline_export_clean.csv",
        crm_rows,
        role="deliverable",
    )
    files["johnson_crm_pipeline_spec.pdf"] = write_pdf_file(
        "johnson_crm_pipeline_spec.pdf",
        "HubSpot CRM Lead-Routing & Deal Stage Specification — Jack Johnson",
        [
            "1. AUTOMATED TERRITORY ROUTING: Round-robin dispatch based on shipping volume and geographic territory.",
            "2. STAGE DEFINITIONS & EXIT CRITERIA: Explicit requirements to move from Technical Scoping to Proposal.",
            "3. STALE DEAL SLA: Automated alert to sales manager when any deal sits in Discovery > 7 business days.",
            "4. WEIGHTED REVENUE FORECAST: Probability coefficients assigned per milestone.",
        ],
        role="deliverable",
    )
    files["johnson_b2b_site_and_deck_brief.docx"] = write_docx_file(
        "johnson_b2b_site_and_deck_brief.docx",
        "Q4 B2B Website & 12-Slide Enterprise Deck Brief",
        [
            "Target Audience: VP of Logistics and Operations Directors at mid-market 3PLs.",
            "Core Goal: Communicate 38% dock turn time improvement and eliminate dispatch friction.",
        ],
        role="source",
    )
    files["johnson_b2b_deck_and_copy_v1.pdf"] = write_pdf_file(
        "johnson_b2b_deck_and_copy_v1.pdf",
        "B2B Enterprise Deck & 5-Page Website Copy (v1 Draft)",
        [
            "Draft slide deck structure and website messaging for third-party logistics buyers.",
        ],
        role="draft",
    )
    files["johnson_b2b_site_and_deck_final.docx"] = write_docx_file(
        "johnson_b2b_site_and_deck_final.docx",
        "5-Page B2B Website Copy Deck — Final (v2)",
        [
            "PAGE 1: Homepage positioning focused on eliminating dock dead-time.",
            "PAGE 2: Platform features: real-time trailer tracking, automated driver manifests.",
            "PAGE 3: Integrations: turnkey sync with EDI, SAP, and major freight TMS platforms.",
            "PAGE 4: Security & SOC2 Type II compliance disclosure.",
            "PAGE 5: Transparent per-dock transparent pricing matrix.",
        ],
        role="deliverable",
    )
    # DIVERSE DELIVERABLE: Real 12-slide OpenXML PPTX Presentation
    files["johnson_12slide_outbound_enterprise_deck.pptx"] = write_pptx_file(
        "johnson_12slide_outbound_enterprise_deck.pptx",
        "Enterprise Logistics Automation Deck — Jack Johnson (12 Slides)",
        [
            {"title": "DockStream: Intelligent Cross-Dock Logistics", "bullets": ["Presented by Jack Johnson, Co-Founder", "Accelerating Mid-Market 3PL Dock Turn Times"]},
            {"title": "The Hidden Cost of Dock Congestion", "bullets": ["Midwest carriers report 14 hours per week lost waiting on paperwork", "Detention fees cost average distribution hubs $180,000 annually", "Fragmented driver texts and phone calls create dockyard gridlock"]},
            {"title": "The DockStream Platform", "bullets": ["Automated driver check-in via mobile geofence", "Dynamic dock door assignment based on pallet count and liftgate need", "Instant electronic BOL generation and ERP sync"]},
            {"title": "Case Study: Midwest 3PL Pilot Results", "bullets": ["38% reduction in average trailer turnaround time", "14 hours per week saved per dispatcher", "Zero lost paperwork across 18,000 consecutive pallet transfers"]},
            {"title": "Architecture & Enterprise Security", "bullets": ["Cloud-native microservices with 99.99% uptime guarantee", "SOC2 Type II certified with end-to-end 256-bit AES encryption", "Native bi-directional API connectors for SAP, Oracle TMS, and Blue Yonder"]},
            {"title": "Driver Experience & Mobile Simplicity", "bullets": ["Drivers check in via SMS link—no mobile app download required", "Multi-language support (English, Spanish, Polish)", "Digital bill of lading signed on glass in under 30 seconds"]},
            {"title": "Real-Time Facility Operations Dashboard", "bullets": ["Bird's-eye view of all active loading bays", "Predictive demurrage alerts 45 minutes before detention penalties trigger", "Automated shift performance and throughput reports"]},
            {"title": "Customer Testimonial: Apex Cold Logistics", "bullets": ["'DockStream paid for itself in reduced detention claims in month one.'", "- Dave Henderson, Director of Terminal Operations"]},
            {"title": "Deployment Timeline: Live in 14 Days", "bullets": ["Week 1: ERP API credential exchange and dockyard mapping", "Week 2: Frontline dispatcher training and pilot bay rollout", "Day 15: Full facility activation with dedicated implementation engineer"]},
            {"title": "Pricing & Licensing Tiers", "bullets": ["Standard Hub: $1,250/month per terminal (up to 20 bays)", "Enterprise Fleet: $2,800/month with unlimited bays and dedicated SLA", "Volume discounts available for multi-facility operations"]},
            {"title": "Customer ROI Payback Model", "bullets": ["Average terminal saves $14,800/month in prevented detention fees", "Labor efficiency yields additional $6,200/month in dispatcher bandwidth", "Net ROI payback achieved in 21 days from facility go-live"]},
            {"title": "Next Steps: Schedule Your Dockyard Scoping Call", "bullets": ["Visit www.dockstream.io/schedule", "Direct contact: Jack Johnson (jack@dockstream.io)"]},
        ],
        role="deliverable",
    )
    # DIVERSE DELIVERABLE: Standalone Interactive 5-Page B2B Web Prototype
    files["johnson_dockstream_b2b_website_prototype.html"] = write_html_file(
        "johnson_dockstream_b2b_website_prototype.html",
        "DockStream · Intelligent Cross-Dock Logistics Automation",
        """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DockStream · Intelligent Cross-Dock Logistics & Yard Automation</title>
  <style>
    :root {
      --bg: #090d16;
      --surface: #111827;
      --surface-2: #1e293b;
      --border: #334155;
      --primary: #0284c7;
      --primary-light: #38bdf8;
      --accent: #10b981;
      --text: #f8fafc;
      --text-muted: #94a3b8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; }
    header { background: rgba(9, 13, 22, 0.95); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 100; backdrop-filter: blur(8px); }
    .nav-inner { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; }
    .logo { font-size: 22px; font-weight: 800; letter-spacing: -0.5px; color: #fff; display: flex; align-items: center; gap: 8px; }
    .logo span { color: var(--primary-light); }
    .nav-tabs { display: flex; gap: 8px; }
    .nav-btn { background: none; border: none; color: var(--text-muted); font-size: 14px; font-weight: 600; padding: 8px 16px; border-radius: 6px; cursor: pointer; transition: all 0.2s; }
    .nav-btn:hover { color: #fff; background: var(--surface-2); }
    .nav-btn.active { color: #fff; background: var(--primary); }
    .container { max-width: 1120px; margin: 0 auto; padding: 48px 24px; }
    .tab-content { display: none; }
    .tab-content.active { display: block; }
    .hero { text-align: center; max-width: 840px; margin: 0 auto 60px auto; }
    .badge { display: inline-block; background: rgba(2, 132, 199, 0.15); border: 1px solid rgba(56, 189, 248, 0.3); color: var(--primary-light); font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; padding: 4px 14px; border-radius: 20px; margin-bottom: 20px; }
    h1 { font-size: 46px; line-height: 1.15; font-weight: 800; color: #fff; margin-bottom: 20px; }
    .hero p { font-size: 19px; color: var(--text-muted); margin-bottom: 32px; }
    .btn-primary { background: var(--primary); color: #fff; border: none; padding: 14px 28px; border-radius: 8px; font-size: 16px; font-weight: 700; cursor: pointer; transition: background 0.2s; text-decoration: none; display: inline-block; }
    .btn-primary:hover { background: #0369a1; }
    .btn-secondary { background: var(--surface-2); color: #fff; border: 1px solid var(--border); padding: 14px 28px; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; margin-left: 12px; }
    .stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin: 40px 0; }
    .stat-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 24px; text-align: center; }
    .stat-val { font-size: 38px; font-weight: 800; color: var(--primary-light); margin-bottom: 6px; }
    .stat-lbl { font-size: 13px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; }
    .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px; margin-top: 32px; }
    .feature-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 32px; }
    .feature-icon { font-size: 32px; margin-bottom: 16px; }
    .feature-card h3 { color: #fff; font-size: 20px; margin-bottom: 10px; }
    .feature-card p { color: var(--text-muted); font-size: 14px; }
    .pricing-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 32px; margin-top: 40px; }
    .pricing-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 40px; position: relative; }
    .pricing-card.popular { border-color: var(--primary-light); }
    .popular-tag { position: absolute; top: -12px; right: 24px; background: var(--primary); color: #fff; font-size: 11px; font-weight: 700; padding: 2px 10px; border-radius: 10px; text-transform: uppercase; }
    .price-num { font-size: 44px; font-weight: 800; color: #fff; margin: 16px 0; }
    .price-num span { font-size: 16px; color: var(--text-muted); font-weight: 400; }
    .calc-box { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 36px; margin: 40px 0; }
    .calc-slider { width: 100%; margin: 12px 0 24px 0; accent-color: var(--primary-light); }
    .bays-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 24px; }
    .bay-card { background: var(--surface-2); border: 1px solid var(--border); border-radius: 8px; padding: 18px; cursor: pointer; transition: transform 0.15s; }
    .bay-card:hover { transform: translateY(-2px); }
    .bay-tag { display: inline-block; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 4px; text-transform: uppercase; margin-bottom: 8px; }
    .bay-tag.busy { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
    .bay-tag.free { background: rgba(16, 185, 129, 0.2); color: #10b981; }
    .bay-tag.docking { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
    .modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.8); z-index: 200; align-items: center; justify-content: center; }
    .modal-box { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 36px; max-width: 500px; width: 90%; }
  </style>
</head>
<body>
  <header>
    <div class="nav-inner">
      <div class="logo">⚡ DOCK<span>STREAM</span></div>
      <div class="nav-tabs">
        <button class="nav-btn active" onclick="switchTab('home')">Home</button>
        <button class="nav-btn" onclick="switchTab('features')">Platform</button>
        <button class="nav-btn" onclick="switchTab('integrations')">Integrations</button>
        <button class="nav-btn" onclick="switchTab('pricing')">Pricing & ROI</button>
        <button class="nav-btn" onclick="openDemo()">Schedule Demo</button>
      </div>
    </div>
  </header>

  <div class="container">
    <!-- TAB 1: HOME -->
    <div id="tab-home" class="tab-content active">
      <div class="hero">
        <span class="badge">Intelligent Cross-Dock Operations</span>
        <h1>Eliminate Dock Dead-Time & Driver Detention Claims.</h1>
        <p>Automate driver check-in via mobile geofence, dynamically assign loading bays, and sync electronic bills of lading in under 30 seconds.</p>
        <div>
          <button class="btn-primary" onclick="openDemo()">Request Terminal Scoping Call</button>
          <button class="btn-secondary" onclick="switchTab('features')">Explore Features →</button>
        </div>
      </div>

      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-val">38%</div>
          <div class="stat-lbl">Faster Trailer Turn Time</div>
        </div>
        <div class="stat-card">
          <div class="stat-val">14 hrs</div>
          <div class="stat-lbl">Saved Per Dispatcher / Wk</div>
        </div>
        <div class="stat-card">
          <div class="stat-val">$14,800</div>
          <div class="stat-lbl">Avg Monthly Detention Savings</div>
        </div>
        <div class="stat-card">
          <div class="stat-val">14 Days</div>
          <div class="stat-lbl">Turnkey Implementation SLA</div>
        </div>
      </div>

      <h2 style="font-size: 24px; color: #fff; margin-top: 48px; margin-bottom: 8px;">Live Facility Bay Status (Interactive Simulation)</h2>
      <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 20px;">Click any loading bay below to toggle trailer docking status and test automated SMS driver routing.</p>
      
      <div class="bays-grid" id="bay-grid">
        <div class="bay-card" onclick="toggleBay(0)">
          <span class="bay-tag busy" id="tag-0">Unloading</span>
          <h4 style="color:#fff; font-size: 15px;">Bay 01 · Swift #4182</h4>
          <p style="color:var(--text-muted); font-size: 12px; margin-top: 4px;">24 pallets · Ice Cream · Dock Door 1</p>
        </div>
        <div class="bay-card" onclick="toggleBay(1)">
          <span class="bay-tag free" id="tag-1">Available</span>
          <h4 style="color:#fff; font-size: 15px;">Bay 02 · Clean Dock</h4>
          <p style="color:var(--text-muted); font-size: 12px; margin-top: 4px;">Ready for inbound assignment</p>
        </div>
        <div class="bay-card" onclick="toggleBay(2)">
          <span class="bay-tag docking" id="tag-2">Check-in SMS</span>
          <h4 style="color:#fff; font-size: 15px;">Bay 03 · Werner #9102</h4>
          <p style="color:var(--text-muted); font-size: 12px; margin-top: 4px;">Driver arrived at geofence gate</p>
        </div>
        <div class="bay-card" onclick="toggleBay(3)">
          <span class="bay-tag busy" id="tag-3">Staging</span>
          <h4 style="color:#fff; font-size: 15px;">Bay 04 · Knight #1105</h4>
          <p style="color:var(--text-muted); font-size: 12px; margin-top: 4px;">Forklift team active (18 min elapsed)</p>
        </div>
        <div class="bay-card" onclick="toggleBay(4)">
          <span class="bay-tag free" id="tag-4">Available</span>
          <h4 style="color:#fff; font-size: 15px;">Bay 05 · Clean Dock</h4>
          <p style="color:var(--text-muted); font-size: 12px; margin-top: 4px;">Reserved for 2:30 PM Carrier</p>
        </div>
        <div class="bay-card" onclick="toggleBay(5)">
          <span class="bay-tag busy" id="tag-5">BOL Signed</span>
          <h4 style="color:#fff; font-size: 15px;">Bay 06 · Schneider #502</h4>
          <p style="color:var(--text-muted); font-size: 12px; margin-top: 4px;">Trailer released · Bay clearing</p>
        </div>
      </div>
    </div>

    <!-- TAB 2: PLATFORM FEATURES -->
    <div id="tab-features" class="tab-content">
      <div style="text-align: center; max-width: 700px; margin: 0 auto 40px auto;">
        <span class="badge">Core Functionality</span>
        <h2 style="font-size: 36px; color: #fff; margin-bottom: 12px;">Purpose-Built for Mid-Market Cross-Dock Operators</h2>
        <p style="color: var(--text-muted);">Replace paper manifests, radio chatter, and whiteboard tracking with automated digital dispatch.</p>
      </div>

      <div class="feature-grid">
        <div class="feature-card">
          <div class="feature-icon">📲</div>
          <h3>Geofenced Driver Check-In</h3>
          <p>Drivers trigger automatic check-in when entering your facility perimeter. No mobile app download required—drivers receive an SMS link with door assignment and terminal guidelines.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🚪</div>
          <h3>Dynamic Dock Door Assignment</h3>
          <p>Algorithms allocate bays based on trailer temperature class, liftgate requirements, forklift staging proximity, and priority dispatch schedules.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">✍️</div>
          <h3>Sign-on-Glass Electronic BOL</h3>
          <p>Drivers inspect master carton tallies and sign digital bills of lading directly on mobile glass in under 30 seconds. PDFs instantly sync to carrier and ERP records.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">⏱️</div>
          <h3>Predictive Demurrage Warnings</h3>
          <p>Automated visual countdown flags trailers approaching detention windows (45 minutes prior), empowering dispatchers to prioritize at-risk freight.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">📊</div>
          <h3>Shift Throughput Analytics</h3>
          <p>Track turnaround times by carrier, driver, shift supervisor, and commodity type. Export audit-ready compliance logs with one click.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🌐</div>
          <h3>Multilingual Driver Interface</h3>
          <p>Instant SMS localization into English, Spanish, Polish, and Russian ensures seamless communication with long-haul regional freight drivers.</p>
        </div>
      </div>
    </div>

    <!-- TAB 3: INTEGRATIONS -->
    <div id="tab-integrations" class="tab-content">
      <div style="text-align: center; max-width: 700px; margin: 0 auto 40px auto;">
        <span class="badge">Enterprise Connectivity</span>
        <h2 style="font-size: 36px; color: #fff; margin-bottom: 12px;">Connects with Your Existing Tech Stack</h2>
        <p style="color: var(--text-muted);">Bi-directional webhooks and native connectors eliminate dual-entry between yard management and enterprise ERPs.</p>
      </div>

      <div class="feature-grid">
        <div class="feature-card">
          <h3 style="color: var(--primary-light);">SAP TMS & S/4HANA</h3>
          <p>Native IDoc and OData REST integration. Pull incoming manifest schedules and push finalized pallet receipts straight into central inventory.</p>
        </div>
        <div class="feature-card">
          <h3 style="color: var(--primary-light);">Oracle Transportation Mgmt</h3>
          <p>Real-time dock appointment synchronization with shipment milestone updates (EDI 214 and XML freight statuses).</p>
        </div>
        <div class="feature-card">
          <h3 style="color: var(--primary-light);">Blue Yonder (JDA)</h3>
          <p>Automated warehouse door reservation mapping and driver staging queue synchronization.</p>
        </div>
        <div class="feature-card">
          <h3 style="color: var(--primary-light);">Standard EDI 204 / 214 / 210</h3>
          <p>Turnkey electronic data interchange compatibility with certified clearinghouse protocols.</p>
        </div>
        <div class="feature-card">
          <h3 style="color: var(--primary-light);">Manhattan Associates WMS</h3>
          <p>Cross-dock pallet put-away routing and carton exception logging.</p>
        </div>
        <div class="feature-card">
          <h3 style="color: var(--primary-light);">Custom Webhook & REST API</h3>
          <p>Full OpenAPI 3.0 documentation for custom in-house terminal management software.</p>
        </div>
      </div>
    </div>

    <!-- TAB 4: PRICING & ROI CALCULATOR -->
    <div id="tab-pricing" class="tab-content">
      <div style="text-align: center; max-width: 700px; margin: 0 auto 20px auto;">
        <span class="badge">Transparent Terminal Licensing</span>
        <h2 style="font-size: 36px; color: #fff; margin-bottom: 12px;">Simple, Predictable Per-Facility Pricing</h2>
        <p style="color: var(--text-muted);">No per-driver fees. Unlimited trailer transactions and dispatcher logins included.</p>
      </div>

      <div class="calc-box">
        <h3 style="color: #fff; font-size: 22px; margin-bottom: 8px;">Interactive Detention ROI Calculator</h3>
        <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 24px;">Estimate your facility's monthly cost savings with DockStream automated dispatch.</p>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 32px;">
          <div>
            <label style="color:#fff; font-size: 14px; font-weight:600; display:block;">Daily Trailer Inbound Volume: <span id="val-trailers" style="color:var(--primary-light);">45</span> trailers/day</label>
            <input type="range" min="10" max="150" value="45" class="calc-slider" id="slide-trailers" oninput="calcROI()">

            <label style="color:#fff; font-size: 14px; font-weight:600; display:block; margin-top: 16px;">Current Avg Turn Time: <span id="val-dwell" style="color:var(--primary-light);">75</span> minutes</label>
            <input type="range" min="30" max="180" value="75" class="calc-slider" id="slide-dwell" oninput="calcROI()">
          </div>

          <div style="background: var(--surface-2); border: 1px solid var(--border); border-radius: 8px; padding: 24px; text-align: center;">
            <div style="font-size: 13px; text-transform: uppercase; color: var(--text-muted); letter-spacing: 1px;">Estimated Monthly Savings</div>
            <div style="font-size: 42px; font-weight: 800; color: #10b981; margin: 10px 0;" id="roi-savings">$15,390</div>
            <div style="font-size: 13px; color: var(--text-muted);" id="roi-hours">Includes 182 dispatcher hours saved and 74 prevented detention claims.</div>
          </div>
        </div>
      </div>

      <div class="pricing-grid">
        <div class="pricing-card">
          <h3 style="color: #fff; font-size: 22px;">Standard Hub</h3>
          <p style="color: var(--text-muted); font-size: 14px; margin-top: 6px;">For regional distribution terminals managing up to 20 bays.</p>
          <div class="price-num">$1,250 <span>/ month</span></div>
          <ul style="color: var(--text-muted); font-size: 14px; list-style: none; line-height: 2; margin-bottom: 28px;">
            <li>✓ Up to 20 Active Loading Bays</li>
            <li>✓ Unlimited Driver SMS Check-ins</li>
            <li>✓ Digital BOL Generation & PDF Export</li>
            <li>✓ Standard 99.9% Uptime SLA</li>
            <li>✓ Email & Phone Dispatch Support</li>
          </ul>
          <button class="btn-primary" style="width: 100%;" onclick="openDemo()">Select Standard Hub</button>
        </div>

        <div class="pricing-card popular">
          <div class="popular-tag">Most Popular</div>
          <h3 style="color: #fff; font-size: 22px;">Enterprise Fleet</h3>
          <p style="color: var(--text-muted); font-size: 14px; margin-top: 6px;">For high-volume multi-facility 3PL operations requiring custom ERP sync.</p>
          <div class="price-num">$2,800 <span>/ month</span></div>
          <ul style="color: var(--text-muted); font-size: 14px; list-style: none; line-height: 2; margin-bottom: 28px;">
            <li>✓ Unlimited Loading Bays & Terminals</li>
            <li>✓ Bi-directional SAP / Oracle TMS Sync</li>
            <li>✓ Predictive Demurrage Alert Engine</li>
            <li>✓ 99.99% Enterprise Uptime Guarantee</li>
            <li>✓ Dedicated Implementation Engineer</li>
          </ul>
          <button class="btn-primary" style="width: 100%;" onclick="openDemo()">Select Enterprise Fleet</button>
        </div>
      </div>
    </div>
  </div>

  <div id="demo-modal" class="modal">
    <div class="modal-box">
      <h3 style="color: #fff; font-size: 22px; margin-bottom: 8px;">Schedule Dockyard Scoping Call</h3>
      <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 20px;">Book a 20-minute operational review with Jack Johnson, Co-Founder.</p>
      <div style="margin-bottom: 16px;">
        <label style="display:block; color:#fff; font-size:13px; margin-bottom:6px;">Your Name</label>
        <input type="text" value="Jack Johnson" style="width:100%; padding:10px; background:var(--surface-2); border:1px solid var(--border); color:#fff; border-radius:6px;">
      </div>
      <div style="margin-bottom: 16px;">
        <label style="display:block; color:#fff; font-size:13px; margin-bottom:6px;">Terminal Location / Company</label>
        <input type="text" value="Apex Cold Logistics — Midwest Hub" style="width:100%; padding:10px; background:var(--surface-2); border:1px solid var(--border); color:#fff; border-radius:6px;">
      </div>
      <div style="margin-bottom: 24px;">
        <label style="display:block; color:#fff; font-size:13px; margin-bottom:6px;">Work Email</label>
        <input type="email" value="jack@dockstream.io" style="width:100%; padding:10px; background:var(--surface-2); border:1px solid var(--border); color:#fff; border-radius:6px;">
      </div>
      <button class="btn-primary" style="width: 100%;" onclick="submitDemo()">Confirm Scoping Reservation</button>
      <button class="btn-secondary" style="width: 100%; margin: 10px 0 0 0;" onclick="closeDemo()">Close</button>
    </div>
  </div>

  <script>
    function switchTab(tabId) {
      document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
      document.querySelectorAll('.nav-btn').forEach(nb => nb.classList.remove('active'));
      const target = document.getElementById('tab-' + tabId);
      if (target) target.classList.add('active');
      event.target.classList.add('active');
    }
    function calcROI() {
      const trailers = parseInt(document.getElementById('slide-trailers').value);
      const dwell = parseInt(document.getElementById('slide-dwell').value);
      document.getElementById('val-trailers').textContent = trailers;
      document.getElementById('val-dwell').textContent = dwell;

      // 38% dwell time reduction
      const minutesSavedPerTruck = dwell * 0.38;
      const hoursSavedMonthly = Math.round((trailers * 26 * minutesSavedPerTruck) / 60);
      const preventedDetentions = Math.round(trailers * 26 * 0.08); // 8% risk
      const dollarSavings = (preventedDetentions * 150) + (hoursSavedMonthly * 28);
      document.getElementById('roi-savings').textContent = '$' + dollarSavings.toLocaleString();
      document.getElementById('roi-hours').textContent = 'Includes ' + hoursSavedMonthly + ' dispatcher hours saved and ' + preventedDetentions + ' prevented detention claims.';
    }
    const bayStates = [
      { text: 'Unloading', cls: 'busy' },
      { text: 'Available', cls: 'free' },
      { text: 'Check-in SMS', cls: 'docking' }
    ];
    function toggleBay(idx) {
      const tag = document.getElementById('tag-' + idx);
      if (tag.classList.contains('busy')) {
        tag.className = 'bay-tag free';
        tag.textContent = 'Available';
      } else if (tag.classList.contains('free')) {
        tag.className = 'bay-tag docking';
        tag.textContent = 'Docking In';
      } else {
        tag.className = 'bay-tag busy';
        tag.textContent = 'Unloading';
      }
    }
    function openDemo() {
      document.getElementById('demo-modal').style.display = 'flex';
    }
    function closeDemo() {
      document.getElementById('demo-modal').style.display = 'none';
    }
    function submitDemo() {
      alert('Scoping call request submitted! Implementation team will contact within 2 hours.');
      closeDemo();
    }
  </script>
</body>
</html>""",
        role="deliverable",
    )

    # =========================================================================
    # 14. Luca Carollo (lucacaro@hawaii.edu)
    # =========================================================================
    # REALISTIC MULTI-ROW CSV: 50+ lines of bank ledger data
    bank_rows = [
        ["Transaction Date", "Account", "Payee / Merchant", "Category", "Amount (USD)", "Balance (USD)"],
    ]
    vendors = [
        ("Pacific Split-AC Services", "Repairs", -620.00),
        ("Hawaiian Electric (HECO)", "Utilities", -245.50),
        ("Board of Water Supply", "Utilities", -118.20),
        ("Kakaako Lock & Hardware", "Maintenance", -185.00),
        ("Waikiki Banyan HOA", "HOA Assessment", -690.00),
        ("Ala Moana Pacific HOA", "HOA Assessment", -810.00),
        ("Tenant ACH Rent - Unit 4B", "Rental Income", 3400.00),
        ("Tenant ACH Rent - Unit 12A", "Rental Income", 4100.00),
        ("CleanTeam Hawaii", "Turnover Cleaning", -280.00),
        ("Island Pest Solutions", "Preventive Pest", -95.00),
    ]
    cur_bal = 18450.00
    for m in range(7, 10):
        for v_name, cat, amt in vendors:
            cur_bal += amt
            bank_rows.append([f"2026-0{m}-15", "First Hawaiian Business Checking", v_name, cat, f"{amt:.2f}", f"{cur_bal:.2f}"])

    files["luca_q3_raw_bank_export.csv"] = write_csv_file(
        "luca_q3_raw_bank_export.csv",
        bank_rows,
        role="source",
    )
    files["luca_partner_distribution_summary.csv"] = write_csv_file(
        "luca_partner_distribution_summary.csv",
        [
            ["Quarter", "Property", "Gross Income", "Operating Expenses", "HOA & Tax", "Net Cash Flow", "Carollo 50% Share", "Partner 50% Share"],
            ["Q3 2026", "Waikiki Unit 4B", 10200.00, 1680.00, 2070.00, 6450.00, 3225.00, 3225.00],
            ["Q3 2026", "Ala Moana Unit 12A", 12300.00, 2140.00, 2430.00, 7730.00, 3865.00, 3865.00],
            ["Q3 2026", "Total Portfolio", 22500.00, 3820.00, 4500.00, 14180.00, 7090.00, 7090.00],
        ],
        role="deliverable",
    )
    files["luca_august_vendor_receipts.pdf"] = write_pdf_file(
        "luca_august_vendor_receipts.pdf",
        "August Maintenance Receipts — Ala Moana & Waikiki Properties",
        [
            "Invoice 4821 — Pacific Split-AC Service: $620.00 (Unit 12A coil cleaning & refrigerant).",
            "Receipt 9102 — Kakaako Hardware: $185.00 (Unit 4B smart keyless deadbolt).",
            "Receipt 3409 — CleanTeam Hawaii: $280.00 (Deep clean between guest stays).",
        ],
        role="source",
    )
    files["luca_q3_property_ledger_reconciled.xlsx"] = write_xlsx_file(
        "luca_q3_property_ledger_reconciled.xlsx",
        "Q3_Reconciled_Property_P&L",
        [
            ["Month", "Unit", "Gross Rent (USD)", "Maintenance (USD)", "HOA & Dues (USD)", "Utilities (USD)", "Net Operating Income"],
            ["July 2026", "Unit 4B - Waikiki", 3400.00, 185.00, 690.00, 363.70, 2161.30],
            ["July 2026", "Unit 12A - Ala Moana", 4100.00, 0.00, 810.00, 363.70, 2926.30],
            ["August 2026", "Unit 4B - Waikiki", 3400.00, 280.00, 690.00, 363.70, 2066.30],
            ["August 2026", "Unit 12A - Ala Moana", 4100.00, 620.00, 810.00, 363.70, 2306.30],
            ["September 2026", "Unit 4B - Waikiki", 3400.00, 95.00, 690.00, 363.70, 2251.30],
            ["September 2026", "Unit 12A - Ala Moana", 4100.00, 0.00, 810.00, 363.70, 2926.30],
        ],
        role="deliverable",
    )
    files["luca_charter_rates_raw.xlsx"] = write_xlsx_file(
        "luca_charter_rates_raw.xlsx",
        "Charter_Pricing_Notes",
        [
            ["Vessel", "Capacity", "Half-Day (4h)", "Full-Day (8h)", "Sunset Cruise (2.5h)", "Captain & Fuel Fee"],
            ["42ft Sailing Catamaran 'Makani'", 18, 1400.00, 2400.00, 950.00, 350.00],
            ["34ft Sportfisher 'Hoku'", 6, 1100.00, 1950.00, 750.00, 280.00],
        ],
        role="source",
    )
    files["luca_oahu_charter_booking_deck_final.pdf"] = write_pdf_file(
        "luca_oahu_charter_booking_deck_final.pdf",
        "Oahu Catamaran & Sportfishing Private Charters — 2026 Guest Brochure",
        [
            "VESSEL 1: 42ft Luxury Sailing Catamaran — Sunset sails, private turtle canyon snorkeling, catering options.",
            "VESSEL 2: 34ft Deep Sea Sportfisher — Offshore pelagic big game fishing out of Kewalo Basin.",
            "INCLUDED AMENITIES: Coast Guard licensed captain, crew, snorkeling gear, coolers, and reef-safe sunscreen.",
        ],
        role="deliverable",
    )
    files["luca_harbor_seasonal_manifest_v2.xlsx"] = write_xlsx_file(
        "luca_harbor_seasonal_manifest_v2.xlsx",
        "Harbor_Manifest_2026",
        [
            ["Berth #", "Vessel Name", "LOA (ft)", "Beam", "Slip Fee / Mo", "Commercial Permit #", "Expiration Date"],
            ["Slip K-14", "Makani Catamaran", 42, 22.5, 940.00, "DOCARE-OAHU-2026-44", "2027-06-30"],
            ["Slip K-15", "Hoku Sportfisher", 34, 12.0, 720.00, "DOCARE-OAHU-2026-45", "2027-06-30"],
        ],
        role="deliverable",
    )
    # 8-Slide Oahu Catamaran & Sportfishing Guest Presentation Deck (.pptx)
    files["luca_oahu_charter_booking_deck_final.pptx"] = write_pptx_file(
        "luca_oahu_charter_booking_deck_final.pptx",
        "Oahu Catamaran & Sportfishing Private Charters — 2026 Presentation",
        [
            {"title": "Oahu Catamaran & Sportfishing Charters", "subtitle": "2026 Private Charter & Concierge Presentation", "bullets": ["Presented by Luca Carollo, Managing Partner", "Kewalo Basin Harbor, Honolulu, Hawaii"]},
            {"title": "Fleet Overview: Makani & Hoku", "subtitle": "USCG Licensed Captained Vessels out of Kewalo Basin", "bullets": ["42ft Luxury Sailing Catamaran 'Makani' (18 passengers) for coastal sails & snorkeling", "34ft Custom Sportfisher 'Hoku' (6 passengers) for offshore big game fishing", "Full marine electronics, sound systems, shaded cockpits, and private heads"]},
            {"title": "Private Sunset & Turtle Canyon Snorkel Sails", "subtitle": "Makani Catamaran Itinerary", "bullets": ["Daily morning & midday turtle canyon snorkeling excursions with sea turtles & rays", "Complimentary reef-safe sunscreen, premium mask/snorkel gear, and floating loungers", "Iconic Waikiki & Diamond Head golden hour private sunset sails", "BYOB friendly with chilled coolers, ice, and optional island-sourced catering"]},
            {"title": "Deep Sea Offshore Big Game Fishing", "subtitle": "Hoku Sportfisher Itinerary", "bullets": ["Targeting Pacific Blue Marlin, Ahi (Yellowfin Tuna), Mahi-Mahi, and Ono (Wahoo)", "Shimano Tiagra 80W & 130 reels, Penn International tackle, green stick gear", "Half-day (4h), 3/4-day (6h), and full-day (8h) private deep sea charters", "Keep your catch: fresh fish cut and bagged for guests at the dock"]},
            {"title": "Charter Rates & Seasonal Packages", "subtitle": "Transparent Fixed Pricing", "bullets": ["Makani Catamaran: $950 Sunset (2.5h) · $1,400 Half-Day (4h) · $2,400 Full-Day (8h)", "Hoku Sportfisher: $750 Sunset · $1,100 Half-Day (4h) · $1,950 Full-Day (8h)", "Captain, first mate, fuel, and marine harbor fees included", "Custom wedding, corporate team-building, and ash scattering charters available"]},
            {"title": "Guest Safety & Environmental Stewardship", "subtitle": "Coast Guard Inspected & Reef Protected", "bullets": ["USCG Master 100-Ton licensed captains with 15+ years Hawaiian waters experience", "Annual marine safety inspections and comprehensive commercial liability insurance", "100% reef-safe sunscreen policy to protect Oahu's nearshore coral ecosystems", "Strict adherence to NOAA whale watching guidelines during humpback season"]},
            {"title": "Concierge & Hotel Partner Program", "subtitle": "Waikiki Luxury Hotel Concierge Desk Tie-Ins", "bullets": ["Direct concierge booking hotline with priority calendar reservation locks", "Transparent 15% concierge commission paid out on the 1st of each month", "Custom co-branded welcome letters and champagne packages for VIP guests", "Automated booking confirmation and digital waiver sent to guest mobile"]},
            {"title": "Booking & Reservations Hotline", "subtitle": "Kewalo Basin Harbor, Slip K-14 & K-15", "bullets": ["Online: www.oahucharterco.com", "Direct Captain Dispatch: (808) 555-0142", "Email: charters@oahucharterco.com", "Dock Location: 1025 Ala Moana Blvd, Honolulu, HI 96814"]},
        ],
        role="deliverable",
    )
    # Multi-Sheet Partner Cash-Flow & Distribution Waterfall Model (.xlsx)
    files["luca_partner_distribution_waterfall_model.xlsx"] = write_xlsx_file(
        "luca_partner_distribution_waterfall_model.xlsx",
        {
            "Partner_Distribution_Model": [
                ["Property Entity", "Gross Rent (USD)", "Operating Expense", "HOA Dues", "Property Tax", "Net Cash Flow", "Carollo 50% Share", "Partner 50% Share"],
                ["Waikiki Banyan Unit 4B (Q3)", 10200.00, 1680.00, 2070.00, 840.00, "=B2-C2-D2-E2", "=F2*0.5", "=F2*0.5"],
                ["Ala Moana Pacific Unit 12A (Q3)", 12300.00, 2140.00, 2430.00, 1020.00, "=B3-C3-D3-E3", "=F3*0.5", "=F3*0.5"],
                ["Total Portfolio Distribution", "=SUM(B2:B3)", "=SUM(C2:C3)", "=SUM(D2:D3)", "=SUM(E2:E3)", "=SUM(F2:F3)", "=SUM(G2:G3)", "=SUM(H2:H3)"],
            ],
            "12_Month_Cash_Flow_Forecast": [
                ["Month", "Gross Rent", "Maintenance", "HOA & Dues", "Net Cash Flow"],
                ["Month 1", 7500.00, 850.00, 1500.00, "=B2-C2-D2"],
                ["Month 2", 7500.00, 600.00, 1500.00, "=B3-C3-D3"],
                ["Month 3", 7500.00, 920.00, 1500.00, "=B4-C4-D4"],
                ["Full Quarter 1 Total", "=SUM(B2:B4)", "=SUM(C2:C4)", "=SUM(D2:D4)", "=SUM(E2:E4)"],
            ]
        },
        role="deliverable",
    )
    files["luca_spring_bookkeeping_ledger_final.xlsx"] = write_xlsx_file(
        "luca_spring_bookkeeping_ledger_final.xlsx",
        "Spring_Bookkeeping_Summary",
        [
            ["Quarter", "Total Gross Revenue", "Operating Expenses", "Net Profit", "Margin %"],
            ["Q1 2026", 42800.00, 14200.00, 28600.00, "66.8%"],
            ["Q2 2026", 51400.00, 16800.00, 34600.00, "67.3%"],
        ],
        role="deliverable",
    )

    # =========================================================================
    # 15. Lina Rickert (linarickert2514@gmail.com)
    # =========================================================================
    files["lina_summer_campaign_emails_rough.docx"] = write_docx_file(
        "lina_summer_campaign_emails_rough.docx",
        "Lina Rickert — Summer Promo Emails Draft",
        [
            "Email 1: Early summer VIP access to new footwear collection.",
            "Email 2: 48-hour flash sale reminder.",
            "Email 3: Last chance checkout cart abandonment.",
        ],
        role="source",
    )
    files["lina_summer_campaign_emails_v1.docx"] = write_docx_file(
        "lina_summer_campaign_emails_v1.docx",
        "Summer Campaign Retention Sequence (v1 Draft)",
        [
            "Reworked subject lines to boost open rates and tightened call-to-action buttons.",
        ],
        role="draft",
    )
    files["lina_summer_campaign_emails_final.docx"] = write_docx_file(
        "lina_summer_campaign_emails_final.docx",
        "High-Converting Summer Retention Sequence (5 Emails) — Final",
        [
            "EMAIL 1 — Subject: VIP early access: 24 hours before public drop",
            "EMAIL 2 — Subject: The silhouette selling out first (and why)",
            "EMAIL 3 — Subject: Quick styling guide: 3 outfits, 1 pair",
            "EMAIL 4 — Subject: 48 hours left: Your size is still reserved in your bag",
            "EMAIL 5 — Subject: Final call: Summer capsule archive closes at midnight",
        ],
        role="deliverable",
    )
    files["lina_spring_launch_copy_final.docx"] = write_docx_file(
        "lina_spring_launch_copy_final.docx",
        "Spring Footwear Launch Campaign Copy Deck (Final)",
        [
            "Complete launch copy deck including announcement email, SMS alerts, and Instagram story captions.",
        ],
        role="deliverable",
    )

    # =========================================================================
    # 16. Patrick Hyland (patrickhyland04@gmail.com)
    # =========================================================================
    files["patrick_newfoundland_dispatch_raw.xlsx"] = write_xlsx_file(
        "patrick_newfoundland_dispatch_raw.xlsx",
        "Raw_Dispatch_Logs",
        [
            ["Trip #", "Driver", "Route", "Mileage", "Fuel Liters", "Diesel Price/L", "Ferry Surcharge"],
            ["TR-401", "G. O'Brien", "St. John's to Corner Brook", 685, 290, 1.84, 0.00],
            ["TR-402", "M. Walsh", "Corner Brook to Port aux Basques", 220, 95, 1.86, 420.00],
            ["TR-403", "C. Power", "St. John's to Gander", 335, 145, 1.84, 0.00],
        ],
        role="source",
    )
    files["patrick_dispatch_and_fuel_tracker_v1.xlsx"] = write_xlsx_file(
        "patrick_dispatch_and_fuel_tracker_v1.xlsx",
        "Dispatch_Tracker_Draft",
        [
            ["Trip #", "Driver", "Mileage", "Fuel Cost (CAD)", "Driver Payout", "Gross Revenue", "Net Margin"],
            ["TR-401", "G. O'Brien", 685, 533.60, 411.00, 1650.00, "42.8%"],
        ],
        role="draft",
    )
    files["patrick_dispatch_and_fuel_tracker_final.xlsx"] = write_xlsx_file(
        "patrick_dispatch_and_fuel_tracker_final.xlsx",
        "Atlantic_Dispatch_&_Fuel_Model",
        [
            ["Trip #", "Driver", "Origin / Dest", "Mileage (KM)", "Fuel Burn (CAD)", "Marine Atlantic Ferry", "Driver Pay ($0.60/km)", "Client Billing", "Net Profit", "Margin %"],
            ["TR-401", "G. O'Brien", "St. John's → Corner Brook", 685, 533.60, 0.00, "=D2*0.60", 1680.00, "=H2-E2-F2-G2", "=I2/H2"],
            ["TR-402", "M. Walsh", "Corner Brook → Port aux Basques", 220, 176.70, 420.00, "=D3*0.60", 1150.00, "=H3-E3-F3-G3", "=I3/H3"],
            ["TR-403", "C. Power", "St. John's → Gander", 335, 266.80, 0.00, "=D4*0.60", 890.00, "=H4-E4-F4-G4", "=I4/H4"],
            ["TR-404", "G. O'Brien", "Gander → Grand Falls-Windsor", 95, 76.50, 0.00, "=D5*0.60", 380.00, "=H5-E5-F5-G5", "=I5/H5"],
            ["TR-405", "D. Murphy", "Port aux Basques → North Sydney", 180, 144.00, 680.00, "=D6*0.60", 1820.00, "=H6-E6-F6-G6", "=I6/H6"],
            ["TOTALS / AVG", "Atlantic Fleet Summary", "", "=SUM(D2:D6)", "=SUM(E2:E6)", "=SUM(F2:F6)", "=SUM(G2:G6)", "=SUM(H2:H6)", "=SUM(I2:I6)", "=AVERAGE(J2:J6)"],
        ],
        role="deliverable",
    )
    files["patrick_spring_freight_rates_final.xlsx"] = write_xlsx_file(
        "patrick_spring_freight_rates_final.xlsx",
        "Atlantic_Freight_Rates_2026",
        [
            ["Zone", "Destination", "LTL Pallet Rate", "Full Truckload", "Fuel Index Tier"],
            ["Zone 1 (Avalon)", "St. John's Metro", 85.00, 650.00, "Base"],
            ["Zone 2 (Central)", "Gander / Grand Falls", 145.00, 1450.00, "Tier 1 (+4%)"],
            ["Zone 3 (West Coast)", "Corner Brook", 195.00, 2100.00, "Tier 2 (+7%)"],
        ],
        role="deliverable",
    )

    # =========================================================================
    # 17. Carter Lemburg (lemburgcarter@gmail.com)
    # =========================================================================
    files["carter_storefront_launch_notes.docx"] = write_docx_file(
        "carter_storefront_launch_notes.docx",
        "Carter Lemburg — Storefront Launch Notes & Wireframe",
        [
            "DTC hardware product launch: Modular MagSafe desk organizer & wireless charger.",
            "Need launch checklist, polished headline copy, and an interactive prototype preview.",
        ],
        role="source",
    )
    # DIVERSE DELIVERABLE: Standalone Interactive HTML Prototype
    files["carter_landing_page_prototype.html"] = write_html_file(
        "carter_landing_page_prototype.html",
        "ApexDesk · Modular MagSafe Desk Dock & Wireless Charger",
        """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ApexDesk · Precision Modular MagSafe Desk Dock & Wireless Charger</title>
  <style>
    :root {
      --bg: #0c0b09;
      --surface: #171612;
      --surface-2: #24221c;
      --border: #36342e;
      --accent: #cc4b2c;
      --accent-hover: #e05837;
      --text: #f7f4ec;
      --text-muted: #9e998c;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; }
    header { border-bottom: 1px solid var(--border); padding: 18px 40px; display: flex; justify-content: space-between; align-items: center; background: rgba(12, 11, 9, 0.95); position: sticky; top: 0; z-index: 100; backdrop-filter: blur(10px); }
    .logo { font-size: 20px; font-weight: 800; letter-spacing: 1.5px; color: #fff; }
    .logo span { color: var(--accent); }
    .container { max-width: 1080px; margin: 0 auto; padding: 50px 24px; }
    .hero-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 48px; align-items: center; }
    .badge { display: inline-block; background: rgba(204, 75, 44, 0.15); color: var(--accent); border: 1px solid rgba(204, 75, 44, 0.3); padding: 4px 12px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 16px; letter-spacing: 1px; }
    h1 { font-size: 40px; line-height: 1.15; font-weight: 800; color: #fff; margin-bottom: 16px; }
    .lead { font-size: 17px; color: var(--text-muted); margin-bottom: 24px; }
    .price-box { display: flex; align-items: baseline; gap: 12px; margin-bottom: 24px; }
    .current-price { font-size: 42px; font-weight: 800; color: #fff; }
    .original-price { font-size: 20px; text-decoration: line-through; color: var(--text-muted); }
    .save-badge { background: #22c55e; color: #000; font-size: 11px; font-weight: 800; padding: 3px 8px; border-radius: 4px; text-transform: uppercase; }
    .product-visual { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 40px; text-align: center; position: relative; }
    .color-pill { width: 32px; height: 32px; border-radius: 50%; display: inline-block; cursor: pointer; border: 2px solid transparent; }
    .color-pill.active { border-color: var(--accent); transform: scale(1.1); }
    .options-box { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 20px; margin: 20px 0; }
    .option-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .btn-buy { background: var(--accent); color: #fff; width: 100%; border: none; padding: 18px; border-radius: 8px; font-size: 17px; font-weight: 700; cursor: pointer; transition: background 0.2s; }
    .btn-buy:hover { background: var(--accent-hover); }
    .specs-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-top: 60px; }
    .spec-card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 24px; }
    .spec-card strong { color: #fff; display: block; font-size: 15px; margin-bottom: 6px; }
    .spec-card p { color: var(--text-muted); font-size: 13px; }
    .modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.8); z-index: 200; align-items: center; justify-content: center; }
    .modal-box { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 36px; max-width: 480px; width: 90%; text-align: center; }
  </style>
</head>
<body>
  <header>
    <div class="logo">APEX<span>DESK</span></div>
    <div style="font-size: 13px; color: var(--text-muted);">Batch 1 Shipping: Nov 2026</div>
  </header>
  <div class="container">
    <div class="hero-grid">
      <div class="product-visual">
        <div style="font-size: 80px; margin-bottom: 20px;" id="dock-emoji">⚡</div>
        <div style="font-size: 13px; text-transform: uppercase; letter-spacing: 2px; color: var(--text-muted); margin-bottom: 8px;" id="variant-label">Matte Black Edition</div>
        <h3 style="font-size: 24px; color: #fff; margin-bottom: 16px;">ApexDesk Modular 4-in-1 Rail</h3>
        <div style="display: flex; justify-content: center; gap: 16px; margin-top: 20px;">
          <div class="color-pill active" style="background: #181714;" onclick="setColor('black', this)" title="Matte Black"></div>
          <div class="color-pill" style="background: #94a3b8;" onclick="setColor('silver', this)" title="Aerospace Silver"></div>
        </div>
      </div>
      <div>
        <span class="badge">DTC Hardware Pre-Order</span>
        <h1>The last desk dock you will ever need.</h1>
        <p class="lead">Precision CNC-machined aerospace 6063 aluminum with Qi2 15W MagSafe fast charging and modular snap-in magnetic rail architecture.</p>
        
        <div class="price-box">
          <div class="current-price" id="total-price">$129</div>
          <div class="original-price">$179</div>
          <span class="save-badge">Save $50 Early Bird</span>
        </div>

        <div class="options-box">
          <strong style="color: #fff; display: block; font-size: 14px; margin-bottom: 12px;">Customize Modular Accessories:</strong>
          <div class="option-item">
            <label style="font-size: 14px; display: flex; align-items: center; gap: 10px; cursor: pointer;">
              <input type="checkbox" id="opt-rail" checked disabled> CNC Aluminum Base Rail + 15W Phone Puck
            </label>
            <span style="font-size: 13px; color: var(--text-muted);">Included</span>
          </div>
          <div class="option-item">
            <label style="font-size: 14px; display: flex; align-items: center; gap: 10px; cursor: pointer;">
              <input type="checkbox" id="opt-watch" onchange="calcTotal()"> 5W Fast-Charge Apple Watch Magnetic Puck
            </label>
            <span style="font-size: 13px; color: var(--accent);">+$39</span>
          </div>
          <div class="option-item">
            <label style="font-size: 14px; display: flex; align-items: center; gap: 10px; cursor: pointer;">
              <input type="checkbox" id="opt-pods" onchange="calcTotal()"> Wireless AirPods Qi Charging Base
            </label>
            <span style="font-size: 13px; color: var(--accent);">+$29</span>
          </div>
          <div class="option-item">
            <label style="font-size: 14px; display: flex; align-items: center; gap: 10px; cursor: pointer;">
              <input type="checkbox" id="opt-tray" onchange="calcTotal()"> American Walnut Magnetic Pen & Card Tray
            </label>
            <span style="font-size: 13px; color: var(--accent);">+$25</span>
          </div>
        </div>

        <button class="btn-buy" onclick="openCheckout()">Pre-Order ApexDesk — <span id="btn-price">$129</span></button>
        <div style="font-size: 12px; color: var(--text-muted); text-align: center; margin-top: 12px;">30-Day Money Back Guarantee · 2-Year Hardware Replacement Warranty</div>
      </div>
    </div>

    <div class="specs-grid">
      <div class="spec-card">
        <strong>Aerospace Aluminum Chassis</strong>
        <p>Unibody solid block 6063 alloy CNC-milled with bead-blasted satin finish.</p>
      </div>
      <div class="spec-card">
        <strong>Qi2 15W MagSafe Standard</strong>
        <p>Certified fast wireless charging compatible with iPhone 12 through 17 series.</p>
      </div>
      <div class="spec-card">
        <strong>Single Cable Cleanliness</strong>
        <p>One 100W USB-C input on back powers all 4 modular accessories simultaneously.</p>
      </div>
      <div class="spec-card">
        <strong>Thermal Management</strong>
        <p>Passive internal copper heatsink prevents thermal throttling during high-speed charging.</p>
      </div>
    </div>
  </div>

  <div id="checkout-modal" class="modal">
    <div class="modal-box">
      <div style="font-size: 48px; margin-bottom: 12px;">🎉</div>
      <h2 style="color: #fff; margin-bottom: 8px;">Batch 1 Reserved!</h2>
      <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 20px;">Your ApexDesk configuration is locked in at early-bird pricing. Production tracking updates will be emailed to your account.</p>
      <div style="background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 14px; margin-bottom: 20px; font-weight: bold; color: var(--accent);" id="modal-summary">$129 — Matte Black Edition</div>
      <button class="btn-buy" onclick="closeCheckout()">Close Window</button>
    </div>
  </div>

  <script>
    let currentColor = 'Matte Black Edition';
    function setColor(color, el) {
      document.querySelectorAll('.color-pill').forEach(p => p.classList.remove('active'));
      el.classList.add('active');
      if (color === 'silver') {
        currentColor = 'Aerospace Silver Edition';
        document.getElementById('dock-emoji').textContent = '✨';
        document.getElementById('variant-label').textContent = 'Aerospace Silver Edition';
      } else {
        currentColor = 'Matte Black Edition';
        document.getElementById('dock-emoji').textContent = '⚡';
        document.getElementById('variant-label').textContent = 'Matte Black Edition';
      }
    }
    function calcTotal() {
      let base = 129;
      if (document.getElementById('opt-watch').checked) base += 39;
      if (document.getElementById('opt-pods').checked) base += 29;
      if (document.getElementById('opt-tray').checked) base += 25;
      document.getElementById('total-price').textContent = '$' + base;
      document.getElementById('btn-price').textContent = '$' + base;
    }
    function openCheckout() {
      const price = document.getElementById('total-price').textContent;
      document.getElementById('modal-summary').textContent = price + ' · ' + currentColor;
      const modal = document.getElementById('checkout-modal');
      modal.style.display = 'flex';
    }
    function closeCheckout() {
      document.getElementById('checkout-modal').style.display = 'none';
    }
  </script>
</body>
</html>""",
        role="deliverable",
    )
    # DIVERSE DELIVERABLE: Real ZIP pack with prototype files
    files["carter_storefront_assets_and_launch_kit.zip"] = write_zip_file(
        "carter_storefront_assets_and_launch_kit.zip",
        {
            "README_LAUNCH.txt": "Carter Lemburg — ApexDesk Launch Kit\nIncludes: HTML Prototype, CSS Stylesheet, Launch Checklist, Asset Manifest.",
            "launch_checklist.md": "# ApexDesk Storefront Launch Checklist\n\n- [x] Configure Shopify variant SKUs (AD-01 Matte Black, AD-02 Silver)\n- [x] Integrate 15W Qi2 fast-charging compliance badge\n- [x] Set up abandoned cart recovery email trigger (1hr / 24hr)\n- [x] Test Apple Pay and Google Pay express checkout buttons",
            "styles.css": "/* ApexDesk Production CSS */\n:root { --accent: #cc4b2c; --bg: #0c0b09; }\nbody { font-family: -apple-system, sans-serif; background: var(--bg); color: #fff; }",
        },
        role="deliverable",
    )
    files["carter_website_launch_checklist_final.pdf"] = write_pdf_file(
        "carter_website_launch_checklist_final.pdf",
        "Carter Lemburg — Storefront Launch & Performance Checklist (Final)",
        [
            "1. CHECKOUT FUNNEL OPTIMIZATION: One-click express checkout enabled on mobile.",
            "2. TRUST PROOF: 30-Day Money Back Guarantee and 2-Year Warranty badges on product cards.",
            "3. PAGE SPEED METRICS: Compressed WebP asset delivery with under 1.2s First Contentful Paint.",
            "4. EMAIL CAPTURE: 10% VIP reservation popup with exit-intent trigger.",
        ],
        role="deliverable",
    )

    # =========================================================================
    # 18. Issa Cuevas (issabelc207@gmail.com)
    # =========================================================================
    files["cuevas_intake_and_consent_draft_messy.docx"] = write_docx_file(
        "cuevas_intake_and_consent_draft_messy.docx",
        "Cuevas Speech & Language Therapy — Rough Intake Notes (Scramble)",
        [
            "Pediatric clinic in Austin. We do speech therapy, language development, and sensory processing.",
            "Current intake has messy cancellation clause: parents argue over late fees.",
            "HIPAA notice is from 2019 and doesn't mention teletherapy video recording.",
            "Need a strict pediatric clinical agreement with legal guarantor designations.",
        ],
        role="source",
    )
    files["cuevas_pediatric_intake_and_consent_v1.docx"] = write_docx_file(
        "cuevas_pediatric_intake_and_consent_v1.docx",
        "Pediatric Clinical Intake & Consent Agreement (v1 Draft)",
        [
            "Initial draft of master service agreement, clinical terms, and HIPAA consent.",
        ],
        role="draft",
    )
    files["cuevas_pediatric_intake_and_consent_final.docx"] = write_docx_file(
        "cuevas_pediatric_intake_and_consent_final.docx",
        "Master Clinical Intake & Patient Guarantor Agreement — Final (v2)",
        [
            "SECTION 1: CLINICAL DESIGNATION & LEGAL GUARANTOR RESPONSIBILITY",
            "Parents / legal guardians are designated as sole financial guarantors for all scheduled therapy hours.",
            "SECTION 2: ATTENDANCE & RESERVED CLINICAL HOUR POLICY",
            "Unscheduled missed sessions without 24-hour advance written notice are subject to the reserved clinical hour fee of $75.",
            "SECTION 3: OBSERVATION & VIDEO RECORDING AUTHORIZATION",
            "Permits observation mirrors and therapeutic video recording strictly for home exercise demonstrations.",
            "SECTION 4: PROGRESS EVALUATION DISCLAIMER",
            "Progress evaluations are clinical estimates and do not constitute guaranteed medical outcomes.",
        ],
        role="deliverable",
    )
    files["cuevas_parent_communication_templates.docx"] = write_docx_file(
        "cuevas_parent_communication_templates.docx",
        "Cuevas Speech Therapy — Front Desk Parent Communication Scripts",
        [
            "TEMPLATE 1: Welcome & Intake Paperwork Completion Reminder",
            "TEMPLATE 2: Explaining the $75 Reserved Clinical Hour Cancellation Policy with Empathy",
            "TEMPLATE 3: Monthly Superbill Reimbursement Delivery Script (Generated on 1st of each month)",
        ],
        role="deliverable",
    )
    files["cuevas_speech_clinic_service_agreement_final.pdf"] = write_pdf_file(
        "cuevas_speech_clinic_service_agreement_final.pdf",
        "Cuevas Speech & Language Therapy — Master Clinical Agreement (Final Print-Ready)",
        [
            "CUEVAS SPEECH & LANGUAGE THERAPY · AUSTIN, TEXAS",
            "1. MASTER CLINICAL INTAKE AGREEMENT & GUARANTOR ATTESTATION",
            "2. ATTENDANCE, ILLNESS DISCLOSURE, AND $75 RESERVED CLINICAL HOUR POLICY",
            "3. HIPAA DISCLOSURE & CONFIDENTIALITY SAFEGUARDS FOR PEDIATRIC SESSIONS",
            "4. OBSERVATION ROOM, MIRROR, AND CLINICAL VIDEO TRAINING AUTHORIZATION",
            "5. TELEHEALTH CLINICAL CONSENT & HOME PRACTICE EXERCISE PROTOCOLS",
            "6. SUPERBILL GENERATION SCHEDULE (FIRST OF CALENDAR MONTH) & REIMBURSEMENT NOTICE",
            "7. SIGNATURE BLOCK: LEGAL GUARANTOR & CLINICAL DIRECTOR ATTESTATION",
        ],
        role="deliverable",
    )
    # DIVERSE DELIVERABLE: Real ZIP pack containing agreements, templates, and clinical forms
    files["cuevas_pediatric_intake_forms_bundle.zip"] = write_zip_file(
        "cuevas_pediatric_intake_forms_bundle.zip",
        {
            "README_CLINICAL_PACK.txt": "Cuevas Speech & Language Therapy — Complete Clinical Onboarding Pack\nIncludes: Master Agreement (.pdf), Editable Word Decks (.docx), Front Desk Scripts (.docx).",
            "Master_Clinical_Agreement_Final.pdf": "%PDF-1.4\n%Cuevas Speech Clinic Final Clinical Agreement",
            "Parent_Communication_Templates.docx": "Front Desk Scripts: Welcome script, cancellation policy explanation, superbill notice.",
            "Emergency_Medical_Contact_Form.csv": "Field,Requirement,Description\nChild_Full_Name,Required,Full legal name of patient\nDate_of_Birth,Required,MM/DD/YYYY\nPrimary_Physician,Required,Pediatrician office phone and clinic name\nAllergies,Required,Sensory sensitivities or dietary restrictions\nEmergency_Contact_1,Required,Parent/Guarantor phone and relation\nEmergency_Contact_2,Optional,Alternate caregiver authorized for pickup",
        },
        role="deliverable",
    )

    return files


CLIENT_PROFILES = {
    'cruzjose6221@gmail.com': {
        'username': 'jose_cruz',
        'first_name': 'Jose',
        'last_name': 'Cruz',
        'channel': 'Snapchat',
        'subject': 'Dallas Metro Freight — Company Bio & 3 Cold Outreach Emails ($25)',
        'status': 'closed',
        'requests': [
            {
                'key': 'jc_rewrite',
                'reference': 'INF-261018-JC',
                'service_family': 'text-intelligence',
                'service_code': 'text-rewrite',
                'title': 'Company profile and client outreach email rewrite',
                'objective': 'Rewrite a regional freight company bio and three cold outreach email templates.',
                'scope': 'USD 25.00 total split into a USD 1.00 card test invoice and a USD 24.00 balance invoice.',
                'deliverable': 'Rewritten company bio and outreach email sequence (.docx & .pdf).',
                'status': 'delivered',
                'estimate_low': Decimal('25.00'),
                'estimate_high': Decimal('25.00'),
                'created_at': dt_utc(2026, 10, 17, 21, 15, 0),
                'deliverables': [
                    {
                        'title': 'Cruz Metro Freight — Final Bio & Outreach Sequence (v2)',
                        'kind': 'Copy rewrite',
                        'status': 'delivered',
                        'version': 2,
                        'notes': 'Settled Oct 18, 2026 across INV-261018-JC01 ($1.00) and INV-261018-JC02 ($24.00); v2 subject lines delivered Oct 19.',
                    },
                    {
                        'title': 'Cruz Metro Freight — DFW Corridors Rate Card.png',
                        'kind': 'Graphic Asset',
                        'status': 'delivered',
                        'version': 1,
                        'notes': 'High-resolution PNG rate card for logistics clients.',
                    },
                ],
            },
        ],
        'invoices': [
            {
                'key': 'inv_jc_1',
                'number': 'INV-261018-JC01',
                'request_key': 'jc_rewrite',
                'amount_due': Decimal('1.00'),
                'amount_paid': Decimal('1.00'),
                'status': 'paid',
                'description': 'Rewrite & adapt — Initial card test & deposit ($1 of $25 total)',
                'created_at': dt_utc(2026, 10, 18, 19, 40, 0),
                'due_at': dt_utc(2026, 10, 19, 19, 40, 0),
                'tx_refs': [
                    'T676780654455055',
                ],
            },
            {
                'key': 'inv_jc_24',
                'number': 'INV-261018-JC02',
                'request_key': 'jc_rewrite',
                'amount_due': Decimal('24.00'),
                'amount_paid': Decimal('24.00'),
                'status': 'paid',
                'description': 'Rewrite & adapt — Remaining balance for company bio & outreach emails ($24 of $25 total)',
                'created_at': dt_utc(2026, 10, 18, 21, 32, 0),
                'due_at': dt_utc(2026, 10, 19, 21, 32, 0),
                'tx_refs': [
                    'T850856961040908',
                ],
            },
        ],
        'messages': [
            (
                'client',
                dt_utc(2026, 10, 17, 21, 13, 22),
                "hey man, need some help with my company bio and a couple cold emails. freight brokers keep lowballing us on DFW box truck runs and i'm trying to get direct contracts with local distributors. typing this from my cab at a dock in Grand Prairie so excuse any typos lol, but i attached my rough notes. how much to clean this up and make us look like a serious carrier?",
                [
                    'cruz_old_bio_draft.docx',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 10, 17, 21, 28, 40),
                "Hey Jose! Good to connect. You're spot on—shippers right now are starving for reliable asset-based carriers who actually own their trucks, instead of brokers who re-broker and drop freight at the last minute. We can take your rough notes and shape them into a punchy executive capability bio plus 3 cold outreach emails targeting warehouse managers and shipping supervisors across DFW. We'll also design a clean digital rate card graphic you can text straight from your phone. Total package is $25.00 flat.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 18, 19, 27, 14),
                "sounds fair man. i tried paying through the normal checkout earlier this afternoon on my tablet, but chase flagged my debit card because of the processor location i think. do you have a direct link or alternate way to run it?",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 18, 19, 41, 33),
                "No worries at all Jose, regional debit and fuel cards trigger that fraud prompt on new merchant codes all the time. Normally for direct referrals and owner-operators we work with, we generate a direct priority settlement link so you can clear it in one tap via Apple Pay right from your truck cab without filling out standard web forms. Let's do a quick $1.00 card authorization test first so Chase whitelists the account—that way your card doesn't get locked up. Then we'll settle the remaining $24 once you've reviewed the draft preview. Posted the $1 test invoice (INV-261018-JC01)—you can tap this direct link right on your phone: https://paystack.shop/pay/4q5iounn6s",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 18, 19, 43, 19),
                "wait where do i pay? is it the link above or inside the portal?",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 18, 19, 44, 10),
                "Tap that direct link right there: https://paystack.shop/pay/4q5iounn6s. Apple Pay is enabled on it so you can just double-click your phone without digging for your card from the cab.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 18, 19, 45, 28),
                "alright that direct link worked smooth! cleared the $1 test deposit on apple pay. send over the preview when you have it.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 18, 21, 28, 52),
                "Payment registered Jose, thank you! Took about an hour and a half to draft the bio and first 2 emails—attached is the v1 preview. Notice how we lead with 100% on-time DFW metro dispatch and direct driver cell contact so shippers know they aren't dealing with a middleman.",
                [
                    'cruz_bio_and_emails_v1_preview.pdf',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 18, 21, 31, 19),
                "man this reads way better than what i had. can we add a line in email 2 about our liftgates having 3500lb capacity? some of these warehouse managers have heavy palletized machinery and ask about that right away. also ready to pay the $24 balance.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 18, 21, 33, 40),
                "Spot on—calling out 3,500-lb tuck-under liftgate capacity proves you can handle heavy machinery without relying on their dock equipment. I'll get that worked into Email 2 right now. Here's the balance invoice link (INV-261018-JC02) for the remaining $24: https://paystack.shop/pay/4q5iounn6s",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 18, 21, 41, 55),
                "done! cleared the $24 balance on apple pay just now.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 19, 13, 41, 29),
                "Morning Jose! Finished polishing the bio, locked in the 3,500-lb liftgate specs in Email 2, and generated your clean 2026 DFW rate card graphic. Attached both files—hope this helps you lock down those local distributor runs! If you have any fellow owner-operators or carrier friends running box trucks around DFW who need their client pitches or rate cards cleaned up, definitely send them our way!",
                [
                    'cruz_bio_and_outreach_final.docx',
                    'cruz_freight_rates_card.png',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 19, 14, 7, 54),
                "downloaded both. that rate card graphic looks awesome on my phone, already texted it to a shipper in Carrollton. appreciate the quick turnaround man! and for sure, i'll tell the guys at the yard to hit you up.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 19, 14, 18, 22),
                "Appreciate that Jose! Good luck locking in that Carrollton run. Holler if you ever need any more lane sheets or flyers.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 19, 14, 22, 5),
                "will do man, thanks again 🚛",
                [],
            ),
        ],
    },
    'audreymbrown2007@gmail.com': {
        'username': 'audrey_brown',
        'first_name': 'Audrey',
        'last_name': 'Brown',
        'channel': 'Snapchat',
        'subject': 'Studio Brown — Homepage & 3-Page Website Copy Overhaul ($360)',
        'status': 'closed',
        'requests': [
            {
                'key': 'ab_audit',
                'reference': 'INF-260930-AB',
                'service_family': 'communication',
                'service_code': 'communication-audit',
                'title': 'Homepage and booking-flow communication audit',
                'objective': 'Review current homepage messaging, layout friction, and booking funnel copy before rewriting the full site.',
                'scope': 'Page-by-page messaging review and wireframe copy recommendations ($90.00).',
                'deliverable': 'Homepage audit and messaging wireframe.',
                'status': 'delivered',
                'estimate_low': Decimal('90.00'),
                'estimate_high': Decimal('90.00'),
                'created_at': dt_utc(2026, 9, 30, 19, 30, 0),
                'deliverables': [
                    {
                        'title': 'Homepage & Booking-Flow Copy Audit',
                        'kind': 'Communication audit',
                        'status': 'delivered',
                        'version': 1,
                        'notes': 'Settled Sep 30, 2026 (T414467630167869) and delivered Oct 1, 2026.',
                    },
                    {
                        'title': 'Audrey Brown Studio — Booking Flow Wireframe Diagram.png',
                        'kind': 'UX Architecture Diagram',
                        'status': 'delivered',
                        'version': 1,
                        'notes': 'Visual PNG layout diagram of studio booking funnel.',
                    },
                ],
            },
            {
                'key': 'ab_copy',
                'reference': 'INF-261015-AB',
                'service_family': 'communication',
                'service_code': 'communication-copy',
                'title': 'Full three-page website copy package (Home, Services, Booking)',
                'objective': 'Write final conversion copy for the three main website pages based on the approved audit.',
                'scope': 'Three core website pages at USD 90.00 per page (USD 270.00 total).',
                'deliverable': 'Final website copy deck for Home, Services, and Booking pages.',
                'status': 'delivered',
                'estimate_low': Decimal('270.00'),
                'estimate_high': Decimal('270.00'),
                'created_at': dt_utc(2026, 10, 14, 18, 20, 0),
                'deliverables': [
                    {
                        'title': 'Three-Page Website Copy Deck — Final (v2)',
                        'kind': 'Website copy',
                        'status': 'delivered',
                        'version': 2,
                        'notes': 'Settled Oct 17, 2026 via Mastercard Apple Pay (T493259790266047) and delivered Oct 17, 2026.',
                    },
                ],
            },
        ],
        'invoices': [
            {
                'key': 'inv_ab_90',
                'number': 'INV-260930-AB01',
                'request_key': 'ab_audit',
                'amount_due': Decimal('90.00'),
                'amount_paid': Decimal('90.00'),
                'status': 'paid',
                'description': 'Communication audit — Homepage & booking-flow copy audit',
                'created_at': dt_utc(2026, 9, 30, 19, 46, 0),
                'due_at': dt_utc(2026, 10, 2, 19, 46, 0),
                'tx_refs': [
                    'T414467630167869',
                ],
            },
            {
                'key': 'inv_ab_270',
                'number': 'INV-261015-AB02',
                'request_key': 'ab_copy',
                'amount_due': Decimal('270.00'),
                'amount_paid': Decimal('270.00'),
                'status': 'paid',
                'description': 'Website / product copy — Full 3-page website copy package (3 pages @ $90)',
                'created_at': dt_utc(2026, 10, 15, 7, 14, 0),
                'due_at': dt_utc(2026, 10, 18, 7, 14, 0),
                'tx_refs': [
                    'T402797112790778',
                    'T686580774909713',
                    'T437373824312474',
                    'T150064978438039',
                    'T493259790266047',
                ],
            },
        ],
        'messages': [
            (
                'client',
                dt_utc(2026, 9, 30, 19, 27, 34),
                "hey there! hope your week is going well. so... my studio booking page on Squarespace is losing people left and right. visitors hit the home page, click 'book a session', and then immediately bounce because my current intake is like 14 questions long and doesn't even tell them what pricing starts at haha. i attached a couple screenshots of what it looks like right now. can you help me audit what to fix?",
                [
                    'audrey_current_site_screenshots.pdf',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 9, 30, 19, 47, 18),
                "Hi Audrey! Love your photography work—the natural lighting in your portrait portfolio is gorgeous. But you're completely right about the friction: asking 14 questions before showing package rates creates massive drop-off because people feel overwhelmed before they even know if you're in their budget. We can do a deep copy & booking funnel audit for $90.00 flat (invoice INV-260930-AB01). Normally for creative studios referred into our private network, we send a direct priority checkout link so you can tap Apple Pay in two seconds without dealing with standard portal setup: https://paystack.shop/pay/ppiajw3f1-. We'll map out an exact 5-question intake, upfront pricing anchors, and hero section fixes.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 9, 30, 19, 58, 43),
                "oh awesome, that was super fast and easy! just cleared the $90 on Apple Pay with that direct link. excited to see what we can streamline.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 30, 20, 4, 12),
                "Payment confirmed! We'll have the full audit report mapped out for you tomorrow afternoon.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 1, 16, 11, 29),
                "Here is your completed audit report Audrey! It breaks down the exact hero headline repositioning, package pricing anchors, and cuts your intake form from 14 questions down to 5 essentials so clients can book in under two minutes.",
                [
                    'audrey_homepage_booking_audit.pdf',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 2, 11, 13, 52),
                "this audit is brilliant! cutting those 9 redundant form questions is going to save my life. i'm having my designer mock up the new layout next week and then i definitely want you guys to write all 3 pages.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 2, 11, 45, 10),
                "Glad it resonated! Ping us as soon as your designer has the layout notes ready and we'll dive right into the copy.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 14, 22, 39, 41),
                "hey! sorry it took almost two weeks, my designer was backed up with fall wedding shoots. here are the wireframe notes for the 3 pages (Home, Services, and Booking). ready to do the $270 package whenever you can send the invoice.",
                [
                    'audrey_wireframe_notes.docx',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 10, 15, 7, 13, 28),
                "Morning Audrey! Got the wireframe notes—the layout is going to look so elevated. Posted invoice INV-261015-AB02 for the $270 package.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 15, 8, 41, 39),
                "card declined :(",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 15, 8, 42, 55),
                "tried twice on apple pay and once typing it in. is something weird going on with the payment button?",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 15, 8, 48, 22),
                "Hey Audrey! Checked the payment logs—your bank (Citizens National Bank of Texas) is flagging the $270 transaction under their automated merchant fraud filter. Totally routine with regional debit cards. We have a direct verified payment link on Paystack that bypasses the generic browser filter and supports Apple Pay: https://paystack.shop/pay/ppiajw3f1-",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 15, 9, 11, 47),
                "Wait, why a separate link? Is that safe? I usually only put card details directly through the main site portal, I get a little nervous paying through external links.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 15, 9, 19, 14),
                "Totally understand being cautious Audrey, you're 100% right to double-check! That's our direct hosted store on Paystack (our payment processor), so your transaction is fully encrypted with 256-bit SSL, has standard buyer protection, and supports Apple Pay without exposing your card numbers. It routes straight to our verified business settlement account and logs right onto your invoice here.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 15, 9, 26, 8),
                "Oh okay, that makes total sense then! Thanks for explaining, was just being careful.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 15, 9, 27, 30),
                "Going to use that link later today once I get back from a client shoot.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 15, 19, 25, 10),
                "Called my bank on the way back from a golden hour shoot—they removed the flag on their end. Heading home now.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 16, 15, 17, 33),
                "Sounds great! While that clears, here is v1 of the 3-page website copy deck so you and your designer can review the messaging over the weekend.",
                [
                    'audrey_3page_website_copy_v1.docx',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 17, 1, 5, 20),
                "paid!",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 17, 1, 7, 44),
                "okay the payment went through on that link with my mastercard just now, super easy. we read through v1—could we rename the 3 tiers on the Services page to 'Essential', 'Studio Session', and 'Full Day Campaign', and take out the note about weekend calls on the Booking page?",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 17, 14, 21, 19),
                "Payment confirmed, thank you Audrey! I updated the three package names on the Services page and switched the Booking page hours to Mon–Fri only. Attached is your final Word copy deck, the standalone interactive HTML website prototype you can open and test directly in your browser, and the UX wireframe diagram. Hope the launch goes amazingly with your designer! By the way, we grow almost entirely through word of mouth from creative studios—if you have friends with photography, design, or local healthcare practices who are losing bookings on their websites, send them our way and we'll take great care of them.",
                [
                    'audrey_3page_website_copy_final.docx',
                    'audrey_studio_brown_website_prototype.html',
                    'audrey_booking_flow_wireframe_diagram.png',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 17, 17, 11, 52),
                "Sent it straight to my designer!",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 17, 17, 14, 25),
                "And 1000% yes—actually one of my close friends runs a pediatric speech therapy clinic here in Austin (Issa Cuevas) and her clinic intake is driving her nuts. I literally just texted her your link. Thank you guys so much for being so patient with the payment questions and turning around such beautiful copy!",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 17, 17, 28, 40),
                "You're wonderful Audrey, thank you! Tell Issa to reach out whenever and we'll take great care of her. Definitely drop the live link in here once your designer launches the new pages!",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 17, 17, 35, 12),
                "Will do! Have a great weekend 😊",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 19, 16, 42, 8),
                "hey!! designer just pushed the new home and booking pages live on squarespace and the bounce rate already dropped by half. thank you guys so much again!",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 19, 17, 5, 30),
                "That is incredible news Audrey! The layout and pricing clarity look gorgeous live. Cheering on your fall wedding and portrait season!",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 19, 17, 12, 15),
                "Couldn't have done it without you guys! 🎉",
                [],
            ),
        ],
    },
    'orozcoazael815@gmail.com': {
        'username': 'azael_orozco',
        'first_name': 'Azael',
        'last_name': 'Orozco',
        'channel': 'Direct site',
        'subject': 'Commercial Flat Roofing Website Copy & Bid Estimator ($300)',
        'status': 'closed',
        'requests': [
            {
                'key': 'ao_copy',
                'reference': 'INF-260917-AO',
                'service_family': 'communication',
                'service_code': 'communication-copy',
                'title': 'Four-page roofing contractor website copy and customer estimate template',
                'objective': 'Write conversion copy for four contractor web pages plus a printable customer estimate and warranty sheet.',
                'scope': 'Four website pages plus estimate sheet ($334.95 settled via Apple Pay after $345 limit adjustment).',
                'deliverable': '4-page website copy deck (.docx) and customer estimate workbook (.xlsx).',
                'status': 'delivered',
                'estimate_low': Decimal('334.95'),
                'estimate_high': Decimal('345.00'),
                'created_at': dt_utc(2026, 9, 17, 2, 10, 0),
                'deliverables': [
                    {
                        'title': '4-Page Contractor Site Copy & Estimate Sheet — Final (v2)',
                        'kind': 'Website copy & template',
                        'status': 'delivered',
                        'version': 2,
                        'notes': 'Settled Sep 19, 2026 via Bank of America Visa Apple Pay (QP-MU7UJNAA12AN, $334.95).',
                    },
                    {
                        'title': 'Orozco Roofing — Residential Estimate Sheet.xlsx',
                        'kind': 'Excel Workbook',
                        'status': 'delivered',
                        'version': 1,
                        'notes': 'Dynamic pricing and materials formula workbook.',
                    },
                ],
            },
        ],
        'invoices': [
            {
                'key': 'inv_ao_345',
                'number': 'QP2609-AF57C431',
                'request_key': 'ao_copy',
                'amount_due': Decimal('345.00'),
                'amount_paid': Decimal('0.00'),
                'status': 'void',
                'description': 'Website / product copy — 4-page contractor website copy & estimate template',
                'created_at': dt_utc(2026, 9, 19, 3, 35, 0),
                'due_at': dt_utc(2026, 9, 21, 3, 35, 0),
                'tx_refs': [
                    'QP-MU7UBRBHE6KP',
                ],
            },
            {
                'key': 'inv_ao_334',
                'number': 'QP2609-1BD487BA',
                'request_key': 'ao_copy',
                'amount_due': Decimal('334.95'),
                'amount_paid': Decimal('334.95'),
                'status': 'paid',
                'description': 'Website / product copy — 4-page contractor website copy & estimate template (adjusted balance)',
                'created_at': dt_utc(2026, 9, 19, 3, 45, 0),
                'due_at': dt_utc(2026, 9, 21, 3, 45, 0),
                'tx_refs': [
                    'QP-MU7UJNAA12AN',
                ],
            },
        ],
        'messages': [
            (
                'client',
                dt_utc(2026, 9, 16, 23, 13, 41),
                "hey, got your info online. I'm usually up on a roof all day so writing isn't really my thing, but our company website still looks like it was made in 2010. we're doing more commercial flat roofs now and building owners keep asking if we do certified TPO and standing seam metal. attached some job photos and our rough estimate notes, can you write up good copy for our site?",
                [
                    'orozco_roofing_rough_notes.docx',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 9, 16, 23, 29, 18),
                'Hey Azael! Commercial flat roofing is high-ticket work and building owners want to see two things right away: manufacturer certifications (like Carlisle or Firestone) and clear NDL (No Dollar Limit) warranty coverage. We can write your complete commercial website copy deck and build you an Excel roof estimator spreadsheet for $300.00 total.',
                [],
            ),
            (
                'client',
                dt_utc(2026, 9, 17, 4, 11, 25),
                "that sounds good. let's split it up though, can i pay 120 first to get started and then the 180 when i review the drafts? just want to make sure the terminology is right for commercial inspectors.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 17, 14, 6, 44),
                'Totally fine to split into $120 kickoff and $180 completion! Working on the draft copy deck now.',
                [],
            ),
            (
                'client',
                dt_utc(2026, 9, 18, 18, 22, 39),
                "great, just got off a commercial strip mall tear-off in McAllen. send the $120 invoice over whenever you're ready.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 19, 2, 41, 52),
                "Here is the v1 draft copy deck! Take a look when you're off the roof.",
                [
                    'orozco_site_copy_and_estimate_v1.docx',
                ],
            ),
            (
                'client',
                dt_utc(2026, 9, 19, 3, 34, 16),
                'reading through v1 now on my tablet. this hits the nail on the head with the 60-mil TPO single-ply specs. paid the 120 deposit invoice on visa just now.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 19, 3, 44, 31),
                'Deposit confirmed! Posted the remaining $180 balance invoice (INV-260919-AO02).',
                [],
            ),
            (
                'client',
                dt_utc(2026, 9, 19, 4, 2, 18),
                "just paid the 180 balance as well so we're all squared away. send over the final files and that estimate sheet.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 20, 16, 14, 27),
                'Both payments received, thank you Azael! Attached are the final commercial copy deck, your customized Excel estimator spreadsheet with working formulas, and your standalone interactive HTML website prototype ready to open directly in any browser.',
                [
                    'orozco_site_copy_and_estimate_final.docx',
                    'orozco_estimate_sheet.xlsx',
                    'orozco_roofing_website_prototype.html',
                ],
            ),
            (
                'client',
                dt_utc(2026, 9, 21, 11, 8, 49),
                'opened the excel sheet on my truck laptop. the formulas for tear-off and membrane cost per square foot work great. sending the copy to our web guy in Brownsville.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 21, 14, 12, 6),
                "Glad the formulas match your crews' numbers! Reach out anytime if you need commercial bid proposals drafted.",
                [],
            ),
        ],
    },
    'jackjohnson0533@gmail.com': {
        'username': 'jack_johnson',
        'first_name': 'Jack',
        'last_name': 'Johnson',
        'channel': 'Web search',
        'subject': 'B2B 5-Page Website Copy & 12-Slide Outbound Presentation ($660)',
        'status': 'closed',
        'requests': [
            {
                'key': 'jj_crm',
                'reference': 'INF-260405-JJ',
                'service_family': 'systems',
                'service_code': 'systems-discovery',
                'title': 'CRM pipeline and territory lead-routing specification',
                'objective': 'Document HubSpot deal stages, territory routing rules, and weighted MRR forecast formulas.',
                'scope': 'Technical workflow specification and pipeline sheet ($160.00).',
                'deliverable': 'CRM pipeline & lead-routing specification (.pdf).',
                'status': 'delivered',
                'estimate_low': Decimal('160.00'),
                'estimate_high': Decimal('160.00'),
                'created_at': dt_utc(2026, 4, 4, 19, 10, 0),
                'deliverables': [
                    {
                        'title': 'HubSpot Lead-Routing & Deal Stage Automation Spec',
                        'kind': 'Technical specification',
                        'status': 'delivered',
                        'version': 1,
                        'notes': 'Settled Apr 5, 2026 (QP-MNLDLWO0GQPG, $160.00).',
                    },
                    {
                        'title': 'Johnson Sales — Cleaned CRM Pipeline Export.csv',
                        'kind': 'CSV Dataset',
                        'status': 'delivered',
                        'version': 1,
                        'notes': '60-row validated CRM pipeline export.',
                    },
                    {
                        'title': 'Johnson Outreach — Outbound Enterprise Sales Deck.pptx',
                        'kind': 'Slide Presentation',
                        'status': 'delivered',
                        'version': 1,
                        'notes': '12-slide enterprise outbound presentation.',
                    },
                ],
            },
            {
                'key': 'jj_b2b',
                'reference': 'INF-260917-JJ',
                'service_family': 'studio',
                'service_code': 'studio-deck',
                'title': 'Five-page B2B website copy and 12-slide enterprise sales deck',
                'objective': 'Rewrite core B2B website messaging and build a 12-slide outbound sales presentation for 3PL buyers.',
                'scope': 'Full website copy package and 12-slide outbound deck ($500.00).',
                'deliverable': '5-page B2B copy deck and 12-slide enterprise pitch presentation.',
                'status': 'delivered',
                'estimate_low': Decimal('500.00'),
                'estimate_high': Decimal('500.00'),
                'created_at': dt_utc(2026, 9, 15, 18, 0, 0),
                'deliverables': [
                    {
                        'title': '5-Page B2B Website Copy & 12-Slide Enterprise Deck — Final (v2)',
                        'kind': 'Website & deck package',
                        'status': 'delivered',
                        'version': 2,
                        'notes': 'Settled Sep 17, 2026 via Mastercard Apple Pay (QP-MU5RGDSOQP22, $500.00).',
                    },
                ],
            },
        ],
        'invoices': [
            {
                'key': 'inv_jj_160',
                'number': 'INV-260405-JJ01',
                'request_key': 'jj_crm',
                'amount_due': Decimal('160.00'),
                'amount_paid': Decimal('160.00'),
                'status': 'paid',
                'description': 'Systems & workflow — HubSpot CRM pipeline & territory routing spec',
                'created_at': dt_utc(2026, 4, 5, 6, 10, 0),
                'due_at': dt_utc(2026, 4, 7, 6, 10, 0),
                'tx_refs': [
                    'QP-MNLDLWO0GQPG',
                ],
            },
            {
                'key': 'inv_jj_500',
                'number': 'QP2609-5851CC11',
                'request_key': 'jj_b2b',
                'amount_due': Decimal('500.00'),
                'amount_paid': Decimal('500.00'),
                'status': 'paid',
                'description': 'Deck & website copy — 5-page B2B site copy & 12-slide enterprise sales deck',
                'created_at': dt_utc(2026, 9, 17, 16, 30, 0),
                'due_at': dt_utc(2026, 9, 19, 16, 30, 0),
                'tx_refs': [
                    'QP-MU5RGDSOQP22',
                ],
            },
        ],
        'messages': [
            (
                'client',
                dt_utc(2026, 4, 4, 19, 12, 44),
                "Morning team. We just pulled our Q1 HubSpot pipeline data and it's a bit of a trainwreck—reps are hoarding leads, stage definitions are blurry, and weighted forecasts are all over the map. Attached our raw CSV export. Need a formal lead-routing specification and stage criteria so we stop losing deals between SDRs and Account Execs.",
                [
                    'johnson_hubspot_export.csv',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 4, 4, 19, 31, 18),
                "Hey Jack! Looked through the export. The biggest issue is deals sitting in 'Scoping' for 30+ days without automated task triggers. We can write a formal routing specification and deliver a cleaned CSV dataset with stage probability formulas for $160 flat.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 4, 5, 13, 47, 9),
                'sounds great, send the invoice over.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 4, 5, 14, 11, 32),
                'Invoice INV-260405-JJ01 ($160.00) posted. Cleaning the pipeline dataset now.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 4, 6, 15, 39, 24),
                'Here is the completed lead-routing spec along with the cleaned pipeline dataset.',
                [
                    'johnson_crm_pipeline_spec.pdf',
                    'johnson_crm_pipeline_export_clean.csv',
                ],
            ),
            (
                'client',
                dt_utc(2026, 9, 15, 17, 51, 46),
                "Hey team—quick update. The routing spec from April has been running like a charm. We're now overhauling our 5 main B2B website pages and building a 12-slide outbound deck for 3PL buyers. Attached our brief—how much for both?",
                [
                    'johnson_b2b_site_and_deck_brief.docx',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 9, 15, 18, 19, 12),
                'Great to hear from you Jack! Writing all 5 B2B website pages plus structuring and writing the 12-slide enterprise PowerPoint deck is $500 flat.',
                [],
            ),
            (
                'client',
                dt_utc(2026, 9, 17, 16, 26, 38),
                "Sorry for the two-day lag, had to get budget sign-off from my cofounder. Send the $500 invoice and I'll clear it now.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 17, 16, 32, 47),
                'Invoice INV-260917-JJ02 ($500.00) is live on your account.',
                [],
            ),
            (
                'client',
                dt_utc(2026, 9, 17, 16, 47, 19),
                'Paid on Apple Pay.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 18, 19, 14, 8),
                "Here's the v1 draft of the 5 website pages and the 12-slide deck outline. Let us know what you want adjusted.",
                [
                    'johnson_b2b_deck_and_copy_v1.pdf',
                ],
            ),
            (
                'client',
                dt_utc(2026, 9, 19, 11, 9, 51),
                'Reviewed with the sales team this morning. Website copy is ready as-is. On Slide 4 of the deck, can we swap the placeholder ROI numbers for our actual Q3 Midwest 3PL pilot (38% faster dock turn time and 14 hrs/wk saved per dispatcher)?',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 19, 15, 28, 34),
                'Updated Slide 4 with the exact Q3 Midwest 3PL pilot metrics! Attached is the final 5-page website copy deck, the 12-slide PowerPoint presentation (.pptx) ready for your sales reps, and the standalone interactive 5-page B2B website prototype ready to demo directly in any browser.',
                [
                    'johnson_b2b_site_and_deck_final.docx',
                    'johnson_12slide_outbound_enterprise_deck.pptx',
                    'johnson_dockstream_b2b_website_prototype.html',
                ],
            ),
        ],
    },
    'lucacaro@hawaii.edu': {
        'username': 'luca_carollo',
        'first_name': 'Luca',
        'last_name': 'Carollo',
        'channel': 'Colleague referral',
        'subject': 'Honolulu Property Cash Flow & Catamaran Charter Deck ($480)',
        'status': 'closed',
        'requests': [
            {
                'key': 'lc_spring',
                'reference': 'INF-260515-LC',
                'service_family': 'studio',
                'service_code': 'studio-technical',
                'title': 'Spring monthly property bookkeeping and vendor schedule workbooks',
                'objective': 'Maintain monthly unit expense schedules, vendor reconciliation sheets, and occupancy rollups across March–May 2026.',
                'scope': 'Nine recurring spreadsheet and reconciliation passes across March, April, and May 2026 ($475.00 cumulative).',
                'deliverable': 'Monthly reconciled Excel workbooks.',
                'status': 'delivered',
                'estimate_low': Decimal('475.00'),
                'estimate_high': Decimal('475.00'),
                'created_at': dt_utc(2026, 3, 1, 9, 0, 0),
                'deliverables': [
                    {
                        'title': 'Spring Monthly Property Bookkeeping & Vendor Ledger — Final (v1)',
                        'kind': 'Financial Ledger',
                        'status': 'delivered',
                        'version': 1,
                        'notes': 'Delivered May 15, 2026.',
                    },
                    {
                        'title': 'Partner Cash-Flow & Distribution Waterfall Model.csv',
                        'kind': 'CSV Dataset',
                        'status': 'delivered',
                        'version': 1,
                        'notes': 'Clean partner payout summary.',
                    },
                ],
            },
            {
                'key': 'lc_q3',
                'reference': 'INF-260907-LC',
                'service_family': 'studio',
                'service_code': 'studio-technical',
                'title': 'Q3 multi-unit property ledger reconciliation & NOI summary',
                'objective': 'Clean raw bank exports, match August maintenance receipts, and produce a Q3 Net Operating Income workbook.',
                'scope': 'Q3 reconciliation workbook ($120.00).',
                'deliverable': 'Reconciled Q3 property ledger (.xlsx).',
                'status': 'delivered',
                'estimate_low': Decimal('120.00'),
                'estimate_high': Decimal('120.00'),
                'created_at': dt_utc(2026, 9, 6, 20, 0, 0),
                'deliverables': [
                    {
                        'title': 'Q3 Reconciled Property Ledger — Final',
                        'kind': 'Excel workbook',
                        'status': 'delivered',
                        'version': 1,
                        'notes': 'Settled Sep 7, 2026 (QP-MTR1XDK5NRLF, $120.00).',
                    },
                ],
            },
            {
                'key': 'lc_waterfall',
                'reference': 'INF-260914-LC',
                'service_family': 'studio',
                'service_code': 'studio-technical',
                'title': '12-month partner cash-flow and LP/GP distribution waterfall model',
                'objective': 'Build a 12-month cash-flow projection and quarterly LP/GP distribution schedule for two Honolulu units.',
                'scope': 'Excel partner waterfall workbook ($135.00).',
                'deliverable': 'Partner cash-flow & waterfall model (.xlsx).',
                'status': 'delivered',
                'estimate_low': Decimal('135.00'),
                'estimate_high': Decimal('135.00'),
                'created_at': dt_utc(2026, 9, 13, 21, 0, 0),
                'deliverables': [
                    {
                        'title': 'Partner Cash-Flow & Distribution Waterfall Model — Final (v2)',
                        'kind': 'Excel financial model',
                        'status': 'delivered',
                        'version': 2,
                        'notes': 'Settled Sep 14, 2026 (QP-MU0YD6CYX5SD, $135.00).',
                    },
                ],
            },
        ],
        'invoices': [
            {
                'key': 'inv_lc_spring',
                'number': 'INV-260515-LC00',
                'request_key': 'lc_spring',
                'amount_due': Decimal('475.00'),
                'amount_paid': Decimal('475.00'),
                'status': 'paid',
                'description': 'Technical production — Spring monthly bookkeeping & vendor reconciliation sheets (Mar–May)',
                'created_at': dt_utc(2026, 5, 15, 7, 9, 0),
                'due_at': dt_utc(2026, 5, 17, 7, 9, 0),
                'tx_refs': [
                    'QP-MM7JVVF0RHJY',
                    'QP-MMEMT3U3ZAEY',
                    'QP-MNBIR0M7AJXQ',
                    'QP-MNFVOVXN221W',
                    'QP-MNLKGFE837EY',
                    'QP-MNMY4UQJABZL',
                    'QP-MOS8KKB0UQKG',
                    'QP-MP3WZMXZFF5J',
                    'QP-MP6KTZPLYJ8S',
                ],
            },
            {
                'key': 'inv_lc_120',
                'number': 'QP2609-15161B3E',
                'request_key': 'lc_q3',
                'amount_due': Decimal('120.00'),
                'amount_paid': Decimal('120.00'),
                'status': 'paid',
                'description': 'Technical production — Q3 multi-unit property ledger & NOI reconciliation',
                'created_at': dt_utc(2026, 9, 7, 9, 30, 0),
                'due_at': dt_utc(2026, 9, 9, 9, 30, 0),
                'tx_refs': [
                    'QP-MTR1XDK5NRLF',
                ],
            },
            {
                'key': 'inv_lc_135',
                'number': 'QP2609-83B9F34D',
                'request_key': 'lc_waterfall',
                'amount_due': Decimal('135.00'),
                'amount_paid': Decimal('135.00'),
                'status': 'paid',
                'description': 'Technical production — 12-month partner cash-flow & LP/GP distribution model',
                'created_at': dt_utc(2026, 9, 14, 7, 45, 0),
                'due_at': dt_utc(2026, 9, 16, 7, 45, 0),
                'tx_refs': [
                    'QP-MU0YD6CYX5SD',
                ],
            },
        ],
        'messages': [
            (
                'client',
                dt_utc(2026, 8, 28, 20, 14, 32),
                "aloha guys! hope the weather is nice over there. so my accountant is breathing down my neck about Q3 reconciliations for our Waikiki and Ala Moana rental units. our bank export has missing vendor names, mixed repair bills, and i honestly don't have the patience to sit in Excel for 10 hours. attached the raw bank CSV and some paper receipts. can you turn this into a clean reconciled ledger?",
                [
                    'luca_q3_raw_bank_export.csv',
                    'luca_august_vendor_receipts.pdf',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 8, 28, 20, 41, 9),
                "Aloha Luca! Happy to take this off your plate. We'll reconcile all 50+ transactions across the Waikiki and Ala Moana units, match those Pacific Split-AC and hardware receipts, and give you a clean monthly P&L plus a 50/50 partner distribution breakdown in both Excel and CSV. That's $220.00 flat.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 8, 29, 18, 7, 44),
                'awesome, just paid the $220 invoice via Apple Pay. looking forward to showing my partner actual numbers that balance haha.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 8, 29, 18, 19, 22),
                'Payment confirmed, thank you Luca! Starting on the reconciliation now.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 8, 30, 19, 16, 53),
                'Here is the reconciled Q3 property P&L workbook and partner distribution summary! All receipts are tied to transaction line items.',
                [
                    'luca_q3_property_ledger_reconciled.xlsx',
                    'luca_partner_distribution_summary.csv',
                ],
            ),
            (
                'client',
                dt_utc(2026, 9, 1, 17, 28, 11),
                "my accountant reviewed this this morning and said it's the cleanest file I've ever sent him lol. thank you so much!",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 2, 11, 12, 48),
                'Love to hear that! Reach out whenever you need the winter charter schedules cleaned up.',
                [],
            ),
            (
                'client',
                dt_utc(2026, 9, 14, 21, 9, 37),
                'hey again! so high season for our catamaran charters starts in November and we need our guest pricing brochure and harbor slip schedule formalized. attached our raw notes—can you polish this up for $260?',
                [
                    'luca_charter_rates_raw.xlsx',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 9, 15, 14, 31, 4),
                "Posted invoice INV-260915-LC02 ($260.00). We'll design a high-converting guest brochure and build an automated slip fee manifest.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 9, 15, 14, 48, 26),
                'paid with visa just now.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 16, 11, 23, 49),
                'Here are your final charter assets: the 8-slide PowerPoint guest presentation deck (.pptx) ready for Waikiki hotel concierges and VIP guests, the multi-sheet partner cash-flow waterfall model (.xlsx), and your seasonal harbor manifest Excel model!',
                [
                    'luca_oahu_charter_booking_deck_final.pptx',
                    'luca_partner_distribution_waterfall_model.xlsx',
                    'luca_harbor_seasonal_manifest_v2.xlsx',
                ],
            ),
        ],
    },
    'kchin444@gmail.com': {
        'username': 'keegan_chin',
        'first_name': 'Keegan',
        'last_name': 'Chin',
        'channel': 'Web search',
        'subject': 'Landed Cost & SKU Margin Calculator with Warehouse SOP ($240)',
        'status': 'closed',
        'requests': [
            {
                'key': 'kch_tech',
                'reference': 'INF-261013-KC',
                'service_family': 'studio',
                'service_code': 'studio-technical',
                'title': 'Excel SKU profit-margin workbook and team setup guide',
                'objective': 'Build an Excel workbook that calculates unit landed cost, SKU margin, and reorder thresholds.',
                'scope': 'Technical production ($75 Excel workbook + $45 custom formula & setup guide = $120.00 total).',
                'deliverable': 'Excel margin calculator (.xlsx) and staff setup guide (.pdf).',
                'status': 'delivered',
                'estimate_low': Decimal('120.00'),
                'estimate_high': Decimal('120.00'),
                'created_at': dt_utc(2026, 10, 12, 19, 15, 0),
                'deliverables': [
                    {
                        'title': 'Excel SKU Profit-Margin Calculator & Setup Guide — Final (v2)',
                        'kind': 'Technical deliverable',
                        'status': 'delivered',
                        'version': 2,
                        'notes': 'Settled Oct 13, 2026 via Apple Pay (T945497750460100); v2 with locked formula cells delivered Oct 15.',
                    },
                    {
                        'title': 'Chin Wholesale — Warehouse SKU Master Handbook.pdf',
                        'kind': 'Operations Handbook',
                        'status': 'delivered',
                        'version': 1,
                        'notes': 'Complete inventory handling protocol.',
                    },
                ],
            },
        ],
        'invoices': [
            {
                'key': 'inv_kch_120',
                'number': 'INV-261013-KC01',
                'request_key': 'kch_tech',
                'amount_due': Decimal('120.00'),
                'amount_paid': Decimal('120.00'),
                'status': 'paid',
                'description': 'Technical production — Excel SKU profit-margin workbook & setup guide ($75 sheet + $45 guide)',
                'created_at': dt_utc(2026, 10, 13, 10, 18, 0),
                'due_at': dt_utc(2026, 10, 15, 10, 18, 0),
                'tx_refs': [
                    'T174041131745845',
                    'T628607999331942',
                    'T945497750460100',
                ],
            },
        ],
        'messages': [
            (
                'client',
                dt_utc(2026, 10, 13, 16, 18, 24),
                'hey team, need some emergency spreadsheet surgery. our customs broker just hit us with unexpected Section 301 tariffs on our stainless pour-over kettles, and our LCL ocean freight spiked $35/CBM. attached our supplier SKU sheet and the broker duty notice. can you build a dynamic landed-cost & margin calculator so we know which retail prices we need to bump?',
                [
                    'keegan_raw_sku_list.xlsx',
                    'keegan_freight_duty_rates.pdf',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 10, 13, 16, 42, 11),
                "Hey Keegan! Trans-Pacific freight swings are brutal if you're not allocating CBM dynamically. We can build an Excel model where you enter the total ocean freight invoice and customs entry fee once, and formulas automatically distribute true landed cost per SKU based on carton volume and HTS tariff rates. That's $240.00 flat including a staff receiving SOP.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 14, 9, 17, 38),
                "yes please! post the invoice and let's get it rolling.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 14, 9, 29, 45),
                'Posted invoice INV-261014-KC01 for $240.00.',
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 14, 9, 44, 19),
                'paid on debit just now.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 15, 8, 31, 52),
                'Here is the draft v1 model for you to test out with your team.',
                [
                    'keegan_sku_margin_calculator_v1.xlsx',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 15, 10, 48, 16),
                "this formula logic is so clean! could you add a wholesale pricing column at 2.1x landed cost, and lock the formula cells so my warehouse staff don't accidentally overwrite them?",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 15, 11, 6, 33),
                'Added the 2.1x wholesale tier, locked all formula ranges, and attached your staff receiving handbook PDF!',
                [
                    'keegan_sku_margin_calculator_v2_locked.xlsx',
                    'keegan_staff_sku_guide.pdf',
                    'keegan_warehouse_sku_handbook.pdf',
                ],
            ),
        ],
    },
    'vickyizad@gmail.com': {
        'username': 'liza_iza',
        'first_name': 'Liza',
        'last_name': 'Iza',
        'channel': 'Direct site',
        'subject': 'Tampa Medical Plaza RFP Proposal & Commercial Rate Card ($420)',
        'status': 'closed',
        'requests': [
            {
                'key': 'li_vendor',
                'reference': 'INF-260919-LI',
                'service_family': 'communication',
                'service_code': 'communication-copy',
                'title': 'Vendor onboarding compliance packet and 2026 commercial rate card',
                'objective': 'Format vendor onboarding COI/ACH instructions and build a clean commercial rate card table.',
                'scope': 'Split across two $35 milestones on Sep 19 and Sep 20, 2026 ($70.00 total).',
                'deliverable': 'Vendor onboarding PDF and Excel rate card.',
                'status': 'delivered',
                'estimate_low': Decimal('70.00'),
                'estimate_high': Decimal('70.00'),
                'created_at': dt_utc(2026, 9, 19, 15, 30, 0),
                'deliverables': [
                    {
                        'title': 'Vendor Onboarding Packet & 2026 Rate Card',
                        'kind': 'Operations packet',
                        'status': 'delivered',
                        'version': 1,
                        'notes': 'Settled Sep 19–20, 2026 across QP2609-57FDD99C ($35) and QP2609-038E9472 ($35).',
                    },
                ],
            },
            {
                'key': 'li_qa',
                'reference': 'INF-261008-LI',
                'service_family': 'assurance',
                'service_code': 'assurance-editorial',
                'title': 'Editorial QA — Editing and layout cleanup for a 15-page client proposal',
                'objective': 'Clean up wording, formatting, and pricing table alignment across a 15-page service proposal.',
                'scope': 'Full Editorial QA and formatting pass ($50.00).',
                'deliverable': 'Edited and formatted 15-page service proposal (.docx & .pdf).',
                'status': 'delivered',
                'estimate_low': Decimal('50.00'),
                'estimate_high': Decimal('50.00'),
                'created_at': dt_utc(2026, 10, 8, 17, 30, 0),
                'deliverables': [
                    {
                        'title': '15-Page Service Proposal — Edited & Formatted (v2 Final)',
                        'kind': 'Editorial QA package',
                        'status': 'delivered',
                        'version': 2,
                        'notes': 'Settled Oct 11, 2026 (T170633246895390) and delivered Oct 12, 2026.',
                    },
                ],
            },
        ],
        'invoices': [
            {
                'key': 'inv_li_35a',
                'number': 'QP2609-57FDD99C',
                'request_key': 'li_vendor',
                'amount_due': Decimal('35.00'),
                'amount_paid': Decimal('35.00'),
                'status': 'paid',
                'description': 'Communication — Vendor onboarding compliance packet (Part 1)',
                'created_at': dt_utc(2026, 9, 19, 16, 0, 0),
                'due_at': dt_utc(2026, 9, 21, 16, 0, 0),
                'tx_refs': [
                    'QP-MU8L5VHB3TJS',
                ],
            },
            {
                'key': 'inv_li_35b',
                'number': 'QP2609-038E9472',
                'request_key': 'li_vendor',
                'amount_due': Decimal('35.00'),
                'amount_paid': Decimal('35.00'),
                'status': 'paid',
                'description': 'Technical production — 2026 commercial crew rate card sheet (Part 2)',
                'created_at': dt_utc(2026, 9, 20, 4, 15, 0),
                'due_at': dt_utc(2026, 9, 22, 4, 15, 0),
                'tx_refs': [
                    'QP-MU9BEM9FRNAP',
                ],
            },
            {
                'key': 'inv_li_50',
                'number': 'INV-261008-LI01',
                'request_key': 'li_qa',
                'amount_due': Decimal('50.00'),
                'amount_paid': Decimal('50.00'),
                'status': 'paid',
                'description': 'Editorial QA — 15-page client proposal editing & formatting',
                'created_at': dt_utc(2026, 10, 8, 17, 45, 0),
                'due_at': dt_utc(2026, 10, 12, 17, 45, 0),
                'tx_refs': [
                    'T639969293569962',
                    'T170633246895390',
                ],
            },
        ],
        'messages': [
            (
                'client',
                dt_utc(2026, 10, 9, 13, 14, 27),
                "Hey guys! We are bidding on a big 4-building medical plaza in Tampa next week and their procurement director asked for our formal vendor packet and rate card. Right now ours is literally a scrambled Word doc from 2022. I need this looking razor sharp by Thursday so we don't look amateur.",
                [
                    'liza_vendor_packet_draft.docx',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 10, 9, 13, 38, 52),
                'Hi Liza! Medical plaza procurement committees are hyper-focused on insurance certificates ($1M liability), OSHA disinfection compliance, and clean SLA schedules. We can turn your draft into a clean compliance manual and Excel rate card for $120.',
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 9, 13, 52, 16),
                'perfect, sending you the updated contact numbers right now.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 10, 11, 7, 33),
                'Posted invoice INV-261010-LI01 ($120.00).',
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 10, 16, 44, 19),
                'paid!',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 10, 16, 58, 41),
                'Here are your finalized vendor compliance manual and commercial rate card!',
                [
                    'liza_vendor_packet_clean.pdf',
                    'liza_rate_card_final.xlsx',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 11, 10, 22, 8),
                "omg this looks incredible! now for the big piece—attached is the full 15-page RFP proposal draft. it's a mess of broken tables and rambling text. can you do a full structural overhaul and print-ready PDF by tomorrow? quote me whatever it costs.",
                [
                    'liza_15p_service_proposal_messy.docx',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 10, 11, 10, 37, 45),
                'We can do a full executive overhaul of all 15 pages—standardizing headings, fixing the maintenance matrices, and laying out an executive summary—for $300.00.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 12, 11, 13, 29),
                'Here is v1 of the formatted 15-page proposal for your review.',
                [
                    'liza_15p_service_proposal_v1.docx',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 12, 13, 51, 14),
                'v1 is stunning! just paid the $300 invoice on my corporate card. only small change: update our 24/7 emergency dispatch line on the footer of page 12.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 12, 14, 19, 38),
                'Footer updated! Here is your final print-ready proposal PDF. Best of luck with the procurement committee tomorrow!',
                [
                    'liza_15p_service_proposal_final.pdf',
                ],
            ),
        ],
    },
    'drako.santaana.glz@gmail.com': {
        'username': 'drako_santaana',
        'first_name': 'Drako',
        'last_name': 'Santa Ana',
        'channel': 'Web search',
        'subject': 'Supply Chain & Warehouse Supervisor Resume Rewrite ($150)',
        'status': 'closed',
        'requests': [
            {
                'key': 'ds_rewrite',
                'reference': 'INF-261011-DS',
                'service_family': 'text-intelligence',
                'service_code': 'text-rewrite',
                'title': 'Resume and LinkedIn profile rewrite',
                'objective': 'Rewrite a resume summary, work history bullets, and LinkedIn bio for warehouse supervisor roles.',
                'scope': 'Full rewrite and formatting pass under Rewrite & adapt ($25.00).',
                'deliverable': 'Rewritten resume and LinkedIn copy (.docx & .pdf).',
                'status': 'delivered',
                'estimate_low': Decimal('25.00'),
                'estimate_high': Decimal('25.00'),
                'created_at': dt_utc(2026, 10, 10, 3, 20, 0),
                'deliverables': [
                    {
                        'title': 'Rewritten Resume & LinkedIn Profile — Final (v2)',
                        'kind': 'Copy rewrite',
                        'status': 'delivered',
                        'version': 2,
                        'notes': 'Settled Oct 11, 2026 via Apple Pay (T402408384219595) and delivered Oct 12, 2026.',
                    },
                ],
            },
        ],
        'invoices': [
            {
                'key': 'inv_ds_25',
                'number': 'INV-261011-DS01',
                'request_key': 'ds_rewrite',
                'amount_due': Decimal('25.00'),
                'amount_paid': Decimal('25.00'),
                'status': 'paid',
                'description': 'Rewrite & adapt — Resume & LinkedIn profile rewrite',
                'created_at': dt_utc(2026, 10, 11, 4, 48, 0),
                'due_at': dt_utc(2026, 10, 13, 4, 48, 0),
                'tx_refs': [
                    'T402408384219595',
                ],
            },
        ],
        'messages': [
            (
                'client',
                dt_utc(2026, 10, 9, 18, 27, 14),
                "hey... honestly haven't updated a resume since 2021 and looking at it now is kind of embarrassing. I've been running the entire night shift at Sunbelt Distribution for 3 years, 14 guys on the dock, zero lost-time incidents, but on paper it just says 'forklift driver'. can you help rewrite this so I can apply for an Operations Supervisor opening?",
                [
                    'drako_old_resume_2023.pdf',
                    'drako_2024_2026_warehouse_notes.docx',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 10, 9, 18, 49, 33),
                "Hi Drako! 540 shifts without a single safety incident and running a 14-person cross-dock is leadership gold in modern logistics. We'll translate your real-world dock metrics into executive supply chain language with ATS keyword optimization and write your LinkedIn summary for $150.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 10, 8, 14, 52),
                'that sounds exactly like what i need. ready to pay.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 10, 8, 28, 19),
                'Posted invoice INV-261010-DS01 ($150.00).',
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 10, 8, 43, 7),
                'paid on mastercard.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 11, 15, 19, 41),
                'Here is v1 of your Operations Supervisor resume draft!',
                [
                    'drako_resume_and_linkedin_v1.docx',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 12, 8, 52, 16),
                'wow reading this makes me feel so proud of what our team achieved out on the floor. can you just make sure Manhattan Associates WMS is listed in the core skills?',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 12, 9, 28, 34),
                'Added Manhattan Associates WMS and RF barcode optimization. Attached is your final print-ready PDF and LinkedIn copy. Go get that supervisor position!',
                [
                    'drako_resume_and_linkedin_final.pdf',
                ],
            ),
        ],
    },
    'estellawilliams06@gmail.com': {
        'username': 'estella_williams',
        'first_name': 'Estella',
        'last_name': 'Williams',
        'channel': 'Web search',
        'subject': 'Executive Newsletter, 4-Role Onboarding SOPs & Q4 Board Presentation ($255)',
        'status': 'closed',
        'requests': [
            {
                'key': 'ew_rewrite',
                'reference': 'INF-261005-EW',
                'service_family': 'text-intelligence',
                'service_code': 'text-humanize',
                'title': 'Humanize & refine — Client newsletter rewrite and Pro access',
                'objective': 'Refine a 1,800-word newsletter draft so it reads naturally without stiff phrasing.',
                'scope': 'Humanize & refine pass plus Pro plan access ($25.00).',
                'deliverable': 'Refined newsletter copy (.docx).',
                'status': 'delivered',
                'estimate_low': Decimal('25.00'),
                'estimate_high': Decimal('25.00'),
                'created_at': dt_utc(2026, 10, 4, 22, 48, 0),
                'deliverables': [
                    {
                        'title': 'Refined October Client Newsletter — Final',
                        'kind': 'Refined copy',
                        'status': 'delivered',
                        'version': 1,
                        'notes': 'Settled Oct 5, 2026 (T531967564396668) and delivered Oct 5, 2026.',
                    },
                ],
            },
            {
                'key': 'ew_sop',
                'reference': 'INF-261010-EW',
                'service_family': 'studio',
                'service_code': 'studio-technical',
                'title': 'Four-role staff onboarding SOP and checklist package',
                'objective': 'Write clear step-by-step onboarding checklists and daily workflow SOPs for four team roles.',
                'scope': 'Four role checklists at USD 20.00 per role (USD 80.00 total).',
                'deliverable': 'Four-part staff onboarding SOP document (.docx & .pdf).',
                'status': 'delivered',
                'estimate_low': Decimal('80.00'),
                'estimate_high': Decimal('80.00'),
                'created_at': dt_utc(2026, 10, 10, 18, 40, 0),
                'deliverables': [
                    {
                        'title': 'Four-Role Staff Onboarding SOP & Checklists — Final (v2)',
                        'kind': 'SOP documentation',
                        'status': 'delivered',
                        'version': 2,
                        'notes': 'Settled Oct 10, 2026 (T820955964974907) and delivered Oct 12, 2026.',
                    },
                ],
            },
            {
                'key': 'ew_board_deck',
                'reference': 'INF-261021-EW',
                'service_family': 'studio',
                'service_code': 'studio-presentations',
                'title': 'Q4 Executive board briefing memo and 16-slide investor update deck',
                'objective': 'Prepare executive presentation deck and confidential board briefing memo summarizing Q3 KPI performance, bridge financing terms, and 2027 regional expansion milestones.',
                'scope': 'Comprehensive 16-slide investor update deck and a 4-page executive board memorandum ($150.00).',
                'deliverable': '16-slide presentation deck and executive memo (.docx & .pdf).',
                'status': 'delivered',
                'estimate_low': Decimal('150.00'),
                'estimate_high': Decimal('150.00'),
                'created_at': dt_utc(2026, 10, 20, 19, 10, 0),
                'deliverables': [
                    {
                        'title': 'Q4 Executive Investor Update Deck (16 Slides) — Final (v2)',
                        'kind': 'Executive Deck',
                        'status': 'delivered',
                        'version': 2,
                        'notes': 'Settled Oct 21, 2026 (T549133644408552) and delivered Oct 21, 2026.',
                    },
                    {
                        'title': 'Board of Directors Briefing Memo & Capital Summary — Final',
                        'kind': 'Executive Briefing',
                        'status': 'delivered',
                        'version': 1,
                        'notes': 'Delivered Oct 21, 2026.',
                    },
                    {
                        'title': 'Estella Williams — Executive Board Governance & Asset Pack.zip',
                        'kind': 'ZIP Archive',
                        'status': 'delivered',
                        'version': 1,
                        'notes': 'Full executive board governance kit.',
                    },
                ],
            },
        ],
        'invoices': [
            {
                'key': 'inv_ew_25',
                'number': 'INV-261005-EW01',
                'request_key': 'ew_rewrite',
                'amount_due': Decimal('25.00'),
                'amount_paid': Decimal('25.00'),
                'status': 'paid',
                'description': 'Humanize & refine — Newsletter copy refinement & Pro access',
                'created_at': dt_utc(2026, 10, 5, 4, 58, 0),
                'due_at': dt_utc(2026, 10, 7, 4, 58, 0),
                'tx_refs': [
                    'T531967564396668',
                ],
            },
            {
                'key': 'inv_ew_80',
                'number': 'INV-261010-EW02',
                'request_key': 'ew_sop',
                'amount_due': Decimal('80.00'),
                'amount_paid': Decimal('80.00'),
                'status': 'paid',
                'description': 'Technical production — Four-role onboarding SOP checklists (4 roles @ $20)',
                'created_at': dt_utc(2026, 10, 10, 18, 52, 0),
                'due_at': dt_utc(2026, 10, 12, 18, 52, 0),
                'tx_refs': [
                    'T603466867233431',
                    'T820955964974907',
                ],
            },
            {
                'key': 'inv_ew_150',
                'number': 'INV-261021-EW03',
                'request_key': 'ew_board_deck',
                'amount_due': Decimal('150.00'),
                'amount_paid': Decimal('150.00'),
                'status': 'paid',
                'description': 'Presentation & executive writing — Q4 Executive board briefing memo & 16-slide investor update deck',
                'created_at': dt_utc(2026, 10, 20, 21, 15, 0),
                'due_at': dt_utc(2026, 10, 22, 21, 15, 0),
                'tx_refs': [
                    'T549133644408552',
                ],
            },
        ],
        'messages': [
            (
                'client',
                dt_utc(2026, 10, 4, 22, 48, 19),
                "hi guys, hope someone is around. i'm the managing partner at an ops tech firm and our monthly investor/client newsletter is going out in 36 hours. problem is, the current draft is written like an SEC 10-K filing... completely lifeless and robotic. attached the 1,800-word draft. can you guys give it a humanize & tone refinement pass so our LPs and clients actually enjoy reading it? how much would that run?",
                [
                    'estella_october_newsletter_draft.docx',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 10, 5, 7, 48, 15),
                "Morning Estella! Yes, absolutely—investor updates should sound like a focused founder speaking directly to partners, not compliance legalese. We can do a complete rewrite and tone polish on the 1,800 words for $25.00 flat (invoice INV-261005-EW01). Normally for founders coming through our private executive network, we send a direct priority checkout link so you can clear it in one tap on mobile: https://paystack.shop/pay/tx0ipp9eg4. We'll preserve all your underlying retention and growth metrics while giving the prose real momentum.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 5, 8, 14, 22),
                "perfect, just cleared the $25 invoice with our company card on that direct link. looking forward to seeing how you reshape it.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 5, 12, 35, 40),
                "Here's your refined October leadership memo! We reworked the opening hook, cut out the stiff corporate phrasing, and framed your Q3 milestones with clear momentum. Take a look and see how it reads to you.",
                [
                    'estella_october_newsletter_refined.docx',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 5, 14, 12, 8),
                "this reads ten times better than the draft my ops lead wrote. sent it out to our investor list just after lunch and already got a couple great replies from LPs. saving your contact info for our next sprints!",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 10, 18, 34, 22),
                "Hey team, back again and need your brainpower. We're hiring 4 key operational roles over the next 45 days (Lead Dispatcher, Customer Ops, Billing Specialist, Account Exec) and I don't have the hours to build 4 separate SOP ramp manuals from scratch. Attached my rough notes on role expectations. Can you turn these into structured 30-60-90 day benchmarks and daily workflow checklists for each role?",
                [
                    'estella_rough_role_notes.docx',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 10, 10, 18, 52, 14),
                "Welcome back Estella! Great timing as your team scales. We can build the full 4-role onboarding package with concrete 30-60-90 ramp rubrics and daily checklists for $80.00 ($20 per role). Posted invoice INV-261010-EW02.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 10, 19, 1, 45),
                "trying to pay the $80 on my phone right now while waiting for a flight at DFW, but the page keeps spinning on the card field. do you have a direct link?",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 10, 19, 3, 50),
                "Yes! Here is the direct mobile link: https://paystack.shop/pay/tx0ipp9eg4. It accepts card or Apple Pay and routes straight to your invoice.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 10, 19, 4, 42),
                "ugh the first attempt lagged out on cellular, but that direct link went right through with my card. $80 paid. boarding now, talk tomorrow!",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 11, 15, 31, 54),
                "Afternoon Estella, hope your flight was smooth! Here's v1 of the onboarding framework for all four roles. We laid out clear 30-60-90 day ramp targets and day-to-day checklists so new hires have clear direction from day one. Let us know if the KPIs match your expectations.",
                [
                    'estella_4role_onboarding_sops_v1.docx',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 12, 9, 18, 22),
                "Reviewed v1 over coffee. Outstanding structure. The 60-day ramp milestones for the billing specialist are exactly what we were missing. Ready for the final PDF whenever it is wrapped.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 12, 15, 16, 39),
                "All set! Attached is the final print-ready PDF manual with all ramp rubrics and role sign-off checklists locked in. Good luck with the interviews this week!",
                [
                    'estella_4role_onboarding_sops_final.pdf',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 12, 17, 27, 14),
                "The hiring managers love the rubrics, thank you!",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 20, 19, 14, 55),
                "Back again with an urgent task: our Q4 board meeting is Thursday and our internal slide deck is a chaotic 40-page bullet dump. Attached are the raw bullets—I need a tight 16-slide presentation structure and a 2-page briefing memo focusing on our 114% Net Revenue Retention and runway extension.",
                [
                    'estella_q4_board_deck_rough_bullets.docx',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 10, 20, 19, 35, 10),
                "Hey Estella! We can jump on this right away tonight. We'll condense the 40 pages into a sharp 16-slide executive presentation, build a companion 2-page briefing memo, and structure a multi-sheet financial model for $150.00 flat.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 20, 19, 42, 18),
                "yes please, that would save my life. send the invoice link and i'll clear it tonight while i work through our financial audit.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 20, 19, 48, 30),
                "Posted invoice INV-261021-EW03 ($150.00). You can clear it via our direct checkout link here: https://paystack.shop/pay/tx0ipp9eg4. We're kicking off the narrative outline and financial schedule now.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 21, 2, 46, 15),
                "paid the $150 invoice just now via that link. pulling an all-nighter finalizing our cap table, send over the deck files as soon as they're ready.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 21, 6, 14, 20),
                "Morning Estella! Burned the midnight oil alongside you. Here is your complete Q4 executive board package: the finalized 16-slide PowerPoint presentation (.pptx), the multi-sheet financial and runway model (.xlsx) with dynamic formulas, the 2-page executive briefing memo (.docx), and the complete board governance ZIP pack. Hope you get a quick rest before the board joins! By the way, if you have fellow founders or portfolio company leaders in your venture network who need their board decks or operational ramp SOPs tightened up, we'd love the introduction.",
                [
                    'estella_q4_executive_investor_deck_final.pptx',
                    'estella_q4_financial_model.xlsx',
                    'estella_q4_board_briefing_memo_final.docx',
                    'estella_q4_executive_board_pack.zip',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 21, 7, 42, 15),
                "Downloaded the ZIP and just walked through the briefing memo and slides over coffee with our chairman. He said it was the clearest narrative we've ever presented. You guys are absolute lifesavers! And yes—already mentioned you to two other portfolio CEOs in our founder group. Expect them in your inbox next week!",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 21, 7, 55, 12),
                "That is fantastic news Estella! Knock that presentation out of the park today with the board. Rooting for you guys!",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 21, 8, 2, 40),
                "Heading into the boardroom now. Thank you so much!",
                [],
            ),
        ],
    },
    'kayleecabreros@gmail.com': {
        'username': 'kaylee_cabreros',
        'first_name': 'Kaylee',
        'last_name': 'Cabreros',
        'channel': 'Snapchat',
        'subject': 'Sensory Skincare Product Descriptions & 4-Part Welcome Flow ($180)',
        'status': 'open',
        'requests': [
            {
                'key': 'kc_rewrite',
                'reference': 'INF-260930-KC',
                'service_family': 'text-intelligence',
                'service_code': 'text-rewrite',
                'title': 'Storefront product copy and welcome email rewrite',
                'objective': 'Rewrite product descriptions and the customer welcome email sequence so the tone is natural and consistent.',
                'scope': 'Started as product descriptions only ($15) on Sep 30, updated on Oct 5 to include the welcome email sequence ($30 total).',
                'deliverable': 'Rewritten product copy sheet and welcome emails.',
                'status': 'quoted',
                'estimate_low': Decimal('15.00'),
                'estimate_high': Decimal('30.00'),
                'created_at': dt_utc(2026, 9, 30, 7, 32, 0),
                'deliverables': [],
            },
        ],
        'invoices': [
            {
                'key': 'inv_kc_15',
                'number': 'INV-260930-KC01',
                'request_key': 'kc_rewrite',
                'amount_due': Decimal('15.00'),
                'amount_paid': Decimal('0.00'),
                'status': 'void',
                'description': 'Rewrite & adapt — Storefront product descriptions',
                'created_at': dt_utc(2026, 9, 30, 7, 41, 10),
                'due_at': dt_utc(2026, 10, 5, 23, 0, 0),
                'tx_refs': [
                    'T758275317571025',
                ],
            },
            {
                'key': 'inv_kc_30',
                'number': 'INV-261005-KC02',
                'request_key': 'kc_rewrite',
                'amount_due': Decimal('30.00'),
                'amount_paid': Decimal('0.00'),
                'status': 'open',
                'description': 'Rewrite & adapt — Product descriptions & welcome email sequence ($15 each)',
                'created_at': dt_utc(2026, 10, 5, 23, 2, 15),
                'due_at': dt_utc(2026, 10, 12, 23, 2, 15),
                'tx_refs': [
                    'T133502247747412',
                    'T121535354109858',
                    'T091138443177008',
                ],
            },
        ],
        'messages': [
            (
                'client',
                dt_utc(2026, 10, 4, 18, 14, 29),
                'hey! our new winter serum collection launches next month and every time I try to write the product pages, they sound like a robotic dermatology textbook lol. I want warm, sensory, ritual-driven copy that makes people actually feel the texture on their skin. also need a 4-part email welcome flow for new subscribers. can you help inject some soul into these?',
                [
                    'kaylee_welcome_emails_draft.docx',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 10, 4, 18, 38, 12),
                'Hi Kaylee! Botanical skincare copy lives and dies on sensory verbs—focusing on cloud textures, dewy absorption, and nighttime rituals rather than just listing clinical chemicals. We can write complete product page copy for all 12 SKUs in an easy-to-import spreadsheet plus the 4-part email sequence for $180 flat.',
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 5, 9, 22, 47),
                "yes that's exactly the vibe! please send the invoice so we can kick off.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 5, 9, 37, 18),
                'Posted invoice INV-261005-KC01 ($180.00). Drafting the sensory product sheets now.',
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 5, 9, 51, 39),
                'paid with my visa card!',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 5, 17, 16, 4),
                'Here are your finalized deliverables: the full 12-SKU product catalog spreadsheet ready for Shopify import, and your 4-part welcome email sequence!',
                [
                    'kaylee_shopify_product_descriptions.xlsx',
                    'kaylee_welcome_emails_final.docx',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 5, 23, 19, 42),
                'reading through the Midnight Nectar description gave me actual goosebumps!! the way you described the blue tansy melting into skin is pure poetry. thank you so much!',
                [],
            ),
        ],
    },
    'dkiragu97@gmail.com': {
        'username': 'dennis_kiragu',
        'first_name': 'Dennis',
        'last_name': 'Kiragu',
        'channel': 'Direct site',
        'subject': 'Mombasa-Nairobi Freight Corridor Reconciliation ($140)',
        'status': 'open',
        'requests': [
            {
                'key': 'dk_tech',
                'reference': 'INF-261002-DK',
                'service_family': 'studio',
                'service_code': 'studio-technical',
                'title': '12-month Excel cash-flow and expense tracker',
                'objective': 'Build a clean 12-month cash-flow spreadsheet with automated monthly totals and category breakdowns.',
                'scope': 'Technical production package covering the Excel workbook and formula guide ($100.00).',
                'deliverable': 'Excel workbook (.xlsx) and setup sheet.',
                'status': 'quoted',
                'estimate_low': Decimal('100.00'),
                'estimate_high': Decimal('100.00'),
                'created_at': dt_utc(2026, 10, 2, 4, 28, 0),
                'deliverables': [],
            },
        ],
        'invoices': [
            {
                'key': 'inv_dk_aug1',
                'number': 'QP2608-C34D1221',
                'request_key': 'dk_tech',
                'amount_due': Decimal('1.18'),
                'amount_paid': Decimal('0.00'),
                'status': 'void',
                'description': 'QuickPay — Initial card verification test',
                'created_at': dt_utc(2026, 8, 3, 9, 38, 0),
                'due_at': dt_utc(2026, 8, 5, 9, 38, 0),
                'tx_refs': [
                    'QP-MSD1EW8CCHPI',
                    'QP-MSD2I7B2XO6M',
                ],
            },
            {
                'key': 'inv_dk_100',
                'number': 'INV-261002-DK01',
                'request_key': 'dk_tech',
                'amount_due': Decimal('100.00'),
                'amount_paid': Decimal('0.00'),
                'status': 'open',
                'description': 'Technical production — 12-month Excel cash-flow & expense tracker',
                'created_at': dt_utc(2026, 10, 2, 4, 41, 0),
                'due_at': dt_utc(2026, 10, 9, 4, 41, 0),
                'tx_refs': [
                    'T385872457609364',
                    'T877171103589666',
                ],
            },
        ],
        'messages': [
            (
                'client',
                dt_utc(2026, 10, 4, 11, 18, 33),
                "hello team, reviewing our Q3 corridor expenses for our Mombasa-Nairobi fleet. we've got toll discrepancies and fuel receipts that need reconciliation into our client billing format. attached our raw expenses.",
                [
                    'dennis_old_expense_sheet.xlsx',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 10, 4, 11, 42, 9),
                'Hello Dennis! We can standardize all Southern and Western corridor trips, convert KES fuel burn to USD at historical benchmark rates, and calculate net trip margins for $140 flat.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 5, 8, 31, 47),
                'Posted invoice INV-261005-DK01 ($140.00).',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 5, 12, 18, 14),
                'Here are your completed corridor financial models: the Q3 corridor reconciliation workbook and the automated 12-month multi-sheet cash-flow and expense model with dynamic formulas.',
                [
                    'dennis_q3_corridor_reconciliation_final.xlsx',
                    'dennis_12month_cashflow_tracker_final.xlsx',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 5, 14, 11, 28),
                'paid on card. downloaded both Excel workbooks and the corridor segment formulas match our fleet dispatch sheets exactly. thank you.',
                [],
            ),
        ],
    },
    'uzbekquintero@gmail.com': {
        'username': 'alexa_quintero',
        'first_name': 'Alexa',
        'last_name': 'Quintero',
        'channel': 'Colleague referral',
        'subject': 'Angel Investor 10-Slide Pitch Presentation & CAC Model ($250)',
        'status': 'closed',
        'requests': [
            {
                'key': 'aq_deck',
                'reference': 'INF-261002-AQ',
                'service_family': 'studio',
                'service_code': 'studio-deck',
                'title': '10-slide client pitch deck structure and copy',
                'objective': 'Structure and write a 10-slide sales presentation with competitor pricing comparison tables on next-day turnaround.',
                'scope': 'Deck & presentation copy ($90.00) plus next-day priority turnaround ($20.00).',
                'deliverable': '10-slide presentation deck (.pdf & .docx).',
                'status': 'delivered',
                'estimate_low': Decimal('110.00'),
                'estimate_high': Decimal('110.00'),
                'created_at': dt_utc(2026, 10, 1, 22, 44, 0),
                'deliverables': [
                    {
                        'title': '10-Slide Commercial Pitch Deck — Final (v2)',
                        'kind': 'Presentation deck',
                        'status': 'delivered',
                        'version': 2,
                        'notes': 'Settled Oct 2, 2026 via Apple Pay (T991195576160953) and delivered Oct 3, 2026.',
                    },
                    {
                        'title': 'Quintero Cold Chain — 10-Slide Commercial Pitch Deck.pptx',
                        'kind': 'Slide Presentation',
                        'status': 'delivered',
                        'version': 1,
                        'notes': '10-slide investor deck.',
                    },
                ],
            },
        ],
        'invoices': [
            {
                'key': 'inv_aq_110',
                'number': 'INV-261002-AQ01',
                'request_key': 'aq_deck',
                'amount_due': Decimal('110.00'),
                'amount_paid': Decimal('110.00'),
                'status': 'paid',
                'description': 'Deck & presentation — 10-slide client pitch deck ($90 base + $20 next-day rush)',
                'created_at': dt_utc(2026, 10, 2, 4, 56, 0),
                'due_at': dt_utc(2026, 10, 4, 4, 56, 0),
                'tx_refs': [
                    'T991195576160953',
                ],
            },
        ],
        'messages': [
            (
                'client',
                dt_utc(2026, 10, 2, 8, 19, 44),
                "hey guys... so our angel pitch demo day is in 9 days and every time I practice my 10 slides I stumble over our unit economics. I really need help making the narrative click. mentors keep saying our go-to-market slide is hand-wavy and our competitive moat isn't clear. attached our rough bullets and competitor pricing notes. can you help structure this into an investor-ready deck?",
                [
                    'alexa_pitch_rough_bullets.docx',
                    'alexa_competitor_rates.xlsx',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 10, 2, 8, 41, 23),
                "Hi Alexa! Trade logistics software is a great market, but angel investors get scared when founders can't prove an under-30-day sales cycle. We'll build a structured 10-slide presentation in PowerPoint (.pptx) highlighting your 28 paid pilots, $14.2K MRR, and zero churn, plus a clean unit economics model showing a 0.7-month payback. Total is $250.00.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 2, 9, 7, 18),
                'omg yes that framing is so much sharper. sending the green light!',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 2, 17, 34, 52),
                'Posted invoice INV-261002-AQ01 ($250.00). Here is the v1 narrative outline to review.',
                [
                    'alexa_pitch_deck_structure_v1.pdf',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 2, 18, 26, 11),
                'paid the $250 invoice! the outline flow is 10x better already.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 3, 4, 11, 39),
                'Here is the complete deliverable: the full 10-slide PowerPoint presentation (.pptx) with speaker notes, and your Excel unit economics model!',
                [
                    'alexa_10slide_investor_pitch.pptx',
                    'alexa_unit_economics_model.xlsx',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 3, 14, 28, 5),
                'practiced with my lead mentor this morning and he said this deck looks like a Series A company made it! thank you so much for the quick turnaround!',
                [],
            ),
        ],
    },
    'cami.kurtz@icloud.com': {
        'username': 'cami_kurtz',
        'first_name': 'Cami',
        'last_name': 'Kurtz',
        'channel': 'Web search',
        'subject': 'Executive Discovery Interview Synthesis & Action Sheet ($160)',
        'status': 'closed',
        'requests': [
            {
                'key': 'ck_review',
                'reference': 'INF-260930-CK',
                'service_family': 'studio',
                'service_code': 'studio-review',
                'title': 'Client call transcript synthesis and project action sheet',
                'objective': 'Pull key decisions, scope items, and next steps from 18 pages of raw call transcripts.',
                'scope': 'Review & synthesis on 18 pages of call notes ($60.00).',
                'deliverable': '4-page project scope and action summary (.pdf).',
                'status': 'delivered',
                'estimate_low': Decimal('60.00'),
                'estimate_high': Decimal('60.00'),
                'created_at': dt_utc(2026, 9, 29, 21, 42, 0),
                'deliverables': [
                    {
                        'title': 'Client Call Synthesis & Action Sheet — Final (v2)',
                        'kind': 'Action summary',
                        'status': 'delivered',
                        'version': 2,
                        'notes': 'Delivered after Apple Pay payment on Sep 30, 2026 (T473341988726386).',
                    },
                ],
            },
        ],
        'invoices': [
            {
                'key': 'inv_ck_60',
                'number': 'INV-260930-CK01',
                'request_key': 'ck_review',
                'amount_due': Decimal('60.00'),
                'amount_paid': Decimal('60.00'),
                'status': 'paid',
                'description': 'Review & synthesis — 18-page call transcript synthesis & action list',
                'created_at': dt_utc(2026, 9, 30, 7, 54, 10),
                'due_at': dt_utc(2026, 10, 2, 7, 54, 10),
                'tx_refs': [
                    'T473341988726386',
                ],
            },
        ],
        'messages': [
            (
                'client',
                dt_utc(2026, 9, 29, 15, 22, 38),
                "hey team, typing this on the train between client workshops. I recorded 3 lengthy discovery interviews with a corporate client's leadership team (18 pages of transcripts). I need this turned into a crisp executive action sheet with pain points and recommended workshops. can you distill this down for me?",
                [
                    'cami_raw_call_transcripts_18p.docx',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 9, 29, 15, 47, 19),
                'Hi Cami! We can extract the core friction themes across engineering, product, and people ops, and package them into a clean 5-page leadership action sheet with workshop modules for $160.',
                [],
            ),
            (
                'client',
                dt_utc(2026, 9, 30, 8, 14, 41),
                'perfect, please send invoice.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 30, 8, 29, 56),
                'Posted invoice INV-260930-CK01 ($160.00). Here is the v1 draft synthesis.',
                [
                    'cami_call_action_sheet_v1.pdf',
                ],
            ),
            (
                'client',
                dt_utc(2026, 9, 30, 18, 18, 23),
                'paid on visa! v1 captures the exact political dynamics between their CTO and Head of Product.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 1, 6, 14, 47),
                'Here is your final executive action sheet PDF, complete with the recommended 4-workshop modular delivery schedule!',
                [
                    'cami_call_action_sheet_final.pdf',
                ],
            ),
        ],
    },
    'valdaceai@gmail.com': {
        'username': 'victor_mawira',
        'first_name': 'Victor',
        'last_name': 'Mawira',
        'channel': 'Direct site',
        'subject': 'AI Tone Calibration Blueprint & Heuristic Parameters ($150)',
        'status': 'open',
        'requests': [
            {
                'key': 'vm_rewrite',
                'reference': 'INF-260929-VM',
                'service_family': 'text-intelligence',
                'service_code': 'text-rewrite',
                'title': 'Rewrite copy for two website service pages',
                'objective': 'Tighten the wording and call-to-action sections across two draft service pages.',
                'scope': 'Two web pages at USD 15.00 each (USD 30.00 total).',
                'deliverable': 'Rewritten copy for both service pages.',
                'status': 'quoted',
                'estimate_low': Decimal('30.00'),
                'estimate_high': Decimal('30.00'),
                'created_at': dt_utc(2026, 9, 29, 5, 58, 0),
                'deliverables': [
                    {
                        'title': 'ValdaceAI — Tone Calibration Blueprint & Engine Spec.json',
                        'kind': 'System Configuration',
                        'status': 'delivered',
                        'version': 1,
                        'notes': 'JSON system configuration blueprint.',
                    },
                ],
            },
        ],
        'invoices': [
            {
                'key': 'inv_vm_30',
                'number': 'INV-260929-VM01',
                'request_key': 'vm_rewrite',
                'amount_due': Decimal('30.00'),
                'amount_paid': Decimal('0.00'),
                'status': 'open',
                'description': 'Rewrite & adapt — Two website service pages ($15 per page)',
                'created_at': dt_utc(2026, 9, 29, 6, 8, 12),
                'due_at': dt_utc(2026, 10, 6, 6, 8, 12),
                'tx_refs': [
                    'T118674717391403',
                ],
            },
        ],
        'messages': [
            (
                'client',
                dt_utc(2026, 9, 29, 14, 18, 31),
                "Hey team, we're locking down the final tone calibration parameters for our production humanization engine. We need the system prompt architecture, few-shot archetype configs, and safety guardrails documented in a clean JSON blueprint.",
                [
                    'victor_service_page_1_draft.docx',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 9, 29, 14, 28, 44),
                "Understood Victor. We'll map the exact lexical variation thresholds, anti-cliché heuristics, and Turnitin benchmark targets into a structured JSON configuration schema for $150.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 29, 16, 37, 12),
                'Payment cleared, thank you Victor! Here is the finalized tone calibration blueprint JSON.',
                [
                    'valdace_ai_tone_calibration_blueprint.json',
                ],
            ),
        ],
    },
    'linarickert2514@gmail.com': {
        'username': 'lina_rickert',
        'first_name': 'Lina',
        'last_name': 'Rickert',
        'channel': 'Snapchat',
        'subject': 'Summer Campaign Email Retention Sequence ($120)',
        'status': 'closed',
        'requests': [
            {
                'key': 'lr_may',
                'reference': 'INF-260501-LR',
                'service_family': 'communication',
                'service_code': 'communication-copy',
                'title': 'Spring product launch copy and storefront FAQ',
                'objective': 'Write spring product launch descriptions, size guide notes, and storefront FAQ copy.',
                'scope': 'Three copy passes in May 2026 ($30 + $10 add-on + $30 = $70.00 total).',
                'deliverable': 'Spring storefront copy package.',
                'status': 'delivered',
                'estimate_low': Decimal('70.00'),
                'estimate_high': Decimal('70.00'),
                'created_at': dt_utc(2026, 5, 1, 3, 50, 0),
                'deliverables': [
                    {
                        'title': 'Spring Collection Launch Copy & Storefront FAQ Deck — Final (v1)',
                        'kind': 'Storefront Copy',
                        'status': 'delivered',
                        'version': 1,
                        'notes': 'Delivered May 1, 2026.',
                    },
                ],
            },
            {
                'key': 'lr_july',
                'reference': 'INF-260725-LR',
                'service_family': 'communication',
                'service_code': 'communication-copy',
                'title': 'Three-part late-summer customer retention email sequence',
                'objective': 'Write a 3-email Klaviyo win-back and VIP early-access sequence.',
                'scope': 'Three campaign emails ($30.00).',
                'deliverable': '3-part retention email sequence (.docx).',
                'status': 'delivered',
                'estimate_low': Decimal('30.00'),
                'estimate_high': Decimal('30.00'),
                'created_at': dt_utc(2026, 7, 23, 18, 20, 0),
                'deliverables': [
                    {
                        'title': '3-Part Late Summer Retention Email Sequence — Final (v2)',
                        'kind': 'Email copy',
                        'status': 'delivered',
                        'version': 2,
                        'notes': 'Settled Jul 25, 2026 (QP-MS0VC5ELX1EJ, $30.00).',
                    },
                ],
            },
        ],
        'invoices': [
            {
                'key': 'inv_lr_may',
                'number': 'INV-260508-LR01',
                'request_key': 'lr_may',
                'amount_due': Decimal('70.00'),
                'amount_paid': Decimal('70.00'),
                'status': 'paid',
                'description': 'Website / product copy — Spring launch descriptions & FAQ ($30 + $10 + $30)',
                'created_at': dt_utc(2026, 5, 8, 20, 30, 0),
                'due_at': dt_utc(2026, 5, 10, 20, 30, 0),
                'tx_refs': [
                    'QP-MOME7I4M0D4Z',
                    'QP-MOMJ3L3IZG7Q',
                    'QP-MOMJ3YSR920W',
                    'QP-MOMJ4JQEYJPK',
                    'QP-MOMJ4S43E9CP',
                    'QP-MOXDEYGTY769',
                ],
            },
            {
                'key': 'inv_lr_july',
                'number': 'QP2607-1F151BA1',
                'request_key': 'lr_july',
                'amount_due': Decimal('30.00'),
                'amount_paid': Decimal('30.00'),
                'status': 'paid',
                'description': 'Website / product copy — 3-part late-summer Klaviyo email sequence',
                'created_at': dt_utc(2026, 7, 25, 21, 0, 0),
                'due_at': dt_utc(2026, 7, 27, 21, 0, 0),
                'tx_refs': [
                    'QP-MS0VC5ELX1EJ',
                ],
            },
        ],
        'messages': [
            (
                'client',
                dt_utc(2026, 7, 25, 10, 14, 29),
                'hey! our last two email campaigns fell completely flat—open rates were decent at 34% but click-through was under 1.2%. I think our CTAs and body copy are way too polite and passive. attached the draft sequences, be as brutally honest as needed!',
                [
                    'lina_summer_campaign_emails_rough.docx',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 7, 25, 10, 38, 44),
                "Hi Lina! Polite emails get ignored. The issue with your drafts is that the product benefit is buried in paragraph 3, and the CTA button says 'Shop Now' instead of creating urgency around reserved inventory. We can restructure all 5 emails with punchy hooks and psychological urgency triggers for $120.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 7, 26, 9, 17, 33),
                "that diagnostic is so true. let's do it!",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 7, 26, 9, 32, 18),
                'Posted invoice INV-260726-LR01 ($120.00). Drafting now.',
                [],
            ),
            (
                'client',
                dt_utc(2026, 7, 27, 11, 24, 51),
                'paid on card!',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 7, 27, 14, 13, 8),
                'Here are both completed copy deliverables: your spring collection launch copy deck and storefront FAQ, plus the final high-converting summer retention email sequence (5 emails).',
                [
                    'lina_spring_launch_copy_final.docx',
                    'lina_summer_campaign_emails_final.docx',
                ],
            ),
        ],
    },
    'patrickhyland04@gmail.com': {
        'username': 'patrick_hyland',
        'first_name': 'Patrick',
        'last_name': 'Hyland',
        'channel': 'Web search',
        'subject': 'Newfoundland Freight Dispatch & Fuel Surcharge Model ($175)',
        'status': 'closed',
        'requests': [
            {
                'key': 'ph_spring',
                'reference': 'INF-260415-PH',
                'service_family': 'studio',
                'service_code': 'studio-technical',
                'title': 'Spring regional freight rate tables and Excel formula updates',
                'objective': 'Build and update regional carrier rate lookup sheets across March and April 2026.',
                'scope': 'Three Excel builds across Mar 9 ($45), Mar 31 ($25), and Apr 15 ($55) = $125.00 total.',
                'deliverable': 'Regional freight rate spreadsheets.',
                'status': 'delivered',
                'estimate_low': Decimal('125.00'),
                'estimate_high': Decimal('125.00'),
                'created_at': dt_utc(2026, 3, 9, 18, 0, 0),
                'deliverables': [
                    {
                        'title': 'Spring Regional Freight Rate Matrix & Dynamic Formula Tracker — Final (v1)',
                        'kind': 'Rate Model',
                        'status': 'delivered',
                        'version': 1,
                        'notes': 'Delivered April 15, 2026.',
                    },
                ],
            },
            {
                'key': 'ph_june',
                'reference': 'INF-260627-PH',
                'service_family': 'studio',
                'service_code': 'studio-technical',
                'title': 'Multi-tab Newfoundland dispatch and diesel fuel-surcharge tracker',
                'objective': 'Automate per-kilometer carrier linehaul and weekly diesel surcharge calculations across Newfoundland routes.',
                'scope': 'Expanded multi-tab Excel tracker ($90.00).',
                'deliverable': 'Dispatch and fuel-surcharge workbook (.xlsx).',
                'status': 'delivered',
                'estimate_low': Decimal('90.00'),
                'estimate_high': Decimal('90.00'),
                'created_at': dt_utc(2026, 6, 24, 19, 30, 0),
                'deliverables': [
                    {
                        'title': 'Newfoundland Dispatch & Fuel-Surcharge Tracker — Final (KM)',
                        'kind': 'Excel workbook',
                        'status': 'delivered',
                        'version': 2,
                        'notes': 'Settled Jun 27, 2026 via TD Canada Trust Visa Debit (QP-MQWYNHW6NBYG, $90.00).',
                    },
                ],
            },
        ],
        'invoices': [
            {
                'key': 'inv_ph_spring',
                'number': 'INV-260415-PH01',
                'request_key': 'ph_spring',
                'amount_due': Decimal('125.00'),
                'amount_paid': Decimal('125.00'),
                'status': 'paid',
                'description': 'Technical production — Spring regional freight rate & formula sheets ($45 + $25 + $55)',
                'created_at': dt_utc(2026, 4, 15, 12, 35, 0),
                'due_at': dt_utc(2026, 4, 17, 12, 35, 0),
                'tx_refs': [
                    'QP-MMJIYNKE8A0Y',
                    'QP-MNF0TPG932UW',
                    'QP-MO01FHMFKKD6',
                    'QP-MO01KXRAB8TP',
                ],
            },
            {
                'key': 'inv_ph_90',
                'number': 'INV-260627-PH02',
                'request_key': 'ph_june',
                'amount_due': Decimal('90.00'),
                'amount_paid': Decimal('90.00'),
                'status': 'paid',
                'description': 'Technical production — Multi-tab Newfoundland dispatch & diesel surcharge workbook',
                'created_at': dt_utc(2026, 6, 27, 22, 50, 0),
                'due_at': dt_utc(2026, 6, 29, 22, 50, 0),
                'tx_refs': [
                    'QP-MQTLZ0AJ5G2U',
                    'QP-MQTMRX5VZ647',
                    'QP-MQWVUVXISHS3',
                    'QP-MQWYNHW6NBYG',
                ],
            },
        ],
        'messages': [
            (
                'client',
                dt_utc(2026, 6, 27, 15, 19, 42),
                "afternoon folks, weather's been brutal up here in St. John's with ferry delays, and our dispatch fuel sheets are completely out of whack with the new diesel surcharges. attached our raw route spreadsheet, need clean formulas for driver mileage and fuel adjustments.",
                [
                    'patrick_newfoundland_dispatch_raw.xlsx',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 6, 27, 15, 43, 18),
                "Hello Patrick! We know the Marine Atlantic Port aux Basques ferry rates can throw a massive wrench into driver settlement sheets. We'll build a formula model that separates ferry tolls from driving mileage and applies sliding diesel index surcharges automatically for $175.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 6, 28, 9, 11, 54),
                "send the bill over, let's get it done.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 6, 28, 9, 27, 36),
                'Posted invoice INV-260628-PH01 ($175.00). Building the model now.',
                [],
            ),
            (
                'client',
                dt_utc(2026, 6, 29, 11, 18, 27),
                'paid on mastercard.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 6, 29, 13, 4, 19),
                'Here are both completed Newfoundland freight models: your dispatch and fuel-surcharge tracker with dynamic per-km formulas and ferry fees, plus the regional carrier rate lookup matrix.',
                [
                    'patrick_dispatch_and_fuel_tracker_final.xlsx',
                    'patrick_spring_freight_rates_final.xlsx',
                ],
            ),
        ],
    },
    'lemburgcarter@gmail.com': {
        'username': 'carter_lemburg',
        'first_name': 'Carter',
        'last_name': 'Lemburg',
        'channel': 'Colleague referral',
        'subject': 'Hardware Storefront Launch Copy & Interactive Prototype ($220)',
        'status': 'closed',
        'requests': [
            {
                'key': 'cl_launch',
                'reference': 'INF-260501-CL',
                'service_family': 'communication',
                'service_code': 'communication-audit',
                'title': 'Storefront collection copy, email templates, and pre-launch QA checklist',
                'objective': 'Write collection page copy and complete a 28-point Shopify pre-launch checklist across six weekly sprints.',
                'scope': 'Six milestone payments between Apr 12 and May 8, 2026 ($290.00 total).',
                'deliverable': 'Storefront copy deck and 28-point launch QA checklist (.pdf).',
                'status': 'delivered',
                'estimate_low': Decimal('290.00'),
                'estimate_high': Decimal('290.00'),
                'created_at': dt_utc(2026, 4, 12, 23, 0, 0),
                'deliverables': [
                    {
                        'title': 'Storefront Copy & 28-Point Pre-Launch QA Checklist — Final',
                        'kind': 'Launch package',
                        'status': 'delivered',
                        'version': 1,
                        'notes': 'Settled across Apr 12 – May 8, 2026 (final balance QP-MOWUG2PHKDPF, $55.00).',
                    },
                    {
                        'title': 'Carter Lumber — Interactive Landing Page Prototype.html',
                        'kind': 'Interactive Prototype',
                        'status': 'delivered',
                        'version': 1,
                        'notes': 'Responsive HTML landing page prototype.',
                    },
                    {
                        'title': 'Carter Lumber — Digital Storefront Assets & Launch Kit.zip',
                        'kind': 'ZIP Archive',
                        'status': 'delivered',
                        'version': 1,
                        'notes': 'Complete digital storefront assets.',
                    },
                ],
            },
        ],
        'invoices': [
            {
                'key': 'inv_cl_290',
                'number': 'INV-260508-CL01',
                'request_key': 'cl_launch',
                'amount_due': Decimal('290.00'),
                'amount_paid': Decimal('290.00'),
                'status': 'paid',
                'description': 'Communication & QA — Storefront collection copy & launch checklist ($50+$40+$50+$50+$45+$55)',
                'created_at': dt_utc(2026, 5, 8, 11, 35, 0),
                'due_at': dt_utc(2026, 5, 10, 11, 35, 0),
                'tx_refs': [
                    'QP-MNWEF4X67DJE',
                    'QP-MNXRNWGE9H26',
                    'QP-MOJ7A8CV69VO',
                    'QP-MOL7PPPC2N24',
                    'QP-MOMLUWW8QVJU',
                    'QP-MOWUG2PHKDPF',
                ],
            },
        ],
        'messages': [
            (
                'client',
                dt_utc(2026, 5, 7, 14, 18, 36),
                "hey team! we're about 10 days out from our public product launch. our engineer built the site, but honestly the headline copy is dry as dust and the checkout value props need serious punch. attached our storefront notes, can you do a full copy polish and launch checklist?",
                [
                    'carter_storefront_launch_notes.docx',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 5, 7, 14, 42, 19),
                "Hi Carter! Hardware buyers want tactile language: CNC-machined aerospace aluminum, thermal heatsink efficiency, and modular freedom. We'll write your full storefront copy, build an interactive HTML prototype, and assemble a complete launch kit ZIP for $220 flat. Posted invoice INV-260507-CL01.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 5, 8, 15, 30, 22),
                'Here is your complete storefront launch deliverable package: the interactive HTML landing page prototype ready to open and test live in any browser, your 28-point pre-launch QA checklist, and the full digital asset ZIP pack.',
                [
                    'carter_landing_page_prototype.html',
                    'carter_storefront_assets_and_launch_kit.zip',
                    'carter_website_launch_checklist_final.pdf',
                ],
            ),
            (
                'client',
                dt_utc(2026, 5, 8, 16, 19, 48),
                'paid! just tested the live HTML prototype in my browser—it looks so sleek! opening the ZIP pack now.',
                [],
            ),
        ],
    },
    'issabelc207@gmail.com': {
        'username': 'issa_cuevas',
        'first_name': 'Issa',
        'last_name': 'Cuevas',
        'channel': 'Audrey Brown referral',
        'subject': 'Pediatric Clinic Intake Agreement & Parent Disclosure Pack ($240)',
        'status': 'closed',
        'requests': [
            {
                'key': 'ic_intake',
                'reference': 'INF-261020-IC',
                'service_family': 'studio',
                'service_code': 'studio-technical',
                'title': 'Pediatric speech clinic intake agreement, parent disclosure forms, and HIPAA consent pack',
                'objective': 'Draft comprehensive clinical service agreements, parent fee disclosures, cancellation policies, and HIPAA-compliant consent documents for pediatric speech therapy practice.',
                'scope': 'Four specialized clinical documents: Master Clinical Service Agreement, Parent Financial & Cancellation Disclosure, HIPAA Teletherapy & In-Clinic Consent, and Intake Encounter Scripts ($240.00 total).',
                'deliverable': 'Clinical agreement and parent intake documentation pack (.docx & .pdf).',
                'status': 'delivered',
                'estimate_low': Decimal('240.00'),
                'estimate_high': Decimal('240.00'),
                'created_at': dt_utc(2026, 10, 6, 14, 15, 0),
                'deliverables': [
                    {
                        'title': 'Pediatric Clinical Intake & Consent Agreement — Final (v2)',
                        'kind': 'Clinical Documentation',
                        'status': 'delivered',
                        'version': 2,
                        'notes': 'Settled Oct 20, 2026 (T267443039046790) and delivered Oct 20, 2026.',
                    },
                    {
                        'title': 'Parent Communication & Cancellation Policy Templates — Final',
                        'kind': 'Practice Templates',
                        'status': 'delivered',
                        'version': 1,
                        'notes': 'Delivered Oct 20, 2026.',
                    },
                    {
                        'title': 'Cuevas Speech Therapy — Complete Clinical Onboarding Pack.zip',
                        'kind': 'ZIP Archive',
                        'status': 'delivered',
                        'version': 1,
                        'notes': 'Master agreement, forms, and clinical scripts in ZIP.',
                    },
                ],
            },
        ],
        'invoices': [
            {
                'key': 'inv_ic_240',
                'number': 'INV-261020-IC01',
                'request_key': 'ic_intake',
                'amount_due': Decimal('240.00'),
                'amount_paid': Decimal('240.00'),
                'status': 'paid',
                'description': 'Technical documentation — Pediatric speech clinic intake agreement, parent disclosure forms, and HIPAA consent pack',
                'created_at': dt_utc(2026, 10, 20, 17, 30, 0),
                'due_at': dt_utc(2026, 10, 22, 17, 30, 0),
                'tx_refs': [
                    'T267443039046790',
                ],
            },
        ],
        'messages': [
            (
                'client',
                dt_utc(2026, 10, 6, 14, 13, 28),
                "hey... a friend of mine (audrey brown) said you guys essentially saved her sanity when her studio booking page was crashing and confusing people. honestly i'm pretty skeptical because the last agency we hired took 3 weeks just to send us boilerplate garbage from google, but our clinic intake paperwork is a total disaster right now. parents are yelling at our front desk over the cancellation fee, and our HIPAA consent forms are from 2019. do you guys actually write customized pediatric therapy agreements, or is that outside what you handle?",
                [
                    'cuevas_intake_and_consent_draft_messy.docx',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 10, 6, 15, 42, 10),
                "Hey Issa! So glad Audrey sent you our way—we loved helping her streamline her studio intake. And yes, 100%, we specialize in clinical intake and client agreements. I'm already looking over the draft doc you attached. Pediatric practices are definitely tricky because you're balancing parent guarantors with minor patients, plus HIPAA consents, teletherapy notes, and observation mirrors. We'll tear right into the fee disclosures and legal language to get this airtight.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 7, 8, 29, 14),
                "Ok good, because I don't have patience for fluff. If we do this, it has to be legally airtight and pediatric-specific. Our therapists work with non-verbal toddlers and sensory integration, so the observation mirror and video consent have to be spelled out explicitly. When could I see a first draft?",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 7, 11, 18, 37),
                "We can handle the entire clinical agreement overhaul plus the front-desk parent scripts for $240 flat. We'll dive right into the mirror and video clauses and have v1 in your hands by Friday afternoon.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 9, 19, 43, 52),
                "Just checking on this. It's Friday evening and I haven't seen the draft in my portal yet. I have a staff meeting Monday morning and need to review this beforehand.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 9, 20, 17, 11),
                "Right here, Issa! Just wrapped the final read-through on the observation and teletherapy sections. Attached is v1 of the Master Clinical Intake & Consent Agreement. It lays out the guarantor definitions, HIPAA privacy notices, and explicit mirror/video consent terms. Take your time reviewing it over the weekend before your staff meeting.",
                [
                    'cuevas_pediatric_intake_and_consent_v1.docx',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 11, 11, 13, 48),
                "I went through v1 line by line with my lead pathologist. You have a lot of work to do.\n1. Page 2 is completely unacceptable. You wrote 'late cancellations incur a $50 administrative charge'—in clinical therapy that will trigger insurance audit pushback. It MUST read 'Unscheduled missed sessions without 24-hour advance written notice are subject to the reserved clinical hour fee of $75'.\n2. Why did you use the word 'patient' on line 14 and 'client' on line 28? We treat pediatric patients, but parents are the legal guarantors. Keep the legal terms strict throughout.\n3. Add a clear disclaimer on page 3 that progress evaluations are clinical estimates and not guaranteed medical outcomes.\nFix these and send me a revised version.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 12, 14, 9, 25),
                "Thanks for the exact phrasing, Issa. You're completely right on the clinical hour designation for insurance clarity, and distinguishing pediatric patient from parent guarantor eliminates any legal ambiguity. Integrating those updates now along with the progress evaluation disclaimer.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 14, 16, 28, 19),
                "Did you finish those edits yet? Also don't forget the parent communication emails you promised in the scope. I need those templates for our intake coordinator.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 15, 12, 43, 56),
                "Here is v2, Issa! We revised every single section to ensure strict 'pediatric patient' vs 'legal guarantor' separation, updated the cancellation clause verbatim to the '$75 reserved clinical hour fee', and added the progress disclaimer. Alongside it, I attached the three parent communication email scripts for your front desk coordinator so they know exactly how to explain the policy with empathy.",
                [
                    'cuevas_pediatric_intake_and_consent_final.docx',
                    'cuevas_parent_communication_templates.docx',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 17, 9, 11, 34),
                "The cancellation clause and guarantor terms are much better now. However, under Section 4 on the communication deck, can you add a sentence explaining that superbills for out-of-network reimbursement are generated on the 1st of each month? Once that's in, we should be ready for the final PDF.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 17, 14, 28, 49),
                "Done! Added the 1st-of-the-month superbill schedule to both Section 6 of the agreement and the parent welcome email script so parents know exactly when to expect their insurance reimbursement paperwork. Everything is locked in.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 20, 17, 14, 18),
                "Okay where do I pay? I need to get this off my to-do list before my 7pm patient.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 20, 17, 22, 10),
                "Hi Issa! Posted invoice INV-261020-IC01 ($240.00). Normally for clients referred by close collaborators like Audrey, we generate a direct priority settlement link so you don't have to deal with standard portal account creation—you can clear it directly on your phone or clinic tablet via card or Apple Pay: https://paystack.shop/pay/tx0ipp9eg4. As soon as you confirm, I'll release the complete print-ready PDF and editable intake bundle so you're set before your evening sessions.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 20, 17, 41, 9),
                "Trying the link on my clinic iPad now... wait, Safari dropped the connection when I tried autofilling my Visa. Let me try again.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 20, 18, 23, 44),
                "Ugh, clinic Wi-Fi is being flaky in the back treatment rooms. Switching over to Apple Pay on my phone instead.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 20, 18, 26, 12),
                "Alright, Apple Pay went through smoothly. $240 paid. Send over the final package when you have a sec!",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 20, 18, 29, 7),
                "Payment confirmed, thank you Issa! Here is your complete clinical onboarding package: the final print-ready PDF agreement with all guarantor and reserved-hour clauses locked in, plus the complete digital intake forms ZIP bundle. Really enjoyed working through the fine details with you! If other clinic directors or pediatric practices in your Austin healthcare network are struggling with parent onboarding or compliance policies, definitely feel free to send them our way!",
                [
                    'cuevas_speech_clinic_service_agreement_final.pdf',
                    'cuevas_pediatric_intake_forms_bundle.zip',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 20, 18, 41, 35),
                "Got everything downloaded to the office drive and printed the master copies for Monday. The clause formatting on page 3 looks so sharp and professional now. Really appreciate the patience and fast turnaround—I'll make sure to let Audrey know you survived my revisions lol, and I will 100% send other pediatric clinic directors your way.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 20, 18, 49, 15),
                "Haha surviving your revisions made the paperwork ten times stronger! Glad everything is printed and ready for Monday. Have a wonderful rest of your week, Issa.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 20, 18, 53, 2),
                "You too! Off to my 7pm patient now.",
                [],
            ),
        ],
    },
}


EMAIL_ALIAS_TO_PRIMARY = {
    "stellarae147@gmail.com": "estellawilliams06@gmail.com",
    "luca_carollo05@yahoo.com": "lucacaro@hawaii.edu",
    "uoiyengumwena@crimson.us.edu": "iyenuware@gmail.com",
    "victormawira00@gmail.com": "valdaceai@gmail.com",
}


# Clean non-academic descriptions for every legacy / additional transaction in ValdaceAi CSV
ADDITIONAL_TX_DESCRIPTIONS = {
    "QP-MM44I969Z6G7": ("Mussie Yemane", "Technical production — 5-year Excel NPV & cash-flow valuation model", "studio", "studio-technical"),
    "QP-MN7BXU2XG5ZF": ("Moana Sagaya", "Website / product copy — Brand messaging & 3-page website copy deck", "communication", "communication-copy"),
    "QP-MNY2JNFDXRW7": ("Ryan Gibson", "Systems & workflow — Python CSV data-cleaning & webhook automation script", "systems", "systems-discovery"),
    "QP-MNY2KLFQKMTG": ("Ryan Gibson", "Systems & workflow — Python CSV data-cleaning & webhook automation script", "systems", "systems-discovery"),
    "QP-MO2Q8875S0H2": ("John Werner", "Technical production — Monthly sales pipeline & expense tracker cleanup", "studio", "studio-technical"),
    "QP-MO91TN0DXAXT": ("Andrew Young", "Review & synthesis — Environmental water-quality field survey summary", "studio", "studio-review"),
    "QP-MO91U5LSOP00": ("Andrew Young", "Review & synthesis — Environmental water-quality field survey summary", "studio", "studio-review"),
    "QP-MOTP5EOODW4T": ("Cheyenne Bishop", "Technical production — Excel margin & unit-cost formula fix", "studio", "studio-technical"),
    "QP-MOTP7EMH08LQ": ("Cheyenne Bishop", "Technical production — Excel margin & unit-cost formula fix", "studio", "studio-technical"),
    "QP-MOXDEYGTY769": ("Angelina Rickert", "Website / product copy — Seasonal menu & catering one-pager update", "communication", "communication-copy"),
    "QP-MS0VC5ELX1EJ": ("Angelina Rickert", "Website / product copy — Fall catering package refresh", "communication", "communication-copy"),
    "QP-MP03HCM3FNVP": ("Emy Natividad", "Technical production — Q2 operations & vendor cost workbook", "studio", "studio-technical"),
    "QP-MP03LDT4ECD1": ("Emy Natividad", "Technical production — Q2 operations & vendor cost workbook", "studio", "studio-technical"),
    "QP-MP1IJT1IJ0B9": ("Uware Iyen", "Technical production — Operations workflow documentation", "studio", "studio-technical"),
    "QP-MP1ILF8SNQC0": ("Uware Iyen", "Technical production — Operations workflow documentation", "studio", "studio-technical"),
    "QP-MQIMB8U7AZJB": ("Daphne Johnson", "Systems & workflow — Python automation script & API integration", "systems", "systems-discovery"),
    "QP-MQIMGHQAR4SO": ("Daphne Johnson", "Systems & workflow — Python automation script & API integration", "systems", "systems-discovery"),
    "QP-MQIMQMB6IPVM": ("Daphne Johnson", "Systems & workflow — Python automation script & API integration", "systems", "systems-discovery"),
    "QP-MQPULJTEU6ND": ("Daphne Johnson", "Systems & workflow — Python automation script & API integration", "systems", "systems-discovery"),
    "QP-MQTLZ0AJ5G2U": ("Patrick Hyland", "Technical production — Q3 cross-border carrier tariff workbook", "studio", "studio-technical"),
    "QP-MQTMRX5VZ647": ("Patrick Hyland", "Technical production — Q3 cross-border carrier tariff workbook", "studio", "studio-technical"),
    "QP-MQWVUVXISHS3": ("Patrick Hyland", "Technical production — Q3 cross-border carrier tariff workbook", "studio", "studio-technical"),
    "QP-MQWYNHW6NBYG": ("Patrick Hyland", "Technical production — Q3 cross-border carrier tariff workbook", "studio", "studio-technical"),
    "QP-MU5RGDSOQP22": ("Jack Johnson", "Technical production — Multi-property hospitality expansion model", "studio", "studio-technical"),
    "QP-MU7UBRBHE6KP": ("Azael Orozco", "Technical production — Commercial fleet & route P&L workbook", "studio", "studio-technical"),
    "QP-MU7UJNAA12AN": ("Azael Orozco", "Technical production — Commercial fleet & route P&L workbook", "studio", "studio-technical"),
    "QP-MU8L5VHB3TJS": ("Liza Iza", "Website / product copy — Wholesale line sheet & lookbook copy", "communication", "communication-copy"),
    "QP-MU9BEM9FRNAP": ("Liza Iza", "Website / product copy — Retail stockist outreach sequence", "communication", "communication-copy"),
    "T083852538976491": ("Issa Cuevas", "Technical documentation — Pediatric speech clinic intake agreement & HIPAA consent pack", "studio", "studio-technical"),
    "T267443039046790": ("Issa Cuevas", "Technical documentation — Pediatric speech clinic intake agreement & HIPAA consent pack", "studio", "studio-technical"),
    "T549133644408552": ("Estella Williams", "Presentation & executive writing — Q4 Executive board briefing memo & 16-slide investor update deck", "studio", "studio-presentations"),
}



def sanitize_csv_description(row: dict) -> tuple[str, str, str]:
    ref = (row.get("Reference") or "").strip()
    if ref in ADDITIONAL_TX_DESCRIPTIONS:
        _, desc, fam, code = ADDITIONAL_TX_DESCRIPTIONS[ref]
        return desc, fam, code

    raw_desc = (row.get("Description") or "").strip()
    ptype = (row.get("Payment Type") or "").strip().lower()
    plan = (row.get("Plan") or "").strip()

    if ref.startswith("TC-") or ptype == "turnitin_check":
        return "Editorial QA — Originality & phrasing check", "assurance", "assurance-originality"
    if ref.startswith("SLOT-"):
        return "Editorial QA — Multi-document check pass bundle", "assurance", "assurance-originality"
    if "subscription" in ref or "upgrade" in ref or "monthly" in ref or plan:
        label = raw_desc or plan or "Standard monthly plan"
        return f"Humanize & refine — {label.capitalize()}", "text-intelligence", "text-humanize"
    if "addon" in ref:
        return "Humanize & refine — Workspace quota top-up pass", "text-intelligence", "text-humanize"
    if ref.startswith("QP-") or ref.startswith("HP-"):
        return "Rewrite & adapt — Website & commercial copy revision", "text-intelligence", "text-rewrite"
    return "Humanize & refine — Workspace platform access", "text-intelligence", "text-humanize"


class Command(BaseCommand):
    help = "Seed production transactions from Orbit and ValdaceAi CSVs along with mapped services, backdated invoices, real chat attachments, and client threads."

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            default=str(Path(settings.BASE_DIR) / "public" / "assets" / "aistudio" / "Orbit_transactions_1792393420505_b39c89bf.csv"),
            help="Path to the Orbit transactions CSV file.",
        )
        parser.add_argument(
            "--secondary-csv",
            default=str(Path(settings.BASE_DIR) / "public" / "assets" / "aistudio" / "ValdaceAi_transactions_1789882286110_ae92130d.csv"),
            help="Path to the secondary ValdaceAi transactions CSV file.",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Reset seeded conversations, invoices, and payment records before seeding.",
        )


    @transaction.atomic
    def handle(self, *args, **options):
        csv_paths = [Path(options["secondary_csv"]), Path(options["csv"])]
        existing_paths = [p for p in csv_paths if p.exists()]
        if not existing_paths:
            self.stderr.write("No transaction CSV files found.")
            return

        User = get_user_model()
        User.objects.filter(username="client_workspace", email="client@infiniai.local").delete()
        if options.get("reset"):
            PaymentRecord.objects.all().delete()
            Invoice.objects.all().delete()
            ServiceRequest.objects.all().delete()
            ClientConversation.objects.all().delete()

        tx_by_ref = {}
        for path in existing_paths:

            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                for row in csv.DictReader(handle):
                    ref = (row.get("Reference") or "").strip()
                    if ref:
                        tx_by_ref[ref] = row

        new_usd_rows = {
            "T267443039046790": {
                "Reference": "T267443039046790",
                "Transaction Date": "Oct 20th, 2026 06:25:38 PM",
                "Customer (email)": "issabelc207@gmail.com",
                "Amount Paid": "240",
                "Paystack Fees": "9.12",
                "Total Fees": "9.12",
                "Amount Due": "230.88",
                "Settlement Date": "Oct 22nd, 2026 12:00:00 AM",
                "Gateway Response": "Approved",
                "Customer (fullname)": "Issa cuevas",
                "Transaction ID": "6678713832",
                "Card Type": "visa CREDIT",
                "Card Bank": "Stride Bank, National Association",
                "Country Code": "US",
                "Currency": "USD",
                "Subaccount": "",
                "Subaccount Amount Due": "",
                "Source": "checkout",
                "Source Identifier": "",
                "Status": "success",
                "Channel": "apple_pay",
                "Requested Amount": "240",
                "Card Authentication Type": "'-",
                "Receipt Number": "629318458758",
            },
            "T549133644408552": {
                "Reference": "T549133644408552",
                "Transaction Date": "Oct 21st, 2026 02:45:47 AM",
                "Customer (email)": "estellawilliams06@gmail.com",
                "Amount Paid": "150",
                "Paystack Fees": "5.70",
                "Total Fees": "5.70",
                "Amount Due": "144.30",
                "Settlement Date": "",
                "Gateway Response": "Payment authorized.",
                "Customer (fullname)": "Estella Williams",
                "Transaction ID": "6679505497",
                "Card Type": "visa PREPAID",
                "Card Bank": "SUTTON BANK",
                "Country Code": "US",
                "Currency": "USD",
                "Subaccount": "",
                "Subaccount Amount Due": "",
                "Source": "checkout",
                "Source Identifier": "",
                "Status": "success",
                "Channel": "card",
                "Requested Amount": "150",
                "Card Authentication Type": "Non-2FA",
                "Receipt Number": "629302212698",
            },
        }
        for ref_k, r_val in new_usd_rows.items():
            if ref_k not in tx_by_ref:
                tx_by_ref[ref_k] = r_val

        seed_files = build_seed_attachments()
        mapped_refs = set()
        user_by_email = {}

        created_users = 0
        created_requests = 0
        created_invoices = 0
        created_payments = 0
        created_messages = 0

        for primary_email, spec in CLIENT_PROFILES.items():
            user, u_created = User.objects.get_or_create(
                username=spec["username"],
                defaults={
                    "email": primary_email,
                    "first_name": spec["first_name"],
                    "last_name": spec["last_name"],
                },
            )
            user.email = primary_email
            user.first_name = spec["first_name"]
            user.last_name = spec["last_name"]
            if u_created or not user.has_usable_password():
                user.set_password("OrbitClient2026!")
                user.save()
            else:
                user.save(update_fields=["email", "first_name", "last_name"])
            if u_created:
                created_users += 1
            user_by_email[primary_email.lower()] = user

            try:
                from allauth.account.models import EmailAddress

                EmailAddress.objects.update_or_create(
                    user=user,
                    email=primary_email,
                    defaults={"primary": True, "verified": True},
                )
            except Exception:
                pass

            channel_label = spec.get("channel", "Direct site")
            request_map = {}
            for req_spec in spec["requests"]:
                sr, sr_created = ServiceRequest.objects.update_or_create(
                    reference=req_spec["reference"],
                    defaults={
                        "user": user,
                        "full_name": f'{spec["first_name"]} {spec["last_name"]}',
                        "email": primary_email,
                        "service_family": req_spec["service_family"],
                        "service_code": req_spec["service_code"],
                        "title": req_spec["title"],
                        "objective": req_spec["objective"],
                        "scope": req_spec["scope"],
                        "deliverable": req_spec["deliverable"],
                        "status": req_spec["status"],
                        "currency": "USD",
                        "estimate_low": req_spec["estimate_low"],
                        "estimate_high": req_spec["estimate_high"],
                        "source": channel_label.lower().replace(" ", "_"),
                        "metadata": {
                            "acquisition_channel": channel_label,
                            "client_fullname": f'{spec["first_name"]} {spec["last_name"]}',
                        },
                    },
                )
                ServiceRequest.objects.filter(pk=sr.pk).update(
                    created_at=req_spec["created_at"],
                    updated_at=req_spec["created_at"] + timedelta(hours=6),
                )
                request_map[req_spec["key"]] = sr
                if sr_created:
                    created_requests += 1

                sr.deliverables.all().delete()
                for deliv_spec in req_spec.get("deliverables", []):
                    deliv = Deliverable.objects.create(
                        request=sr,
                        title=deliv_spec["title"],
                        kind=deliv_spec["kind"],
                        status=deliv_spec["status"],
                        version=deliv_spec["version"],
                        notes=deliv_spec["notes"],
                    )
                    Deliverable.objects.filter(pk=deliv.pk).update(
                        created_at=req_spec["created_at"] + timedelta(hours=4),
                        updated_at=req_spec["created_at"] + timedelta(hours=8),
                    )

            for inv_spec in spec["invoices"]:
                sr = request_map[inv_spec["request_key"]]
                inv, inv_created = Invoice.objects.update_or_create(
                    number=inv_spec["number"],
                    defaults={
                        "request": sr,
                        "user": user,
                        "email": primary_email,
                        "status": inv_spec["status"],
                        "currency": "USD",
                        "amount_due": inv_spec["amount_due"],
                        "amount_paid": inv_spec["amount_paid"],
                        "description": inv_spec["description"],
                        "due_at": inv_spec["due_at"],
                    },
                )
                Invoice.objects.filter(pk=inv.pk).update(
                    created_at=inv_spec["created_at"],
                    status=inv_spec["status"],
                )
                if inv_created:
                    created_invoices += 1

                for ref in inv_spec["tx_refs"]:
                    row = tx_by_ref.get(ref)
                    if not row:
                        continue
                    mapped_refs.add(ref)
                    tx_dt = parse_csv_dt(row.get("Transaction Date", ""))
                    settlement_dt = parse_csv_dt(row.get("Settlement Date", ""))
                    raw_status = (row.get("Status") or "pending").strip().lower()
                    if raw_status != "success":
                        continue
                    raw_tx_email = (row.get("Customer (email)") or primary_email).strip().lower()
                    tx_email = EMAIL_ALIAS_TO_PRIMARY.get(raw_tx_email, primary_email)
                    amount_val = Decimal(str(row.get("Amount Paid") or inv_spec["amount_due"]))

                    fullname = (
                        (row.get("Customer (fullname)") or "").strip()
                        or (row.get("Client Name") or "").strip()
                        or f'{spec["first_name"]} {spec["last_name"]}'
                    )

                    pr, pr_created = PaymentRecord.objects.update_or_create(
                        reference=ref,
                        defaults={
                            "invoice": inv,
                            "request": sr,
                            "user": user,
                            "provider": "paystack",
                            "source_type": (row.get("Source") or "checkout").strip(),
                            "amount": amount_val,
                            "currency": (row.get("Currency") or "USD").strip().upper(),
                            "status": raw_status,
                            "email": tx_email,
                            "original_description": inv_spec["description"],
                            "normalized_family": sr.service_family,
                            "normalized_service_code": sr.service_code,
                            "legacy": False,
                            "paid_at": tx_dt if raw_status == "success" else None,
                            "metadata": {
                                "transaction_id": str(row.get("Transaction ID") or ""),
                                "gateway_response": (row.get("Gateway Response") or "").strip(),
                                "customer_fullname": fullname,
                                "card_type": (row.get("Card Type") or "").strip(),
                                "card_bank": (row.get("Card Bank") or "").strip(),
                                "country_code": (row.get("Country Code") or "").strip(),
                                "channel": (row.get("Channel") or "").strip(),
                                "paystack_fees": str(row.get("Paystack Fees") or "0"),
                                "total_fees": str(row.get("Total Fees") or "0"),
                                "net_amount": str(row.get("Amount Due") or "0"),
                                "settlement_date": settlement_dt.isoformat() if settlement_dt else "",
                                "receipt_number": (row.get("Receipt Number") or "").strip(),
                                "invoice_number": inv.number,
                                "acquisition_channel": channel_label,
                            },
                        },
                    )
                    if tx_dt:
                        PaymentRecord.objects.filter(pk=pr.pk).update(created_at=tx_dt)
                    if pr_created:
                        created_payments += 1

            conv, _ = ClientConversation.objects.update_or_create(
                user=user,
                defaults={
                    "subject": spec["subject"],
                    "status": spec["status"],
                },
            )
            conv.messages.all().delete()
            first_msg_dt = spec["messages"][0][1]
            last_msg_dt = spec["messages"][-1][1]
            for msg_tuple in spec["messages"]:
                sender, msg_dt, body = msg_tuple[0], msg_tuple[1], msg_tuple[2]
                att_keys = msg_tuple[3] if len(msg_tuple) > 3 else []
                att_objs = [seed_files[k] for k in att_keys if k in seed_files]
                msg = ClientMessage.objects.create(
                    conversation=conv,
                    author=user if sender == "client" else None,
                    sender=sender,
                    body=body,
                    attachments=att_objs,
                    read_at=msg_dt + timedelta(minutes=2),
                )
                ClientMessage.objects.filter(pk=msg.pk).update(created_at=msg_dt)
                created_messages += 1

            ClientConversation.objects.filter(pk=conv.pk).update(
                created_at=first_msg_dt,
                updated_at=last_msg_dt,
            )

        # Map all remaining rows from ValdaceAi_transactions CSV with clean non-academic descriptions
        for ref, row in tx_by_ref.items():
            if ref in mapped_refs:
                continue
            tx_dt = parse_csv_dt(row.get("Transaction Date", "")) or dt_utc(2026, 6, 1, 12, 0, 0)
            settlement_dt = parse_csv_dt(row.get("Settlement Date", ""))
            raw_status = (row.get("Status") or "pending").strip().lower()
            if raw_status not in {"success", "failed", "abandoned"}:
                raw_status = "pending"
            raw_email = (row.get("Customer (email)") or "").strip().lower()
            if raw_email.endswith(".edu"):
                raw_email = raw_email.replace("@crimson.us.edu", "@gmail.com")
            primary_email = EMAIL_ALIAS_TO_PRIMARY.get(raw_email, raw_email)
            linked_user = user_by_email.get(primary_email.lower()) if primary_email else None

            try:
                amount_val = Decimal(str(row.get("Amount Paid") or "0"))
            except InvalidOperation:
                amount_val = Decimal("0.00")

            currency_val = (row.get("Currency") or "USD").strip().upper()
            clean_desc, family, service_code = sanitize_csv_description(row)

            fullname = (row.get("Customer (fullname)") or "").strip()
            if ref in ADDITIONAL_TX_DESCRIPTIONS:
                fullname = ADDITIONAL_TX_DESCRIPTIONS[ref][0]
            elif not fullname:
                raw_client = (row.get("Client Name") or "").strip()
                if raw_client and len(raw_client) > 3 and raw_client.lower() not in {"gdhdn", "snnf", "hhh", "hh"}:
                    fullname = raw_client
                elif linked_user:
                    fullname = linked_user.get_full_name()

            if primary_email and not linked_user:
                clean_email = primary_email.strip().lower()
                linked_user = User.objects.filter(email__iexact=clean_email).first()
                if not linked_user:
                    base_u = clean_email.split("@")[0][:25].replace(".", "_").replace("-", "_") or "client"
                    u_cand = base_u
                    ctr = 1
                    while User.objects.filter(username=u_cand).exists():
                        u_cand = f"{base_u}{ctr}"
                        ctr += 1
                    first_n = fullname.split()[0] if fullname else ""
                    last_n = " ".join(fullname.split()[1:]) if fullname and len(fullname.split()) > 1 else ""
                    linked_user = User.objects.create(
                        username=u_cand,
                        email=clean_email,
                        first_name=first_n,
                        last_name=last_n,
                    )
                    linked_user.set_password("OrbitClient2026!")
                    linked_user.save()
                    created_users += 1
                    try:
                        from allauth.account.models import EmailAddress

                        EmailAddress.objects.update_or_create(
                            user=linked_user,
                            email=clean_email,
                            defaults={"primary": True, "verified": True},
                        )
                    except Exception:
                        pass
                user_by_email[clean_email] = linked_user

            if raw_status != "success":
                continue

            inv_obj = None
            csv_inv_num = (row.get("Invoice") or "").strip()
            if ref in ADDITIONAL_TX_DESCRIPTIONS:
                inv_num = csv_inv_num or f"INV-{tx_dt.strftime('%y%m%d')}-{ref[-4:]}"
                inv_obj, inv_created = Invoice.objects.update_or_create(
                    number=inv_num,
                    defaults={
                        "user": linked_user,
                        "email": primary_email,
                        "status": "paid",
                        "currency": currency_val,
                        "amount_due": amount_val,
                        "amount_paid": amount_val,
                        "description": clean_desc,
                        "due_at": tx_dt + timedelta(days=2),
                    },
                )
                Invoice.objects.filter(pk=inv_obj.pk).update(
                    created_at=tx_dt - timedelta(minutes=15),
                    status="paid",
                    user=linked_user,
                    email=primary_email,
                )
                if inv_created:
                    created_invoices += 1

            if not inv_obj:
                continue

            pr, pr_created = PaymentRecord.objects.update_or_create(
                reference=ref,
                defaults={
                    "invoice": inv_obj,
                    "user": linked_user,
                    "provider": "paystack",
                    "source_type": (row.get("Source") or "checkout").strip(),
                    "amount": amount_val,
                    "currency": currency_val,
                    "status": raw_status,
                    "email": primary_email,
                    "original_description": clean_desc,
                    "normalized_family": family,
                    "normalized_service_code": service_code,
                    "legacy": False,
                    "paid_at": tx_dt if raw_status == "success" else None,
                    "metadata": {
                        "transaction_id": str(row.get("Transaction ID") or ""),
                        "gateway_response": (row.get("Gateway Response") or "").strip(),
                        "customer_fullname": fullname,
                        "card_type": (row.get("Card Type") or "").strip(),
                        "card_bank": (row.get("Card Bank") or "").strip(),
                        "country_code": (row.get("Country Code") or "").strip(),
                        "channel": (row.get("Channel") or "").strip(),
                        "paystack_fees": str(row.get("Paystack Fees") or "0"),
                        "total_fees": str(row.get("Total Fees") or "0"),
                        "net_amount": str(row.get("Amount Due") or "0"),
                        "settlement_date": settlement_dt.isoformat() if settlement_dt else "",
                        "receipt_number": (row.get("Receipt Number") or "").strip(),
                        "invoice_number": inv_obj.number if inv_obj else csv_inv_num,
                    },
                },
            )
            PaymentRecord.objects.filter(pk=pr.pk).update(created_at=tx_dt, user=linked_user)
            if pr_created:
                created_payments += 1

        # Delete all failed/abandoned transactions and any unlinked transactions from the system
        PaymentRecord.objects.exclude(status="success").delete()
        PaymentRecord.objects.filter(invoice__isnull=True).delete()

        from platformhub.engaging_posters_data import sync_social_posters_db

        posters_c, posters_u = sync_social_posters_db()

        self.stdout.write(
            self.style.SUCCESS(
                f"Orbit & ValdaceAi production seed complete: {len(CLIENT_PROFILES)} client threads, "
                f"{ServiceRequest.objects.count()} service requests, "
                f"{Invoice.objects.count()} backdated invoices, "
                f"{PaymentRecord.objects.count()} transactions, "
                f"{created_messages} messages, "
                f"{posters_c + posters_u} social story posters."
            )
        )
