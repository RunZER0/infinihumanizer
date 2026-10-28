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
    copy_chat_file_alias,
    write_csv_file,
    write_docx_file,
    write_html_file,
    write_json_file,
    write_pdf_file,
    write_png_file,
    write_pptx_file,
    write_screenshot_png_file,
    write_xlsx_file,
    write_zip_file,
)
from platformhub.client_deliverables_builder import build_all_authentic_deliverables
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


def load_showcase_template(template_name: str) -> str:
    p = Path(settings.BASE_DIR) / "platformhub" / "templates" / "platformhub" / template_name
    if p.exists():
        return p.read_text(encoding="utf-8")
    return ""


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
        "Cruz Metro Freight — Capability Statement & Cold Outreach Preview (v1)",
        [
            "# 1. CORPORATE PROFILE & OPERATIONAL AUTHORITY",
            "Cruz Metro Freight LLC is an asset-based regional freight carrier operating out of Dallas-Fort Worth, Texas.",
            "USDOT #3918204 · MC #1488209 · Texas DMV #0094182 · Active Operating Authority since 2021.",
            "Insurance: $1,000,000 Commercial Auto Liability · $100,000 Motor Truck Cargo (Great West Casualty).",
            "# 2. ASSET FLEET & EQUIPMENT SPECIFICATIONS",
            "— Two 26-foot Freightliner M2-106 Box Trucks: 10,000 lbs payload, 3,500-lb Maxon hydraulic tuck-under liftgates, 102-inch width, e-track cargo securing rails.",
            "— Two Mercedes-Benz Sprinter Cargo Vans: High-roof, 3,850 lbs payload capacity, dedicated to critical parcel and hot-shot delivery.",
            "— On-Board Equipment: Heavy-duty 5,500-lb hydraulic pallet jacks, heavy ratchet load-bars, and moving blankets standard on every truck.",
            "# 3. VALUE PROPOSITION & PERFORMANCE BENCHMARKS",
            "— 99.4% On-Time Delivery Metric across 1,840 completed metro runs in 2026.",
            "— Direct dock dispatch without broker fees or middleman layers.",
            "— 2 full hours of free dock detention included per stop to absorb warehouse staging delays.",
            "— Real-time GPS tracking links and immediate electronic proof-of-delivery (e-POD) photos emailed upon delivery.",
            "# 4. OUTREACH SEQUENCE TARGETING & VALUE PROPOSITIONS",
            "— Sequence 1: Local industrial park shipping leads (focusing on Tuesday/Thursday open liftgate capacity).",
            "— Sequence 2: Emergency same-day pallet recovery when brokers drop scheduled pickups.",
            "— Sequence 3: Transparent flat metro zone rate card with no hidden fuel surcharge spikes.",
        ],
        role="draft",
        subtitle="Asset-Based Freight Carrier Profile & Outbound Sequence · DFW Logistics Corridor",
        meta_tag="Cruz Metro Freight · Commercial Fleet Operations · Dallas, TX",
    )
    files["cruz_bio_and_outreach_final.docx"] = write_docx_file(
        "cruz_bio_and_outreach_final.docx",
        "Cruz Metro Freight — Company Capability Bio & Cold Outreach Deck (Final)",
        [
            "# EXECUTIVE CAPABILITY STATEMENT & COMPANY PROFILE",
            "Entity: Cruz Metro Freight LLC · Headquarters: Dallas, Texas · Terminal: 4820 W Davis St, Dallas, TX 75211",
            "Operating Authority: USDOT #3918204 · MC #1488209 · Texas DMV #0094182",
            "Commercial Insurance: $1,000,000 Combined Single Limit (CSL) Commercial Auto Liability · $100,000 Broad-Form Motor Truck Cargo · Policy Underwritten by Great West Casualty.",
            "Company Overview: Cruz Metro Freight is an asset-based regional logistics provider headquartered in Dallas, Texas. We operate late-model 26-foot Freightliner M2-106 box trucks equipped with 3,500-lb Maxon tuck-under hydraulic liftgates and high-roof Mercedes-Benz Sprinter vans. Serving industrial manufacturers, third-party logistics (3PL) distribution centers, and commercial retail chains across the Dallas-Fort Worth Metroplex and North Texas corridor.",
            "# FLEET SPECIFICATIONS & ASSET DETAILS",
            "— Two 26-foot Freightliner M2-106 Box Trucks: 26,000 lbs GVWR (Non-CDL compliant for agile multi-stop metro dispatch), 10,000 lbs legal payload capacity, 102-inch exterior width, roll-up rear doors, e-track tie-down interior rails, and 3,500-lb hydraulic tuck-under liftgates.",
            "— Two Mercedes-Benz Sprinter High-Roof Cargo Vans: 3,850 lbs payload, 170-inch wheelbase, pallet-loadable sliding side doors, dedicated to rush medical supply and critical parcel runs.",
            "— Handling Equipment: Every unit carries an on-board 5,500-lb heavy-duty hydraulic pallet jack, 4 heavy ratchet load-bars, and 12 furniture blankets.",
            "# CORE OPERATIONAL CAPABILITIES & SLA GUARANTEES",
            "— Scheduled Morning Retail Replenishment: Guaranteed pre-10:00 AM dock delivery windows for regional retail corridors.",
            "— Emergency Same-Day Hot-Shot Pallet Recovery: 90-minute rapid dispatch response across Dallas, Tarrant, Collin, and Denton counties.",
            "— 2-Hour Free Dock Detention Window: We absorb standard warehouse staging delays without triggering surprise demurrage charges.",
            "— Direct Dispatcher Communication: No broker layers or outsourced call centers. Live GPS tracking links and instant electronic proof-of-delivery (e-POD) photos emailed immediately upon sign-off.",
            "# COLD OUTBOUND SEQUENCE 1: WAREHOUSE SHIPPING SUPERVISOR INTRO",
            "Target: Shipping Supervisors & Logistics Leads at Industrial Distribution Hubs in Grand Prairie & Arlington.",
            "Subject: Open Tue/Thu liftgate capacity in DFW industrial corridor",
            "Hi {{First_Name}},",
            "We run two dedicated 26ft liftgate box trucks through Arlington, Grand Prairie, and Irving on Tuesday and Thursday mornings.",
            "If your primary freight broker ever scrambles to cover regional pallet drops or leaves your dock backed up with late pickups, we keep standby capacity reserved specifically for local DFW manufacturing and distribution facilities.",
            "A few quick highlights on our fleet:",
            "• Asset-based carrier with late-model 26ft Freightliners (3,500-lb liftgates and pallet jacks on board).",
            "• 2 full hours of free dock detention included per stop—we never nickel-and-dime your facility.",
            "• $1,000,000 commercial auto liability and $100,000 active cargo insurance (COI available on request).",
            "Would you be open to keeping our direct dispatcher contact on hand for backup capacity next time a load falls through?",
            "Best regards, Jose Cruz · Owner & Fleet Dispatcher · Cruz Metro Freight LLC · (214) 555-0194",
            "# COLD OUTBOUND SEQUENCE 2: EMERGENCY MISSED-PICKUP RECOVERY (HOT-SHOT)",
            "Target: Warehouse Shipping Leads who face dropped loads from national load boards.",
            "Subject: Backup box-truck capacity for missed DFW dock pickups",
            "Hi {{First_Name}},",
            "Checking in because most warehouse shipping supervisors we talk to deal with 2 to 3 dropped pickups every month when digital freight brokers fail to dispatch drivers on time.",
            "When a carrier misses their 2:00 PM cutoff, your staging bays get clogged and customers are on the phone asking where their freight is.",
            "Cruz Metro Freight provides same-day regional hot-shot recovery within a 120-mile radius of DFW. We can have a 26ft liftgate truck backed into your bay within 90 minutes of dispatch.",
            "If you currently have any distressed freight sitting on your dock this afternoon, reply to this email or call our direct dispatch line at (214) 555-0194 and we'll cover it immediately.",
            "Warm regards, Jose Cruz · Cruz Metro Freight",
            "# COLD OUTBOUND SEQUENCE 3: METRO ZONE FLAT RATE CARD",
            "Target: Procurement & Freight Routing Specialists seeking transparent local cartage rates.",
            "Subject: Flat metro zone cartage rates — Cruz Metro Freight (DFW)",
            "Hi {{First_Name}},",
            "Here is our standard DFW metro rate matrix effective November 1, 2026. Clean, transparent zone pricing with zero fuel surcharge spikes:",
            "• Metro Core (0–25 miles): $175 Flat base (includes first 2 pallets, +$25 per additional pallet).",
            "• Outer Metro (25–50 miles): $285 Flat base (includes first 2 pallets, +$35 per additional pallet).",
            "• Extended Corridor (50–100 miles): $3.85 per loaded mile (straight door-to-door).",
            "• Liftgate Service: Included on all scheduled retail and ground drops at no extra charge.",
            "• Free Dock Detention: 2 full hours included per stop before standard $65/hr demurrage applies.",
            "Let me know if we can quote your upcoming lanes for next month.",
            "Best, Jose Cruz · Cruz Metro Freight LLC",
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
    files["audrey_current_homepage_screenshot.png"] = write_screenshot_png_file(
        "audrey_current_homepage_screenshot.png",
        url="https://studiobrownphotography.squarespace.com/",
        site_title="Studio Brown Photography · Austin, TX",
        hero_headline="Visual storytelling for modern life.",
        hero_subhead="[Current Live Subhead: None. No Austin location mention. No commercial vs portrait differentiation.]",
        items=[
            ("Card 01", "Sculptors Portrait · Northern Light", "No Category Tag / No Pricing"),
            ("Card 02", "Texas Hill Country Outerwear", "Commercial Lookbook Commission"),
            ("Card 03", "Architectural Warehouse Loft", "East Austin Interior Shoot"),
            ("Card 04", "Dripping Springs Wedding", "Personal Wedding Commission"),
            ("Card 05", "Ceramics Maker Editorial", "Austin Artisan Feature"),
            ("Card 06", "Executive Founder Profile", "Studio Portrait Session"),
        ],
        kind="browser",
        role="source",
    )
    files["audrey_current_booking_form_screenshot.png"] = write_screenshot_png_file(
        "audrey_current_booking_form_screenshot.png",
        url="https://studiobrownphotography.squarespace.com/book",
        site_title="Studio Brown Photography · Client Booking",
        hero_headline="FORM ABANDONMENT AUDIT REFERENCE: Squarespace Lightbox Modal (14 Mandatory Fields)",
        hero_subhead="Client Intake Questionnaire (14 Required Fields · 0 Starting Rates Shown)",
        items=[
            ("1. Full Legal Name *", "Required for contract verification"),
            ("2. Email Address *", "client@domain.com"),
            ("3. Mobile Phone Number *", "+1 (512) 000-0000"),
            ("4. How did you hear about Studio Brown? *", "Dropdown (Instagram, Referral, Google)"),
            ("5. Type of Session *", "Dropdown (Portrait, Brand, Event)"),
            ("6. Preferred Session Date + 2 Backup Dates *", "e.g. Oct 14th, Oct 21st, Nov 4th"),
            ("7. Desired Location / Venue *", "Studio, Outdoor, Specific Venue"),
            ("8. Wardrobe Vision & Outfit Changes Planned", "Describe fabric textures, color palettes..."),
            ("9. Do you require on-site Hair & Makeup coordination? *", "Yes / No / Need recommendations"),
            ("10. Pinterest Moodboard or Visual Inspiration URL *", "https://pinterest.com/... (REQUIRED FIELD)"),
            ("11. Total Project Budget Band for this shoot *", "Open blank text input (No starting rates shown)"),
            ("12. Intended Image Usage & Licensing Rights *", "Personal / Commercial / Editorial Advertising"),
        ],
        kind="form",
        role="source",
    )
    files["audrey_homepage_booking_audit.pdf"] = write_pdf_file(
        "audrey_homepage_booking_audit.pdf",
        "Studio Brown — Homepage & Booking Flow Copy Audit Report",
        [
            "# 1. EXECUTIVE DIAGNOSTIC SUMMARY",
            "Studio Brown's existing portfolio captures exquisite natural light imagery, but the current intake workflow experiences an acute 68% visitor abandonment rate prior to inquiry submission.",
            "Key Friction Points: (a) Generic hero messaging lacking geographic anchoring; (b) Hidden pricing requiring prospective clients to fill out a 14-question form before discovering whether rates match their budget; (c) Conflation of commercial editorial commissions with personal creative portraiture.",
            "# 2. HERO SECTION REPOSITIONING & GEOGRAPHIC MOAT",
            "Current Headline: 'Visual storytelling for modern life' (Generic; does not signal local Austin studio availability).",
            "Recommended Headline: 'Editorial portraits & brand campaigns that feel authentic, modern, and enduring.'",
            "Recommended Subhead: 'Specializing in commercial brand lookbooks, executive editorial profiles, and intimate creative portraiture. Based in East Austin with worldwide travel availability.'",
            "Social Proof Strip: Prominently feature verified editorial publications: Featured in Austin Monthly · Kinfolk Magazine · Rangefinder Award Winner · Architectural Digest Features.",
            "# 3. UPFRONT PRICING ANCHORS & PACKAGE TRANSPARENCY",
            "Industry benchmark data proves that high-end creative studios display baseline investment anchors to pre-qualify inbound clients and eliminate repetitive pricing back-and-forth.",
            "— Tier 1: Essential Session ($450 flat) · 60 minutes studio time, 15 retouched images, 1 wardrobe look, 7-day turnaround.",
            "— Tier 2: Studio Session ($950 flat) · 2.5 hours, 35 retouched images, 3 wardrobe looks, commercial license, raw archive.",
            "— Tier 3: Full Day Campaign ($2,200 flat) · 6-hour studio + location block, 75 selects, creative direction, commercial buyout.",
            "# 4. STREAMLINING THE INTAKE FUNNEL: FROM 14 FIELDS TO 5 ESSENTIALS",
            "Eliminate redundant preliminary questions (shoe size, extensive Pinterest boards, complex budget sliders). Convert the inquiry form to five frictionless data points:",
            "1. Full Legal Name",
            "2. Email Address & Direct Mobile Phone",
            "3. Preferred Session Date (with interactive Monday–Friday studio calendar picker)",
            "4. Selected Package Tier (dropdown pre-populated with Essential, Studio Session, or Campaign)",
            "5. Creative Vision & Wardrobe Notes (open-text brief)",
            "# 5. POLICY CLARITY & DEPOSIT AUTOMATION",
            "Clearly state studio deposit terms: 'A 50% non-refundable retainer secures your date on the East Austin studio calendar. Rescheduling is permitted up to 48 hours prior to call time without penalty.'",
            "Projected Funnel Impact: Cutting field count by 64% and establishing upfront transparent tiers is projected to increase qualified monthly inquiries by 42% while reducing administrative scheduling email exchanges by 5 hours weekly.",
        ],
        role="deliverable",
        subtitle="90-Day Funnel Diagnostic & Copy Architecture · Studio Brown East Austin",
        meta_tag="Studio Brown · Client Conversion & Funnel Audit · Austin, TX",
    )
    files["audrey_wireframe_notes.docx"] = write_docx_file(
        "audrey_wireframe_notes.docx",
        "Studio Brown — 3-Page Wireframe Notes & Sitemap",
        [
            "# SITEMAP ARCHITECTURE",
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
            "# PAGE 1: HOMEPAGE HERO",
            "Headline: Editorial photography crafted for brands and individuals with distinct vision.",
            "Subhead: Based in East Austin. Natural light studio sessions, on-location campaigns, and brand lookbooks.",
            "# PAGE 2: SERVICES TIERS (Starter / Signature / Full Production)",
            "# PAGE 3: BOOKING CALENDAR INTAKE & POLICIES",
        ],
        role="draft",
    )
    files["audrey_3page_website_copy_final.docx"] = write_docx_file(
        "audrey_3page_website_copy_final.docx",
        "Studio Brown — 3-Page Website Copy Deck (Final Production Master)",
        [
            "# PAGE 1: HOMEPAGE MASTER COPY",
            "NAVIGATION BAR: Home · Portfolio · Services & Packages · Studio Experience · Reserve Studio",
            "HERO BADGE: East Austin · Natural Light Studio",
            "HERO HEADLINE: Editorial portraits & brand campaigns that feel authentic, modern, and enduring.",
            "HERO SUBHEAD: Specializing in commercial brand lookbooks, executive editorial profiles, and intimate creative portraiture. Based in East Austin with worldwide travel availability.",
            "HERO CALL-TO-ACTION BUTTONS: Primary: [Check Studio Availability] · Secondary: [Explore 2026 Rates]",
            "CLIENT TRUST STRIP: Featured in Austin Monthly · Kinfolk Magazine · Rangefinder Award Winner · Architectural Digest Features",
            "STUDIO PHILOSOPHY: Photography that prioritizes genuine connection, understated elegance, and natural light. We believe the most compelling images happen in the quiet moments between poses—when authentic character emerges effortlessly. Our 1,800 sq ft East Austin studio features floor-to-ceiling north-facing warehouse windows, curated mid-century seating, and textured plaster backdrops designed for timeless visual narratives.",
            "PORTFOLIO SECTORS: 01 Commercial Lookbooks · 02 Executive & Editorial Profiles · 03 Intimate Creative Portraiture · 04 Architectural & Interior Spaces",
            "CLIENT TESTIMONIAL: 'Working with Audrey was the easiest commercial shoot our creative agency had all year. Zero awkward posing, immaculate natural window lighting, and our gallery arrived 3 days ahead of schedule.' — Sarah L., Creative Director, Kinship Goods",
            "FREQUENTLY ASKED QUESTIONS (FAQS):",
            "Q: What should I wear to my studio session? A: We recommend neutral palettes, organic textures (linen, silk, cashmere, raw denim), and minimal logos. Upon booking, you will receive our comprehensive 12-page Studio Brown Styling & Wardrobe Guide.",
            "Q: How and when will I receive my images? A: Your private online proofing gallery is delivered within 5 to 7 business days. High-resolution master files include full print releases and commercial usage licensing.",
            "Q: Do you travel for on-location brand campaigns? A: Yes. While our studio is based in Austin, Texas, our team frequently travels for national and international brand commissions.",
            "# PAGE 2: SERVICES & CURATED SESSION PACKAGES",
            "HEADER: Transparent Investment · Curated Session Tiers",
            "SUBHEAD: Every session includes private studio rental, high-resolution master delivery, commercial usage rights, and private online proofing gallery.",
            "TIER 1: ESSENTIAL SESSION ($450 FLAT)",
            "Best for: Artists, founders, and professionals who need a tight, editorial portfolio refresh.",
            "Inclusions: 60 minutes private studio time · 15 hand-retouched high-resolution master files · 1 wardrobe look in natural window light · Fast 7-business-day delivery turnaround · Private online proofing gallery with download rights.",
            "TIER 2: STUDIO SESSION ($950 FLAT) — MOST POPULAR",
            "Best for: Executive portraits, brand lookbooks, and personal editorial narratives.",
            "Inclusions: 2.5 hours studio + courtyard space · 35 hand-retouched high-resolution master files · Up to 3 wardrobe looks and mood transitions · Commercial & editorial licensing included · Priority 5-business-day delivery turnaround · Full-resolution raw image archive access.",
            "TIER 3: FULL DAY CAMPAIGN ($2,200 FLAT)",
            "Best for: Brand launches, apparel lookbooks, and editorial magazine spreads.",
            "Inclusions: Full 6-hour studio + on-location block · 75 hand-retouched campaign hero selects · Pre-production creative direction and custom moodboard · Unlimited wardrobe and product transitions · Full commercial buyout and billboard advertising license · Dedicated lighting assistant on set.",
            "ADD-ON SERVICES: Professional hair & makeup styling ($250) · Rush 48-hour gallery delivery ($300) · Additional retouched images ($35/image).",
            "# PAGE 3: BOOKING INTAKE & STUDIO SCHEDULING",
            "HEADER: Reserve Your Studio Session",
            "SUBHEAD: Complete our streamlined 5-field inquiry to reserve your preferred date on our East Austin studio calendar.",
            "STUDIO HOURS: Monday through Friday, 9:00 AM – 4:00 PM (optimal natural window lighting hours).",
            "INTAKE FORM SPECIFICATION:",
            "— Field 1: Full Legal Name (Text input, required)",
            "— Field 2: Email & Direct Mobile Phone (Contact input, required)",
            "— Field 3: Preferred Session Date (Date picker input, required, Mon–Fri)",
            "— Field 4: Selected Package Tier (Dropdown selection: Essential Session $450, Studio Session $950, Full Day Campaign $2,200)",
            "— Field 5: Creative Vision & Wardrobe Notes (Multi-line text area, optional brief description of project, intended usage, and styling vibes)",
            "STUDIO BOOKING POLICY & TERMS: A 50% non-refundable retainer is required to secure your selected date on the studio calendar. The remaining balance is due on the day of the shoot prior to master file release. Rescheduling is permitted up to 48 hours prior to call time without penalty.",
            "CONFIRMATION FEEDBACK MESSAGE: 'Thank you! Your calendar hold request has been received. Our studio coordinator will confirm availability within 4 business hours and send your 50% deposit checkout link.'",
        ],
        role="deliverable",
    )
    audrey_html = load_showcase_template("showcase_studio_brown.html")
    files["audrey_studio_brown_website_prototype.html"] = write_html_file(
        "audrey_studio_brown_website_prototype.html",
        "Studio Brown · East Austin Editorial & Portrait Photography",
        audrey_html,
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
                ["HTS 8423.81.00", "Digital Scale Electronic", "4.5%", "Ad Valorem", "USB-C rechargeable micro-timer"],
                ["POLA Drayage", "Deconsolidation & Transfer", 140.00, "Entry Flat", "Plus $18.50 per pallet handling"],
            ]
        },
        role="deliverable",
    )
    files["keegan_warehouse_sku_handbook.pdf"] = write_pdf_file(
        "keegan_warehouse_sku_handbook.pdf",
        "Warehouse Receiving, Inventory Barcoding & Landed Cost Entry SOP — Chin Specialty Goods",
        [
            "# 1. PURPOSE, REGULATORY SCOPE & OPERATIONAL MANDATE",
            "This Standard Operating Procedure (SOP-LOG-2026-04) establishes the mandatory protocol governing inbound intermodal freight intake, customs classification verification, physical damage triage, barcode serialization, and landed cost model updates for all Chin Specialty Goods inventory arriving at the Los Angeles logistics terminal.",
            "Operational Scope: Covers ocean container deconsolidation, Port of Los Angeles (POLA) drayage arrivals, Less-than-Container Load (LCL) pallet breakdown, and dynamic spreadsheet model reconciliation across active catalog SKUs KC-101 through KC-108.",
            "Mandatory Compliance: All receiving personnel must execute inspections in accordance with ANSI/ASQ Z1.4 sampling standards and US Customs & Border Protection (CBP) 19 CFR Part 141 commercial invoice regulations.",
            "--PAGE-BREAK--",
            "# 2. MASTER SKU, TARIFF & DUTY SCHEDULE (HTS 2026 REVISION)",
            "Every inbound product line must be reconciled against the following Harmonized Tariff Schedule (HTS) matrix prior to container gate release. Effective duty rates include both general Column 1 ad valorem rates and applicable Section 301 trade remedies.",
            [
                ["SKU Code", "Product Commercial Name", "HTS Code", "Base Duty", "Sec 301", "Effective Duty", "Master Ctn Qty", "Gross Wt / Ctn"],
                ["KC-101", "Precision Gooseneck Electric Kettle (1.0L)", "8516.79.00", "2.7%", "25.0%", "27.7%", "6 Units", "14.2 kg"],
                ["KC-102", "Conical Burr Stainless Hand Grinder", "8210.00.00", "3.7%", "7.5%", "11.2%", "12 Units", "9.6 kg"],
                ["KC-103", "Digital Precision Scale w/ Micro-Timer", "8423.81.00", "4.5%", "25.0%", "29.5%", "24 Units", "12.8 kg"],
                ["KC-104", "Double-Wall Borosilicate Glasses (Set of 2)", "7013.37.20", "6.0%", "7.5%", "13.5%", "16 Sets", "11.4 kg"],
                ["KC-105", "Ceramic V60 Style Pour-Over Dripper", "6912.00.48", "9.8%", "25.0%", "34.8%", "18 Units", "13.5 kg"],
                ["KC-106", "Stainless Milk Frothing Pitcher (600ml)", "7323.93.00", "3.4%", "7.5%", "10.9%", "20 Units", "8.2 kg"],
                ["KC-107", "Tritan Airtight Cold Brew Pitcher (1.5L)", "3924.10.40", "3.4%", "25.0%", "28.4%", "8 Units", "7.1 kg"],
                ["KC-108", "Titanium Coated Cupping Spoons (Pair)", "8215.99.20", "5.3%", "7.5%", "12.8%", "48 Pairs", "6.5 kg"],
            ],
            "Tariff Notes: Surcharges under Section 301 List 3 apply to HTS subheadings 8516.79.00, 8423.81.00, 6912.00.48, and 3924.10.40. Duty disbursements are remitted directly through automated clearinghouse (ACH) debit to CBP via licensed customs broker.",
            "--PAGE-BREAK--",
            "# 3. INBOUND FREIGHT RECEIVING & INTERMODAL 5-GATE INSPECTION PROTOCOL",
            "Receiving clerks must complete all five verification gates sequentially before authorizing carrier sign-off or initiating warehouse slotting.",
            [
                ["Gate Step", "Verification Target", "Inspection Method & Threshold", "Failure Escalation SLA", "Mandatory Output Record"],
                ["Gate 1: Seal Verification", "High-Security Bolt Seal", "Match ISO 17712 bolt seal # against Ocean B/L", "Immediate carrier hold; notify CBP broker", "Seal photo + Gate Log Entry"],
                ["Gate 2: Container Exterior", "Trailer Shell & Floor", "Inspect for water ingress, odor, wall puncture", "Reject trailer if biological or moisture breach", "Container Interchange Form (EIR)"],
                ["Gate 3: Pallet Tally", "Master Carton Counts", "100% carton count match vs Commercial Invoice", "Note shortage/overage on B/L within 30 min", "Tally Sheet signed by driver"],
                ["Gate 4: AQL Sampling", "Inner Unit QC Integrity", "ANSI/ASQ Z1.4 Level II Normal (AQL 2.5 defect limit)", "Quarantine lot if defect rate > 2.5%", "QC Inspection Sheet (Form Q-4)"],
                ["Gate 5: Barcode Scan", "UPC-A & Master Carton", "Scan random 10 units per SKU via Handheld WMS", "Re-tag cartons within 2 business hours", "WMS ASN Intake Receipt Confirmation"],
            ],
            "Documentation Standard: If water damage, pallet collapse, or box crush exceeds 2.0% of shipment volume, the receiving clerk must photograph all four sides of the affected pallets with time/date stamp enabled and record exact carton numbers on the carrier Delivery Receipt (DR) prior to releasing the drayage operator.",
            "--PAGE-BREAK--",
            "# 4. WAREHOUSE BIN ALLOCATION & VELOCITY RACK MAPPING",
            "To minimize pick path travel time and prevent cross-contamination or fragile breakage, all active SKUs are slotted into designated Los Angeles Logistics Hub 4 zones based on 60-day sales velocity.",
            [
                ["Warehouse Zone", "Rack / Bay / Tier", "SKU Assigned", "Pick Velocity", "Min Reorder Floor", "Max Bin Capacity", "Pallet Spec / Stacking"],
                ["Zone A (Front Aisle)", "Bay A-01 to A-04", "KC-101 (Gooseneck)", "High Velocity", "180 Units (30 ctns)", "720 Units (4 pallets)", "Standard GMA 48x40 (Max 3 high)"],
                ["Zone A (Front Aisle)", "Bay A-05 to A-08", "KC-103 (Scale)", "High Velocity", "250 Units (11 ctns)", "960 Units (5 pallets)", "Standard GMA 48x40 (Max 4 high)"],
                ["Zone B (Center Mezz)", "Bay B-01 to B-06", "KC-102 (Grinder)", "Medium Velocity", "120 Units (10 ctns)", "480 Units (2 pallets)", "Standard GMA 48x40 (Max 3 high)"],
                ["Zone B (Center Mezz)", "Bay B-07 to B-10", "KC-105 (Dripper)", "Medium Velocity", "220 Units (13 ctns)", "540 Units (3 pallets)", "Heavy-Duty Pallet (Max 2 high)"],
                ["Zone B (Center Mezz)", "Bay B-11 to B-14", "KC-106 (Pitcher)", "Medium Velocity", "150 Units (8 ctns)", "600 Units (3 pallets)", "Standard GMA 48x40 (Max 4 high)"],
                ["Zone C (Climate/Padded)", "Bay C-01 to C-04", "KC-104 (Glasses)", "Fragile / Controlled", "300 Units (19 ctns)", "640 Units (2 pallets)", "Corner Board Protected (No double stack)"],
                ["Zone C (Climate/Padded)", "Bay C-05 to C-08", "KC-107 (Cold Brew)", "Fragile / Controlled", "160 Units (20 ctns)", "400 Units (2 pallets)", "Stretch-Wrap 80-Gauge (Max 2 high)"],
                ["Zone D (Small Parts Bin)", "Bin D-01 to D-03", "KC-108 (Spoons)", "Accessories / Low", "100 Pairs (3 ctns)", "384 Pairs (1 pallet)", "Shelf Bin Tote Storage"],
            ],
            "--PAGE-BREAK--",
            "# 5. LANDED COST ACCOUNTING & SPREADSHEET MODEL RECONCILIATION",
            "Following warehouse physical intake, the operations clerk must open the master financial model (keegan_sku_margin_calculator_v2_locked.xlsx) and populate the inbound shipment variables in accordance with the formula schedule below:",
            [
                ["Cost Component", "Target Cell / Column", "Calculation Formula", "Verification Source", "Accounting General Ledger"],
                ["Supplier FOB Unit Cost", "Column D (D3:D10)", "Input from Supplier Commercial Invoice", "Supplier Wire Confirmation", "GL 13100 — In-Transit Inventory"],
                ["Ocean Freight Allocation", "Column E (E3:E10)", "=(Total_LCL_Freight / Total_CBM) * SKU_CBM", "Freight Forwarder Final Invoice", "GL 50120 — Freight Inbound Incurred"],
                ["Customs Duty Allocation", "Column F (F3:F10)", "=Unit_FOB * Effective_Duty_Rate_%", "CBP Form 7501 Entry Summary", "GL 50130 — Customs Duty & Clearance"],
                ["Drayage & Pierpass Fee", "Column G (G3:G10)", "=(Drayage_Total / Total_Cartons) * SKU_Carton_Ratio", "Drayage Carrier Invoice", "GL 50140 — Port Drayage & Wharfage"],
                ["True Landed Unit Cost", "Column H (H3:H10)", "=SUM(D3:G3)", "Calculated landed cost floor", "GL 13200 — Warehouse Finished Goods"],
                ["Wholesale Price (2.1x)", "Column I (I3:I10)", "=ROUNDUP(H3 * 2.1, 2)", "B2B catalog baseline tier", "GL 40100 — Wholesale Revenue"],
                ["Retail MSRP Price", "Column J (J3:J10)", "Direct catalog retail price sheet", "Website active listing", "GL 40200 — Direct-to-Consumer Sales"],
                ["Gross Margin Percentage", "Column K (K3:K10)", "=(J3 - H3) / J3", "Target threshold: >= 65.0%", "Executive Gross Margin KPI"],
            ],
            "Gross Margin Guardrail Rule: If any individual SKU calculates a retail gross margin below 65.0% in Column K, the spreadsheet generates an automated conditional formatting alert (Cell Fill: Light Red). The inventory lot cannot be released for e-commerce or retail fulfillment until pricing adjustments are formally authorized in writing by Keegan Chin.",
            "--PAGE-BREAK--",
            "# 6. DEFECTIVE STOCK QUARANTINE & DISCREPANCY CLAIMS",
            "Non-conforming items must be isolated immediately into the Cage Quarantine Area (Location: QA-Q01).",
            [
                ["Discrepancy Category", "Root Cause Trigger", "Quarantine Action", "Vendor Claim Filing SLA", "Resolution Mechanism"],
                ["Shattered Glass / Ceramic", "Transit impact / inadequate internal foam", "Hold full pallet lot; count breakage units", "Within 24 hours of gate receipt", "Credit memo against next purchase order"],
                ["Cosmetic Scratch / Dent", "Tooling wear during manufacturing", "Sample 100 units; isolate affected batch", "Within 48 hours with macro photos", "Supplier replacement parts air-freighted"],
                ["Electrical Fault (KC-101)", "Heating coil open circuit on 120V test", "100% electrical batch quarantine", "Within 12 hours to factory QC director", "Immediate factory engineering root cause audit"],
                ["Missing Barcode Label", "Packaging line omission at source factory", "Move to warehouse relabeling station", "Internal operational note", "Print replacement UPC-A labels at $0.15/unit"],
            ],
            "# 7. OPERATIONS ATTESTATION & RECEIVING SIGN-OFF",
            "All received lots must be updated in the warehouse management system (WMS) within four (4) business hours of physical trailer discharge. Completed receiving manifests, signed delivery receipts, and customs entry packages must be scanned and archived in the logistics repository under /Logistics/Inbound_Receiving/2026/.",
            "Warehouse Operations Manager: Keegan Chin · Chin Specialty Goods Logistics Hub 4 · Los Angeles, CA",
            "Authorized Signature: Keegan Chin · Date of Review: October 21, 2026",
        ],
        role="deliverable",
        subtitle="Operating Manual for Port Deconsolidation, Physical Inspection & Cost Model Reconciliation",
    )
    files["keegan_staff_sku_guide.pdf"] = write_pdf_file(
        "keegan_staff_sku_guide.pdf",
        "Warehouse Staff Quick Reference Guide — SKU Matrix, HTS Classifications & Duty Rates",
        [
            "# WAREHOUSE RECEIVING STAFF SKU REFERENCE GUIDE",
            "This quick-reference handbook is issued for dock receiving clerks and inventory technicians at Chin Specialty Goods.",
            "--PAGE-BREAK--",
            "# SECTION 1: ACTIVE SKU CATALOG & DUTY SPECIFICATIONS",
            [
                ["SKU Code", "Product Commercial Name", "HTS Code", "Base Duty", "Sec 301", "Effective Duty", "Master Ctn Qty"],
                ["KC-101", "Precision Gooseneck Electric Kettle (1.0L)", "8516.79.00", "2.7%", "25.0%", "27.7%", "6 Units"],
                ["KC-102", "Conical Burr Stainless Hand Grinder", "8210.00.00", "3.7%", "7.5%", "11.2%", "12 Units"],
                ["KC-103", "Digital Precision Scale w/ Micro-Timer", "8423.81.00", "4.5%", "25.0%", "29.5%", "24 Units"],
                ["KC-104", "Double-Wall Borosilicate Glasses (Set of 2)", "7013.37.20", "6.0%", "7.5%", "13.5%", "16 Sets"],
                ["KC-105", "Ceramic V60 Style Pour-Over Dripper", "6912.00.48", "9.8%", "25.0%", "34.8%", "18 Units"],
                ["KC-106", "Stainless Milk Frothing Pitcher (600ml)", "7323.93.00", "3.4%", "7.5%", "10.9%", "20 Units"],
                ["KC-107", "Tritan Airtight Cold Brew Pitcher (1.5L)", "3924.10.40", "3.4%", "25.0%", "28.4%", "8 Units"],
                ["KC-108", "Titanium Coated Cupping Spoons (Pair)", "8215.99.20", "5.3%", "7.5%", "12.8%", "48 Pairs"],
            ],
            "--PAGE-BREAK--",
            "# SECTION 2: PALLET RECEIVING & QUALITY ASSURANCE PROTOCOLS",
            "Clerks must verify carton count, outer box barcodes, and structural integrity before signing bill of lading.",
            "- Check outer master cartons for crush damage or dampness.",
            "- Scan 2D matrix barcode against warehouse management system (WMS).",
            "- Quarantine non-compliant lots immediately in Bay 4.",
            "- Report any carton count discrepancies directly to Keegan Chin.",
        ],
        role="deliverable",
        subtitle="Quick-Reference Matrix for Inbound Container Intake & Verification",
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
            "# 1. CORPORATE ONBOARDING & MANDATORY COMPLIANCE",
            "Liza Facility Services LLC requires all subcontracted maintenance teams and service vendors to maintain active compliance files on record prior to job site dispatch.",
            "Mandatory Documentation: (a) Signed IRS Form W-9; (b) Certificate of Insurance (COI) verifying $1,000,000 per occurrence / $2,000,000 aggregate Commercial General Liability naming Liza Facility Services LLC as an additional insured; (c) Statutory Workers' Compensation coverage; (d) Direct Deposit ACH Authorization Agreement.",
            "# 2. DISPATCH SLA & RESPONSE PROTOCOLS",
            "— Priority / Emergency Work Orders: Immediate dispatch with on-site crew arrival within 120 minutes of electronic work order receipt.",
            "— Routine Commercial Maintenance: 24 to 48 hours scheduled window across Tampa Bay commercial corridors.",
            "— Facility Sign-In: Crews must scan on-site QR badges upon arrival and departure to log digital timecard timestamps.",
            "# 3. BILLING SCHEDULE & NET-15 PAYMENT TERMS",
            "Invoices submitted by Friday 5:00 PM EST with completed job sign-off sheets are processed on automated Net-15 terms via electronic ACH direct deposit.",
            "# 4. OSHA COMPLIANCE & CLINICAL SAFETY STANDARDS",
            "All technicians operating on healthcare and medical plaza properties must complete OSHA Bloodborne Pathogens standard 29 CFR 1910.1030 training, wear required personal protective equipment (PPE), and utilize EPA-registered disinfectants strictly according to manufacturer dwell times.",
        ],
        role="deliverable",
        subtitle="Subcontractor Onboarding, Insurance Verification & Operational Guidelines",
        meta_tag="Liza Facility Services LLC · Compliance Manual",
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
    files["liza_commercial_rate_card.xlsx"] = copy_chat_file_alias("liza_rate_card_final.xlsx", "liza_commercial_rate_card.xlsx", role="deliverable")
    files["liza_15p_service_proposal_messy.docx"] = write_docx_file(
        "liza_15p_service_proposal_messy.docx",
        "Tampa Bay Medical Plaza RFP Response — 15 Pages (Rough Scramble)",
        [
            "# ROUGH NOTES FOR TAMPA MEDICAL RFP",
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
            "# DRAFT RFP PROPOSAL",
            "Standardized RFP response layout, structured SLA tables, and executive summary for medical plaza review.",
        ],
        role="draft",
    )
    files["liza_15p_service_proposal_final.pdf"] = write_pdf_file(
        "liza_15p_service_proposal_final.pdf",
        "Commercial Facility Maintenance Proposal — Tampa Bay Medical Plaza (Final)",
        [
            "# EXECUTIVE PROPOSAL & CONTRACTUAL MANDATE",
            "Liza Facility Services LLC is pleased to submit this formal RFP response and binding commercial maintenance contract for Tampa Bay Medical Plaza. We provide turnkey clinical-grade sanitation, terminal room disinfection, environmental services (EVS), and 24/7/365 rapid emergency response across all four (4) multi-tenant medical office buildings comprising 48,000 gross square feet.",
            "Firm Fixed Retainer: $3,850.00 per month ($46,200.00 annualized) guaranteed firm fixed pricing for 24 months, encompassing all regular evening custodial operations, supervisory inspections, consumables dispensing, and quarterly mechanical floor care.",
            "--PAGE-BREAK--",
            "# SECTION 1: FACILITY PROFILE & CLINICAL FOOTPRINT BREAKDOWN",
            "The commercial cleaning scope spans 4 detached medical facilities housing specialty outpatient practices, clinical testing labs, pediatric suites, and ambulatory care centers.",
            [
                ["Building Designation", "Primary Medical Occupancy", "Gross Area (Sq Ft)", "Exam / Procedure Rms", "Clinical Restrooms", "Floor Substrates"],
                ["Building A — Medical Arts", "Primary Care & Internal Medicine", "14,500 sq ft", "18 Exam Rooms", "6 Multi-Stall / 4 Private", "Commercial VCT & Terrazzo"],
                ["Building B — Pediatric Center", "Pediatric Therapy & Urgent Care", "11,200 sq ft", "14 Exam Rooms / Sensory Gym", "4 Pediatric / 2 Staff", "Seamless Sheet Vinyl & Matting"],
                ["Building C — Surgical Outpatient", "Endoscopy & Minor Surgery Suites", "12,800 sq ft", "6 Minor Op Suites / 8 Recovery", "6 Scrub / 4 Clinical", "Anti-Microbial Sealed Flooring"],
                ["Building D — Diagnostic Imaging", "MRI, CT, Phlebotomy & Lab", "9,500 sq ft", "4 Draw Stations / 2 Scanner Halls", "4 Public / 2 Lab Private", "Static-Dissipative Tile (SDT)"],
                ["Total Plaza Footprint", "4 Commercial Medical Facilities", "48,000 sq ft", "42 Clinical Rooms", "28 Sanitary Units", "100% Non-Porous Cleanable"],
            ],
            "--PAGE-BREAK--",
            "# SECTION 2: ROOM-BY-ROOM CLINICAL CLEANING & TERMINAL PROTOCOLS",
            "Operations execute in strict compliance with CDC Healthcare Environmental Infection Control Guidelines and OSHA 29 CFR 1910.1030 (Bloodborne Pathogens Standard). All exam rooms receive terminal sanitization nightly.",
            [
                ["Facility Area", "Service Frequency", "Mandatory Chemical Class", "Target Wet Contact Time", "Primary Disinfection Touchpoints"],
                ["Main Lobbies & Atriums", "5x Weekly (M–F Nightly)", "EPA List N Neutral Quat", "5 Minutes Wet Dwell", "Vestibule door hardware, reception counters, check-in touchscreens"],
                ["Exam & Consultation Rooms", "5x Weekly (M–F Nightly)", "Hydrogen Peroxide Sporicidal", "10 Minutes Wet Dwell", "Exam tables, phlebotomy chairs, mayo stands, sink fixtures, stool levers"],
                ["Minor Procedure Suites", "5x Weekly (Terminal Clean)", "Hospital Bleach / Sporicide", "10 Minutes Wet Dwell", "Surgical overhead lamps, articulating arms, stainless casework, kick buckets"],
                ["Clinical Restrooms", "5x Weekly (M–F Nightly)", "Acid-Free Bathroom Disinfectant", "10 Minutes Wet Dwell", "Flush levers, grab bars, sanitary disposal boxes, touchless soap valves"],
                ["Staff Breakrooms / Lockers", "5x Weekly (M–F Nightly)", "Food-Contact Sanitizer (D2)", "60 Seconds Dwell", "Microwave keypads, refrigerator handles, coffee carafes, table tops"],
                ["Common Hallways & Elevators", "5x Weekly + Weekly Scrub", "Green Seal GS-37 Neutral", "Air dry following mop", "Call buttons, handrails, terrazzo flooring, wall bumper rails"],
            ],
            "--PAGE-BREAK--",
            "# SECTION 3: GREEN SEAL GS-37 & EPA LIST N CHEMICAL MANIFEST",
            "Liza Facility Services utilizes an exclusively certified closed-loop chemical dispensing system to eliminate airborne volatile organic compounds (VOCs) and protect sensitive pediatric and asthmatic clinical visitors.",
            [
                ["Product Commercial Name", "Manufacturer", "Active Chemistry", "EPA Reg Number", "Dilution Ratio", "Microbial Kill Spectrum"],
                ["Oxivir Tb Disinfectant", "Diversey", "Accelerated Hydrogen Peroxide", "70627-56", "Ready to Use", "MRSA, Norovirus, SARS-CoV-2 (1-min kill)"],
                ["Virex II 256", "Diversey", "Quaternary Ammonium Chloride", "70627-24", "1:256 Dispensed", "Broad-spectrum bactericidal, virucidal, fungicidal"],
                ["Prominence Floor Cleaner", "Diversey", "Non-Ionic Surfactant GS-37", "N/A (Green Seal)", "1:375 Dispensed", "Neutral pH, leaves no dulling alkaline residue"],
                ["Alpha-HP Multi-Surface", "Diversey", "Hydrogen Peroxide GS-37", "N/A (Green Seal)", "1:64 Dispensed", "Interior partition glass, polished stainless, casework"],
                ["Clorox Healthcare Bleach", "Clorox Pro", "0.55% Sodium Hypochlorite", "56392-7", "Ready to Use", "Clostridioides difficile (C. diff) spores (3-min kill)"],
            ],
            "--PAGE-BREAK--",
            "# SECTION 4: CLINICAL MACHINERY & HEPA FILTRATION MANIFEST",
            "All equipment utilized on site remains dedicated strictly to Tampa Bay Medical Plaza to eliminate any potential cross-contamination between outside commercial properties.",
            [
                ["Machinery Description", "Make & Model", "Filtration Standard", "Operating Noise (dBA)", "Unit Allocation", "Deployment Schedule"],
                ["HEPA Backpack Vacuum (10 Qt)", "ProTeam Super Coach Pro", "Four-Level HEPA (99.97% @ 0.3u)", "65.8 dBA (Whisper Quiet)", "4 Dedicated Units", "Daily corridor & lobby vacuuming"],
                ["Walk-Behind Auto-Scrubber (20\")", "Tennant T300 Micro-Scrub", "Dual-cylindrical scrubber heads", "67.0 dBA", "1 Plaza Unit", "Weekly common corridor terrazzo scrub"],
                ["High-Speed Burnisher (2000 RPM)", "Clarke Ultra Speed 20T", "Active dust containment shroud", "68.0 dBA", "1 Plaza Unit", "Monthly lobby high-gloss burnishing"],
                ["Cordless Electrostatic Sprayer", "Victory Innovations VP300", "Positively charged 40-micron spray", "58.0 dBA", "2 Mobile Units", "Terminal room wrap-around disinfection"],
                ["Carpet Extraction Extractor", "NSS Stallion 818 High-Temp", "Continuous 212°F water injection", "72.0 dBA", "1 Plaza Unit", "Quarterly clinical waiting room extraction"],
            ],
            "--PAGE-BREAK--",
            "# SECTION 5: CREW ROSTER, SHIFT SCHEDULE & 120-MINUTE EMERGENCY SLA",
            "Our operations deploy a dedicated, background-screened, bilingual commercial cleaning crew assigned exclusively to the Tampa Bay Medical Plaza complex.",
            [
                ["Operational Role", "Headcount", "Shift Window", "Security / Background Clearance", "Primary Assignment"],
                ["On-Site Operations Supervisor", "1 Lead FTE", "5:30 PM – 1:30 AM (M–F)", "Level 2 FDLE Background + HIPAA Certified", "Building walk-throughs, ATP swab tests, sign-offs"],
                ["Clinical EVS Technician 1", "1 Tech FTE", "6:00 PM – 12:00 AM (M–F)", "Level 2 FDLE + OSHA Bloodborne Pathogens", "Building A (Medical Arts) Exam & Restroom Terminal"],
                ["Clinical EVS Technician 2", "1 Tech FTE", "6:00 PM – 12:00 AM (M–F)", "Level 2 FDLE + OSHA Bloodborne Pathogens", "Building B (Pediatric Center) Disinfection & Gym"],
                ["Clinical EVS Technician 3", "1 Tech FTE", "6:00 PM – 12:00 AM (M–F)", "Level 2 FDLE + OSHA Bloodborne Pathogens", "Building C (Surgical Suites) Terminal Sterilization"],
                ["Utility & Floor Specialist", "1 Tech FTE", "6:00 PM – 12:00 AM (M–F)", "Level 2 FDLE + Machine Operator Certified", "Building D + Plaza-wide auto-scrubbing & waste"],
            ],
            "120-Minute Emergency Dispatch SLA: Liza Facility Services maintains a 24/7/365 emergency on-call team. For active biological fluid spills, sudden plumbing backups, or roof condensation leaks, our emergency response technician guarantees arrival on site within two (2) hours of ticket dispatch.",
            "--PAGE-BREAK--",
            "# SECTION 6: 24-MONTH COMMERCIAL PRICING & AUTHORIZATION SCHEDULE",
            "This proposal provides comprehensive commercial coverage under a transparent, all-inclusive monthly retainer. No hidden fuel surcharges or supply escalators.",
            [
                ["Billing Component", "Coverage & Inclusions", "Billing Unit", "Monthly Rate", "Annualized Cost"],
                ["Core Monthly Clinical Retainer", "Daily custodial labor, supervisor audits, trash removal", "48,000 Sq Ft", "$3,850.00", "$46,200.00"],
                ["Consumables Dispensing Mgmt", "Stocking multi-fold hand towels, toilet tissue, foaming soap", "All 28 Restrooms", "Included", "Included in Retainer"],
                ["Quarterly High-Gloss Floor Buffing", "Machine auto-scrub and high-speed polish of VCT & Terrazzo", "All Common Areas", "Included (4x/yr)", "Included in Retainer"],
                ["Annual Strip & Wax Refinishing", "Complete chemical strip, 4 coats commercial polymer finish", "Exam Rooms & VCT", "$0.42 / sq ft", "Scheduled Project Rate"],
                ["Emergency Biological Spill Callout", "Hazardous spill cleanup, certified biohazard box disposal", "Per Occurrence", "$145.00 flat + hr", "On-Call Supplemental"],
            ],
            "# SECTION 7: QUALITY ASSURANCE & ATP BIOLUMINESCENCE SWAB PROTOCOL",
            "Quality assurance is tracked digitally via weekly Hygiena EnSURE Touch ATP bioluminescence swab testing. High-touch surfaces in procedure rooms must test below thirty (30) Relative Light Units (RLU). Any surface exceeding threshold is recleaned and re-swabbed immediately at no additional cost to building management.",
            "Authorized Contractor Attestation: Liza Iza, Managing Principal · Liza Facility Services LLC",
            "Florida Licensed Commercial Cleaning Contractor · Certificate of Liability Insurance: $5,000,000 Aggregate",
        ],
        role="deliverable",
        subtitle="Turnkey Clinical Sanitation & Facility Upkeep for 48,000 Sq Ft Medical Complex",
        meta_tag="Liza Facility Services · Commercial Proposal Deliverable",
    )

    # =========================================================================
    # 5. Drako Santa Ana (drako.santaana.glz@gmail.com)
    # =========================================================================
    files["drako_old_resume_2023.pdf"] = write_pdf_file(
        "drako_old_resume_2023.pdf",
        "Drako Santa Ana — Resume (Outdated 2021 Version)",
        [
            "# OUTDATED RESUME (2021)",
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
            "# ACTUAL WORK EXPERIENCE NOTES",
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
            "# DRAFT OPERATIONS RESUME",
            "Target Title: Logistics & Warehouse Operations Supervisor.",
            "Executive summary highlighting 14-person shift leadership and 99.8% shipping accuracy.",
        ],
        role="draft",
    )
    files["drako_resume_and_linkedin_final.pdf"] = write_pdf_file(
        "drako_resume_and_linkedin_final.pdf",
        "Drako Santa Ana — Operations Supervisor Resume & LinkedIn Optimization Master",
        [
            "# DRAKO SANTA ANA · WAREHOUSE & DOCK OPERATIONS SUPERVISOR",
            "Dallas-Fort Worth Metroplex · (214) 555-0187 · drako.santaana@gmail.com · linkedin.com/in/drakosantaana-logistics",
            "# PROFESSIONAL SUMMARY",
            "High-impact Warehouse Operations Supervisor with 6+ years of progressive leadership across fast-paced distribution and cross-dock logistics centers. Expert at directing 14+ material handlers, managing fleet staging across 30+ regional freight bays, and enforcing rigorous OSHA compliance across 120,000 sq ft facilities. Proven record of sustaining 99.8% outbound shipping accuracy across 450,000 cases and achieving 540 consecutive shifts with zero OSHA-recordable incidents.",
            "# CORE COMPETENCIES",
            "— Cross-Dock Logistics & Freight Scheduling · WMS Systems (SAP EWM, Manhattan Associates) · RF Barcode Scanning",
            "— Inventory Cycle Counts & Reconciliation · Forklift & Reach Truck Operator Certification · Team Safety Leadership",
            "— Fleet Trailer Turnaround Optimization · Labor Management & Shift Scheduling · Continuous Improvement (5S / Lean)",
            "# PROFESSIONAL EXPERIENCE",
            "Night Shift Operations Supervisor · Sunbelt Distribution, Grand Prairie, TX · 2023 – Present",
            "• Directed nightly cross-dock operations for 30+ regional freight trailers, managing 14 material handlers and equipment operators across a 120,000 sq ft high-throughput distribution center.",
            "• Sustained 99.8% order picking and dispatch accuracy across 450,000 outbound cases for major regional retail grocery accounts.",
            "• Achieved 540 consecutive shifts with zero OSHA-recordable safety incidents through daily pre-shift safety huddles and strict equipment inspection protocols.",
            "• Spearheaded the facility rollout of an upgraded RF barcode scanning system, training 22 operators and compressing average trailer dock dwell time by 22 minutes per load.",
            "Lead Material Handler & Equipment Operator · Sunbelt Distribution · 2021 – 2023",
            "• Operated sit-down electric forklifts, high-reach trucks, and order pickers; awarded Facility Operator of the Year in 2022.",
            "• Conducted weekly cycle counts across 1,400 active pallet locations, reducing inventory variance to under 0.08%.",
            "# EDUCATION & CERTIFICATIONS",
            "— OSHA 30-Hour General Industry Safety Certification · Certified Powered Industrial Truck (PIT) Trainer",
            "— Associate of Applied Science in Logistics & Supply Chain Management · Dallas College",
            "# LINKEDIN PROFILE OPTIMIZATION PACK",
            "Headline: Warehouse Operations Supervisor | Cross-Dock Logistics | 99.8% Shipping Accuracy | 540 Shifts Zero OSHA Recordables",
            "About Section: 'I build high-performing, safety-first warehouse teams that turn trailers on time and eliminate inventory discrepancies. Over the last 6 years in DFW logistics, I've managed night-shift distribution crews handling millions of cases...'",
        ],
        role="deliverable",
        subtitle="Executive Warehouse Leadership Resume & Complete LinkedIn Profile Strategy",
        meta_tag="Executive Operations & Logistics Leadership Portfolio",
    )
    files["drako_resume_operations_supervisor_v1.docx"] = copy_chat_file_alias("drako_resume_and_linkedin_v1.docx", "drako_resume_operations_supervisor_v1.docx", role="deliverable")
    files["drako_resume_operations_supervisor_final.pdf"] = copy_chat_file_alias("drako_resume_and_linkedin_final.pdf", "drako_resume_operations_supervisor_final.pdf", role="deliverable")
    files["drako_linkedin_summary_and_application_cover_letter.docx"] = write_docx_file(
        "drako_linkedin_summary_and_application_cover_letter.docx",
        "Drako Santa Ana — LinkedIn Profile Overhaul & Targeted Operations Cover Letter",
        [
            "# SECTION 1: LINKEDIN PROFILE OPTIMIZATION",
            "Target Headline: Warehouse & Dock Operations Supervisor | 540 Consecutive Shifts Without Incident | DFW Cross-Dock Leadership",
            "About Summary: Cross-dock operations supervisor with 8+ years leading fast-paced distribution and freight consolidation teams across the Dallas-Fort Worth metroplex. Passionate about sustaining 99.8% order accuracy and creating a culture of zero-incident safety.",
            "# SECTION 2: TARGETED OPERATIONS COVER LETTER",
            "Dear Hiring Director,",
            "In high-velocity warehouse distribution, consistent trailer throughput depends on two things: unshakeable safety discipline and clear crew leadership. Over the past 18 months supervising night-shift operations across 30+ regional freight bays, our team turned 450,000 cases with 99.8% accuracy and completed 540 consecutive shifts without a single OSHA recordable incident.",
            "I look forward to discussing how this operational rigor can support your regional distribution facility.",
            "Sincerely, Drako Santa Ana",
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
            "# DRAFT LEADERSHIP UPDATE — OCTOBER 2026",
            "Rough draft of Q3 recap for company all-hands and investor circular.",
            "Needs executive tone, crisp numbers on customer retention, and clear strategic goals.",
        ],
        role="source",
    )
    files["estella_october_newsletter_refined.docx"] = write_docx_file(
        "estella_october_newsletter_refined.docx",
        "Estella Williams — Refined Q3 Leadership Memo (Final)",
        [
            "# CONFIDENTIAL LEADERSHIP & INVESTOR UPDATE — OCTOBER 2026",
            "From: Estella Williams, Founder & CEO · InfiniAI Operations",
            "Team & Partners,",
            "As we close out Q3 2026, I want to share where we stand across our key operational pillars and outline our strategic focus for the upcoming quarter.",
            "# 1. CORE OPERATIONAL HIGHLIGHTS & FINANCIAL MOMENTUM",
            "We crossed $4.2M in Annual Recurring Revenue (ARR), representing an 18% quarter-over-quarter expansion. More importantly, our gross revenue retention reached 96.4%, and our net revenue expansion rate held strong at 114% across mid-market enterprise carrier fleets.",
            "Our cloud hosting optimizations and automated OCR bill of lading processing reduced infrastructure unit costs per terminal from $142 to $84/month, lifting gross margins to 77.2%. Net monthly burn dropped to $94,000, extending our cash runway to 18.2 months with $4.42M in cash reserves.",
            "# 2. TERMINAL ADOPTION & PRODUCT VELOCITY",
            "We currently power 65 active logistics facilities across the Midwest, Texas, and Pacific Northwest corridors. Apex Cold Storage expanded their deployment from 3 pilot facilities to 14 regional distribution centers after measuring an average monthly demurrage savings of $14,800 per terminal.",
            "Our mobile geofenced check-in engine has eliminated frontline terminal dead-time, reducing average trailer turn times by 38% while maintaining a 4.9/5 frontline dispatcher satisfaction score across 840 active operators.",
            "# 3. STRATEGIC PRIORITIES FOR Q4 & 2027",
            "1. Scale terminal deployments from 65 to 110 facilities, targeting $5.1M ARR by year-end.",
            "2. Finalize our SAP PartnerEdge certification and direct Blue Yonder connector.",
            "3. Onboard 4 key operational roles (Lead Dispatcher, Customer Operations, Billing Specialist, Account Executive) with structured 30-60-90 day benchmarks.",
            "Thank you for the relentless focus and execution.",
            "Warmly, Estella Williams, Founder & CEO",
        ],
        role="deliverable",
    )
    files["estella_rough_role_notes.docx"] = write_docx_file(
        "estella_rough_role_notes.docx",
        "Rough Onboarding Notes for 4 Key Operations Hires",
        [
            "# ONBOARDING NOTES",
            "Roles: Lead Logistics Dispatcher, Customer Operations Associate, Billing Specialist, Account Exec.",
            "Need 30-60-90 day benchmarks and operational KPIs for each hire.",
        ],
        role="source",
    )
    files["estella_4role_onboarding_sops_v1.docx"] = write_docx_file(
        "estella_4role_onboarding_sops_v1.docx",
        "4-Role Operations Onboarding SOPs (v1 Draft)",
        [
            "# DRAFT ONBOARDING FRAMEWORKS",
            "Draft onboarding frameworks and 30-60-90 day ramp schedules for all 4 positions.",
        ],
        role="draft",
    )
    files["estella_4role_onboarding_sops_final.pdf"] = write_pdf_file(
        "estella_4role_onboarding_sops_final.pdf",
        "Executive Operations Onboarding SOP Manual (4 Key Roles) — Final",
        [
            "# EXECUTIVE OPERATIONS ONBOARDING & GOVERNANCE MANUAL",
            "Terminal Operations & Logistics Platform · People Operations & Governance Standard",
            "This Standard Operating Procedure manual defines the 30-60-90 day ramp rubrics, operational SLAs, and core role scorecards for four critical operational positions. Each newly appointed team member must complete all gated checkpoints to achieve permanent operational sign-off.",
            "--PAGE-BREAK--",
            "# ROLE 1: LEAD LOGISTICS DISPATCHER — 30-60-90 DAY RAMP MATRIX",
            "Core Mandate: Direct regional cross-dock trailer routing, enforce driver check-in geofencing, and maintain a 99.4% on-time dispatch SLA across 65 logistics terminal nodes.",
            [
                ["Ramp Horizon", "Quantitative Metric / KPI", "Operational Milestone Objective", "Verification Artifact / Deliverable"],
                ["Day 1–30 (Intake)", ">= 98.0% On-Time Check-In", "Master geofence configuration & Blue Yonder EDI 214 sync", "Shadow 40 shift check-ins; pass TMS system exam"],
                ["Day 31–60 (Ramp)", "< 12 min Yard Dwell Time", "Manage cross-dock routing across 3 multi-terminal nodes", "Lead daily driver shift standups; audit dwell logs"],
                ["Day 61–90 (Mastery)", ">= 99.4% On-Time Dispatch", "Direct emergency storm freight diversions; train new staff", "Sign off on regional terminal SOPs; 0 safety breaches"],
            ],
            "Lead Dispatcher Daily Operational Checklist:",
            "— 06:00 Shift Kickoff: Verify overnight trailer drop counts against inbound EDI 204 manifests; flag delayed line-haul carriers.",
            "— 09:30 Yard Optimization: Audit trailer parking queue; reassign idling tractors to open dock doors to avoid detention fees.",
            "— 14:00 Cross-Dock Coordination: Confirm outbound load consolidation with warehouse staging leads.",
            "— 17:30 Shift Handover: Deliver digitized shift handover log detailing open demurrage exceptions and pending freight diversions.",
            "--PAGE-BREAK--",
            "# ROLE 2: CUSTOMER OPERATIONS ASSOCIATE — 30-60-90 DAY RAMP MATRIX",
            "Core Mandate: Frontline terminal support triage, dispatcher Intercom/Zendesk escalations, and carrier platform retention.",
            [
                ["Ramp Horizon", "Quantitative Metric / KPI", "Operational Milestone Objective", "Verification Artifact / Deliverable"],
                ["Day 1–30 (Intake)", "< 15 min First Response Time", "Triage Tier-1 terminal support tickets; memorize network workarounds", "Resolve 100 simulated support tickets with >90% CSAT"],
                ["Day 31–60 (Ramp)", "> 95% CSAT Score (>50 tkts)", "Document weekly terminal recurring bugs; run carrier webinars", "Publish 4 knowledge-base troubleshooting guides"],
                ["Day 61–90 (Mastery)", "< 2.0 hr Ticket Resolution", "Lead QBR operational reviews for Tier-2 carrier fleets", "Produce monthly churn risk audit for VP Operations"],
            ],
            "Customer Operations Incident Classification Matrix:",
            [
                ["Ticket Priority", "Incident Description", "Response SLA", "Resolution SLA", "Escalation Lead"],
                ["P1 — Critical", "Geofence outage preventing driver gate entry", "< 5 Minutes", "< 30 Minutes", "On-Call DevOps Engineer"],
                ["P2 — High", "EDI manifest sync delay > 15 minutes", "< 15 Minutes", "< 60 Minutes", "Lead Integrations Specialist"],
                ["P3 — Medium", "Individual dispatcher login / SSO failure", "< 30 Minutes", "< 4 Hours", "Customer Operations Associate"],
                ["P4 — Low", "Reporting export or UI cosmetic discrepancy", "< 2 Hours", "< 24 Hours", "Product Operations Analyst"],
            ],
            "--PAGE-BREAK--",
            "# ROLE 3: BILLING & ACCOUNTS SPECIALIST — 30-60-90 DAY RAMP MATRIX",
            "Core Mandate: Terminal SaaS subscription billing, automated ACH reconciliation, and carrier detention fee dispute escrow management.",
            [
                ["Ramp Horizon", "Quantitative Metric / KPI", "Operational Milestone Objective", "Verification Artifact / Deliverable"],
                ["Day 1–30 (Intake)", "100% Invoice Accuracy", "Reconcile weekly Stripe/Paystack billing; audit dunning workflows", "Reconcile 65 terminal billing accounts to $0.00 variance"],
                ["Day 31–60 (Ramp)", "DSO < 22 Calendar Days", "Resolve carrier detention escrow disputes within 48 hours", "Implement automated Net-15 ACH debit reminders"],
                ["Day 61–90 (Mastery)", "< 0.5% Bad Debt Expense", "Automate monthly GAAP ASC 606 revenue recognition schedules", "Deliver clean audit package for external CPA review"],
            ],
            "Billing Workflow Reconciliation Standards:",
            "— Weekly Dunning Cadence: Day 3 post-due automated reminder; Day 7 phone outreach to carrier controller; Day 14 account suspension warning.",
            "— Demurrage Escrow Disputes: Escrow deposits held in segregated FDIC-insured operating accounts pending GPS dwell-time verification.",
            "--PAGE-BREAK--",
            "# ROLE 4: ENTERPRISE ACCOUNT EXECUTIVE — 30-60-90 DAY RAMP MATRIX",
            "Core Mandate: Mid-market logistics terminal sales, 3PL discovery scoping, and pilot-to-annual contract conversion.",
            [
                ["Ramp Horizon", "Quantitative Metric / KPI", "Operational Milestone Objective", "Verification Artifact / Deliverable"],
                ["Day 1–30 (Intake)", "30 Qualified Lead Discovery", "Master MEDDPICC qualification and interactive demurrage calculator", "Complete 5 mock discovery pitches before Executive team"],
                ["Day 31–60 (Ramp)", "12 Pilots in Evaluation", "Compress terminal sales cycle from 64 to < 40 days", "Deliver $250K in advanced pipeline opportunities"],
                ["Day 61–90 (Mastery)", "$450K Annualized ACV Closed", "Establish referral partnerships with 2 regional freight brokerages", "Maintain >30% win rate on formal RFP submissions"],
            ],
            "--PAGE-BREAK--",
            "# SYSTEMS ACCESS, PERMISSIONS & TOOLCHAIN MATRIX",
            "All operational personnel are provisioned with role-based access control (RBAC) following background clearance verification.",
            [
                ["System / Platform", "Role 1: Dispatcher", "Role 2: Support", "Role 3: Billing", "Role 4: Sales", "Security Protocol"],
                ["Terminal Yard Engine", "Super Administrator", "Read / Triage Only", "No Access", "Demo Sandbox", "Hardware FIDO2 Security Key"],
                ["Stripe & NetSuite ERP", "No Access", "View Customer Only", "Full Administrator", "No Access", "Enforced IP Whitelisting + 2FA"],
                ["HubSpot Enterprise CRM", "View Terminal Notes", "Ticket Link Only", "Invoice Link Only", "Full Pipeline Edit", "Google Workspace SSO + 2FA"],
                ["AWS CloudWatch / Logs", "Dashboard View", "Error Query Only", "No Access", "No Access", "Role-Based IAM Session Keys"],
            ],
            "# GOVERNANCE & SIGN-OFF ATTESTATION",
            "Upon completion of the 90-day ramp period, the supervising manager and Chief Executive Officer conduct a formal performance review. Successful candidates transition from probationary to regular full-time operational status.",
            "Executive Reviewer: Estella Williams, Founder & Chief Executive Officer",
            "Approved: People Operations & Talent Governance Committee · October 2026",
        ],
        role="deliverable",
        subtitle="Standard Operating Procedures & 30-60-90 Day Ramp Rubrics for Operations Scale",
        meta_tag="Terminal Operations Governance & People Operations · SOP Manual",
    )
    files["estella_q4_board_deck_rough_bullets.docx"] = write_docx_file(
        "estella_q4_board_deck_rough_bullets.docx",
        "Q4 Board Deck — Unformatted Bullet Dump (40 Pages)",
        [
            "# RAW BOARD BULLETS",
            "Raw bullets on Q3 financials, ARR expansion, churn breakdown, and 2027 hiring plan.",
            "Need condensed into a powerful 16-slide presentation and 2-page briefing memo.",
        ],
        role="source",
    )
    files["estella_q4_executive_investor_deck_v1.docx"] = write_docx_file(
        "estella_q4_executive_investor_deck_v1.docx",
        "Q4 Board Deck Slide Outline & Speaker Script (v1 Draft)",
        [
            "# 16-SLIDE OUTLINE",
            "16-slide narrative outline structured for Series A/B board members.",
        ],
        role="draft",
    )
    files["estella_q4_board_briefing_memo_final.docx"] = write_docx_file(
        "estella_q4_board_briefing_memo_final.docx",
        "Q4 Executive Board Briefing Memo — Estella Williams (Final)",
        [
            "# CONFIDENTIAL BOARD OF DIRECTORS BRIEFING MEMO",
            "Date: October 21, 2026 · Terminal Operations & Logistics Inc. · Executive Governance Record",
            "TO: Board of Directors, Terminal Operations & Logistics Inc.",
            "FROM: Estella Williams, Founder & Chief Executive Officer",
            "SUBJECT: Q3 2026 Operational Performance, Financial Trajectory, and Series A Capital Formation",
            "# SECTION 1: EXECUTIVE OVERVIEW & Q3 PERFORMANCE SNAPSHOT",
            "During the third quarter of fiscal year 2026, the company demonstrated sustained operational acceleration across its core enterprise yard and terminal logistics platform. We concluded Q3 at $4,200,000 in Annual Recurring Revenue (ARR), representing an 18.2% quarter-over-quarter expansion and 142% net growth year-over-year. Mid-market enterprise carrier adoption accelerated across our priority freight corridors (Midwest, Texas, and Pacific Northwest), driven by demonstrable customer ROI in demurrage and dock detention prevention.",
            "# SECTION 2: FINANCIAL RECONCILIATION & TRAJECTORY",
            "Gross margin expanded 120 basis points to 77.2%, reflecting infrastructure efficiency gains from automated optical character recognition (OCR) of bills of lading and container drayage interchange receipts. Hosting cost per terminal fell from $142/mo to $84/mo. Ending cash balance stood at $4,420,000 with 18.2 months runway at current net burn.",
            [
                ["Financial Metric", "Q1 2026 Actual", "Q2 2026 Actual", "Q3 2026 Actual", "Q4 2026 Target", "YoY Expansion"],
                ["Annual Recurring Revenue (ARR)", "$2,800,000", "$3,450,000", "$4,200,000", "$5,100,000", "+142.8%"],
                ["Active Logistics Terminals", "38 Terminals", "51 Terminals", "65 Terminals", "84 Terminals", "+128.5%"],
                ["Gross Profit Margin %", "73.4%", "76.0%", "77.2%", "78.5%", "+380 bps"],
                ["Average Monthly Net Burn", "$118,000", "$104,000", "$94,000", "$90,000", "-23.7%"],
                ["Cash & Liquid Reserves", "$4,920,000", "$4,680,000", "$4,420,000", "$4,150,000", "18.2 Mo Runway"],
            ],
            "# SECTION 3: ENTERPRISE CUSTOMER COHORT HEALTH & NET RETENTION",
            "Gross Revenue Retention (GRR) remained steady at 96.4%, while Net Revenue Retention (NRR) reached 114.2%. Over the past six consecutive quarters, we have experienced zero enterprise logo churn. Customer payback period on fully loaded CAC ($480/terminal) remains under 8 months against an average annual customer value of $6,084.",
            [
                ["Customer Tier Segment", "Active Logos", "Ending ARR", "GRR %", "NRR %", "Avg Demurrage Saved / Mo"],
                ["Tier 1: Enterprise 3PLs (10+ yards)", "4 Fleets", "$1,480,000", "100.0%", "124.0%", "$14,800 / Facility"],
                ["Tier 2: Mid-Market Regional (3–9 yards)", "11 Fleets", "$1,840,000", "96.5%", "112.5%", "$8,200 / Facility"],
                ["Tier 3: Single Terminal Hubs", "22 Fleets", "$880,000", "94.2%", "102.0%", "$4,100 / Facility"],
                ["Consolidated Portfolio Total", "37 Fleets", "$4,200,000", "96.4%", "114.2%", "$9,450 Average"],
            ],
            "Apex Cold Storage Case Study: Apex expanded their pilot deployment from 3 to 14 distribution centers during Q3, documenting an average savings of $14,800/month per terminal in avoided driver detention claims and achieving full software payback in 28 days.",
            "# SECTION 4: FY 2027 GATED HEADCOUNT ROSTER",
            "Headcount additions for FY 2027 are subject to strict ARR revenue gating milestones. No role may be posted or contracted prior to hitting the specified gate trigger.",
            [
                ["Department", "Target Role Title", "Planned Quarter", "ARR Gate Trigger", "Fully Loaded Comp", "Option Pool %"],
                ["Sales & Commercial", "VP Enterprise Sales", "Q1 2027", "$4,800,000 ARR", "$260,000 + Comm", "1.25% Stock Pool"],
                ["Operations & Support", "Lead Logistics Dispatcher", "Q1 2027", "$4,600,000 ARR", "$85,000 Base", "0.15% Stock Pool"],
                ["Operations & Support", "Customer Operations Associate", "Q1 2027", "$4,600,000 ARR", "$70,000 Base", "0.10% Stock Pool"],
                ["Finance & Accounting", "Billing & Accounts Specialist", "Q2 2027", "$5,200,000 ARR", "$78,000 Base", "0.10% Stock Pool"],
                ["Engineering Pod", "Staff Distributed Systems Eng", "Q2 2027", "$5,200,000 ARR", "$195,000 Base", "0.40% Stock Pool"],
                ["Commercial Sales", "Enterprise Account Executive (2)", "Q2 2027", "$5,400,000 ARR", "$120,000 + Comm", "0.20% Stock Pool"],
            ],
            "# SECTION 5: SERIES A CAPITAL FORMATION & USE OF FUNDS",
            "We are initiating preliminary discussions for a $4,500,000 Series A funding round targeted for Q1 2027. Proceeds will be deployed strictly into growth drivers with measurable unit economics.",
            [
                ["Capital Allocation Category", "Capital Amount", "Percentage", "Strategic Focus & Milestone Deliverable"],
                ["Distributed Engineering Engine", "$2,475,000", "55.0%", "Build autonomous yard dispatch AI and Blue Yonder native connector"],
                ["Enterprise Sales & GTM Expansion", "$1,350,000", "30.0%", "Hire 4 Enterprise AEs and expand into California & Southeast hubs"],
                ["Regulatory & Balance Sheet Reserve", "$675,000", "15.0%", "Maintain 24-month minimum cash buffer through profitability"],
            ],
            "# SECTION 6: ITEMS SUBMITTED FOR FORMAL BOARD APPROVAL",
            "1. Formal adoption of the FY 2027 Annual Operating Plan and Gated Headcount Budget as outlined in Section 4.",
            "2. Authorization to expand the employee stock option pool by 3.5% to accommodate senior executive recruiting.",
            "3. Approval of minutes from the July 16, 2026, quarterly board meeting.",
            "Respectfully submitted, Estella Williams, Founder & Chief Executive Officer",
        ],
        role="deliverable",
    )
    files["estella_q4_investor_deck_slide_copy_final.pdf"] = write_pdf_file(
        "estella_q4_investor_deck_slide_copy_final.pdf",
        "Q4 Board Deck — Slide Copy & Executive Visual Layouts",
        [
            "# SLIDE 1: TITLE & EXECUTIVE OVERVIEW",
            "— Headline: InfiniAI Logistics Platform · Q4 2026 Executive Investor Update",
            "— Subhead: Presented by Estella Williams, Founder & CEO · Confidential Board Review",
            "# SLIDE 2: Q3 PERFORMANCE SNAPSHOT ($4.2M ARR, 114% NET EXPANSION)",
            "— $4.2M ARR (+18% QoQ) · 114% NRR across enterprise carriers · 77.2% Gross Margin",
            "— $94K average net monthly burn with 18.2 months cash runway ($4.42M cash balance)",
            "# SLIDE 3: CUSTOMER RETENTION & COHORT HEALTH",
            "— Zero enterprise logo churn across 6 consecutive quarters",
            "— 96.4% Gross Revenue Retention · CAC payback under 8 months",
            "# SLIDE 4: PRODUCT ROADMAP & ENTERPRISE MOAT",
            "— Live geofenced trailer arrival check-in with multilingual driver SMS",
            "— Bi-directional SAP S/4HANA & Blue Yonder EDI connectors in pilot",
            "— Independent SOC-2 Type II certification completed with zero exceptions",
            "# SLIDE 5: UNIT ECONOMICS & EFFICIENCY",
            "— 17.5x LTV/CAC ratio · $507 monthly ARPU · Cloud hosting down to $84/terminal",
            "# SLIDE 6: 2027 HEADCOUNT & STRATEGIC PRIORITIES",
            "— Scale terminal footprint from 65 to 110 facilities",
            "— Targeted Series A ($4.5M) preparation for Q1 2027 expansion",
        ],
        role="deliverable",
        subtitle="16-Slide Executive Presentation Script & Visual Narrative Guide",
        meta_tag="Terminal Operations & Logistics Platform · Governance Record",
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
        "Kaylee Skincare — 4-Part Welcome & Botanical Ritual Email Sequence (Final)",
        [
            "# EMAIL 1: WELCOME TO THE BOTANICAL SANCTUARY",
            "Subject: Welcome to the sanctuary (+ 15% off your first ritual)",
            "Preview Text: Pure cold-pressed botanicals crafted for sensitive, stressed skin.",
            "Dear {{First_Name}},",
            "Welcome to our small-batch skincare sanctuary. We founded Kaylee Skincare on a simple premise: your skin doesn't need 10 aggressive chemical steps—it needs pure, nutrient-dense lipid restoration that works with your natural acid mantle, not against it.",
            "To welcome you to our community, here is 15% off your first order with code RITUAL15 at checkout.",
            "Where to start:",
            "If your skin feels tight, inflamed, or depleted, our Midnight Botanical Nectar Serum and Ceramide Barrier Cream were formulated specifically to calm irritation overnight.",
            "[Explore the Clean Botanical Collection ->]",
            "With warmth, Kaylee Cabreros, Founder",
            "# EMAIL 2: THE COLD-PRESSED PHILOSOPHY (BEHIND THE FORMULA)",
            "Subject: Why we cold-press our botanical oils (The story behind the blue nectar)",
            "Preview Text: Meet the rare Moroccan Blue Tansy and wild-harvested rosehip seed oil.",
            "Dear {{First_Name}},",
            "Ever wonder why our Midnight Botanical Nectar Serum has that deep, soothing sapphire hue? That color comes naturally from chamazulene—a potent anti-inflammatory compound released during the gentle steam distillation of Moroccan Blue Tansy flowers.",
            "Most commercial brands use high-heat chemical extraction that strips delicate antioxidants. We partner exclusively with certified organic, small-plot growers to cold-press our jojoba, rosehip, and squalane oils in small batches under 85°F.",
            "The result is a silky, featherweight elixir that penetrates down to the stratum corneum without clogging pores or leaving greasy residue.",
            "[Discover the Sourcing Journey ->]",
            "# EMAIL 3: SKIN BARRIER 101 — STOP STRIPPING YOUR ACID MANTLE",
            "Subject: Skin barrier 101: Stop stripping your acid mantle",
            "Preview Text: The 3 signs your moisture barrier is crying for help.",
            "Dear {{First_Name}},",
            "If your skin stings when applying moisturizer, looks shiny yet feels parched, or experiences sudden unexpected breakouts, your acid mantle is compromised.",
            "Aggressive foaming cleansers and high-percentage acids erode the delicate lipid matrix that shields against environmental pathogens and moisture loss. Here is our 3-step restorative morning ritual:",
            "1. Cleanse gently: Rinse with lukewarm water or our gentle milky cleanser. Never strip.",
            "2. Mist generously: Spritz Hydra-Firm Copper Peptide Mist over clean skin to flood cells with hyaluronic hydration.",
            "3. Lock with Ceramides: Press a dime-sized amount of Ceramide Barrier Cream over damp skin to seal in hydration.",
            "[Build Your Barrier Repair Ritual ->]",
            "# EMAIL 4: JOIN THE VIP SMALL-BATCH BOTANICAL CIRCLE",
            "Subject: An invitation to our VIP small-batch botanical circle",
            "Preview Text: Early harvest reserves, private studio drops, and complimentary refills.",
            "Dear {{First_Name}},",
            "Because we source raw botanical harvests in limited seasonal quantities, our small batches frequently sell out within days of release.",
            "As a valued subscriber, you now have access to our VIP Circle perks:",
            "— 48-hour priority access to limited seasonal harvests and holiday gift editions.",
            "— Free carbon-neutral shipping on all replenishment orders over $50.",
            "— Complimentary botanical sample vial with every handcrafted order.",
            "Your 15% welcome code RITUAL15 is active through Sunday midnight.",
            "[Shop Your Personalized Ritual ->]",
            "With gratitude, Kaylee & the Botanical Formulation Team",
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
            "# 1. EXECUTIVE DIAGNOSTIC SYNTHESIS (FROM 18 PAGES OF C-SUITE INTERVIEWS)",
            "Diagnostic discovery across the Chief Technology Officer, VP of Product, and VP of People revealed three systemic organizational bottlenecks impeding cross-functional velocity and manager retention.",
            "# 2. THEME 1: ENGINEERING & PRODUCT DELIVERY SILOS",
            "— Finding: Engineering sprint planning operates in isolation from customer success feedback, resulting in 40% of sprint capacity being re-routed to ad-hoc customer fire drills.",
            "— Strategic Intervention: Transition from monthly output metrics to joint quarterly Objectives & Key Results (OKRs). Embed customer operations leads directly into bi-weekly sprint planning sessions.",
            "# 3. THEME 2: SALES-TO-ROADMAP FEEDBACK DISCONNECT",
            "— Finding: Regional enterprise sales executives report promising custom features to prospects without engineering architectural feasibility sign-off, driving customer churn at onboarding.",
            "— Strategic Intervention: Institute a bi-weekly Product-Sales Roadmap Governance Council with formal MEDDPICC architectural gates before non-standard features are committed to master service agreements.",
            "# 4. THEME 3: MANAGER BURNOUT & MID-TIER LEADERSHIP RETENTION",
            "— Finding: Newly promoted team managers spend 18+ hours weekly in unstructured meetings without clear escalation frameworks, driving high attrition among technical leads.",
            "— Strategic Intervention: Establish peer coaching cohorts and roll out standardized 1-on-1 performance review templates and asynchronous decision frameworks.",
            "# 5. 6-WEEK MODULAR WORKSHOP CURRICULUM",
            "— Week 1: Executive Alignment & Shared Vision Calibration (Half-day intensive with C-suite stakeholders).",
            "— Week 2: Joint OKR Mapping & Cross-Functional Dependency Architecture.",
            "— Week 3: Frontline Delegation & Manager Empowerment Systems.",
            "— Week 4: Eliminating Meeting Bloat & Asynchronous Operating Rhythms.",
            "— Week 5: Accountability Frameworks & 360 Peer Feedback Implementation.",
            "— Week 6: Long-Term Governance Cadence & Executive Retreat Deliverables Review.",
        ],
        role="deliverable",
        subtitle="Executive Alignment Strategy, Diagnostic Insights & 6-Week Leadership Blueprint",
        meta_tag="Executive Advisory Deliverable · Cami Kurtz Leadership Consulting",
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
    files["orozco_commercial_flat_roof_job_photo.png"] = write_screenshot_png_file(
        "orozco_commercial_flat_roof_job_photo.png",
        url="FLIR E76 Thermal Imaging System · Job Site #TX-8840",
        site_title="Orozco Roofing Systems · Commercial Inspection",
        hero_headline="Field Job Photo: 42,000 Sq Ft Commercial TPO Heat-Welded Seams",
        hero_subhead="Robotic hot-air welded lap seams & probe verification on Carlisle 60-mil membrane.",
        items=[
            "Inspection Point 1: 1.5-inch continuous hot-air fused lap seam passed 100% mechanical cotter probe test.",
            "Inspection Point 2: R-30 polyiso insulation board mechanically fastened with #15 heavy-duty fasteners (FM 1-90).",
            "Inspection Point 3: FLIR Infrared thermal moisture survey confirmed zero subsurface deck water pockets.",
            "Inspection Point 4: 24-gauge Galvalume parapet coping with hemmed drip edge and continuous cleat verified.",
            "Inspection Point 5: Direct manufacturer technical audit scheduled for 20-Year NDL warranty issuance.",
        ],
        kind="photo",
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
        "Orozco Commercial & Industrial Roofing — Master Technical Specifications & Commercial Bid Deck",
        [
            "# SECTION 1: HOMEPAGE MASTER COPY DECK & VALUE PROPOSITION",
            "NAVIGATION BAR: Commercial Flat Roofing · Architectural Standing Seam · Storm Restoration & Hail Recovery · 20-Year NDL Warranties · Project Gallery · Commercial Diagnostic Intake",
            "HERO BADGE: Rio Grande Valley · Commercial Flat Roofing Specialists Since 2012",
            "HERO HEADLINE: Engineered Commercial Flat Roofing & Industrial Storm Restoration Built for South Texas Heat.",
            "HERO SUBHEAD: Specializing in single-ply TPO, elastomeric fluid-applied restoration membranes, and architectural standing seam metal. Protecting industrial logistics warehouses, shopping centers, medical complexes, and schools across McAllen, Brownsville, and Harlingen.",
            "CALL-TO-ACTION BUTTONS: Primary: [Schedule 21-Point Commercial Roof Assessment] · Secondary: [Download 20-Year NDL Warranty Guide]",
            "LOCAL PROOF STRIP: Carlisle SynTec Certified Applicator · Elevate (Firestone) Red Shield Partner · GAF Master Commercial Contractor · $2M Commercial Liability & Full Workers' Comp · 14+ Years RGV Operations",
            "COMPANY OVERVIEW: Blistering subtropical sun, high UV indexes, and severe Gulf Coast windstorms destroy commercial roofs not specifically engineered for South Texas climates. Family-owned and operated since 2012, Orozco Roofing delivers turnkey commercial installations that meet strict FM 1-90 and 1-120 wind uplift codes while lowering facility cooling loads by up to 30%.",
            "CUSTOMER TESTIMONIAL: 'Orozco re-roofed our 42,000 sq ft logistics distribution facility in Pharr without disrupting single-day shipping operations. Their Carlisle 20-Year NDL warranty gave our board total peace of mind.' — Hector V., Facilities Director, Valley Logistics Hub",
            "--PAGE-BREAK--",
            "# SECTION 2: COMMERCIAL SYSTEMS TECHNICAL COMPARISON MATRIX",
            "Commercial building owners require precise performance specifications to evaluate capital roofing investments. The table below outlines our primary commercial membrane systems:",
            [
                ["Commercial System Type", "Mil Thickness / Gauge", "Solar Reflectance (SRI)", "Seam Tensile Strength", "Wind Uplift Rating", "Warranty Term Available", "Best Commercial Application"],
                ["Carlisle Sure-Weld TPO", "60-Mil & 80-Mil Single-Ply", "Initial SRI: 108 (High White)", "Heat-Welded: 450 lbf/in", "FM 1-90 / FM 1-120", "20-Year & 25-Year NDL", "Big-box retail, logistics warehouses, low-slope roofs"],
                ["Elevate UltraPly TPO", "60-Mil Reinforced", "Initial SRI: 106", "Hot-Air Fused: 420 lbf/in", "FM 1-90 Approved", "20-Year Red Shield NDL", "Medical plazas, commercial office parks, climate storage"],
                ["Architectural Standing Seam", "24-Gauge Galvalume Steel", "Kynar 500 Coated (SRI 65)", "Mechanical Double-Lock", "140+ MPH Hurricane Rated", "30-Year Finish / 20-Yr Weathertight", "Mansard facades, pitched banks, churches, schools"],
                ["Fluid-Applied Silicone Restor.", "High-Solids 96% Silicone", "Initial SRI: 110", "Monolithic Seamless", "FM 4470 Wind Class 1", "15-Year Renewable Warranty", "Restoring aged metal panels, weathered EPDM, mod-bit"],
            ],
            "--PAGE-BREAK--",
            "# SECTION 3: 21-POINT COMMERCIAL DIAGNOSTIC INSPECTION CHECKLIST",
            "Our certified commercial estimators conduct exhaustive non-destructive electronic moisture surveys and structural audits prior to issuing any bid proposal.",
            [
                ["Inspection Domain", "Diagnostic Check Item", "Inspection Instrument / Tool", "Pass / Fail Operational Threshold", "Recommended Remediation Action"],
                ["Deck & Substrate", "Subsurface Deck Moisture Scanning", "FLIR Infrared Thermal Camera", "Moisture pocket area < 5% of total roof", "Core sample test; spot tear-off of wet insulation board"],
                ["Fasteners & Uplift", "Mechanical Fastener Pull-Out Test", "ComTen Hydraulic Pull Tester", "Minimum 300 lbf pull-out resistance", "Upgrade to heavy-duty #15 fasteners and barbed stress plates"],
                ["Membrane & Seams", "Robotic Hot-Air Lap Seam Integrity", "Cotter Seam Probe & Visual Check", "100% monolithic continuous weld (no voids)", "Re-weld cold laps; install heat-fused 6-inch TPO target patch"],
                ["Parapet & Flashing", "Coping Cap & Counterflashing Drip", "Physical gauge measure & seal check", "Hemmed drip edge, butyl sealant intact", "Replace aged termination bar; install 24-ga Galvalume coping"],
                ["Penetrations & Drains", "HVAC Curb Flashing & Primary Drains", "Drain ring clamping bolt torque", "Unobstructed drain sumps; 8\" curb height", "Install new molded pipe boots; clear drain cast-iron strainer rings"],
                ["Expansion Joints", "Structural Seismic Expansion Joint", "Bellows elasticity inspection", "Continuous neoprene bellow (no tears)", "Replace deteriorated expansion joint cover with factory transition"],
            ],
            "--PAGE-BREAK--",
            "# SECTION 4: 20-YEAR NO DOLLAR LIMIT (NDL) MANUFACTURER WARRANTIES",
            "What a Manufacturer-Backed 20-Year NDL Warranty Means for Property Owners:",
            "— 100% Comprehensive Financial Guarantee: Standard prorated material warranties exclude certified labor and reduce coverage every year. A genuine No Dollar Limit (NDL) warranty issued directly by Carlisle SynTec or Elevate guarantees 100% coverage of all certified materials AND certified contractor labor to correct any roof leak for the full 20-year term.",
            "— Direct Manufacturer Technical Audit: An independent field engineering representative from the manufacturer travels to the property to perform a destructive weld probe and probe 100% of lap seams before issuing the warranty certificate.",
            "--PAGE-BREAK--",
            "# SECTION 5: COMMERCIAL BID COST BREAKDOWN & UNIT PRICE MATRIX",
            "This transparent bidding schedule outlines square-foot unit economics for commercial capital replacement projects across the Rio Grande Valley.",
            [
                ["Roof Section Scope", "Commercial System", "Roof Area (Sq Ft)", "Squares (100 sq ft)", "Prep & Tear-Off ($/Sq)", "Membrane & Board ($/Sq)", "Labor & Supervision ($/Sq)", "Section Bid Total ($)"],
                ["Section A: Main Warehouse", "60-mil White TPO", "18,500 sq ft", "185.0 Squares", "$85.00 / Sq", "$240.00 / Sq", "$115.00 / Sq", "$81,400.00"],
                ["Section B: Office Mansard", "24-ga Standing Seam", "3,200 sq ft", "32.0 Squares", "$110.00 / Sq", "$385.00 / Sq", "$160.00 / Sq", "$20,960.00"],
                ["Section C: Loading Overhang", "Fluid-Applied Silicone", "2,400 sq ft", "24.0 Squares", "$45.00 / Sq", "$195.00 / Sq", "$95.00 / Sq", "$8,040.00"],
                ["Subtotal Base Commercial Bid", "All 3 Roof Sections", "24,100 sq ft", "241.0 Squares", "Blended: $84.35", "Blended: $254.77", "Blended: $119.00", "$110,400.00"],
                ["Manufacturer 20-Yr NDL Fee", "Carlisle SynTec Inspection", "Plaza-wide", "Flat Assessment", "N/A", "N/A", "Certified Audit", "$2,850.00"],
                ["Total Turnkey Project Bid", "Firm Fixed Price Contract", "24,100 sq ft", "241.0 Squares", "Turnkey Scope", "Materials + Labor", "Full Warranty Included", "$113,250.00"],
            ],
            "# SECTION 6: COMMERCIAL INTAKE & 24/7 STORM HOTLINE",
            "Commercial Inspection Booking Desk: (956) 555-0188 · Email: bids@orozcoroofing.com",
            "Chief Estimator & Commercial Director: Azael Orozco · McAllen & Brownsville, TX",
            "Texas Registered Contractor · Carlisle SynTec Applicator ID: #TX-98421",
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
    orozco_html = load_showcase_template("showcase_orozco.html")
    files["orozco_roofing_website_prototype.html"] = write_html_file(
        "orozco_roofing_website_prototype.html",
        "Orozco Commercial & Residential Roofing · South Texas",
        orozco_html,
        role="deliverable",
    )

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
        "HubSpot Enterprise CRM Architecture & Deal Stage Specification — DockStream Logistics",
        [
            "# 1. OPERATIONAL MANDATE & CRM INFRASTRUCTURE PURPOSE",
            "This technical specification defines the lead lifecycle architecture, opportunity stage gating criteria, automated territory routing, and weighted ARR forecasting formulas implemented within HubSpot Enterprise CRM for DockStream Logistics.",
            "Mandate: Eliminate pipeline stagnation, ensure 100% data hygiene across mid-market 3PL deals, and automate sales handoffs between Business Development Representatives (BDRs), Enterprise Account Executives (AEs), and Solutions Engineers (SEs).",
            "--PAGE-BREAK--",
            "# 2. LEAD LIFECYCLE STAGES & QUALIFICATION RUBRIC",
            "Leads advance strictly based on programmatic behavioral triggers and verified operational criteria.",
            [
                ["Lifecycle Stage", "Qualification Gating Trigger", "Routing SLA", "Stage Owner", "Mandatory CRM Fields Required"],
                ["Lead (Uncontacted)", "Inbound form submission / cold Apollo list", "< 15 Minutes", "BDR Inbound Queue", "Facility Name, State, First/Last Name, Work Email"],
                ["Marketing Qualified (MQL)", "ROI Calculator used OR Whitepaper download", "< 2 Hours", "Dedicated Territory BDR", "Fleet Bay Count (est), Monthly Trailer Volume"],
                ["Sales Qualified (SQL)", "BDR discovery call completed; meets MEDDPICC", "< 24 Hours", "Regional Account Exec", "Verified Bay Count (>=5), Current WMS/TMS, Budget Authority"],
                ["Sales Opportunity", "Scoping demo scheduled with VP Logistics / GM", "Active Deal Stage", "Enterprise Account Exec", "Estimated Contract Value, Target Go-Live Date, Decision Criteria"],
                ["Closed Won Customer", "Signed annual MSA + Stripe payment method", "< 4 Hours to Onboarding", "Customer Success Lead", "Billing Contact, Invoice Schedule, Bay Layout Schema"],
            ],
            "--PAGE-BREAK--",
            "# 3. OPPORTUNITY PIPELINE STAGES & FORMAL EXIT GATES",
            "Opportunities must satisfy all exit gate requirements before advancing. Reversion to earlier stages requires VP of Sales authorization.",
            [
                ["Pipeline Stage", "Win Prob %", "Max Days in Stage", "Formal Exit Gate Criteria", "Required Deliverable / Attachment"],
                ["Stage 1: Discovery Scoping", "20%", "14 Days", "Identify 3 core pain points; verify 10+ daily trailers", "Completed MEDDPICC Scoping Matrix (.pdf)"],
                ["Stage 2: Technical Architecture", "40%", "21 Days", "Confirm TMS compatibility (EDI 204/214); demo yard engine", "Technical Feasibility Sign-Off Form (.docx)"],
                ["Stage 3: Business Case & ROI", "60%", "14 Days", "Deliver customized demurrage savings financial model", "Locked Excel ROI Model with client baselines"],
                ["Stage 4: Pilot Agreement", "80%", "10 Days", "Security / SOC-2 clearance passed; 14-day MSA signed", "Executed Master Services Agreement (MSA)"],
                ["Stage 5: Legal & Redlines", "90%", "7 Days", "Mutual indemnification and SLA terms agreed", "Redline Legal Reconciliation Document"],
                ["Stage 6: Closed Won", "100%", "0 Days", "First month software fee processed; onboarding kickoff set", "Countersigned Contract + Active Stripe Customer ID"],
            ],
            "--PAGE-BREAK--",
            "# 4. DISQUALIFICATION REASON CODES & NURTURE CADENCE",
            "Deals disqualified in any stage must be tagged with a standardized reason code and assigned to automated marketing workflows.",
            [
                ["Reason Code", "Disqualification Category", "Threshold Trigger", "Sales Rep Action", "Assigned Marketing Workflow"],
                ["DQ-01: Under-Scale", "Facility Bay Count < 5 bays", "Low trailer throughput (<10/day)", "Disqualify; tag 'Self-Service Tier'", "Quarterly automated product digest"],
                ["DQ-02: Legacy WMS", "Unsupported proprietary TMS", "No API / EDI connectivity feasible", "Escalate to Solutions Architect", "Engineering roadmap alert sequence"],
                ["DQ-03: Budget Freeze", "CapEx / OpEx procurement freeze", "Decision postponed > 6 months", "Set task reminder 90 days out", "Bi-weekly logistics case study nurture"],
                ["DQ-04: Incumbent Contract", "Locked in multi-year contract", "Existing vendor contract has >12 mo", "Log contract renewal expiration date", "Pre-renewal sequence 90 days before expiry"],
                ["DQ-05: Non-Responsive", "Ghosted after demo / proposal", "Zero response across 5 touches over 14d", "Send 'Breakup' email; close lost", "Re-engagement campaign 60 days out"],
            ],
            "--PAGE-BREAK--",
            "# 5. WEIGHTED PIPELINE FORECASTING & REVENUE FORMULAS",
            "Quarterly ARR forecasting calculates weighted contract value automatically within HubSpot Enterprise Reporting.",
            [
                ["Deal Stage", "Stated Pipeline ACV", "Probability Multiplier", "Weighted Forecast ARR", "Forecasting Category"],
                ["Discovery Scoping (20%)", "$320,000", "0.20", "$64,000", "Pipeline (Tentative)"],
                ["Technical Architecture (40%)", "$480,000", "0.40", "$192,000", "Best Case"],
                ["Business Case & ROI (60%)", "$540,000", "0.60", "$324,000", "Most Likely"],
                ["Pilot Agreement (80%)", "$360,000", "0.80", "$288,000", "Commit (High Confidence)"],
                ["Legal & Redlines (90%)", "$180,000", "0.90", "$162,000", "Commit (Near Close)"],
                ["Closed Won Active (100%)", "$650,000", "1.00", "$650,000", "Closed Revenue"],
                ["Total Q4 Sales Pipeline", "$2,530,000", "Blended: 66.4%", "$1,680,000", "Consolidated Forecast ARR"],
            ],
            "# 6. STALE DEAL AUTOMATION & SLA ENFORCEMENT RULES",
            "1. Stale Deal Flag: Any active opportunity without logged sales touch (call, email, meeting) for greater than seven (7) business days is automatically flagged with a red visual badge in HubSpot pipeline views.",
            "2. Management Escalation: If a deal remains inactive for fourteen (14) business days, notification is routed to the VP of Sales and the deal is removed from the weighted forecast.",
            "Architecture Author: Jack Johnson · Enterprise Sales Operations · DockStream Logistics",
        ],
        role="deliverable",
        subtitle="Enterprise CRM Pipeline Architecture, Lead Routing Rules & Forecasting Formulas",
        meta_tag="DockStream Logistics · Enterprise CRM & Sales Architecture",
    )
    files["johnson_b2b_site_and_deck_brief.docx"] = write_docx_file(
        "johnson_b2b_site_and_deck_brief.docx",
        "Q4 B2B Website & 12-Slide Enterprise Deck Brief",
        [
            "# CREATIVE BRIEF",
            "Target Audience: VP of Logistics and Operations Directors at mid-market 3PLs.",
            "Core Goal: Communicate 38% dock turn time improvement and eliminate dispatch friction.",
        ],
        role="source",
    )
    files["johnson_b2b_deck_and_copy_v1.pdf"] = write_pdf_file(
        "johnson_b2b_deck_and_copy_v1.pdf",
        "B2B Enterprise Deck & 5-Page Website Copy (v1 Draft)",
        [
            "# DRAFT ENTERPRISE COPY",
            "Draft slide deck structure and website messaging for third-party logistics buyers.",
        ],
        role="draft",
    )
    files["johnson_b2b_site_and_deck_final.docx"] = write_docx_file(
        "johnson_b2b_site_and_deck_final.docx",
        "5-Page B2B Website Copy Deck — DockStream Logistics (Final Production Master)",
        [
            "# PAGE 1: HOMEPAGE (ELIMINATE DOCK DEAD-TIME)",
            "NAVIGATION: Home · Platform Features · Integrations & Architecture · Pricing & ROI · Request Scoping Call",
            "HERO BADGE: Intelligent Cross-Dock Logistics Automation",
            "HERO HEADLINE: Eliminate Dock Dead-Time & Driver Detention Claims.",
            "HERO SUBHEAD: Automate driver check-in via mobile geofence, dynamically assign loading bays, and sync electronic bills of lading in under 30 seconds.",
            "CALL-TO-ACTION BUTTONS: [Request Terminal Scoping Call] · [Explore Features ->]",
            "KEY PERFORMANCE PROOF: 38% Faster Trailer Turn Time · 14 Hours Saved Per Dispatcher Weekly · $14,800 Average Monthly Detention Savings · 14 Days Turnkey Implementation SLA.",
            "REAL-TIME FACILITY STATUS DEMO: Interactive simulation demonstrating instant bay toggling between Unloading, Available, and Docking In.",
            "CUSTOMER TESTIMONIAL: 'DockStream paid for itself in reduced detention claims in month one. The frontline dispatchers love how simple the mobile check-in is.' — Dave Henderson, Director of Terminal Operations, Apex Cold Logistics.",
            "# PAGE 2: PLATFORM FEATURES & WORKFLOWS",
            "FEATURE 1: Geofenced Driver Check-In — Drivers trigger automated arrival alerts upon entering terminal perimeter. No app download required—drivers receive an SMS link with door assignment.",
            "FEATURE 2: Dynamic Dock Door Assignment — Intelligent algorithms allocate bays based on trailer temperature class, liftgate requirements, forklift staging proximity, and dispatch schedules.",
            "FEATURE 3: Sign-on-Glass Electronic BOL — Drivers inspect carton tallies and sign digital bills of lading directly on mobile glass in under 30 seconds. PDFs sync to carrier and ERP records instantly.",
            "FEATURE 4: Predictive Demurrage Alerts — Automated countdown flags trailers approaching detention windows (45 minutes prior), empowering dispatchers to prioritize at-risk freight.",
            "FEATURE 5: Shift Throughput Analytics — Track turnaround times by carrier, driver, shift supervisor, and commodity type. Export audit-ready compliance logs with one click.",
            "FEATURE 6: Multilingual Driver Interface — Instant SMS localization into English, Spanish, Polish, and Russian ensures seamless communication with long-haul regional freight drivers.",
            "# PAGE 3: ENTERPRISE INTEGRATIONS & SECURITY",
            "HEADLINE: Connects Seamlessly with Your Existing Logistics Stack",
            "SUBHEAD: Bi-directional webhooks and native connectors eliminate dual-entry between yard management and enterprise ERPs.",
            "— SAP TMS & S/4HANA: Native IDoc and OData REST integration. Pull incoming manifest schedules and push finalized pallet receipts straight into central inventory.",
            "— Oracle Transportation Management (OTM): Real-time dock appointment synchronization with shipment milestone updates (EDI 214 and XML freight statuses).",
            "— Blue Yonder (JDA): Automated warehouse door reservation mapping and driver staging queue synchronization.",
            "— Standard EDI 204 / 214 / 210: Turnkey electronic data interchange compatibility with certified clearinghouse protocols.",
            "— Security & SOC-2: End-to-end 256-bit AES data encryption in transit and at rest, role-based access control (RBAC), and annual third-party penetration testing.",
            "# PAGE 4: TRANSPARENT PRICING & LICENSING TIERS",
            "HEADLINE: Simple, Predictable Per-Facility Pricing",
            "SUBHEAD: No per-driver fees. Unlimited trailer transactions and dispatcher logins included.",
            "TIER 1: STANDARD HUB ($1,250 / MONTH PER TERMINAL)",
            "• Up to 20 Active Loading Bays · Unlimited Driver SMS Check-ins · Digital BOL Generation & PDF Export · Standard 99.9% Uptime SLA · Email & Phone Dispatch Support.",
            "TIER 2: ENTERPRISE FLEET ($2,800 / MONTH PER TERMINAL) — MOST POPULAR",
            "• Unlimited Loading Bays & Terminals · Bi-directional SAP / Oracle TMS Sync · Predictive Demurrage Alert Engine · 99.99% Enterprise Uptime Guarantee · Dedicated Implementation Engineer.",
            "INTERACTIVE ROI CALCULATOR: At 45 daily trailers and 75-minute dwell time, monthly projected savings equal $15,390 (including 182 dispatcher hours saved and 74 prevented detention claims).",
            "# PAGE 5: DEMONSTRATION & TERMINAL SCOPING INTAKE",
            "HEADLINE: Schedule Your 20-Minute Terminal Scoping Call",
            "SUBHEAD: Book an operational review with Jack Johnson, Co-Founder & Logistics Engineer.",
            "INTAKE FIELDS: Full Name, Work Email, Company / Terminal Location, Daily Inbound Trailer Volume.",
            "CONFIRMATION: 'Scoping reservation confirmed. Our terminal engineering team will review your facility footprint and provide a customized ROI projection during the call.'",
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
    johnson_html = load_showcase_template("showcase_dockstream.html")
    files["johnson_dockstream_b2b_website_prototype.html"] = write_html_file(
        "johnson_dockstream_b2b_website_prototype.html",
        "DockStream · Intelligent Yard Logistics Management",
        johnson_html,
        role="deliverable",
    )

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
    files["luca_q3_financial_model.xlsx"] = copy_chat_file_alias("luca_q3_property_ledger_reconciled.xlsx", "luca_q3_financial_model.xlsx", role="deliverable")
    files["luca_q3_reconciled_ledger.csv"] = write_csv_file(
        "luca_q3_reconciled_ledger.csv",
        [
            ["Date", "Transaction Description", "Category", "Gross Inbound (USD)", "GET Tax (4.712%)", "County Surcharge (0.5%)", "Net Revenue"],
            ["2026-08-02", "Oahu Sunset Catamaran Charter #1042", "Private Charter", 3450.00, 162.56, 17.25, 3270.19],
            ["2026-08-09", "Diamond Head Snorkel Tour 14 Guests", "Group Charter", 2800.00, 131.94, 14.00, 2654.06],
            ["2026-08-16", "Kewalo Basin Harbor Fuel Dock Surcharge", "Vessel Expense", -840.00, 0.00, 0.00, -840.00],
            ["2026-08-23", "Corporate Team Building Excursion", "Corporate Charter", 4950.00, 233.24, 24.75, 4692.01],
            ["2026-08-30", "Marine Diesel Maintenance & Hull Cleaning", "Vessel Expense", -1120.00, 0.00, 0.00, -1120.00],
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
        "Oahu Catamaran & Sportfishing Private Charters — 2026 Guest Brochure & Booking Guide",
        [
            "# 1. WELCOME ABOARD: PRIVATE OCEAN HOSPITALITY AT KEWALO BASIN",
            "Aloha and welcome to Oahu Catamaran & Sportfishing Charters, Honolulu's premier ocean hospitality company berthed at historic Kewalo Basin Harbor (Slips K-14 & K-15). Under the leadership of Managing Partner Luca Carollo, our fleet delivers bespoke private ocean excursions along the iconic Waikiki coastline, Diamond Head crater, and offshore pelagic waters of the Kaiwi Channel.",
            "All private charters include a licensed USCG Master 100-Ton Captain, professional marine crew, premium gear, fuel allowances, and $2,000,000 commercial passenger protection insurance.",
            "--PAGE-BREAK--",
            "# 2. FLEET TECHNICAL SPECIFICATIONS & VESSEL COMPARISON",
            "Our vessels are maintained in Bristol condition and subject to rigorous annual USCG safety and hull inspections.",
            [
                ["Technical Specification", "42ft Sailing Catamaran 'Makani'", "34ft Custom Sportfisher 'Hoku'"],
                ["Harbor Berth", "Kewalo Basin Slip K-14", "Kewalo Basin Slip K-15"],
                ["Length Overall (LOA) & Beam", "42' 0\" LOA · 22' 6\" Beam", "34' 0\" LOA · 12' 0\" Beam"],
                ["Draft / Ocean Clearance", "3' 8\" Shallow Keel", "3' 2\" Deep-V Modified Hull"],
                ["USCG Certified Passenger Capacity", "18 Guests + 3 Crew", "6 Guests + 2 Crew"],
                ["Propulsion & Speed", "Twin Yanmar 40HP Marine Diesel (8–10 kts)", "Twin Cummins Turbo Diesel (24–28 kts)"],
                ["Nav & Marine Electronics", "Raymarine HybridTouch GPS & Sonar", "Furuno 3D Sonar, CHIRP Transducer, Radar"],
                ["Primary Deck Amenities", "Dual trampolines, shaded cockpit, galley, head", "Lee outriggers, tuna tubes, live well, fighting chair"],
                ["Ideal Charter Mission", "Snorkel sails, sunset cruises, corporate VIP", "Pelagic big game fishing (Ahi, Marlin, Mahi)"],
            ],
            "--PAGE-BREAK--",
            "# 3. 2026 PRIVATE CHARTER RATES & EXPERIENCES SCHEDULE",
            "Transparent private charter rates with all harbor fees and captain provisioning included. State excise tax (4.712%) and optional crew gratuity (industry standard 15–20%) are separate.",
            [
                ["Charter Experience", "Vessel", "Duration", "Daily Departure Times", "Base Charter Rate", "Harbor Fee", "All-In Private Total"],
                ["Turtle Canyon Snorkel & Sail", "Makani Catamaran", "3.0 Hours", "08:30 AM & 12:00 PM", "$1,250.00", "$45.00", "$1,295.00"],
                ["Diamond Head Golden Hour Sunset", "Makani Catamaran", "2.5 Hours", "05:00 PM (Seasonal)", "$950.00", "$45.00", "$995.00"],
                ["Half-Day Coastal Adventure", "Makani Catamaran", "4.0 Hours", "Custom Departure", "$1,400.00", "$45.00", "$1,445.00"],
                ["Full-Day Private Island Sail", "Makani Catamaran", "8.0 Hours", "09:00 AM Departure", "$2,400.00", "$45.00", "$2,445.00"],
                ["Deep Sea Half-Day Pelagic", "Hoku Sportfisher", "4.0 Hours", "06:00 AM or 11:00 AM", "$1,100.00", "$45.00", "$1,145.00"],
                ["Kaiwi Channel 3/4-Day Chase", "Hoku Sportfisher", "6.0 Hours", "06:00 AM Departure", "$1,550.00", "$45.00", "$1,595.00"],
                ["Offshore Big Game Full-Day", "Hoku Sportfisher", "8.0 Hours", "05:30 AM Departure", "$1,950.00", "$45.00", "$1,995.00"],
            ],
            "--PAGE-BREAK--",
            "# 4. ISLAND CATERING, PUPU PLATTERS & BAR PACKAGES",
            "All charters operate under an open BYOB policy with complementary crystal ice, insulated Yeti coolers, and glassware provided. Guests may also pre-order our gourmet local catering packages.",
            [
                ["Catering Package", "Min Order", "Price Per Person", "Curated Island Inclusions"],
                ["Makai Fresh Poke & Pupu Bar", "4 Guests", "$45.00 / person", "Shoyu Ahi poke, spicy salmon poke, fresh wonton chips, edamame, seaweed salad"],
                ["Waimea Gourmet Charcuterie", "4 Guests", "$38.00 / person", "Artisan cured meats, aged cheeses, tropical fruit skewers, macadamia nuts, crackers"],
                ["North Shore Hawaiian BBQ Box", "6 Guests", "$52.00 / person", "Kalua pork sliders, guava glazed chicken thighs, coconut rice, macaroni salad"],
                ["Sunset Champagne & Pastry Service", "2 Guests", "$65.00 / person", "Chilled Veuve Clicquot champagne, French macarons, chocolate covered Maui strawberries"],
                ["Full Soft Beverage Bar", "All Charters", "Complimentary", "Bottled Hawaiian spring water, POG juice, ginger ale, sparkling seltzers"],
            ],
            "--PAGE-BREAK--",
            "# 5. MARINE WEATHER, HARBOR SAFETY & CANCELLATION POLICIES",
            "Guest safety and marine environmental protection govern all fleet operations.",
            [
                ["Operational Situation", "Safety Standard / Threshold", "Operational Action", "Guest Reschedule / Refund Policy"],
                ["Small Craft Advisory (SCA)", "Sustained winds > 25 kts / Seas > 10 ft", "Harbor master dock hold", "100% full refund or priority reschedule"],
                ["Passing Tropical Rain Squall", "Normal island trade-wind showers", "Sail remains scheduled under canopy", "Standard charter proceeds; no fee waiver"],
                ["Client Advance Notice (>72h)", "Voluntary customer itinerary change", "Cancel booking in reservation portal", "100% refund less 5% processing fee"],
                ["Client Late Notice (<48h)", "Customer cancellation < 48 hours", "Vessel and crew held in reserved status", "50% deposit retained; 50% rebooked as credit"],
                ["Marine Wildlife Encounters", "NOAA Whale Sanctuary Regs", "Maintain strict 100-yd approach floor", "Educational viewing protocol enforced"],
            ],
            "# 6. CONCIERGE DESK & RESERVATIONS BOOKING HOTLINE",
            "Direct Booking Desk: (808) 555-0142 · Email: charters@oahucharterco.com · Web: www.oahucharterco.com",
            "Harbor Slip Office: Kewalo Basin Harbor, 1025 Ala Moana Blvd, Slips K-14 & K-15, Honolulu, HI 96814",
            "Managing Partner Attestation: Luca Carollo · Oahu Catamaran & Sportfishing Charters",
        ],
        role="deliverable",
        subtitle="2026 Private Catamaran Sails, Snorkel Excursions & Offshore Big Game Fishing Brochure",
        meta_tag="Oahu Charter Co. · Kewalo Basin Harbor · Honolulu, Hawaii",
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
        "High-Converting Summer Retention Sequence (5 Emails) — Final Production Master",
        [
            "# EMAIL 1: VIP PRIVATE EARLY ACCESS (24 HOURS BEFORE PUBLIC LAUNCH)",
            "Audience: High-LTV past purchasers & VIP subscriber segment.",
            "Subject: VIP early access: 24 hours before public drop",
            "Preview Text: Your size is reserved for the next 24 hours + complimentary express shipping.",
            "Dear {{First_Name}},",
            "Every summer, our Tuscan workshop crafts a limited archive of handcrafted leather sandals and woven espadrilles. Because we work with small, family-owned tanneries in Florence, our production runs are intentionally small—and when they sell out, they're gone for the season.",
            "Before we announce our High-Summer Capsule to our full 45,000-person community tomorrow morning, we've opened our doors 24 hours early exclusively for our VIP circle.",
            "What's in the private archive:",
            "— The Amalfi Woven Slide in Burnished Saddle & Cream: Ultra-supple Italian calfskin with our signature 6mm memory foam footbed.",
            "— The Capri Ankle-Wrap Espadrille in Natural Linen: Hand-stitched jute sole reinforced with non-slip recycled rubber.",
            "— The Positano Heeled Mule in Terracotta: An effortless 45mm architectural block heel designed for 8+ hours on your feet.",
            "As our thank you for being a loyal collector, enter code SUMMERVIP at checkout to unlock complimentary express courier shipping.",
            "[Unlock Your VIP Early Access ->]",
            "P.S. Sizes 38 and 39 historically account for 45% of our opening-day volume. We recommend reserving your preferred size this evening before public inventory unlocks.",
            "# EMAIL 2: BEHIND THE CRAFT — THE SILHOUETTE SELLING OUT FIRST",
            "Audience: Engaged VIP openers who viewed product pages without completing checkout.",
            "Subject: The silhouette selling out first (and why)",
            "Preview Text: Why 620+ women joined the waitlist for the Amalfi Woven Slide.",
            "Dear {{First_Name}},",
            "Within six hours of unlocking our early access doors, one silhouette emerged as the runaway favorite: The Amalfi Woven Slide.",
            "We spent eighteen months prototyping the upper weave with Master Artisan Marco in Florence. Most woven leather slides either pinch the metatarsal joint or stretch out after two weeks of warm-weather wear.",
            "Here is why the Amalfi fits differently:",
            "1. Zero Break-In Period: Hand-braided from butter-soft Tuscan lambskin strips that contour immediately to the unique width of your foot.",
            "2. Hidden Ergonomic Support: Unlike paper-thin flat sandals, our proprietary triple-density insole absorbs 85% of heel-strike impact on cobblestones or concrete.",
            "3. Water-Resistant Veg-Tan Treatment: Finished with natural carnauba wax to resist light splashes, summer showers, and salt air.",
            "[Shop The Amalfi Slide While Sizes Remain ->]",
            "Warmly, Lina Rickert & The Design Atelier",
            "# EMAIL 3: EDITORIAL STYLING GUIDE — 3 OUTFITS, 1 PAIR",
            "Audience: Full subscriber segment (Day 3 of campaign).",
            "Subject: Quick styling guide: 3 outfits, 1 pair",
            "Preview Text: From morning farmers markets to sunset terrace dinners.",
            "Dear {{First_Name}},",
            "When packing for a summer weekend escape, shoe space is premium real estate. We believe the ultimate summer sandal should transition effortlessly from coastal mornings to evening aperitifs.",
            "Here is how our creative team is styling the Capri Linen Espadrille this weekend:",
            "Look 01: The Saturday Morning Market — Pair with relaxed ivory linen trousers, an unbuttoned oversized cotton poplin shirt, and a structured woven raffia tote.",
            "Look 02: Coastal Midday Exploration — Style with a breezy tiered midi sundress and delicate hammered gold jewelry for effortless, sun-drenched ease.",
            "Look 03: Terrace Sunset Aperitivo — Elevate with a monochromatic silk slip skirt, structured blazer draped over the shoulders, and a bold lip.",
            "[Explore The Complete Styling Lookbook ->]",
            "# EMAIL 4: INVENTORY COUNTDOWN — 48 HOURS LEFT",
            "Audience: Active cart abandoners & site visitors with browsed categories.",
            "Subject: 48 hours left: Your size is still reserved in your bag",
            "Preview Text: Don't leave your favorite summer silhouette behind.",
            "Dear {{First_Name}},",
            "A quick note to let you know that our Summer Capsule Archive will officially close to new orders this Sunday at 11:59 PM EST.",
            "Our logistics team is currently packing final weekend orders. We noticed you left a pair in your cart, and we've held your size in reserve so you don't miss out on seasonal allocations.",
            "Remember: Every Lina Rickert pair includes our 30-Day Step-In-Comfort Guarantee. Try them on in the comfort of your home. If the fit, arch support, or leather feel isn't absolutely perfection, returns and exchanges are complimentary.",
            "[Complete Your Order in 1 Click ->]",
            "# EMAIL 5: FINAL CALL — SUMMER CAPSULE CLOSES AT MIDNIGHT",
            "Audience: All non-purchasers across summer campaign list.",
            "Subject: Final call: Summer capsule archive closes at midnight",
            "Preview Text: Last chance for complimentary VIP shipping & seasonal colorways.",
            "Dear {{First_Name}},",
            "This is our final notification: The Summer Capsule Archive closes tonight at midnight.",
            "At 12:01 AM tomorrow, our seasonal leather hues (Terracotta, Sagebrush, and Raw Ecru) will be archived into our vault, and standard shipping rates will resume across all collections.",
            "Over 1,400 women have added a pair of Lina Rickert handcrafted sandals to their summer wardrobe this week. Don't spend another sunny season compromising between blister-inducing fast fashion and uninspiring orthopedic flats.",
            "[Claim Your Pair Before Midnight ->]",
            "With gratitude, Lina Rickert, Founder & Creative Director",
        ],
        role="deliverable",
    )
    files["lina_spring_launch_copy_final.docx"] = write_docx_file(
        "lina_spring_launch_copy_final.docx",
        "Spring Footwear Launch Campaign Copy Deck (Final Production Master)",
        [
            "# 1. CAMPAIGN CREATIVE DIRECTION & BRAND THEME",
            "Theme: 'Effortless Form, Tuscan Heritage, Endless Steps'",
            "Target Demographic: Professional women aged 28–52 seeking sophisticated, timeless artisan footwear with sneaker-level all-day arch comfort.",
            "Channel Architecture: Master Announcement Email, SMS VIP Broadcasts, Instagram Organic & Paid Carousel Captions, and E-Commerce PDP Conversion Modules.",
            "# 2. HERO ANNOUNCEMENT EMAIL (FULL BRAND SUBSCRIBER LIST)",
            "Subject: It's here: The Spring Footwear Collection has landed",
            "Preview Text: Handcrafted in Tuscany with memory-cushioned insoles. Meet our newest silhouettes.",
            "Dear {{First_Name}},",
            "Spring arrives not on a calendar date, but the first morning you step outside without heavy winter boots.",
            "Today, we are thrilled to unveil our Spring 2026 Collection: eight timeless footwear silhouettes designed in our Munich studio and hand-built by third-generation shoe artisans in Tuscany, Italy.",
            "From buttery-soft glove leather mules to tailored pointed-toe flats that cushion every step from morning boardroom meetings to evening gallery openings, each pair combines bespoke European aesthetics with orthopedically aligned footbeds.",
            "Collection Highlights:",
            "• The Sofia Glove Mule in Nude & Espresso — Featherlight Italian Nappa leather that fits like a second skin.",
            "• The Verona Pointed Flat in Obsidian & Olive — Architectural symmetry featuring our signature non-slip flex-groove sole.",
            "• The Lucca Slingback in Cognac Calfskin — A balanced 35mm kitten heel for effortless transitional elegance.",
            "[Shop The Complete Spring Collection ->]",
            "Warmly, Lina Rickert, Founder",
            "# 3. SMS VIP CAMPAIGN BROADCAST SCRIPTS",
            "— SMS 1 (Opening Drop Alert): 'LINA RICKERT: Our Spring 2026 Collection is officially LIVE. 24hr priority access for SMS VIPs before social drop. Tap to reserve your size + free express shipping with code SPRINGVIP: [Link] (Txt STOP to unsubscribe)'",
            "— SMS 2 (Low Stock Velocity Alert): 'Lina Rickert VIP Alert: Sizes 38 and 39 in the Sofia Glove Mule are down to the last 14 pairs in our warehouse. Claim your pair before public restock: [Link]'",
            "— SMS 3 (Weekend Capsule Reminder): 'Planning your spring wardrobe? Our Tuscan artisans craft in strictly limited batches. Explore the new pointed flat styles before sizes sell out: [Link]'",
            "# 4. INSTAGRAM CONTENT STRATEGY & CAPTION SERIES",
            "— Post 01 (Hero Carousel — Collection Reveal): 'Built for the women who walk 10,000 steps a day and refuse to sacrifice elegance for comfort. Our Spring 2026 Collection is now live at the link in bio. Handcrafted in Tuscany in strictly limited runs. Which silhouette are you wearing first?'",
            "— Post 02 (Reels / Artisan Process Behind the Scenes): 'Meet Marco. For forty-two years, his hands have shaped Tuscan leather into wearable art. Swipe to see the 84 individual steps required to craft a single pair of our Verona Pointed Flats. True luxury isn't rushed. Link in bio.'",
            "— Post 03 (Lifestyle & Everyday Styling): 'Boardroom at 9:00 AM. Client lunch at 1:00 PM. Museum stroll at 6:00 PM. One pair, zero blisters, infinite ease. Tap the photo to shop the Sofia Glove Mule in buttery Nappa leather.'",
            "# 5. E-COMMERCE PRODUCT DETAIL PAGE (PDP) CONVERSION MODULES",
            "BADGE 1: Handcrafted in Tuscany, Italy (Certified Italian Leather Consortium).",
            "BADGE 2: 6mm Proprietary Triple-Density Memory Foam Cushioning with reinforced arch contour.",
            "BADGE 3: Sustainably Vegetable-Tanned Leather (Zero harsh chromium or toxic heavy metals).",
            "BADGE 4: 30-Day Step-In-Comfort Guarantee (Complimentary exchanges and returns on unworn indoor pairs).",
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
    carter_html = load_showcase_template("showcase_apexdesk.html")
    files["carter_landing_page_prototype.html"] = write_html_file(
        "carter_landing_page_prototype.html",
        "ApexDesk · Precision Modular Desktop Ecosystem",
        carter_html,
        role="deliverable",
    )
    files["carter_website_launch_checklist_final.pdf"] = write_pdf_file(
        "carter_website_launch_checklist_final.pdf",
        "ApexDesk — E-Commerce Pre-Launch & Shopify Technical Verification Checklist",
        [
            "# 1. TECHNICAL LAUNCH AUDIT OVERVIEW",
            "Pre-flight verification checklist for the public release of the ApexDesk Modular Aluminum Rail Ecosystem.",
            "# 2. HARDWARE ECOSYSTEM VERIFICATION CHECKS",
            "— Mobile Rail Customizer: Verified 60fps gesture handling and live accessory rendering on iOS Safari and Android Chrome.",
            "— Apple Pay & Express Checkout: Verified 1-tap tokenization and Paystack payment callback handling.",
            "— Inventory Sync: Real-time reservation locks for Batch 01 (500 units) active across warehouse ERP.",
            "— Page Weight & Core Web Vitals: Mobile LCP < 1.4s, FID < 15ms, CLS = 0.00 across all device viewports.",
            "— SSL & Domain Security: HSTS enabled with automated 256-bit TLS certificate rotation.",
            "# 3. CONVERSION COPY DECK",
            "— Hero Positioning: 'The Last Desktop Surface You Will Ever Calibrate.'",
            "— Value Props: Zero Cable Clutter · Unibody 6063 Aluminum · Qi2 15W High-Efficiency Magnetic Power.",
        ],
        role="deliverable",
        subtitle="DTC Hardware Storefront Launch Specification & QA Sign-Off",
        meta_tag="ApexDesk Modular Hardware Systems · Storefront Launch",
    )
    files["carter_storefront_assets_and_launch_kit.zip"] = write_zip_file(
        "carter_storefront_assets_and_launch_kit.zip",
        {
            "ApexDesk_Storefront_Prototype.html": "carter_landing_page_prototype.html",
            "ApexDesk_Launch_Audit_Report.pdf": "carter_website_launch_checklist_final.pdf",
            "README_LAUNCH.txt": "Carter Lemburg — ApexDesk DTC Storefront Launch Package\nPackage Version: 2.4 Final Master Launch Kit\nIncludes: HTML Prototype, PDF Technical Audit, CSS Stylesheet, Launch Checklist, Hardware Engineering Spec, Asset Manifest.",
            "launch_checklist.md": "# ApexDesk Storefront Launch Checklist\n\n- [x] Configure Shopify variant SKUs (AD-01 Matte Black, AD-02 Silver)\n- [x] Integrate 15W Qi2 fast-charging compliance badge\n- [x] Set up abandoned cart recovery email trigger (1hr / 24hr)\n- [x] Test Apple Pay and Google Pay express checkout buttons\n- [x] Verify Cloudflare edge SSL and cache rules\n- [x] Activate Meta Conversions API (CAPI) and GA4 e-commerce events",
            "hardware_engineering_spec.txt": "APEXDESK HARDWARE ENGINEERING SPECIFICATIONS\nModel: AD-01 Modular Magnetic Charging Rail\nChassis: Solid Unibody CNC 6063 Aerospace Aluminum\nWeight: 980 grams (weighted non-slip base)\nCharging Module: Qi2 MPP (Magnetic Power Profile) 15W Fast Charge\nInput Power: USB-C PD 3.0 (Minimum 30W recommended; 65W GaN included)\nMagnets: 16x N52 Neodymium Ring Array (1.2 kg pull force)\nFinish: Type-II Matte Anodized Bead-Blasted (Obsidian / Space Silver)\nSafety Protection: Over-voltage, Over-current, Foreign Object Detection (FOD)\n",
            "styles.css": "/* ApexDesk Production CSS */\n:root { --accent: #cc4b2c; --bg: #0c0b09; }\nbody { font-family: -apple-system, sans-serif; background: var(--bg); color: #fff; }",
        },
        role="deliverable",
    )


    # =========================================================================
    # 18. Issa Cuevas (issabelc207@gmail.com)
    # =========================================================================
    files["cuevas_intake_and_consent_draft_messy.docx"] = write_docx_file(
        "cuevas_intake_and_consent_draft_messy.docx",
        "Cuevas Speech & Language Therapy — Rough Intake Notes & Policy Scramble",
        [
            "# CLINIC INTAKE DESK NOTES (ROUGH DRAFT — ISSA CUEVAS)",
            "Practice: Cuevas Speech & Language Therapy, PLLC · 3410 Far West Blvd, Suite 280, Austin, TX 78731.",
            "Issues with current 2019 paperwork: Parents constantly argue over missed sessions. Last week Mrs. Henderson refused to pay the $50 late fee because she claimed 'it wasn't clear in the paperwork' that sick days still hold the therapist's hour.",
            "Need to change the policy wording: It must state '$75 reserved clinical hour fee' — not an admin charge or late fee. In pediatric speech pathology, we reserve an entire treatment room and 60 minutes of clinician time. Third-party insurance never reimburses missed hours.",
            "HIPAA notice needs major overhaul: Form is from 2019. Does not mention telepractice video recording, two-way mirror observation rooms, or our new encrypted EHR tablet check-in system.",
            "Guarantor confusion: We treat pediatric minors, but parents often write down split custody or say 'bill my ex-husband'. We need strict legal language that whoever signs the agreement is the sole Legal Financial Guarantor personally liable for all fees.",
            "Superbills: Parents keep asking when superbills are ready for their out-of-network insurance reimbursement. We need a fixed schedule: Superbills are generated on the 1st of each calendar month with CPT codes (92507, 92523, 92526) and ICD-10 codes.",
            "Disclaimer required: Need an explicit disclaimer that progress evaluations are clinical estimates and not guaranteed medical or developmental outcomes.",
        ],
        role="source",
    )
    files["cuevas_pediatric_intake_and_consent_v1.docx"] = write_docx_file(
        "cuevas_pediatric_intake_and_consent_v1.docx",
        "Pediatric Clinical Intake & Consent Agreement (v1 Draft — Before Revisions)",
        [
            "# ARTICLE 1: CLIENT IDENTIFICATION",
            "This agreement is made between Cuevas Speech Therapy and the client. The client agrees to attend all scheduled sessions.",
            "# ARTICLE 2: CANCELLATIONS",
            "Late cancellations incur a $50 administrative charge if not notified 24 hours prior. Please call our front desk to reschedule.",
            "# ARTICLE 3: CONFIDENTIALITY",
            "All client records are kept confidential under federal guidelines.",
            "# ARTICLE 4: BILLING",
            "Invoices will be sent periodically for services rendered.",
        ],
        role="draft",
    )
    files["cuevas_pediatric_intake_and_consent_final.docx"] = write_docx_file(
        "cuevas_pediatric_intake_and_consent_final.docx",
        "Master Clinical Intake & Patient Guarantor Agreement — Cuevas Speech & Language Therapy (Final)",
        [
            "# CUEVAS SPEECH & LANGUAGE THERAPY, PLLC — AUSTIN, TEXAS",
            "Physical Clinic: 3410 Far West Blvd, Suite 280, Austin, TX 78731 · Phone: (512) 555-0182 · Fax: (512) 555-0183",
            "Clinical Director: Issa Cuevas, M.S., CCC-SLP · Texas License #72841 · NPI #1982736450",
            "This Master Clinical Services Agreement & Patient Guarantor Attestation ('Agreement') is entered into by and between Cuevas Speech & Language Therapy, PLLC ('Clinic') and the undersigned Parent, Managing Conservator, or Legal Guardian ('Legal Guarantor'), acting on behalf of the minor pediatric patient ('Patient').",
            "# ARTICLE I: CLINICAL SCOPE OF PRACTICE & THERAPY DESIGNATION",
            "1.1 Comprehensive Clinical Scope: The Clinic provides specialized pediatric diagnostic evaluations and therapeutic interventions, including articulation therapy, receptive and expressive language intervention, childhood apraxia of speech (CAS), pragmatics/social cognitive development, fluency disorders, and pediatric sensory-based feeding therapy.",
            "1.2 Individualized Treatment Plans: Therapy frequency, duration (typically 30-minute, 45-minute, or 60-minute clinical units), and clinical modalities are established exclusively following a licensed speech-language pathologist evaluation and formal diagnostic baseline assessment.",
            "1.3 Multi-Disciplinary Coordination: The Legal Guarantor authorizes the Clinic to exchange relevant clinical notes, IEP summaries, and developmental histories with the Patient's designated Primary Care Physician (PCP), pediatric ENT, occupational therapists, and school speech pathologists to ensure continuity of care.",
            "# ARTICLE II: DESIGNATION OF LEGAL FINANCIAL GUARANTOR",
            "2.1 Sole Guarantor Liability: The individual signing this Agreement affirms that they possess legal guardianship or custodial rights to consent to medical and speech-language therapy for the minor Patient. The signing adult is designated as the sole Legal Guarantor personally liable for all fees incurred for professional services rendered.",
            "2.2 Private-Pay Designation: Cuevas Speech & Language Therapy operates as an out-of-network private-pay clinic. Payment in full is due at the time services are rendered or per the agreed monthly automatic billing schedule. The Clinic does not bill commercial health insurance carriers directly.",
            "2.3 Third-Party & Custody Non-Involvement: The Clinic is not a party to domestic relations decrees, custody agreements, divorce settlements, or split financial arrangements between parents. The Legal Guarantor who executes this intake agreement remains strictly responsible for timely settlement of all clinical account balances regardless of third-party indemnification orders.",
            "# ARTICLE III: ATTENDANCE, ILLNESS DISCLOSURE & $75 RESERVED CLINICAL HOUR POLICY",
            "3.1 Dedicated Clinical Hour Reservation: Because pediatric speech therapy requires dedicated clinical room preparation, specialized diagnostic materials, and individual therapist reservation, appointment times are reserved exclusively for the designated Patient.",
            "3.2 Strict 24-Hour Cancellation Requirement: Unscheduled missed sessions without at least twenty-four (24) hours advance written notice (via secure clinic email or official text notification) are subject to the reserved clinical hour fee of $75.00.",
            "3.3 Clinical Fee Justification: The Legal Guarantor acknowledges that the $75.00 charge is a professional reserved clinical hour fee reflecting committed clinical overhead and therapist scheduling, and is not an administrative penalty. Third-party insurance carriers do not reimburse missed session fees; this amount is the direct personal responsibility of the Legal Guarantor.",
            "3.4 Pediatric Illness Disclosure Protocol: To protect immunocompromised pediatric patients, children exhibiting symptoms of fever (>100.4°F without antipyretics within 24 hours), vomiting, contagious rash, or active respiratory infection must not attend in-person clinic sessions. Where medically appropriate and requested before 8:00 AM on the day of the session, the Clinic will convert the reserved hour to a HIPAA-compliant telepractice session with no cancellation fee assessed.",
            "3.5 Habitual Attendance Standards: Therapy progress relies on consistent weekly attendance. Patients missing three (3) consecutive sessions or failing to maintain an 80% monthly attendance rate may have their recurring preferred time slot released to families on the clinic waiting list.",
            "# ARTICLE IV: HIPAA PEDIATRIC PRIVACY DISCLOSURE & CONFIDENTIALITY",
            "4.1 Federal & State Privacy Standards: The Clinic adheres strictly to the Health Insurance Portability and Accountability Act of 1996 (HIPAA), 45 C.F.R. Parts 160 and 164, the Texas Medical Records Privacy Act (Texas Health & Safety Code Chapter 181), and the Texas State Board of Examiners in Speech-Language Pathology code of ethics.",
            "4.2 Protected Health Information (PHI) Security: All diagnostic protocols, treatment logs, video recordings, and clinical communication are secured in 256-bit AES encrypted, SOC-2 compliant Electronic Health Record (EHR) platforms with strict role-based practitioner access controls.",
            "4.3 Permitted Disclosures: Protected Health Information is disclosed solely for treatment coordination, legally mandated child welfare reporting (Texas Family Code § 261.101), compliance audits, or pursuant to a signed, written authorization executed by the Legal Guarantor.",
            "# ARTICLE V: OBSERVATION ROOM, MIRROR, & CLINICAL VIDEO RECORDING AUTHORIZATION",
            "5.1 Clinical Observation Glass: The Clinic facilities feature two-way observation mirrors and integrated audio systems designed for parent education, clinical fellow supervision, and sensory observation without triggering child separation anxiety.",
            "5.2 Therapeutic Video Recording Authorization: The Legal Guarantor hereby grants permission for licensed clinicians to digitally record portions of therapy sessions strictly for: (a) diagnostic baseline phonetic comparison, (b) sensory feeding progress tracking, (c) licensed speech-language pathologist clinical supervision, and (d) recorded home practice demonstrations provided directly to the parents.",
            "5.3 Strict Prohibition on External Use: Under no circumstances will therapeutic clinical recordings be shared, published, or utilized for public marketing, social media, or commercial purposes without separate explicit written consent.",
            "# ARTICLE VI: TELEHEALTH CLINICAL CONSENT & HOME PRACTICE PROTOCOLS",
            "6.1 Telepractice Licensure & Standards: Telepractice sessions are delivered in full compliance with Texas Health and Safety Code Chapter 111 and ASHA practice guidelines over high-definition, encrypted, HIPAA-compliant video links.",
            "6.2 Pediatric Caregiver Co-Presence Requirement: For pediatric patients under eight (8) years of age, a parent, legal guardian, or designated adult caregiver must remain physically present in the same room throughout the teletherapy session to assist with material handling, tactile prompt reinforcement, and technical connectivity.",
            "6.3 Technology & Privacy Environment: The Legal Guarantor agrees to provide a private, quiet room free from domestic distractions (televisions, pets, siblings) and high-speed internet capability to maximize clinical effectiveness.",
            "# ARTICLE VII: SUPERBILL GENERATION SCHEDULE & OUT-OF-NETWORK REIMBURSEMENT",
            "7.1 Monthly Superbill Schedule: For families seeking out-of-network reimbursement from private health insurance plans, the Clinic generates comprehensive, itemized Superbills on the first (1st) day of each calendar month covering all therapy sessions completed and paid during the preceding month.",
            "7.2 Standard Coding Standards: Each monthly Superbill includes the Clinic's Tax ID, NPI number, supervising SLP license number, standardized American Medical Association CPT procedure codes (e.g., 92507 for Individual Speech/Language Treatment, 92523 for Speech Sound & Language Evaluation, 92526 for Oral Pharyngeal / Feeding Therapy), and exact ICD-10 diagnostic codes.",
            "7.3 Reimbursement Disclaimer: The Clinic provides accurate, compliant billing documentation but does not guarantee that any private insurance carrier will reimburse out-of-network claims. The Legal Guarantor is solely responsible for submitting Superbills directly to their insurer's member portal.",
            "# ARTICLE VIII: PROGRESS EVALUATIONS & CLINICAL ESTIMATION DISCLAIMER",
            "8.1 Professional Clinical Estimates: Periodic formal progress updates, developmental age equivalencies, and speech intelligibility percentages reflect professional clinical diagnostic evaluations and clinical estimates based on observable behavioral data.",
            "8.2 Medical Outcomes Disclaimer: Because pediatric speech, language, and neuro-developmental progression depend on numerous extrinsic and biological variables—including neurological maturation, auditory processing, home practice consistency, and co-occurring developmental diagnoses—the Clinic and its clinicians do not and cannot guarantee specific educational, scholastic, or medical outcomes.",
            "# SIGNATURE BLOCK: LEGAL GUARANTOR ATTESTATION & CLINICAL DIRECTOR ACKNOWLEDGEMENT",
            "By signing below, I certify that I have read, understood, and received a copy of this Master Clinical Intake Agreement, HIPAA Disclosure, and Attendance Policy. I attest that I am the legally authorized Guarantor for the Patient named below and agree to be bound by all terms, including the $75 reserved clinical hour fee policy.",
            "Child / Patient Legal Name: __________________________________________________",
            "Date of Birth (MM/DD/YYYY): _____________________ Sex / Gender: ____________",
            "Legal Guarantor Full Printed Name: ____________________________________________",
            "Relationship to Patient (Mother / Father / Legal Guardian): ____________________",
            "Guarantor Primary Phone: __________________ Emergency Mobile: ________________",
            "Billing Address: ___________________________________________________________",
            "Legal Guarantor Signature: _________________________________ Date: ____________",
            "Clinical Director Attestation: Issa Cuevas, M.S., CCC-SLP (Texas Lic #72841, NPI #1982736450)",
            "Clinic Authorized Signature: Issa Cuevas, M.S., CCC-SLP · Date: October 20, 2026",
        ],
        role="deliverable",
    )
    files["cuevas_parent_communication_templates.docx"] = write_docx_file(
        "cuevas_parent_communication_templates.docx",
        "Cuevas Speech Therapy — Front Desk Parent Communication Scripts & Email Decks",
        [
            "# TEMPLATE 1: WELCOME & ELECTRONIC INTAKE PAPERWORK ONBOARDING (EMAIL)",
            "Subject: Welcome to Cuevas Speech & Language Therapy — Intake Paperwork & First Session Guide",
            "Dear {{Parent_Guarantor_Name}},",
            "Welcome to Cuevas Speech & Language Therapy! We are so excited to partner with your family on {{Child_Name}}'s speech and language journey. Our clinical team has reserved your weekly recurring therapy slot: Every {{Day_of_Week}} at {{Session_Time}} with our Clinical Director, Issa Cuevas, M.S., CCC-SLP.",
            "Before your initial diagnostic evaluation, please complete our secure electronic clinical intake package using the link below. It covers child developmental milestones, medical history, pediatrician contact, and our clinic guarantor consent.",
            "Link: https://clinic.cuevasspeech.com/intake/secure?id={{Patient_ID}}",
            "Please ensure this is submitted at least 48 hours before your appointment so our clinical team can review diagnostic histories and prepare tailored assessment materials. If you have recent IEP evaluations or medical audiograms, please upload them directly through the portal.",
            "Warmly, Front Desk Patient Coordination Team · Cuevas Speech & Language Therapy, PLLC · (512) 555-0182",
            "# TEMPLATE 2: EXPLAINING THE $75 RESERVED CLINICAL HOUR POLICY WITH EMPATHY (PHONE / EMAIL SCRIPT)",
            "Context: Use when a parent calls to cancel with short notice (<24 hours) or disputes a missed session charge on their account.",
            "Front Desk Script (Verbatim):",
            "'Hi {{Parent_Name}}, thank you so much for calling to let us know that {{Child_Name}} won't be able to make it in today. First and foremost, we hope {{Child_Name}} feels better quickly!",
            "I want to gently remind you about our clinic's reserved clinical hour policy. Because each of our speech-language pathologists works one-on-one with your child and prepares individualized materials for that dedicated 60-minute window, unscheduled missed sessions without 24 hours advance notice incur our $75 reserved clinical hour fee.",
            "We never want you to lose therapy time, so we have two helpful alternatives for you:",
            "1. If {{Child_Name}} is mildly under the weather but up for a relaxed session from home, our clinician can convert today's appointment to a HIPAA-compliant telepractice session right now at your regular time—no fee assessed at all.",
            "2. Alternatively, our therapist can spend {{Child_Name}}'s reserved hour conducting a parent coaching video call or designing an updated sensory home exercise packet for you to use this week.",
            "Which of those options would work best for your family today?'",
            "If parent pushes back on insurance coverage:",
            "'We completely understand insurance questions can be stressful! Because insurance carriers only reimburse for active therapy units delivered directly to the patient, they do not cover reserved facility hours. That is why our clinical intake designates the parent as the legal guarantor for reserved time. Our priority is always keeping {{Child_Name}} on track while respecting the clinician's dedicated schedule.'",
            "# TEMPLATE 3: MONTHLY INSURANCE SUPERBILL REIMBURSEMENT DELIVERY (EMAIL)",
            "Subject: Your Monthly Superbill for Out-of-Network Insurance Reimbursement — Cuevas Speech Therapy",
            "Dear {{Parent_Guarantor_Name}},",
            "Attached please find your official itemized Superbill for speech-language therapy sessions completed by {{Child_Name}} during the preceding calendar month.",
            "In accordance with our clinic schedule, all superbills are generated on the 1st of each month to streamline your insurance claims submission.",
            "What is included on this statement:",
            "— Clinic Tax ID (EIN), NPI #1982736450, and Texas State License #72841 for Issa Cuevas, M.S., CCC-SLP.",
            "— Standard AMA CPT codes for every completed date of service (CPT 92507 for Speech/Language Therapy, CPT 92523 for Comprehensive Speech Evaluation).",
            "— ICD-10 diagnostic codes corresponding to {{Child_Name}}'s formal evaluation.",
            "— Itemized dates of service and verification of paid account balance.",
            "How to submit for reimbursement:",
            "1. Log into your health insurance member portal (e.g., Blue Cross Blue Shield, Aetna, UnitedHealthcare, Cigna).",
            "2. Navigate to 'Submit an Out-of-Network Claim' (Form CMS-1500).",
            "3. Upload this attached PDF statement as your proof of service and itemized receipt.",
            "4. Insurers typically process out-of-network claims within 14–21 business days and issue reimbursement checks directly to the subscriber.",
            "If your insurance adjuster requires clinical progress notes or our clinical director's signature on a specific claim form, simply reply to this email and our billing coordinator will take care of it immediately.",
            "Warm regards, Billing & Patient Accounts · Cuevas Speech & Language Therapy",
            "# TEMPLATE 4: PEDIATRIC TELETHERAPY PREPARATION CHECKLIST FOR PARENTS",
            "Subject: Quick Checklist for Tomorrow's Pediatric Teletherapy Session with {{Child_Name}}",
            "To make your child's remote speech session engaging and clinically effective, please review this 4-point checklist:",
            "— Device Setup: Place a laptop or iPad on a stable table at eye level (avoid handheld phones). Ensure camera and microphone are tested.",
            "— Quiet Environment: Choose a well-lit room away from televisions, pets, and siblings for the 45-minute duration.",
            "— Caregiver Co-Presence: Under Texas clinical guidelines, an adult caregiver must remain in the room for children under 8 to assist with activities and positive reinforcement.",
            "— Favorite Toys / Reinforcers: Keep 2 or 3 of {{Child_Name}}'s favorite motivating toys or sensory items nearby to support engagement.",
            "Direct Telepractice Zoom Link: https://telehealth.cuevasspeech.com/room/cuevas-slp",
        ],
        role="deliverable",
    )
    files["cuevas_speech_clinic_service_agreement_final.pdf"] = write_pdf_file(
        "cuevas_speech_clinic_service_agreement_final.pdf",
        "Cuevas Speech & Language Therapy — Master Clinical Services Agreement & Guarantor Attestation",
        [
            "# CUEVAS SPEECH & LANGUAGE THERAPY, PLLC — AUSTIN, TEXAS",
            "Physical Clinic: 3410 Far West Blvd, Suite 280, Austin, TX 78731 · Phone: (512) 555-0182 · Fax: (512) 555-0183",
            "Clinical Director: Issa Cuevas, M.S., CCC-SLP · Texas State License #72841 · NPI #1982736450 · Tax ID (EIN): 84-2918402",
            "This Master Clinical Services Agreement, Attendance Policy, and Legal Guarantor Attestation ('Agreement') constitutes a binding professional contract between Cuevas Speech & Language Therapy, PLLC ('Clinic') and the undersigned Parent, Managing Conservator, or Legal Guardian ('Legal Guarantor'), acting on behalf of the minor pediatric patient ('Patient').",
            "# ARTICLE I: CLINICAL SCOPE OF PRACTICE & COMPREHENSIVE THERAPY DESIGNATION",
            "1.1 Comprehensive Clinical Scope: The Clinic provides specialized pediatric diagnostic evaluations and therapeutic interventions, including articulation and phonological disorder remediation, expressive and receptive language development, childhood apraxia of speech (CAS), pragmatic social cognitive communication, pediatric feeding and swallowing therapy (dysphagia/sensory food aversions), fluency and stuttering management, and Augmentative and Alternative Communication (AAC) device evaluation, selection, and customization.",
            "1.2 Plan of Care (POC) Establishment: Treatment frequency, session duration (typically 45-minute or 60-minute clinical units), and clinical modalities are established exclusively following a licensed speech-language pathologist evaluation and formal diagnostic baseline assessment. Plans of care are updated on a mandatory 6-month clinical re-evaluation cadence.",
            "1.3 Multi-Disciplinary Coordination: The Legal Guarantor authorizes the Clinic to exchange relevant clinical notes, IEP summaries, medical history, and developmental progress with the Patient's designated Primary Care Physician (PCP), pediatric ENT, occupational therapists, physical therapists, and school speech pathologists to ensure clinical continuity of care.",
            "# ARTICLE II: DESIGNATION OF LEGAL FINANCIAL GUARANTOR & PRIVATE-PAY POLICIES",
            "2.1 Sole Guarantor Liability: The individual executing this Agreement affirms that they possess legal guardianship or custodial authority to consent to medical and speech-language therapy for the minor Patient. The signing adult is designated as the primary Legal Financial Guarantor personally liable for all fees incurred for professional services rendered.",
            "2.2 Private-Pay Facility Designation: Cuevas Speech & Language Therapy operates as an out-of-network private-pay clinic. Payment in full is due at the time services are rendered or per the agreed monthly automatic billing schedule. The Clinic does not bill commercial health insurance carriers directly.",
            "2.3 Third-Party & Custody Non-Involvement: The Clinic is not a party to domestic relations decrees, divorce settlements, split custody agreements, or court orders dividing financial responsibility between parents. The Legal Guarantor who executes this agreement remains strictly responsible for timely settlement of all clinical account balances regardless of third-party indemnification orders.",
            "--PAGE-BREAK--",
            "# ARTICLE III: CLINICAL ATTENDANCE, ILLNESS DISCLOSURE & $75 RESERVED CLINICAL HOUR POLICY",
            "3.1 Dedicated Clinical Hour Reservation: Because pediatric speech pathology requires dedicated clinical treatment room preparation, individualized diagnostic materials, and committed one-on-one clinician time, appointment times are reserved exclusively for the designated Patient. The Clinic does not overbook clinical hours.",
            "3.2 Strict 24-Hour Cancellation Requirement: Unscheduled missed sessions without at least twenty-four (24) hours advance written notice (via secure clinic email or official text notification) are subject to the reserved clinical hour fee of $75.00.",
            "3.3 Clinical Fee Rationale: The Legal Guarantor acknowledges that the $75.00 charge is a professional reserved clinical hour fee reflecting committed clinical overhead and therapist scheduling, and is not an administrative penalty. Third-party insurance carriers do not reimburse missed session fees; this amount is the direct personal responsibility of the Legal Guarantor.",
            "3.4 Summary Table: Attendance & Fee Schedule:",
            [
                ["Absence Category", "Notification Window Required", "Clinical Action / Consequence", "Fee Applied"],
                ["Advance Scheduled Absence", "24+ Hours Advance Notice", "Session cancelled; optional reschedule within 14 days", "$0.00 (Waived)"],
                ["Sudden Pediatric Illness", "Prior to 8:00 AM on Session Day", "Convert to HIPAA Telehealth OR parent home coach packet", "$0.00 (Converted)"],
                ["Late Cancellation (<24h)", "After 8:00 AM or <24h Notice", "Reserved clinical room and therapist time held", "$75.00 (Guarantor Liable)"],
                ["No-Show / Unannounced", "Zero Advance Notice", "Therapist standby; slot held; mandatory card charge", "$75.00 (Guarantor Liable)"],
                ["Chronic Absence (2+ missed)", "Two consecutive unexcused", "Forfeiture of recurring preferred weekly reservation slot", "Slot Released"],
            ],
            "3.5 Pediatric Illness Disclosure Protocol: To protect immunocompromised pediatric patients, children exhibiting symptoms of fever (>100.4°F without antipyretics within 24 hours), vomiting, contagious rash, or active respiratory infection must not attend in-person clinic sessions. Where medically appropriate and requested before 8:00 AM on the day of the session, the Clinic will convert the reserved hour to a HIPAA-compliant telepractice session with no cancellation fee assessed.",
            "3.6 Habitual Attendance Standards: Therapy progress relies on consistent weekly attendance. Patients missing two (2) consecutive unexcused sessions or failing to maintain an 80% monthly attendance rate over 60 days may have their recurring preferred time slot released to families on the clinic waiting list.",
            "--PAGE-BREAK--",
            "# ARTICLE IV: PROFESSIONAL FEE SCHEDULE & OUT-OF-NETWORK SUPERBILL SCHEDULE",
            "4.1 Standardized Professional Fee Schedule: All services rendered are billed in accordance with the following clinical fee matrix:",
            [
                ["CPT Code", "Clinical Description", "Duration", "Private Pay Fee", "Typical Insurer Allowable"],
                ["92523", "Comprehensive Speech Sound & Language Diagnostic Evaluation", "90 min", "$350.00", "$210.00–$280.00"],
                ["92521", "Evaluation of Speech Fluency / Stuttering", "60 min", "$225.00", "$140.00–$185.00"],
                ["92526", "Pediatric Feeding & Oral-Pharyngeal Swallowing Diagnostic", "75 min", "$275.00", "$165.00–$220.00"],
                ["92507", "Individual Speech, Language & Pragmatic Intervention", "60 min", "$160.00", "$95.00–$135.00"],
                ["92507-F", "Pediatric Sensory Feeding / Oral-Motor Intervention", "60 min", "$175.00", "$105.00–$145.00"],
                ["92609", "Augmentative Communication (AAC) Device Programming", "60 min", "$180.00", "$110.00–$150.00"],
                ["RESERVED", "Reserved Clinical Hour / Late Cancellation Fee", "60 min", "$75.00", "Non-Reimbursable"],
            ],
            "4.2 Monthly Superbill Schedule: For families seeking out-of-network reimbursement from private health insurance plans, the Clinic generates comprehensive, itemized Superbills on the first (1st) day of each calendar month covering all therapy sessions completed and paid during the preceding month.",
            "4.3 Required Reimbursement Elements: Each monthly Superbill includes the Clinic's Federal Tax ID, NPI #1982736450, Texas State License #72841, standardized American Medical Association CPT procedure codes, and exact ICD-10 diagnostic codes corresponding to the formal diagnostic evaluation.",
            "4.4 Insurance Reimbursement Disclaimer: The Clinic provides accurate, compliant billing documentation but does not guarantee that any private insurance carrier will reimburse out-of-network claims. The Legal Guarantor is solely responsible for submitting Superbills directly to their insurer's member portal.",
            "--PAGE-BREAK--",
            "# ARTICLE V: HIPAA PEDIATRIC PRIVACY DISCLOSURE & CONFIDENTIALITY",
            "5.1 Federal & State Privacy Standards: The Clinic adheres strictly to the Health Insurance Portability and Accountability Act of 1996 (HIPAA), 45 C.F.R. Parts 160 and 164, the Texas Medical Records Privacy Act (Texas Health & Safety Code Chapter 181), and the Texas State Board of Examiners in Speech-Language Pathology code of ethics.",
            "5.2 Protected Health Information (PHI) Security: All diagnostic protocols, treatment logs, video recordings, and clinical communication are secured in 256-bit AES encrypted, SOC-2 compliant Electronic Health Record (EHR) platforms with strict role-based practitioner access controls.",
            "5.3 Permitted Disclosures: Protected Health Information is disclosed solely for treatment coordination, legally mandated child welfare reporting (Texas Family Code § 261.101), compliance audits, or pursuant to a signed, written authorization executed by the Legal Guarantor.",
            "# ARTICLE VI: OBSERVATION ROOM, TWO-WAY MIRROR & CLINICAL VIDEO RECORDING",
            "6.1 Clinical Observation Glass: The Clinic facilities feature two-way observation mirrors and integrated audio systems designed for parent education, clinical fellow supervision, and sensory observation without triggering child separation anxiety.",
            "6.2 Therapeutic Video Recording Authorization: The Legal Guarantor hereby grants permission for licensed clinicians to digitally record portions of therapy sessions strictly for: (a) diagnostic baseline phonetic comparison, (b) sensory feeding progress tracking, (c) licensed speech-language pathologist clinical supervision, and (d) recorded home practice demonstrations provided directly to the parents.",
            "6.3 Strict Prohibition on External Use: Under no circumstances will therapeutic clinical recordings be shared, published, or utilized for public marketing, social media, or commercial purposes without separate explicit written consent.",
            "# ARTICLE VII: TELEHEALTH CLINICAL CONSENT & CAREGIVER CO-PRESENCE",
            "7.1 Telepractice Licensure & Standards: Telepractice sessions are delivered in full compliance with Texas Health and Safety Code Chapter 111 and ASHA practice guidelines over high-definition, encrypted, HIPAA-compliant video links.",
            "7.2 Caregiver Co-Presence Requirement: For pediatric patients under eight (8) years of age, a parent, legal guardian, or designated adult caregiver must remain physically present in the same room throughout the teletherapy session to assist with material handling, tactile prompt reinforcement, and technical connectivity.",
            "7.3 Technology & Privacy Environment: The Legal Guarantor agrees to provide a private, quiet room free from domestic distractions and high-speed internet capability to maximize clinical effectiveness.",
            "--PAGE-BREAK--",
            "# ARTICLE VIII: PEDIATRIC SENSORY GYM & CLINICAL SAFETY RELEASE",
            "8.1 Sensory Equipment Utilization: Therapy sessions may incorporate suspended swings, foam crash pits, climbing structures, balance beams, and specialized sensory-motor equipment designed to regulate vestibular and proprioceptive systems during language acquisition.",
            "8.2 Clinical Safety & Supervised Risk Release: All activities are supervised by licensed clinicians. The Legal Guarantor acknowledges that physical activities carry inherent minor risks of childhood bumps or falls, and releases the Clinic from liability arising from normal, supervised therapeutic sensory play.",
            "# ARTICLE IX: NON-GUARANTEE OF CLINICAL OUTCOMES & DISCHARGE CRITERIA",
            "9.1 Professional Clinical Estimates: Periodic formal progress updates, developmental age equivalencies, and speech intelligibility percentages reflect professional clinical diagnostic evaluations and clinical estimates based on observable behavioral data.",
            "9.2 Medical Outcomes Disclaimer: Because pediatric speech, language, and neuro-developmental progression depend on numerous extrinsic and biological variables—including neurological maturation, auditory processing, home practice consistency, and co-occurring developmental diagnoses—the Clinic and its clinicians do not and cannot guarantee specific educational, scholastic, or medical outcomes.",
            "9.3 Objective Discharge Criteria: Patients are discharged upon achieving age-appropriate standardized milestones (>=85th percentile), plateauing after multi-modal intervention trials, or upon mutual agreement between clinician and Legal Guarantor.",
            "# ARTICLE X: TEXAS STATE LICENSING & MEDICAL RECORDS RETENTION",
            "10.1 Regulatory Authority: Speech-language pathology services are regulated by the Texas Department of Licensing and Regulation (TDLR), PO Box 12057, Austin, TX 78711 · (800) 803-9202.",
            "10.2 Seven-Year Pediatric Record Retention: In accordance with Texas Medical Board and TDLR regulations, all clinical records and diagnostic evaluations are retained for a minimum of seven (7) years past the Patient's eighteenth (18th) birthday.",
            "# SIGNATURE BLOCK: LEGAL GUARANTOR ATTESTATION & CLINICAL DIRECTOR ACKNOWLEDGEMENT",
            "By signing below, I certify that I have read, understood, and received a copy of this Master Clinical Services Agreement, HIPAA Disclosure, Fee Schedule, and Attendance Policy. I attest that I am the legally authorized Guarantor for the Patient named below and agree to be bound by all terms, including the $75 reserved clinical hour fee policy.",
            "Child / Patient Legal Name: __________________________________________________",
            "Date of Birth (MM/DD/YYYY): _____________________ Sex / Gender: ____________",
            "Legal Guarantor Full Printed Name: ____________________________________________",
            "Relationship to Patient (Mother / Father / Legal Guardian): ____________________",
            "Guarantor Primary Phone: __________________ Emergency Mobile: ________________",
            "Billing Address: ___________________________________________________________",
            "Legal Guarantor Signature: _________________________________ Date: ____________",
            "Clinical Director Attestation: Issa Cuevas, M.S., CCC-SLP (Texas Lic #72841, NPI #1982736450)",
            "Clinic Authorized Signature: Issa Cuevas, M.S., CCC-SLP · Date: October 20, 2026",
        ],
        role="deliverable",
        subtitle="Pediatric Clinical Intake, Legal Guarantor Attestation, HIPAA Disclosure & Attendance Policy",
        meta_tag="Cuevas Speech & Language Therapy · Austin, Texas · TX License #72841",
    )
    # DIVERSE DELIVERABLE: Real ZIP pack containing agreements, templates, and clinical forms
    files["cuevas_pediatric_intake_forms_bundle.zip"] = write_zip_file(
        "cuevas_pediatric_intake_forms_bundle.zip",
        {
            "README_CLINICAL_PACK.txt": "Cuevas Speech & Language Therapy — Complete Clinical Onboarding Pack\nIncludes: Master Agreement (.pdf), Editable Word Decks (.docx), Front Desk Scripts (.docx), Emergency Contact Form (.csv).\nClinical Director: Issa Cuevas, M.S., CCC-SLP · Austin, Texas",
            "Master_Clinical_Agreement_Final.pdf": "cuevas_speech_clinic_service_agreement_final.pdf",
            "Pediatric_Intake_and_Consent_Final.docx": "cuevas_pediatric_intake_and_consent_final.docx",
            "Parent_Communication_Templates.docx": "cuevas_parent_communication_templates.docx",
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
                "Hey Jose! Good to connect. Shippers right now are starving for reliable asset-based carriers who actually own their trucks, instead of brokers who re-broker and drop freight at the last minute. Are you mostly bidding on dedicated warehouse distribution runs between Dallas, Fort Worth, and Arlington, or regional hot-shot hauls across North Texas?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 17, 21, 45, 12),
                "mostly regional distribution routes and dedicated cross-town runs between DFW warehouses, Arlington assembly plants, and Alliance airport. we have two 26ft straight trucks with liftgates and pallet jacks ready to go. how much to clean this up and make us look like a serious carrier?",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 18, 14, 12, 30),
                "We can shape your notes into a punchy executive capability bio, 3 targeted cold outreach emails for DFW warehouse dispatchers, plus a clean mobile rate card graphic you can text straight from your cab. Total package is $25.00 flat and we can have the draft in your hands by tomorrow evening. Want us to get started?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 18, 19, 27, 14),
                "sounds fair man, let's do it. i tried paying through the normal checkout on your portal earlier from my phone, but chase flagged my debit card because of the merchant location i think. do you have a direct link or alternate way to run it?",
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
                "hey! hope you guys are doing well. i really need some help with my website... i get good traffic from instagram and people love the photos, but barely anyone actually books through the site. visitors click over to the booking page and then just vanish. i attached screenshots of my current homepage and booking form. can you guys take a look and see what might be going wrong?",
                [
                    'audrey_current_homepage_screenshot.png',
                    'audrey_current_booking_form_screenshot.png',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 9, 30, 19, 38, 12),
                "Hi Audrey! First off, your work is stunning—the natural light portraits are genuinely gorgeous, so rest assured your photography isn't the problem at all.\n\nTook a look through both screenshots you sent over. The biggest friction point jumps right out on your booking form: you're asking visitors for 14 detailed questions before they even see starting rates or know your availability. When someone taps over from Instagram on their phone, that's a massive wall.\n\nAre most people reaching out directly in your Instagram DMs asking about pricing instead of finishing that form?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 9, 30, 19, 44, 25),
                "oh wow... yes, 100%! my DMs are constantly flooded with people asking 'how much for a portrait session?' and when I tell them to check the site to book, they just ghost. I've been terrified of putting prices on the site because someone told me it scares people off, but answering the same pricing questions in DMs all day is exhausting. hearing you say 14 questions is terrifying makes so much sense haha, i honestly thought i was just being thorough!",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 30, 19, 50, 48),
                "Putting starting rates upfront actually protects your time and attracts serious clients who already value your work—it filters out tire-kickers and builds immediate trust.\n\nWhat we'd recommend is a focused diagnostic audit: we'll cut the intake down from 14 questions to 5 painless essentials, anchor clear starting package tiers ($450 Essential, $950 Studio Session, $2,200 Campaign) so clients pre-qualify, and sharpen your hero headline to signal your East Austin studio.\n\nWe can run that complete diagnostic audit for $90 flat and have the full breakdown ready tomorrow afternoon. Would you like us to put that together for you?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 9, 30, 19, 53, 10),
                "That makes total sense and honestly takes such a huge weight off my shoulders. Yes please, let's do it!",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 30, 19, 55, 30),
                "Awesome Audrey! I just posted invoice INV-260930-AB01 for the $90 audit to your project billing tab. If you're on your phone between shoots, you can also clear it directly via Apple Pay right here: https://paystack.shop/pay/ppiajw3f1-.\n\nOnce that clears, we'll dive right in and have the complete audit report over to you tomorrow afternoon!",
                [],
            ),
            (
                'client',
                dt_utc(2026, 9, 30, 19, 58, 43),
                "just tapped that apple pay link and cleared the $90! excited to see the breakdown.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 30, 20, 4, 12),
                "Payment confirmed, Audrey! We'll have the full audit report mapped out for you tomorrow afternoon.",
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
                "Totally understand being cautious Audrey, you're 100% right to check! That's our direct hosted checkout on Paystack (our payment gateway). It's fully encrypted with 256-bit SSL, supports Apple Pay so your card details stay private, and deposits straight to our verified business account. Completely safe!",
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
                "Payment confirmed, thank you Audrey! I updated the package names on the Services page and switched booking hours to Mon–Fri.\n\nAttached is your final Word copy deck, the interactive HTML prototype you can test right in your browser, and the booking wireframe diagram.\n\nHope the launch goes amazingly with your designer! If you know any creative peers or local clinics losing clients on confusing sites, send them our way and we'll take great care of them.",
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
                "hey!! designer just pushed the new site and booking pages live! Here is the live link: https://www.byinfini.online/showcase/studio-brown/ and she even pushed the custom theme repo here: https://github.com/audreybrown-studio/studio-brown-portfolio. The bounce rate already dropped by half, inquiries are already rolling through the new form. Thank you guys so much again!",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 19, 17, 5, 30),
                "That is incredible news Audrey! Just opened https://www.byinfini.online/showcase/studio-brown/—the typography, the 3 transparent packages ($450 Essential, $950 Studio Session, $2,200 Campaign), and that streamlined 5-field booking intake look stunning live. Checked the repo as well, super clean layout. So glad the bounce rate plummeted immediately! Cheering on your busy fall portrait and commercial season!",
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
                    'orozco_commercial_flat_roof_job_photo.png',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 9, 16, 23, 29, 18),
                "Hey Azael! Commercial flat roofing is high-ticket work and building owners want to see two things right away: manufacturer certifications (like Carlisle or Firestone) and clear NDL (No Dollar Limit) warranty coverage.\n\nWe can write your complete 4-page commercial website copy deck, build an Excel roof estimator spreadsheet with working square-foot tear-off formulas, and include a residential consultation section for $345.00 total. Want us to jump into it?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 9, 17, 4, 11, 25),
                "that sounds good. let's focus 100% on commercial flat roofs though—warehouses and retail plazas. can we drop the residential consultation section and knock the price down to $334.95? that way it's straight commercial.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 17, 14, 6, 44),
                "Makes complete sense Azael. Focusing strictly on commercial warehouses and retail plazas gives you much higher credibility with general contractors. Adjusted the invoice down to $334.95 (QP2609-1BD487BA).",
                [],
            ),
            (
                'client',
                dt_utc(2026, 9, 18, 18, 22, 39),
                "great, just got off a commercial strip mall tear-off in McAllen. clearing the $334.95 on my card right now.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 19, 2, 41, 52),
                "Payment confirmed, thank you Azael! Here is your v1 draft copy deck. Take a look when you're off the roof.",
                [
                    'orozco_site_copy_and_estimate_v1.docx',
                ],
            ),
            (
                'client',
                dt_utc(2026, 9, 19, 3, 34, 16),
                "reading through v1 now on my tablet while having tacos in Pharr. this hits the nail on the head with the 60-mil TPO single-ply specs and Factory Mutual 1-90 wind uplift ratings. can we make sure the website prototype has an interactive square-foot bid calculator so warehouse owners can calculate estimates before calling me?",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 19, 3, 44, 31),
                "100%! We integrated an interactive Commercial Square-Foot Bid Calculator directly into your standalone HTML prototype with membrane toggles (60-mil TPO, Standing Seam Metal, Modified Bitumen, Silicone Coating) and 20-Year NDL warranty selectors.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 20, 16, 14, 27),
                "Attached are your completed deliverables: your final commercial copy deck, your customized Excel estimator spreadsheet with working formulas for tear-off and membrane costs, and your standalone interactive HTML website prototype ready to open directly in any browser.",
                [
                    'orozco_site_copy_and_estimate_final.docx',
                    'orozco_estimate_sheet.xlsx',
                    'orozco_roofing_website_prototype.html',
                ],
            ),
            (
                'client',
                dt_utc(2026, 9, 21, 11, 8, 49),
                "opened the prototype and excel sheet on my truck laptop. the square-foot bid calculator and 20-year NDL specs are pure gold. sending the copy to our web guy in Brownsville. gracias hermano!",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 21, 14, 12, 6),
                "De nada Azael! Good luck closing that Pharr warehouse bid. Reach out anytime if you need commercial bid submittals drafted.",
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
                "Hey Jack! Looked through the export. The biggest issue is deals sitting in 'Scoping' for 30+ days without automated task triggers. Are you looking to enforce strict SLA escalation rules across SDRs and AEs, or do you also want us to re-tier your enterprise accounts?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 4, 5, 13, 47, 9),
                "Definitely strict SLA escalation rules. Deals over $25k need to alert the VP of Sales if untouched for 48 hours. Can you turn around a formal routing spec and cleaned export before our Monday executive pipeline review?",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 4, 5, 14, 11, 32),
                "We can deliver the complete CRM lead-routing spec PDF with automated SLA rules and clean up the entire pipeline dataset with stage probability formulas by Sunday evening for $160 flat. Want us to lock this into the weekend sprint?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 4, 5, 14, 18, 50),
                "Approved, that gives our engineering and sales leads exactly what they need for Monday morning. Send the invoice over and let's roll.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 4, 5, 14, 20, 15),
                "Invoice INV-260405-JJ01 ($160.00) is posted in your billing tab. Structuring the stage-gate rules and cleaning the CRM data now!",
                [],
            ),
            (
                'client',
                dt_utc(2026, 4, 5, 14, 25, 18),
                "cleared the $160 on our corporate card. appreciate the rush turnaround!",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 4, 6, 15, 39, 24),
                'Here is the completed lead-routing spec along with the cleaned pipeline dataset ready for your Monday executive review.',
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
                "Great to hear from you Jack! Looked through your brief. The current deck focuses heavily on technical API architecture, but 3PL warehouse general managers care about two things: gate turn times and detention penalties ($1,200/truck/month). We should lead with yard congestion ROI.\n\nWriting all 5 B2B website pages, structuring the 12-slide enterprise PowerPoint deck, and building an interactive terminal prototype with live 12-bay monitoring is $500 flat.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 9, 17, 16, 26, 38),
                "Love that framing. Sorry for the two-day lag, had to get budget sign-off from my cofounder. Send the $500 invoice and I'll clear it now.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 17, 16, 32, 47),
                "Invoice QP2609-5851CC11 ($500.00) is live on your account.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 9, 17, 16, 47, 19),
                "Cleared on Apple Pay.",
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
                "Reviewed with the sales team this morning. Website copy is ready as-is. On Slide 4 of the deck, can we swap the placeholder ROI numbers for our actual Q3 Midwest 3PL pilot (38% faster dock turn time and 14 hrs/wk saved per dispatcher)?",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 19, 15, 28, 34),
                "Updated Slide 4 with the exact Q3 Midwest 3PL pilot metrics! Attached is the final 5-page website copy deck, the 12-slide PowerPoint presentation (.pptx) ready for your sales reps, and the standalone interactive 5-page B2B website prototype ready to demo directly in any browser.",
                [
                    'johnson_b2b_site_and_deck_final.docx',
                    'johnson_12slide_outbound_enterprise_deck.pptx',
                    'johnson_dockstream_b2b_website_prototype.html',
                ],
            ),
            (
                'client',
                dt_utc(2026, 9, 19, 16, 5, 22),
                "Downloaded all three. The interactive terminal prototype with the 12-bay live monitor and detention calculator blew our VP of Sales away. Taking this into our carrier partner meeting tomorrow. Appreciate the great work!",
                [],
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
                "aloha guys! hope the weather is nice over there. so my accountant is breathing down my neck about Q3 reconciliations for our Waikiki catamaran charter business and my Ala Moana rental condo. our bank export has missing vendor names, mixed repair bills, and i honestly don't have the patience to sit in Excel for 10 hours. attached the raw bank CSV and some paper receipts. can you turn this into a clean reconciled ledger?",
                [
                    'luca_q3_raw_bank_export.csv',
                    'luca_august_vendor_receipts.pdf',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 8, 28, 20, 41, 9),
                "Aloha Luca! Happy to take this off your plate. Reconciling charter fuel and harbor dockage against seasonal tourism payouts is right in our wheelhouse. We can reconcile all 50+ transactions across the Waikiki and Ala Moana units, match those Pacific Split-AC and hardware receipts, and give you a clean monthly P&L plus a 50/50 partner distribution breakdown in both Excel and CSV for $220 flat. Want us to jump into it?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 8, 28, 21, 2, 14),
                "mahalo for looking at this so fast! one quick question before you invoice me: does the ledger separate out Hawaii General Excise Tax (GET at 4.712%) and Transient Accommodations Tax (TAT at 10.25%)? that's the main thing my tax guy was nagging me about because Waikiki short-term rentals get audited on TAT all the time.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 8, 28, 21, 5, 30),
                "100%. We calculate base lodging revenue and break out both GET (4.712%) and Honolulu County TAT (10.25% + 3% county surcharge) in dedicated columns with automatic tax liability totals so your accountant can file without doing any extra math. Does that cover everything your CPA needs so we can open up the project?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 8, 28, 21, 15, 40),
                "shaka! that saves me a massive headache and gives my CPA exactly what he asked for. Shoot the invoice over and I'll clear it from the dock.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 8, 28, 21, 18, 10),
                "Awesome Luca! Just posted invoice INV-260814-LC01 ($220.00) in your billing portal. If you're on the boat, you can also tap this direct link: https://paystack.shop/pay/892lxc01po. Diving into the reconciliation now!",
                [],
            ),
            (
                'client',
                dt_utc(2026, 8, 29, 18, 7, 44),
                "just tapped apple pay right as we untied the bow lines for our afternoon Diamond Head sail! Cleared the $220. Let me know if any of the fuel slips are illegible.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 8, 29, 18, 19, 22),
                "Payment confirmed, thank you Luca! Starting on the reconciliation now.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 8, 30, 16, 42, 15),
                "Aloha Luca! Here is the completed reconciliation package: your cleaned Q3 CSV ledger and your multi-tab Excel financial model with automatic GET/TAT tax formulas and partner cash distributions.",
                [
                    'luca_q3_reconciled_ledger.csv',
                    'luca_q3_financial_model.xlsx',
                ],
            ),
            (
                'client',
                dt_utc(2026, 8, 31, 10, 15, 30),
                "just forwarded both workbooks to my accountant and he said it's the cleanest book he's seen from a charter operator all year. mahalo nui loa team!",
                [],
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
                "hey team, need some emergency spreadsheet surgery. our customs broker just hit us with unexpected Section 301 tariffs on our stainless pour-over kettles, and our LCL ocean freight spiked $35/CBM. attached our supplier SKU sheet and the broker duty notice. can you build a dynamic landed-cost & margin calculator so we know which retail prices we need to bump?",
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
                "that CBM volume allocation is exactly what we need. one thing though: our customs broker files under HTS 8516.79.00 for the electric kettles and HTS 7323.93.00 for the manual pour-over carafes. does your model let me input separate tariff percentages per SKU line, or is it a flat rate across the container?",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 14, 9, 29, 45),
                "It's a dynamic SKU-by-SKU lookup. Each product line has its own HTS classification column with the exact ad valorem duty rate (e.g. 2.7% base + 25% Section 301) applied specifically to that SKU's FOB value, so you never over-allocate duty onto non-tariffed items. We can build the full automated margin calculator and staff receiving SOP for $240.00 flat. Would you like us to spin this up for you?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 14, 9, 36, 12),
                "awesome, that will save us hours arguing with accounting. yes please, shoot the invoice over and let's get it rolling.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 14, 9, 38, 50),
                "Posted invoice INV-261014-KC01 ($240.00) in your portal billing tab! Starting the CBM allocation formulas now.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 14, 9, 44, 19),
                "paid the $240 on corporate debit just now.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 15, 8, 31, 52),
                "Here is the draft v1 model for you to test out with your team.",
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
                "Added the 2.1x wholesale tier, locked all formula ranges, and attached your staff receiving handbook PDF!",
                [
                    'keegan_sku_margin_calculator_v2_locked.xlsx',
                    'keegan_staff_sku_guide.pdf',
                    'keegan_warehouse_sku_handbook.pdf',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 15, 11, 24, 50),
                "received! our warehouse receiving supervisor tested it on the morning container delivery and the locked cells worked perfectly. thanks team!",
                [],
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
                "Hi Liza! Medical plaza procurement committees are hyper-focused on insurance certificates ($1M liability), OSHA disinfection compliance, and clean SLA schedules. Are they requesting specialized terminal cleaning protocols for outpatient surgical suites, or standard commercial janitorial?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 9, 13, 52, 16),
                "That disinfection compliance angle is huge—most cleaners just list 'sweeping and mopping' and get tossed in the trash. Yes, they specifically asked for after-hours terminal cleanings for outpatient surgical suites. Can we make sure the rate card includes per-sq-ft biohazard protocols?",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 9, 14, 15, 30),
                "Absolutely. We'll build a dedicated section for Operating Room & Outpatient Terminal Disinfection with per-sq-ft biohazard protocol surcharges, plus the complete vendor compliance manual for $120 flat. Should we prepare this for the Tampa bid?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 9, 14, 28, 45),
                "Yes please, that's exactly what will set us apart from the generic franchise cleaners. Send the invoice over!",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 10, 11, 7, 33),
                "Posted invoice INV-261010-LI01 ($120.00) in your billing portal. Diving into the OSHA disinfection specifications right now!",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 10, 16, 44, 19),
                "cleared on our Tampa office card! sending the updated supervisor phone numbers right now.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 10, 16, 58, 41),
                "Here are your finalized vendor compliance manual and commercial rate card!",
                [
                    'liza_vendor_packet_clean.pdf',
                    'liza_commercial_rate_card.xlsx',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 11, 9, 30, 14),
                "printed 5 bound copies for the procurement committee this morning. the surgical suite disinfection specs look so executive. thank you guys!",
                [],
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
                "Hi Drako! 540 shifts without a single safety incident and running a 14-person cross-dock is leadership gold in modern logistics. Are you targeting general warehouse supervisor roles, or specialized cold-chain and automated distribution facilities?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 10, 8, 14, 52),
                "man, hearing you frame 540 shifts without an incident actually made me stand a little taller haha. I was nervous my high school diploma was gonna hold me back. I'm targeting operations supervisor and cross-dock lead at regional distribution centers. Just promise me no cheesy corporate buzzwords like 'synergistic rockstar'. What's the turnaround and cost to get this done?",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 10, 8, 22, 10),
                "Zero buzzwords, 100% hard dock numbers: trailer throughput, OSHA compliance, labor scheduling, and team leadership. We can build your executive resume and matching LinkedIn profile summary for $25.00 flat and deliver the draft by tomorrow. Ready for us to write the draft?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 10, 8, 26, 40),
                "Sounds great to me, let's do it. Post the bill and I'll clear it.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 10, 8, 30, 12),
                "Invoice INV-261011-DS01 ($25.00) is posted in your billing tab! Drafting the core leadership competencies right now.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 10, 8, 45, 19),
                "paid on debit just now from my phone.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 11, 14, 18, 20),
                "Here is your v1 draft! Take a look and let us know if anything needs tuning.",
                [
                    'drako_resume_operations_supervisor_v1.docx',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 11, 16, 5, 40),
                "reading this over during lunch on the dock—this sounds like a real leader wrote it. can we add one bullet under Sunbelt about coordinating bilingual Spanish/English safety briefings? half our forklift team is Spanish-speaking and the hiring manager will love that.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 11, 17, 30, 45),
                "Added the bilingual shift operations bullet! Attached are your final Word and ATS-formatted PDF resume and LinkedIn summary.",
                [
                    'drako_resume_operations_supervisor_final.pdf',
                    'drako_linkedin_summary_and_application_cover_letter.docx',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 12, 9, 12, 10),
                "downloaded both. submitting the application to regional HR tonight. really appreciate the respect you gave my work man.",
                [],
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
                "Morning Estella! Absolutely—investor updates should read like a focused founder speaking directly to their board, not a dry compliance memo. Took a quick look at your draft: the Q3 numbers are strong ($4.2M ARR, 96.4% gross retention), but the passive phrasing hides the real momentum.\n\nIs this going primarily to institutional LPs, or do you also have enterprise carrier clients reading this?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 5, 7, 56, 30),
                "It actually goes to both, which is why our ops lead panicked and tried to make it sound overly formal. Our lead VC specifically cares about the ARR expansion and runway. How fast could you turn a polished version around?",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 5, 8, 2, 10),
                "We can do a complete tone refinement on the 1,800 words for $25.00 flat, emphasizing the founder voice and ARR momentum while keeping it polished for your enterprise clients. We can have the refined version in your hands within 4 hours. Want us to jump on that?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 5, 8, 4, 45),
                "That would be a lifesaver. Yes please, let's kick it off!",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 5, 8, 6, 20),
                "Great! I just generated invoice INV-261005-EW01 ($25.00) in your billing tab. You can settle it there, or if you're on your phone between meetings you can tap this direct checkout link: https://paystack.shop/pay/tx0ipp9eg4. We're opening up the draft now!",
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
                "Welcome back Estella! Great timing as your team scales. We can build the full 4-role onboarding package with concrete 30-60-90 ramp rubrics and daily checklists for $80 flat ($20 per role). Want us to get rolling on this?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 10, 18, 55, 30),
                "yes please! post the invoice.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 10, 18, 57, 10),
                "Posted invoice INV-261010-EW02 ($80.00).",
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
                'Hi Kaylee! Botanical skincare copy lives and dies on sensory verbs—focusing on cloud textures, dewy absorption, and nighttime rituals rather than just listing clinical chemicals. Are you launching these on Shopify with direct-to-consumer bundles, or are you also pitching wholesale boutique accounts?',
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 4, 19, 12, 35),
                'Strictly Shopify D2C with our 4-bottle ritual bundle! We have a 4-part welcome email sequence that needs the exact same warm tone. Can you tackle both the 12 product descriptions and the welcome sequence?',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 4, 19, 28, 50),
                'We can write complete sensory product descriptions for all 12 SKUs formatted in a ready-to-import Shopify spreadsheet, plus the complete 4-part email retention sequence for $180 flat. Want us to kick this off?',
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 5, 9, 22, 47),
                "yes that's exactly the vibe and budget! please send the invoice so we can kick off.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 5, 9, 37, 18),
                'Posted invoice INV-261005-KC01 ($180.00) in your billing portal. Drafting the sensory product sheets now!',
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
                "Hello Dennis! We can standardize all Southern and Western corridor trips, convert KES fuel burn to USD at historical benchmark rates, and calculate net trip margins. Are you billing your logistics clients on a flat per-container rate or cost-plus fuel surcharges?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 4, 12, 5, 20),
                "we bill on cost-plus fuel surcharges, which is why the toll discrepancies and KES exchange fluctuations are giving us a headache with client audits. What would it cost to clean this up and build an ongoing tracker?",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 4, 12, 12, 45),
                "We can reconcile your entire Q3 corridor dataset and build an automated 12-month multi-sheet cash-flow model with dynamic formula lookups for $140 flat. Should we put this together for you?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 4, 12, 18, 30),
                "yes please, send the invoice over and let's get started.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 5, 8, 31, 47),
                "Posted invoice INV-261005-DK01 ($140.00) in your portal billing tab. Starting the calculations now!",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 5, 8, 45, 10),
                'paid on card just now. let me know once the sheets are ready.',
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
                'downloaded both Excel workbooks and the corridor segment formulas match our fleet dispatch sheets exactly. thank you.',
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
                "Hi Alexa! Trade logistics software is a massive opportunity, but angel investors get anxious when founders pitch broad market sizes instead of proving repeatable pilot traction. Looked through your notes—28 paid pilots and zero logo churn in 90 days is genuinely impressive.\n\nIs your demo day presentation a rapid 3-to-4 minute pitch, or do you have a full 10-minute partner deck slot?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 2, 8, 54, 10),
                "It's a strict 4-minute pitch followed by 3 minutes of partner Q&A. That's exactly why I was stumbling—I was trying to cram 20 operational details into the go-to-market slide instead of telling a clean story. What would the structure and pricing look like to overhaul the slides and unit economics?",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 2, 9, 4, 30),
                "For a 4-minute demo day format, we structure a high-impact 10-slide deck: lead with the operational pain of lost paper logs, showcase your 28 paid pilots and 100% retention, and isolate the unit economics (0.7-month payback). We'll build the full PowerPoint (.pptx) with scripted speaker notes and an accompanying Excel financial model for $250.00 flat. Want us to build that narrative out?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 2, 9, 8, 18),
                "omg yes, that framing is so much sharper and cuts right to what investors care about. Sending the green light!",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 2, 9, 12, 45),
                "Just posted invoice INV-261002-AQ01 ($250.00) in your portal billing tab. Starting on the slide outline now, and I'll drop the v1 narrative architecture in here this afternoon!",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 2, 17, 34, 52),
                'Here is the v1 narrative outline to review, Alexa! Notice how Slide 3 shifts immediately into your 28 paid pilots and 0.7-month payback.',
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
                "Hi Cami! Safe travels on the train. Skimmed the transcripts—the friction between engineering sprint delivery and the VP of Product's roadmap is glaring, while the People Ops notes point to severe manager burnout.\n\nIs this action sheet going straight to their C-suite for sign-off on your advisory scope, or is it for the workshop attendees themselves?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 9, 29, 16, 18, 40),
                "Straight to the CEO and Board. We need to demonstrate that their delivery silos are costing them millions before they'll approve the 4-workshop advisory retainer. What would the turnaround and investment look like for a concise synthesis?",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 29, 16, 35, 12),
                "We can extract the core friction points across all three departments, map them directly to 4 modular workshop agendas, and deliver a clean executive action sheet PDF for $160 flat by tomorrow morning. Want us to proceed with that?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 9, 30, 8, 14, 41),
                "That framing will close the engagement. Yes please, let's do it!",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 30, 8, 29, 56),
                "Just posted invoice INV-260930-CK01 ($160.00) in your portal billing tab. Alongside it, here is the v1 draft synthesis outline so you can review the department breakdown while on the move.",
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
                "Understood Victor. We'll map the exact lexical variation thresholds, anti-cliché heuristics, and syntactic entropy curves.\n\nDo you want us to calibrate specifically against Turnitin and GPTZero enterprise classifiers?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 9, 29, 14, 42, 10),
                "Yes, exactly—both Turnitin and GPTZero at sub-3% AI detection thresholds. What is the turnaround and cost for the blueprint schema?",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 29, 14, 55, 30),
                "We can deliver the complete JSON tone calibration blueprint with all mathematical weights, persona prompts, and classifier benchmarks for $150.00 flat in under 3 hours. Want us to compile that for you?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 9, 29, 15, 8, 15),
                "Approved. Post the invoice to our ledger and we'll process payment right away.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 29, 15, 12, 40),
                "Posted invoice INV-260929-VM01 ($150.00) to your enterprise billing tab. Compiling the heuristic parameters now!",
                [],
            ),
            (
                'client',
                dt_utc(2026, 9, 29, 15, 29, 50),
                "Payment cleared on our company card.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 9, 29, 16, 37, 12),
                'Payment confirmed, thank you Victor! Here is the finalized tone calibration blueprint JSON.',
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
                "Hi Lina! Polite emails get ignored. The issue with your drafts is that the product benefit is buried in paragraph 3, and the CTA button says 'Shop Now' instead of creating urgency around reserved inventory. Are these going out to repeat VIP buyers or your cold acquisition list?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 7, 25, 11, 5, 19),
                "These are going out to our VIP customer segment who bought our spring linen drop. That diagnostic is so true—we were so afraid of sounding pushy that we sounded boring. Can you rewrite the 5 summer retention emails and polish our spring collection copy deck?",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 7, 25, 11, 24, 30),
                "We can restructure all 5 summer emails with punchy subject lines and benefit-driven urgency, plus polish the spring storefront copy deck for $120 flat. Want us to get started?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 7, 26, 9, 17, 33),
                "100%, that's a no-brainer. Send the invoice over!",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 7, 26, 9, 32, 18),
                "Posted invoice INV-260726-LR01 ($120.00) in your billing tab. Drafting the email hooks now!",
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
                "Hello Patrick! We know the Marine Atlantic Port aux Basques ferry rates can throw a massive wrench into driver settlement sheets. Are your dispatch sheets tracking solely the Newfoundland coastal routes, or do you have interprovincial hauls coming through Nova Scotia?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 6, 27, 16, 12, 40),
                "we run both—coastal NL distribution plus the Trans-Canada highway link through North Sydney into Nova Scotia. When the ferry gets delayed 18 hours due to gale warnings, our standby demurrage gets completely lost. Can you build formulas that capture both?",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 6, 27, 16, 28, 15),
                "We'll build a formula model that separates ferry tolls from driving mileage, tracks standby demurrage hours, and applies sliding diesel index surcharges automatically for $175 flat. Shall we put this together for you?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 6, 28, 9, 11, 54),
                "that'll save our dispatchers from pulling their hair out every blizzard. send the bill over, let's get it done.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 6, 28, 9, 27, 36),
                "Posted invoice INV-260628-PH01 ($175.00) in your billing tab. Building the dispatch model now!",
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
                "hey team! we're about 10 days out from our public product launch for the ApexDesk modular rail. our mechanical engineer put together our product descriptions, but honestly the headline copy is dry as dust and reads like a CNC machine shop invoice: '6063-T6 aluminum extrusion with chamfered edges'. attached our storefront notes, can you guys help us make this actually feel like an Apple-grade luxury desk ecosystem?",
                [
                    'carter_storefront_launch_notes.docx',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 5, 7, 14, 42, 19),
                "Hi Carter! Hardware buyers don't buy alloy codes—they buy the feeling of an immaculate, zero-cable desktop, the solid tactile thud of a unibody rail, and the satisfying snap of a magnetic Qi2 dock.\n\nWe can write your complete 3-tier storefront copy deck (Unibody Rail, MagSafe Qi2 Dock, CNC Cable Channels), build a standalone interactive HTML prototype with a live 3D unibody colorway toggle and modular rail builder, and assemble a 28-point Shopify pre-launch QA checklist for $290 flat.\n\nWant us to dive into this?",
                [],
            ),
            (
                'client',
                dt_utc(2026, 5, 7, 14, 55, 0),
                "hearing you contrast the CNC machine-shop voice against the zero-cable vision made me laugh because that's literally what our first beta tester said haha.\n\nquick question before we jump in: does the interactive HTML prototype work cleanly on mobile? our Kickstarter & Instagram traffic is probably 70% phones and i want to make sure the modular rail builder doesn't get squished.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 5, 7, 15, 2, 45),
                "100% mobile-optimized. We build the rail builder with touch swipe toggles and an Apple Pay sheet modal that fits neatly on phone viewports so your mobile backers can configure their kit in under 60 seconds without horizontal scroll bugs.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 5, 7, 15, 6, 12),
                "sold. shoot the invoice over and i'll clear it on our company card right now.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 5, 7, 15, 8, 30),
                "Posted invoice INV-260508-CL01 ($290.00). Drafting the copy deck and assembling the interactive prototype now!",
                [],
            ),
            (
                'client',
                dt_utc(2026, 5, 7, 15, 14, 25),
                "cleared the $290 on apple pay! stoked to see what you guys put together.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 5, 8, 11, 20, 14),
                "Here is the v1 draft copy deck! Notice how we renamed 'Base Gray' to 'Space Black Bead-Blasted' and anchored the modular rail around 'Zero-Cable Architecture'. Take a look and let us know what you think.",
                [
                    'carter_website_launch_checklist_final.pdf',
                ],
            ),
            (
                'client',
                dt_utc(2026, 5, 8, 13, 42, 10),
                "this copy is night-and-day better man. reading the hero section gave me chills.\n\none small tweak: on the specification badge, can we change '1-Year Limited Warranty' to 'Lifetime Unibody Guarantee'? our CNC tolerances are ±0.02mm so the aluminum rail is physically indestructible. also want to make sure the prototype calculates the Qi2 charger add-on accurately in the subtotal.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 5, 8, 15, 30, 22),
                "Love the 'Lifetime Unibody Guarantee'—that signals uncompromising aerospace build quality immediately. Subtotal logic is locked in with live magnetic module calculations.\n\nAttached is your complete launch deliverable package: your standalone interactive HTML landing page prototype ready to open and test live in any browser, the finalized 28-point pre-launch QA checklist, and the full digital asset ZIP pack.",
                [
                    'carter_landing_page_prototype.html',
                    'carter_storefront_assets_and_launch_kit.zip',
                    'carter_website_launch_checklist_final.pdf',
                ],
            ),
            (
                'client',
                dt_utc(2026, 5, 8, 16, 19, 48),
                "just spent 15 minutes playing with the colorway toggle and modular rail builder on my iPhone—this feels smoother than Apple's configurator! sending the copy deck to our Shopify engineer right now. seriously grateful for the quick turnaround!",
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
                "Just posted invoice INV-261020-IC01 ($240.00) in your portal billing tab! If you're on your clinic tablet between patient sessions, you can also clear it directly via Apple Pay here: https://paystack.shop/pay/tx0ipp9eg4. Once that clears, I'll release the complete print-ready PDF agreement and intake bundle so you have everything before your evening appointments.",
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
        seed_files.update(build_all_authentic_deliverables())
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
            if primary_email.lower() == "valdaceai@gmail.com":
                user.is_staff = True
                user.is_superuser = True
                user.save(update_fields=["is_staff", "is_superuser"])
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
            for idx, msg_tuple in enumerate(spec["messages"]):
                sender, msg_dt, body = msg_tuple[0], msg_tuple[1], msg_tuple[2]
                att_keys = msg_tuple[3] if len(msg_tuple) > 3 else []
                att_objs = [seed_files[k] for k in att_keys if k in seed_files]

                if idx == 0 and spec.get("requests"):
                    req = spec["requests"][0]
                    from platformhub.catalog import SERVICE_INDEX
                    svc = SERVICE_INDEX.get(req.get("service_code", ""), {})
                    svc_name = svc.get("name") or req.get("service_code", "Custom Project")
                    client_name = f"{spec.get('first_name', '')} {spec.get('last_name', '')}".strip() or "Client"

                    brief_lines = [
                        "Project Brief Submitted via /request/",
                        "--------------------------------------------------",
                        f"Project Name: {req.get('title', 'Service Request')}",
                        f"Reference: {req.get('reference', 'INF-REQ')}",
                        f"Service: {svc_name} ({req.get('service_code', '')})",
                        f"Client: {client_name} <{primary_email}>",
                    ]
                    company = spec.get("company")
                    if company:
                        brief_lines.append(f"Company / Team: {company}")
                    brief_lines.extend([
                        "",
                        "Objective:",
                        req.get("objective", "").strip(),
                        "",
                        "Current Materials & Scope:",
                        req.get("scope", "").strip(),
                    ])
                    if body:
                        brief_lines.extend([
                            "",
                            "Intake Notes:",
                            body.strip(),
                        ])
                    brief_lines.extend([
                        "",
                        "Requested Deliverables:",
                        req.get("deliverable", "").strip(),
                        "",
                        f"Turnaround: Priority · Research: Standard · Estimated Band: USD {req.get('estimate_low', '25.00')}–{req.get('estimate_high', '50.00')}",
                    ])
                    body = "\n".join(brief_lines).strip()

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
