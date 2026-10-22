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
        "Landed_Cost_&_Margin_Model",
        [
            ["SKU", "Item Description", "Supplier FOB", "Allocated Ocean", "Customs Duty", "Landed Cost", "Wholesale (2.1x)", "MSRP Retail", "Gross Margin", "45-Day Reorder"],
            ["KC-101", "Precision Kettle 1.2L", 8.40, 1.05, 0.92, 10.37, 21.78, 34.00, "69.5%", 180],
            ["KC-102", "Burr Hand Grinder", 14.20, 0.51, 0.53, 15.24, 32.00, 58.00, "73.7%", 120],
            ["KC-103", "Espresso Scale USB-C", 6.15, 0.26, 0.28, 6.69, 14.05, 29.00, "76.9%", 250],
            ["KC-104", "Glass Mug 2pk", 3.80, 0.63, 0.23, 4.66, 9.79, 24.00, "80.6%", 300],
            ["KC-105", "Ceramic Dripper 02", 2.90, 0.25, 0.19, 3.34, 7.01, 18.00, "81.4%", 220],
            ["KC-106", "Silicone Tamping Mat", 1.45, 0.13, 0.05, 1.63, 3.42, 12.00, "86.4%", 400],
            ["KC-107", "Cold Brew Pitcher", 5.20, 0.72, 0.18, 6.10, 12.81, 28.00, "78.2%", 150],
            ["KC-108", "WDT Needle Tool", 2.10, 0.09, 0.08, 2.27, 4.77, 16.00, "85.8%", 350],
        ],
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
    # DIVERSE DELIVERABLE: Real ZIP pack containing PPTX, XLSX, and DOCX
    files["estella_q4_executive_board_pack.zip"] = write_zip_file(
        "estella_q4_executive_board_pack.zip",
        {
            "README_BOARD_PACK.txt": "Estella Williams — Q4 Executive Board Package\nIncludes: 16-Slide Board Deck (.pptx), Cap Table & Projections (.xlsx), Briefing Memo (.docx).",
            "Q4_Board_Briefing_Memo.docx": "Executive Board Briefing Memo\nPrepared for Q4 Board of Directors Review.\nKey Highlights:\n- 114% Net Revenue Retention\n- 18.2-month cash runway\n- Headcount plan frozen until Q1 ARR target achieved.",
            "Q4_Financial_Projections_Model.csv": "Metric,Q1 2026,Q2 2026,Q3 2026,Q4 Forecast,FY 2027\nARR ($M),2.8,3.4,4.2,5.1,7.8\nGross Margin (%),74%,76%,77%,78%,81%\nBurn Multiple,1.4,1.1,0.85,0.72,0.55\nEnding Cash ($M),6.2,5.5,4.9,4.4,7.5",
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
        "Commercial_Roof_Estimator",
        [
            ["Roof Section", "System Type", "Square Footage", "Tear-Off Cost / Sq", "Membrane / Sq", "Labor / Sq", "Total Section Cost"],
            ["Main Warehouse Deck", "60-mil TPO Single-Ply", 18500, 85.00, 240.00, 115.00, 81400.00],
            ["Front Office Mansard", "24-Gauge Standing Seam", 3200, 110.00, 385.00, 160.00, 20960.00],
            ["Loading Dock Overhang", "EPDM Ballasted", 2400, 75.00, 195.00, 95.00, 8760.00],
        ],
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
            ["Trip #", "Driver", "Origin / Dest", "Mileage", "Fuel Burn (CAD)", "Marine Atlantic Ferry", "Driver Pay ($0.60/km)", "Client Billing", "Net Profit", "Margin %"],
            ["TR-401", "G. O'Brien", "St. John's → Corner Brook", 685, 533.60, 0.00, 411.00, 1680.00, 735.40, "43.8%"],
            ["TR-402", "M. Walsh", "Corner Brook → Port aux Basques", 220, 176.70, 420.00, 132.00, 1150.00, 421.30, "36.6%"],
            ["TR-403", "C. Power", "St. John's → Gander", 335, 266.80, 0.00, 201.00, 890.00, 422.20, "47.4%"],
            ["TR-404", "G. O'Brien", "Gander → Grand Falls-Windsor", 95, 76.50, 0.00, 57.00, 380.00, 246.50, "64.9%"],
            ["TR-405", "D. Murphy", "Port aux Basques → North Sydney", 180, 144.00, 680.00, 108.00, 1820.00, 888.00, "48.8%"],
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
        "ApexDesk MagSafe Modular Dock — Live Storefront Preview",
        """
        <p><strong>The last desk dock you will ever need.</strong> Precision CNC-machined aerospace aluminum with modular 15W wireless charging pucks.</p>
        <h2>Key Product Highlights</h2>
        <ul>
          <li><strong>Universal Modular Rail:</strong> Snap in phone mounts, earbud pads, and pencil docks in any order.</li>
          <li><strong>Single-Cable Cleanliness:</strong> One braided 100W USB-C input powers all 4 accessories.</li>
          <li><strong>Thermal Management:</strong> Solid aluminum heatsink keeps MagSafe charging at full speed.</li>
        </ul>
        <h2>Launch Pricing & Packages</h2>
        <p>— <em>Starter Kit:</em> $129 (Base Rail + 15W Phone Charger + Cable Caddy)<br>
        — <em>Studio Pro Bundle:</em> $199 (Base Rail + Phone + Watch + AirPods Pad + Walnut Pen Tray)</p>
        <p style="margin-top: 30px;"><a href="#preorder" style="display:inline-block; background:#cc4b2c; color:#fff; padding:12px 24px; text-decoration:none; border-radius:6px; font-weight:bold;">Pre-Order Now — Limited First Batch</a></p>
        """,
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
                dt_utc(2026, 10, 17, 21, 26, 48),
                "Hey Jose! Good to connect. Asset-based carriers have a huge edge right now because shippers are fed up with brokers dropping loads. We can turn your rough notes into a punchy executive capability bio plus 3 cold outreach emails targeting warehouse dock managers and shipping supervisors across DFW. We'll also throw in a clean digital rate card graphic. Total package is $25.00 flat. We typically do an initial $1.00 card test deposit to clear fraud filters with your bank, with the remaining $24.00 on final approval.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 18, 19, 27, 14),
                'sounds fair. i tried paying through the normal checkout earlier this afternoon but my debit card got flagged for fraud by chase bank because of the processor location i think. do you have a direct link?',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 18, 19, 41, 33),
                'Posted the $1.00 card test deposit invoice INV-261018-JC01. You can clear it directly here: https://paystack.shop/pay/4q5iounn6s',
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 18, 19, 43, 19),
                'wait where do I pay? is it the link above or inside the portal?',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 18, 19, 44, 10),
                'You can tap that direct link right on your phone: https://paystack.shop/pay/4q5iounn6s. It supports Apple Pay or standard debit card and syncs straight to this ticket.',
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 18, 19, 45, 28),
                'alright that direct link worked smooth! paid the $1 test deposit on apple pay. send over the preview when you have it.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 18, 21, 28, 52),
                'Payment received, thank you Jose! Here is the v1 draft preview of your capability bio and the first 2 outreach emails.',
                [
                    'cruz_bio_and_emails_v1_preview.pdf',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 18, 21, 31, 19),
                'man this reads way better than what i had. can we add a line in email 2 about our liftgates having 3500lb capacity? some of these warehouse managers have heavy palletized machinery and ask about that right away. also ready to pay the $24 balance.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 18, 21, 33, 40),
                'Spot on—highlighting 3,500-lb tuck-under liftgate capacity proves you can handle heavy machinery without relying on their dock equipment. Added to Email 2 and posted the remaining $24 balance invoice (INV-261018-JC02). You can use the same direct link: https://paystack.shop/pay/4q5iounn6s',
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 18, 21, 41, 55),
                'done! cleared the $24 balance on apple pay just now.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 19, 13, 41, 29),
                'Payment confirmed, thank you Jose! Here is your complete final package: the final Word copy deck and your clean 2026 DFW rate card graphic.',
                [
                    'cruz_bio_and_outreach_final.docx',
                    'cruz_freight_rates_card.png',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 19, 14, 7, 54),
                'downloaded both. that rate card graphic looks awesome on my phone, already texted it to a shipper in Carrollton. appreciate the quick turnaround man!',
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
                "Hi Audrey! Love your photography work—the lighting in your portfolio is stunning. But you're totally right about the funnel leak: asking 14 questions before showing package rates creates massive anxiety for clients. We can do a deep copy & funnel audit for $90 (posted INV-260930-AB01) that maps out an exact 5-question intake, upfront pricing anchors, and hero copy fixes.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 9, 30, 19, 58, 43),
                'oh awesome, that was fast! just paid the $90 with apple pay. excited to see what we can streamline.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 1, 16, 11, 29),
                'Here is your completed audit report! It breaks down the exact hero headline repositioning, package pricing anchors, and cuts your intake form from 14 questions down to 5 essentials.',
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
                'client',
                dt_utc(2026, 10, 14, 22, 39, 41),
                'hey! sorry it took almost two weeks, my designer was backed up with wedding season. here are the wireframe notes for the 3 pages (Home, Services, and Booking). ready to do the $270 package whenever you can send the invoice.',
                [
                    'audrey_wireframe_notes.docx',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 10, 15, 7, 13, 28),
                'Morning Audrey! Got the wireframe doc and posted INV-261015-AB02 for $270.00.',
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 15, 8, 41, 39),
                'ugh my card keeps declining on checkout. tried twice on apple pay and once typing it in. is something weird going on with the payment button?',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 15, 8, 48, 22),
                'We actually noticed an issue with our normal payment route this morning—our processor is undergoing a scheduled gateway maintenance sync which is causing card checkout drops. You can use our direct verified link instead to clear the invoice: https://paystack.shop/pay/ppiajw3f1-',
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 15, 9, 11, 47),
                'Wait, why a separate link? Is that safe? I usually only put card details directly through the main site portal, I get a little nervous paying through external links.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 15, 9, 19, 14),
                "Totally get the caution Audrey, you're 100% right to double-check! That's our direct hosted merchant store on Paystack (our payment processor), so your transaction is fully encrypted with 256-bit SSL, has standard buyer protection, and supports Apple Pay without exposing your card numbers. It routes straight to our verified business settlement account and logs right onto your invoice here.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 15, 9, 26, 8),
                'Oh okay, that makes total sense then! Thanks for explaining, was just being careful. Going to use that link right now.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 16, 15, 17, 33),
                'Sounds great! While the payment clears, here is v1 of the 3-page website copy deck so you and your designer can start reviewing it over the weekend.',
                [
                    'audrey_3page_website_copy_v1.docx',
                ],
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
                'Payment confirmed, thank you Audrey! I updated the three package names on the Services page and switched the Booking page hours to Mon–Fri only. Attached is your final Word copy deck plus a crisp UX wireframe diagram for your designer.',
                [
                    'audrey_3page_website_copy_final.docx',
                    'audrey_booking_flow_wireframe_diagram.png',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 17, 17, 11, 52),
                'Sent it straight to my designer! Thank you guys for being so patient with the payment questions and turning around such beautiful copy.',
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
                'Both payments received, thank you Azael! Attached are the final commercial copy deck and your customized Excel estimator spreadsheet.',
                [
                    'orozco_site_copy_and_estimate_final.docx',
                    'orozco_estimate_sheet.xlsx',
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
                'Updated Slide 4 with the exact Q3 Midwest 3PL pilot metrics! Attached is the final 5-page website copy deck plus the complete 12-slide PowerPoint presentation (.pptx) ready for your sales reps.',
                [
                    'johnson_b2b_site_and_deck_final.docx',
                    'johnson_12slide_outbound_enterprise_deck.pptx',
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
                'Here are your final charter assets: the guest booking brochure PDF and your seasonal harbor manifest Excel model!',
                [
                    'luca_oahu_charter_booking_deck_final.pdf',
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
                dt_utc(2026, 10, 5, 4, 58, 32),
                'Morning Estella! Yes, absolutely—executive communication should sound like an authentic leader speaking directly to partners, not compliance disclaimers. We can do a comprehensive humanize & refine pass on the 1,800 words for $25.00 flat (posted invoice INV-261005-EW01). We will preserve all your underlying growth metrics while giving the prose energy and flow.',
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 5, 5, 9, 41),
                'perfect, just paid the $25 invoice with our company card. looking forward to seeing how you reshape it.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 5, 11, 34, 15),
                'Here is your refined October leadership memo! We restructured the opening hooks, trimmed passive clauses, and framed your Q3 milestones with clear narrative momentum.',
                [
                    'estella_october_newsletter_refined.docx',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 5, 14, 12, 8),
                'this reads ten times better than the draft my ops lead wrote. sent it to our email list this morning and already got 4 positive replies from LPs. saving your contact info for our next sprints!',
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
                'Welcome back Estella! Great timing as your team scales. We can build the full 4-role onboarding package with concrete 30-60-90 ramp rubrics and daily checklists for $80.00 ($20 per role). Posted invoice INV-261010-EW02.',
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 10, 19, 1, 45),
                'trying to pay the $80 on my phone right now while waiting for a flight at DFW, but the page keeps spinning on the card field. do you have a direct link?',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 10, 19, 2, 50),
                'Yes! You can clear it directly here on mobile: https://paystack.shop/pay/tx0ipp9eg4. It accepts card or Apple Pay and routes straight to your invoice.',
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 10, 19, 4, 12),
                'ugh the first attempt lagged out on cellular, but that direct link went right through with my card. $80 paid. boarding now, talk tomorrow!',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 11, 14, 31, 54),
                'Here is the draft v1 of the 4-role onboarding framework covering Lead Dispatcher, Customer Ops, Billing Specialist, and Account Exec.',
                [
                    'estella_4role_onboarding_sops_v1.docx',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 12, 9, 18, 22),
                'Reviewed v1 over coffee. Outstanding structure. The 60-day ramp milestones for the billing specialist are exactly what we were missing. Ready for the final PDF whenever it is wrapped.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 12, 15, 16, 39),
                'Here is the finalized executive onboarding manual PDF with all ramp rubrics and role sign-off checklists locked in.',
                [
                    'estella_4role_onboarding_sops_final.pdf',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 12, 17, 27, 14),
                'The hiring managers love the rubrics, thank you!',
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 20, 19, 14, 55),
                'Back again with an urgent task: our Q4 board meeting is Thursday and our internal slide deck is a chaotic 40-page bullet dump. Attached are the raw bullets—I need a tight 16-slide presentation structure and a 2-page briefing memo focusing on our 114% Net Revenue Retention and runway extension.',
                [
                    'estella_q4_board_deck_rough_bullets.docx',
                ],
            ),
            (
                'admin',
                dt_utc(2026, 10, 20, 19, 38, 21),
                'We can turn this into an executive 16-slide presentation, briefing memo, and financial schedule for $150.00 flat.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 20, 21, 13, 38),
                'Posted invoice INV-261021-EW03 ($150.00). Drafting the board pack now. You can clear the invoice via our direct checkout store here: https://paystack.shop/pay/tx0ipp9eg4',
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
                dt_utc(2026, 10, 21, 4, 17, 49),
                'Here is the final deliverable package: your executive briefing memo, slide copy layouts, and the full downloadable board pack ZIP bundle containing deck, financial CSV, and memos.',
                [
                    'estella_q4_board_briefing_memo_final.docx',
                    'estella_q4_investor_deck_slide_copy_final.pdf',
                    'estella_q4_executive_board_pack.zip',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 21, 7, 4, 12),
                "Downloaded the ZIP and walked through the briefing memo with our chairman. He said it was the clearest narrative we've ever presented. You guys are lifesavers!",
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
                'client',
                dt_utc(2026, 10, 5, 14, 11, 28),
                'paid on card. downloaded the reconciliation workbook and the corridor segment margins match our dispatch sheets exactly. thank you.',
                [
                    'dennis_q3_corridor_reconciliation_final.xlsx',
                ],
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
                'Here is your final 5-email retention sequence with 2 subject line variants per blast!',
                [
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
                'Here is your completed Atlantic dispatch and fuel surcharge workbook! All ferry crossing line items are isolated from driver mileage payouts.',
                [
                    'patrick_dispatch_and_fuel_tracker_final.xlsx',
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
                'client',
                dt_utc(2026, 5, 8, 16, 19, 48),
                'paid! just tested the live HTML prototype in my browser—it looks so sleek! opening the ZIP pack now.',
                [
                    'carter_landing_page_prototype.html',
                    'carter_storefront_assets_and_launch_kit.zip',
                    'carter_website_launch_checklist_final.pdf',
                ],
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
                dt_utc(2026, 10, 6, 15, 38, 42),
                "Hey Issa! Haha yeah, Audrey’s booking flow had about 14 questions too many—we had to strip it down to the essentials. We definitely do clinical intake and compliance workflows. Pediatric practices are tricky because you've got parent guarantors vs minor patients, plus observation video consent if therapists record sessions for home practice. Send over whatever messy Word doc or Google Doc you're currently using; don't worry about tidying it up, we'll tear into the fee disclosures and legal language directly.",
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
                "We tailor clinical terms directly to therapy practices—including explicit clauses for parent observation mirrors, home exercise video authorization, and sensory therapy safety disclosures. We'll have v1 ready for your review by Friday.",
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
                'Here is v1 of the Pediatric Clinical Intake & Consent Agreement. It includes all specialized observation clauses, HIPAA consents, and parent financial disclosure terms.',
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
                'Here is v2 of the Clinical Intake Agreement incorporating all three revisions: strict patient/guarantor designations, the $75 reserved clinical hour term, and the progress evaluation disclaimer. Attached alongside is the Parent Communication Templates deck with all 3 intake and fee scripts.',
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
                'Added the superbill 1st-of-month generation schedule to both the intake agreement and the parent welcome email script. All clauses are locked.',
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 20, 17, 14, 18),
                'Okay where do I pay? I need to get this off my to-do list before my 7pm patient.',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 20, 17, 29, 43),
                "We are actually experiencing a temporary sync issue with our normal payment route at the moment; our payment gateway is running an internal maintenance cycle. We'll share the direct link with you shortly once it clears.",
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 20, 17, 41, 9),
                "Are you serious? Why didn't you mention that earlier? Is my delivery going to be delayed because of this? I have a new speech pathologist starting clinical intake on Monday and parents need to sign this paperwork before their morning sessions. I can't wait around for IT issues.",
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 20, 18, 9, 26),
                'Completely understand the urgency Issa, and apologize for the inconvenience. The cleared route is live right now: https://paystack.shop/pay/tx0ipp9eg4. As soon as that clears, the final binder-ready PDF will unlock immediately.',
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 20, 18, 23, 44),
                'Trying my card now... Ugh, the form dropped the connection on my autofill. Let me switch to Apple Pay.',
                [],
            ),
            (
                'client',
                dt_utc(2026, 10, 20, 18, 26, 12),
                'Alright Apple Pay went through. $240 paid. Where are my clean Word docs?',
                [],
            ),
            (
                'admin',
                dt_utc(2026, 10, 20, 18, 29, 7),
                'Payment received, thank you Issa! Here is the complete clinical delivery: your final print-ready PDF agreement and the full downloadable clinical intake forms ZIP bundle.',
                [
                    'cuevas_speech_clinic_service_agreement_final.pdf',
                    'cuevas_pediatric_intake_forms_bundle.zip',
                ],
            ),
            (
                'client',
                dt_utc(2026, 10, 20, 18, 41, 35),
                "Got them downloaded. The clause formatting on page 3 looks much cleaner now. Thank you for turning it around so fast—I'll let Audrey know you survived my revisions lol.",
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
