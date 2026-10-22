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
    write_pdf_file,
    write_xlsx_file,
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
    """Generate real downloadable DOCX, XLSX, PDF, and CSV files for all chat threads."""
    files = {}

    # 1. Jose Cruz
    files["cruz_old_bio_draft.docx"] = write_docx_file(
        "cruz_old_bio_draft.docx",
        "Cruz Metro Freight — Draft Bio & Cold Emails (Rough)",
        [
            "About Us: Cruz Metro Freight is a regional box-truck and sprinter van carrier based in Dallas. We do same-day pallet drops and scheduled retail replenishment.",
            "Email 1 (Cold intro to warehouse managers): Hey [Name], reaching out because we have two 26ft box trucks with liftgates open on Tuesdays and Thursdays in DFW...",
            "Email 2 (Follow up): Just checking in to see if your current broker ever misses morning dock windows...",
            "Email 3 (Rate sheet follow-up): Here is our standard per-mile and flat metro rate— [note: need to finish typing the detention policy part]",
        ],
        role="source",
    )
    files["cruz_bio_and_emails_v1_preview.pdf"] = write_pdf_file(
        "cruz_bio_and_emails_v1_preview.pdf",
        "Cruz Metro Freight — Company Bio & 3 Outreach Emails (v1 Preview)",
        [
            "1. COMPANY BIO (WEBSITE & CAPABILITY STATEMENT)",
            "Cruz Metro Freight runs dedicated 26-foot liftgate box trucks and high-roof sprinters",
            "across the Dallas-Fort Worth corridor. We handle scheduled dock-to-dock retail",
            "replenishment, same-day pallet recovery, and time-critical warehouse transfers.",
            "",
            "2. OUTREACH EMAIL #1 — INITIAL DOCK MANAGER INTRO",
            "Subject: Dedicated liftgate capacity in DFW (Tue/Thu dock windows)",
            "Hi {{First_Name}}, we have two 26ft liftgate trucks running DFW industrial parks...",
            "",
            "3. OUTREACH EMAIL #2 — MISSED PICKUP RECOVERY",
            "Subject: Backup carrier for same-day DFW pallet recovery",
            "",
            "4. OUTREACH EMAIL #3 — RATE & DETENTION TERMS",
            "Includes 2-hour free dock window and transparent flat metro zone pricing.",
        ],
        role="draft",
    )
    files["cruz_bio_and_outreach_final.docx"] = write_docx_file(
        "cruz_bio_and_outreach_final.docx",
        "Cruz Metro Freight — Final Bio & Outreach Sequence (v2 Final)",
        [
            "COMPANY PROFILE: Cruz Metro Freight provides direct, asset-based box-truck and sprinter van freight across DFW without broker markups.",
            "EMAIL 1 — Subject: Open Tue/Thu liftgate capacity in DFW",
            "EMAIL 2 — Subject: Same-day DFW pallet backup",
            "EMAIL 3 — Subject: Flat metro rates (Effective Nov 1, 2026)",
            "Rates effective November 1, 2026. Includes 2-hour free dock window and flat metro zone pricing within 40 miles.",
            "Templates formatted with short mobile-friendly subject lines and clear dispatcher contact info.",
        ],
        role="deliverable",
    )

    # 2. Audrey Brown
    files["audrey_current_site_screenshots.pdf"] = write_pdf_file(
        "audrey_current_site_screenshots.pdf",
        "Studio Brown — Current Homepage & Booking Funnel Captures",
        [
            "Captured mobile and desktop views of current Squarespace homepage.",
            "Issue 1: Above-the-fold headline doesn't mention location or core service packages.",
            "Issue 2: Booking button opens a 14-field intake form before showing base pricing.",
            "Issue 3: Services page mixes add-ons with full packages in one long paragraph.",
        ],
        role="source",
    )
    files["audrey_homepage_booking_audit.pdf"] = write_pdf_file(
        "audrey_homepage_booking_audit.pdf",
        "Homepage & Booking-Flow Copy Audit — Studio Brown",
        [
            "1. HERO SECTION FIXES",
            "Replace generic welcome headline with clear positioning + direct 'Check Availability' CTA.",
            "2. BOOKING FUNNEL FRICTION",
            "Cut intake form from 14 fields down to 5 essential fields (Name, Date, Package, Phone, Notes).",
            "3. PRICING ANCHOR",
            "Display starting package rates on the Services cards before sending visitors to the calendar.",
        ],
        role="deliverable",
    )
    files["audrey_wireframe_notes.docx"] = write_docx_file(
        "audrey_wireframe_notes.docx",
        "Designer Wireframe Notes — 3-Page Site Rebuild",
        [
            "Page 1: Home (Hero, 3 signature packages preview, client reviews, FAQ strip)",
            "Page 2: Services & Pricing (3 tiers + add-on menu)",
            "Page 3: Booking page ( Calendar embed + 5-question intake + deposit policy)",
        ],
        role="source",
    )
    files["audrey_3page_website_copy_v1.docx"] = write_docx_file(
        "audrey_3page_website_copy_v1.docx",
        "Studio Brown — 3-Page Website Copy Deck (v1 Draft)",
        [
            "HOME PAGE COPY: Headline, subhead, 3 service cards, and trust strip.",
            "SERVICES PAGE COPY: Tier 1 (Starter), Tier 2 (Signature), Tier 3 (Full Production).",
            "BOOKING PAGE COPY: Expectations checklist, 48-hour reschedule notice, and confirmation blurb.",
        ],
        role="draft",
    )
    files["audrey_3page_website_copy_final.docx"] = write_docx_file(
        "audrey_3page_website_copy_final.docx",
        "Studio Brown — 3-Page Website Copy Deck (v2 Final)",
        [
            "Updated Services tier names to Essential, Studio Session, and Full Day Campaign per feedback.",
            "Removed Saturday/Sunday call scheduling note on the Booking page and updated hours to Mon-Fri.",
            "Ready for direct paste into Figma and Squarespace.",
        ],
        role="deliverable",
    )

    # 3. Keegan Chin
    files["keegan_raw_sku_list.xlsx"] = write_xlsx_file(
        "keegan_raw_sku_list.xlsx",
        "Raw_SKUs",
        [
            ["SKU", "Item Name", "FOB Unit Cost (USD)", "Carton Qty", "Carton CBM", "Duty %", "Current Retail"],
            ["KC-101", "Stainless Pour-Over Kettle 1.2L", 8.40, 12, 0.068, "", 34.00],
            ["KC-102", "Burr Hand Grinder Aluminum", 14.20, 20, 0.055, "", 58.00],
            ["KC-103", "Digital Espresso Scale", 6.15, 30, 0.042, 0.045, 29.00],
            ["KC-104", "Double-Wall Glass Mug Set (2pk)", 3.80, 24, 0.082, "", 24.00],
        ],
        role="source",
    )
    files["keegan_freight_duty_rates.pdf"] = write_pdf_file(
        "keegan_freight_duty_rates.pdf",
        "Customs BrokerHTS Duty & Ocean LCL Rates",
        [
            "HTS 7323.93 (Stainless kitchenware): 3.4% duty + 7.5% Section 301 tariff",
            "HTS 8210.00 (Mechanical hand grinders): 3.7% duty",
            "HTS 7013.42 (Borosilicate glassware): 6.0% duty",
            "LCL Ocean + Drayage to LA warehouse: $185.00 per CBM + $140 flat customs entry fee.",
        ],
        role="source",
    )
    files["keegan_sku_margin_calculator_v1.xlsx"] = write_xlsx_file(
        "keegan_sku_margin_calculator_v1.xlsx",
        "Margin_Calculator_v1",
        [
            ["SKU", "Item Name", "FOB Cost", "Freight/Unit", "Duty/Unit", "Landed Cost", "Retail Price", "Gross Margin %", "Reorder Point"],
            ["KC-101", "Stainless Pour-Over Kettle 1.2L", 8.40, 1.05, 0.92, 10.37, 34.00, "69.5%", 180],
            ["KC-102", "Burr Hand Grinder Aluminum", 14.20, 0.51, 0.53, 15.24, 58.00, "73.7%", 120],
            ["KC-103", "Digital Espresso Scale", 6.15, 0.26, 0.28, 6.69, 29.00, "76.9%", 250],
            ["KC-104", "Double-Wall Glass Mug Set (2pk)", 3.80, 0.63, 0.23, 4.66, 24.00, "80.6%", 300],
        ],
        role="draft",
    )
    files["keegan_staff_sku_guide.pdf"] = write_pdf_file(
        "keegan_staff_sku_guide.pdf",
        "Staff SOP — Entering New SKUs & Updating Container Freight Rates",
        [
            "Step 1: Enter only the yellow input columns (A through E) when adding a new supplier SKU.",
            "Step 2: Select the HTS category from the dropdown in Column F.",
            "Step 3: Enter the total container invoice and total CBM in cells B2:B3 on the Summary tab.",
            "Note: Columns G through K calculate landed cost, net margin, and 45-day reorder triggers.",
        ],
        role="deliverable",
    )
    files["keegan_sku_margin_calculator_v2_locked.xlsx"] = write_xlsx_file(
        "keegan_sku_margin_calculator_v2_locked.xlsx",
        "Margin_Calculator_Locked",
        [
            ["SKU", "Item Name", "FOB Cost", "Freight/Unit", "Duty/Unit", "Landed Cost (Locked)", "Wholesale 2.2x", "Retail Price", "Net Margin %"],
            ["KC-101", "Stainless Pour-Over Kettle 1.2L", 8.40, 1.05, 0.92, 10.37, 22.81, 34.00, "69.5%"],
            ["KC-102", "Burr Hand Grinder Aluminum", 14.20, 0.51, 0.53, 15.24, 33.53, 58.00, "73.7%"],
            ["KC-103", "Digital Espresso Scale", 6.15, 0.26, 0.28, 6.69, 14.72, 29.00, "76.9%"],
            ["KC-104", "Double-Wall Glass Mug Set (2pk)", 3.80, 0.63, 0.23, 4.66, 10.25, 24.00, "80.6%"],
        ],
        role="deliverable",
    )

    # 4. Liza Iza
    files["liza_vendor_packet_draft.docx"] = write_docx_file(
        "liza_vendor_packet_draft.docx",
        "Vendor Onboarding Packet & Billing Terms (Rough Draft)",
        [
            "1. New vendor W-9 and COI requirements before first dispatch.",
            "2. Net-15 invoice submission cutoff is Friday 3:00 PM.",
            "3. Standard rate card table needs cleanup.",
        ],
        role="source",
    )
    files["liza_vendor_packet_clean.pdf"] = write_pdf_file(
        "liza_vendor_packet_clean.pdf",
        "Vendor Onboarding Packet & COI Checklist — Final",
        [
            "1. COMPLIANCE DOCUMENTS REQUIRED: Signed W-9, Certificate of Insurance ($1M General Liability), ACH form.",
            "2. BILLING SCHEDULE: Invoices received by Friday 3:00 PM EST clear via ACH on the 15th and 30th.",
            "3. DISPATCH COMMUNICATION: All change orders require written sign-off from the project coordinator.",
        ],
        role="deliverable",
    )
    files["liza_rate_card_final.xlsx"] = write_xlsx_file(
        "liza_rate_card_final.xlsx",
        "2026_Rate_Card",
        [
            ["Service Tier", "Turnaround", "Base Rate (USD)", "Additional Unit", "Weekend Surcharge"],
            ["Standard Commercial Crew", "48 Hours", 450.00, 85.00, 125.00],
            ["Priority Same-Day Crew", "Same Day", 650.00, 110.00, 150.00],
            ["Monthly Retainer Visit (4x)", "Scheduled", 1450.00, 75.00, 0.00],
        ],
        role="deliverable",
    )
    files["liza_15p_service_proposal_messy.docx"] = write_docx_file(
        "liza_15p_service_proposal_messy.docx",
        "Commercial Facility Maintenance Proposal — 15 Pages (Unformatted)",
        [
            "Section 1: Executive Summary & Scope of Work (pages 1-4).",
            "Section 2: Preventive Maintenance Schedule (pages 5-9) — tables currently wrap unevenly across page breaks.",
            "Section 3: Pricing Breakdown & SLA Response Times (pages 10-15).",
        ],
        role="source",
    )
    files["liza_15p_service_proposal_v1.docx"] = write_docx_file(
        "liza_15p_service_proposal_v1.docx",
        "Commercial Facility Maintenance Proposal — Edited & Formatted (v1)",
        [
            "Standardized all headings, fixed page breaks across the 5 preventive maintenance tables, and tightened scope language.",
            "Aligned pricing columns and SLA response tiers on pages 11-15.",
        ],
        role="draft",
    )
    files["liza_15p_service_proposal_final.pdf"] = write_pdf_file(
        "liza_15p_service_proposal_final.pdf",
        "Commercial Facility Maintenance Proposal — Final Print-Ready PDF (v2)",
        [
            "Updated footer contact phone number on all 15 pages per client review.",
            "Includes Executive Summary, Quarterly Maintenance Matrix, SLA Response Table, and Signature Block.",
        ],
        role="deliverable",
    )

    # 5. Drako Santa Ana
    files["drako_old_resume_2023.pdf"] = write_pdf_file(
        "drako_old_resume_2023.pdf",
        "Drako Santa Ana — Resume (Last Updated 2023)",
        [
            "Experience: Warehouse Lead, Sunbelt Distribution (2020 - 2023).",
            "Managed receiving dock, cycle counts, and 8 material handlers.",
            "[Missing 2024 - 2026 Shift Supervisor role]",
        ],
        role="source",
    )
    files["drako_2024_2026_warehouse_notes.docx"] = write_docx_file(
        "drako_2024_2026_warehouse_notes.docx",
        "Notes on Current Job (2023 - Present)",
        [
            "Promoted to Outbound Shift Supervisor in Nov 2023 at Westside Cold Storage.",
            "Running a crew of 19 people across 14 dock doors.",
            "Cut mis-picks from 2.4% down to 0.6% after we switched to RF barcode scanners.",
            "Have OSHA 30-Hour and Sit-Down/Reach Forklift Trainer certs.",
        ],
        role="source",
    )
    files["drako_resume_and_linkedin_v1.docx"] = write_docx_file(
        "drako_resume_and_linkedin_v1.docx",
        "Drako Santa Ana — Rewritten Resume & LinkedIn Profile (v1)",
        [
            "SUMMARY: Operations & Warehouse Shift Supervisor with 6+ years leading cold-storage and high-volume distribution teams.",
            "WESTSIDE COLD STORAGE (2023–Present): Supervise 19 associates across 14 outbound dock doors; reduced order mis-picks from 2.4% to 0.6%.",
            "LINKEDIN HEADLINE & ABOUT SECTION included on page 2.",
        ],
        role="draft",
    )
    files["drako_resume_and_linkedin_final.pdf"] = write_pdf_file(
        "drako_resume_and_linkedin_final.pdf",
        "Drako Santa Ana — Final Resume & LinkedIn Copy (v2 Final)",
        [
            "Added Certifications section at bottom: OSHA 30-Hour General Industry, Certified Forklift & Reach-Truck Instructor, WMS RF Administration.",
            "Formatted for ATS parsing and direct PDF upload.",
        ],
        role="deliverable",
    )

    # 6. Estella Williams
    files["estella_october_newsletter_draft.docx"] = write_docx_file(
        "estella_october_newsletter_draft.docx",
        "October Client Newsletter — 1,800 Words (Draft)",
        [
            "Drafted seasonal update for our bookkeeping and payroll clients covering Q4 year-end prep, 1099 contractor W-9 collection, and holiday payroll cutoff dates.",
        ],
        role="source",
    )
    files["estella_october_newsletter_refined.docx"] = write_docx_file(
        "estella_october_newsletter_refined.docx",
        "October Client Newsletter — Refined & Formatted (Final)",
        [
            "Tightened all 4 sections to 1,450 words with clear subheadings, scannable deadline callouts, and natural client-facing tone.",
        ],
        role="deliverable",
    )
    files["estella_rough_role_notes.docx"] = write_docx_file(
        "estella_rough_role_notes.docx",
        "Rough Notes — 4 Staff Roles Onboarding Checklists",
        [
            "Role 1: Front Desk Coordinator",
            "Role 2: Shift Lead",
            "Role 3: Inventory & Receiving Clerk",
            "Role 4: Client Account Associate",
        ],
        role="source",
    )
    files["estella_4role_onboarding_sops_v1.docx"] = write_docx_file(
        "estella_4role_onboarding_sops_v1.docx",
        "Four-Role Staff Onboarding SOPs & Daily Checklists (v1)",
        [
            "Includes Day 1-5 software access checklist, opening/closing procedures, and escalation matrix for all 4 roles.",
        ],
        role="draft",
    )
    files["estella_4role_onboarding_sops_final.pdf"] = write_pdf_file(
        "estella_4role_onboarding_sops_final.pdf",
        "Four-Role Staff Onboarding SOPs & Checklists — Final PDF (v2)",
        [
            "Moved morning POS & register opening checklist from Shift Lead (Role 2) to Front Desk Coordinator (Role 1) per Estella's review.",
            "Ready to print for employee binders.",
        ],
        role="deliverable",
    )

    # 7. Kaylee Cabreros
    files["kaylee_shopify_product_descriptions.xlsx"] = write_xlsx_file(
        "kaylee_shopify_product_descriptions.xlsx",
        "Shopify_Products",
        [
            ["Handle", "Product Title", "Current Bullet Points", "Materials", "Sizes"],
            ["linen-set-sand", "Two-Piece Washed Linen Set", "soft linen set great for summer", "100% European Flax Linen", "XS-XL"],
            ["ribbed-tank-oat", "Everyday Ribbed Tank", "stretchy modal tank top", "95% Modal 5% Spandex", "XS-XL"],
            ["canvas-tote-natural", "Heavyweight Market Tote", "thick canvas bag with inside pocket", "16oz Cotton Canvas", "One Size"],
        ],
        role="source",
    )
    files["kaylee_welcome_emails_draft.docx"] = write_docx_file(
        "kaylee_welcome_emails_draft.docx",
        "Klaviyo 3-Part Welcome Flow (Rough Draft)",
        [
            "Email 1: Welcome + 10% off code WELCOME10 (sent immediately)",
            "Email 2: How we source our fabrics + care guide (sent Day 2)",
            "Email 3: Customer favorites + reminder to use code (sent Day 5)",
        ],
        role="source",
    )

    # 8. Dennis Kiragu
    files["dennis_old_expense_sheet.xlsx"] = write_xlsx_file(
        "dennis_old_expense_sheet.xlsx",
        "2026_Expenses_Rough",
        [
            ["Date", "Vendor", "Category", "Amount (USD)", "Payment Method", "Notes"],
            ["2026-09-02", "AWS Cloud", "Hosting", 412.50, "Corp Visa", ""],
            ["2026-09-05", "Safaricom Fiber", "Utilities", 115.00, "M-Pesa", "Office internet"],
            ["2026-09-12", "Contractor Payroll", "Operations", 2400.00, "Wire", ""],
        ],
        role="source",
    )

    # 9. Alexa Quintero
    files["alexa_pitch_rough_bullets.docx"] = write_docx_file(
        "alexa_pitch_rough_bullets.docx",
        "10-Slide Client Pitch Deck — Bullet Notes",
        [
            "Slide 1: Title & value prop for commercial solar O&M",
            "Slide 2: Why panel output drops 14-18% without scheduled wash & thermal inspection",
            "Slide 3: Our inspection + preventative maintenance workflow",
            "Slide 4-10: Pricing tiers, competitor comparison, case study, and Q4 rollout schedule.",
        ],
        role="source",
    )
    files["alexa_competitor_rates.xlsx"] = write_xlsx_file(
        "alexa_competitor_rates.xlsx",
        "Competitor_Comparison",
        [
            ["Provider", "Per-MW Annual Fee", "Thermal Drone Scan", "SLA Response", "Inverter Preventative Check"],
            ["Our Package", "$2,850", "Included (2x/yr)", "24 Hours", "Included"],
            ["Competitor A", "$3,400", "$650 extra", "72 Hours", "Included"],
            ["Competitor B", "$2,950", "Not offered", "5 Business Days", "Extra fee"],
        ],
        role="source",
    )
    files["alexa_pitch_deck_structure_v1.pdf"] = write_pdf_file(
        "alexa_pitch_deck_structure_v1.pdf",
        "10-Slide Commercial Pitch Deck — v1 Draft",
        [
            "Slides 1-3: Problem, Yield Loss Data, and Inspection Methodology.",
            "Slide 4: Pricing & Competitor Comparison Matrix.",
            "Slide 5: 4.2 MW Warehouse Rooftop Case Study.",
            "Slides 6-10: SLA Guarantees, Reporting Portal, and Onboarding Timeline.",
        ],
        role="draft",
    )
    files["alexa_10slide_pitch_deck_final.pdf"] = write_pdf_file(
        "alexa_10slide_pitch_deck_final.pdf",
        "10-Slide Commercial Pitch Deck — Final (v2)",
        [
            "Swapped Slide 4 and Slide 5 so the 4.2 MW Rooftop Case Study precedes the Pricing & Competitor Matrix.",
            "Includes full speaker notes and print-ready table formatting.",
        ],
        role="deliverable",
    )

    # 10. Cami Kurtz
    files["cami_raw_call_transcripts_18p.docx"] = write_docx_file(
        "cami_raw_call_transcripts_18p.docx",
        "Zoom Auto-Transcripts — 3 Client Kickoff Calls (18 Pages)",
        [
            "[00:02:14] Speaker 1 (Cami): Okay let's lock the phase 1 deliverables before November...",
            "[00:08:42] Speaker 2 (Marcus): We need the Shopify ERP inventory sync live before Black Friday...",
            "[00:19:05] Speaker 3: Billing migration can wait until January 15...",
        ],
        role="source",
    )
    files["cami_call_action_sheet_v1.pdf"] = write_pdf_file(
        "cami_call_action_sheet_v1.pdf",
        "Client Call Synthesis & 4-Page Action Sheet (v1)",
        [
            "1. LOCKED PHASE 1 DECISIONS (NOVEMBER LAUNCH)",
            "2. DEFERRED TO PHASE 2 (JANUARY 15)",
            "3. OWNER & DEADLINE MATRIX (14 Action Items)",
        ],
        role="draft",
    )
    files["cami_call_action_sheet_final.pdf"] = write_pdf_file(
        "cami_call_action_sheet_final.pdf",
        "Client Call Synthesis & 4-Page Action Sheet — Final (v2)",
        [
            "Corrected owner name from 'Mark' to 'Marcus Vance' across all ERP sync action items.",
            "Organized by Immediate (48hr), Pre-Launch (Nov 1), and Post-Holiday (Jan 15) milestones.",
        ],
        role="deliverable",
    )

    # 11. Victor Mawira
    files["victor_service_page_1_draft.docx"] = write_docx_file(
        "victor_service_page_1_draft.docx",
        "Service Page 1 Draft — Managed Cloud & API Integration",
        [
            "Rough draft for our first service page. My partner is still finishing Page 2 (Data Automation) and will send it over once he's out of his meeting.",
        ],
        role="source",
    )

    # 12. Azael Orozco (New client from ValdaceAi CSV)
    files["orozco_roofing_rough_notes.docx"] = write_docx_file(
        "orozco_roofing_rough_notes.docx",
        "Orozco Exterior & Roofing — 4-Page Site & Estimate Sheet Notes",
        [
            "Pages needed: Home, Commercial Flat Roofs, Shingle & Tile Replacement, Storm Damage & Insurance Claims.",
            "Also need a clean 1-page customer estimate & warranty sheet we can hand homeowners on-site.",
            "[Note: need to add Maricopa County zip codes and workmanship warranty length]",
        ],
        role="source",
    )
    files["orozco_site_copy_and_estimate_v1.docx"] = write_docx_file(
        "orozco_site_copy_and_estimate_v1.docx",
        "Orozco Exterior & Roofing — 4-Page Website Copy & Estimate Sheet (v1)",
        [
            "Includes full copy for Home, Commercial TPO/Elastomeric, Residential Tile/Shingle, and Hail/Monsoon Claims.",
            "Includes 10-year workmanship warranty terms on the customer estimate sheet.",
        ],
        role="draft",
    )
    files["orozco_site_copy_and_estimate_final.docx"] = write_docx_file(
        "orozco_site_copy_and_estimate_final.docx",
        "Orozco Exterior & Roofing — 4-Page Website Copy & Estimate Sheet (v2 Final)",
        [
            "Updated workmanship warranty from 10-year to 12-year across the Services page and Customer Estimate Sheet.",
            "Added ROC license placeholder and Phoenix/Scottsdale/Mesa service corridor callouts.",
        ],
        role="deliverable",
    )
    files["orozco_estimate_sheet.xlsx"] = write_xlsx_file(
        "orozco_estimate_sheet.xlsx",
        "Customer_Estimate",
        [
            ["Line Item", "Roof Area (Sq)", "Material Spec", "Rate / Sq (USD)", "Line Total (USD)"],
            ["Tear-off & Disposal", 32, "Existing 3-tab shingle haul-off", 95.00, 3040.00],
            ["Underlayment", 32, "Synthetic high-temp peel & stick", 65.00, 2080.00],
            ["Architectural Shingle Install", 32, "Owens Corning Duration Cool", 245.00, 7840.00],
            ["Flashing, Ridge Vent & 12-Yr Warranty", 1, "Complete perimeter & valley metal", 890.00, 890.00],
        ],
        role="deliverable",
    )

    # 13. Jack Johnson (New client from ValdaceAi CSV)
    files["johnson_hubspot_export.csv"] = write_csv_file(
        "johnson_hubspot_export.csv",
        [
            ["Deal ID", "Company", "Stage", "Territory", "MRR (USD)", "Days in Stage"],
            ["DL-401", "Apex Cold Logistics", "Technical Scoping", "Midwest", 3200, 14],
            ["DL-402", "Vanguard Parts Co", "Proposal Sent", "Southeast", 4800, 9],
            ["DL-403", "Harbor Marine Supply", "Discovery", "West", 2500, 21],
        ],
        role="source",
    )
    files["johnson_crm_pipeline_spec.pdf"] = write_pdf_file(
        "johnson_crm_pipeline_spec.pdf",
        "HubSpot Lead-Routing & Deal Stage Automation Spec (April Deliverable)",
        [
            "1. Territory round-robin routing rules by state and fleet size.",
            "2. Automated SLA task triggers when a deal sits in Discovery > 7 days.",
            "3. Weighted MRR forecast formulas by stage probability.",
        ],
        role="deliverable",
    )
    files["johnson_b2b_site_and_deck_brief.docx"] = write_docx_file(
        "johnson_b2b_site_and_deck_brief.docx",
        "Q4 B2B Website Overhaul & Outbound Sales Deck Brief",
        [
            "Scope: 5 core website pages (Home, Platform, Integrations, Security, Pricing) + 12-slide outbound enterprise deck.",
            "Need sharper positioning for mid-market distribution and 3PL buyers.",
        ],
        role="source",
    )
    files["johnson_b2b_deck_and_copy_v1.pdf"] = write_pdf_file(
        "johnson_b2b_deck_and_copy_v1.pdf",
        "5-Page B2B Website Copy & 12-Slide Enterprise Deck (v1 Draft)",
        [
            "Full page copy and slide deck structure for 3PL and wholesale distribution buyers.",
            "Slide 4 features ROI payback comparison table.",
        ],
        role="draft",
    )
    files["johnson_b2b_site_and_deck_final.docx"] = write_docx_file(
        "johnson_b2b_site_and_deck_final.docx",
        "5-Page B2B Website Copy & 12-Slide Enterprise Deck — Final (v2)",
        [
            "Updated Slide 4 ROI table with Q3 Midwest 3PL case study numbers (38% faster dock turn time).",
            "Includes final website copy deck and slide-by-slide speaker script.",
        ],
        role="deliverable",
    )

    # 14. Luca Carollo (New client from ValdaceAi CSV)
    files["luca_q3_raw_bank_export.csv"] = write_csv_file(
        "luca_q3_raw_bank_export.csv",
        [
            ["Date", "Unit", "Payee / Memo", "Category", "Amount (USD)"],
            ["2026-07-03", "Unit 4B - Waikiki", "Oahu Plumbing & Drain", "Repairs", -485.00],
            ["2026-07-05", "Unit 4B - Waikiki", "Tenant ACH Rent", "Rental Income", 3400.00],
            ["08/14/2026", "Unit 12A - Ala Moana", "[MISSING VENDOR]", "Maintenance", -620.00],
        ],
        role="source",
    )
    files["luca_august_vendor_receipts.pdf"] = write_pdf_file(
        "luca_august_vendor_receipts.pdf",
        "August Maintenance Invoices — Ala Moana & Waikiki Units",
        [
            "Aug 14, 2026 — Pacific Split-AC Service LLC — $620.00 (Unit 12A condenser coil & refrigerant recharge)",
            "Aug 22, 2026 — Kakaako Lock & Hardware — $185.00 (Unit 4B smart deadbolt replacement)",
        ],
        role="source",
    )
    files["luca_q3_property_ledger_reconciled.xlsx"] = write_xlsx_file(
        "luca_q3_property_ledger_reconciled.xlsx",
        "Q3_Reconciled_Ledger",
        [
            ["Month", "Unit", "Gross Rent (USD)", "Operating Expenses (USD)", "HOA & Taxes (USD)", "Net Operating Income (USD)"],
            ["July 2026", "Unit 4B - Waikiki", 3400.00, 485.00, 690.00, 2225.00],
            ["August 2026", "Unit 4B - Waikiki", 3400.00, 185.00, 690.00, 2525.00],
            ["August 2026", "Unit 12A - Ala Moana", 4100.00, 620.00, 810.00, 2670.00],
            ["September 2026", "Combined Portfolio", 7500.00, 310.00, 1500.00, 5690.00],
        ],
        role="deliverable",
    )
    files["luca_partner_distribution_model_v1.xlsx"] = write_xlsx_file(
        "luca_partner_distribution_model_v1.xlsx",
        "Partner_Waterfall_v1",
        [
            ["Quarter", "Portfolio NOI (USD)", "Mgmt Fee (8.0%)", "Reserve Holdback", "Distributable Cash", "LP 60% Share", "GP 40% Share"],
            ["Q4 2026 Proj", 22800.00, 1824.00, 1500.00, 19476.00, 11685.60, 7790.40],
            ["Q1 2027 Proj", 23400.00, 1872.00, 1500.00, 20028.00, 12016.80, 8011.20],
        ],
        role="draft",
    )
    files["luca_partner_distribution_model_final.xlsx"] = write_xlsx_file(
        "luca_partner_distribution_model_final.xlsx",
        "Partner_Waterfall_Final",
        [
            ["Quarter", "Portfolio NOI (USD)", "Mgmt Fee (7.5%)", "Reserve Holdback", "Distributable Cash", "LP 60% Share", "GP 40% Share"],
            ["Q4 2026 Proj", 22800.00, 1710.00, 1500.00, 19590.00, 11754.00, 7836.00],
            ["Q1 2027 Proj", 23400.00, 1755.00, 1500.00, 20145.00, 12087.00, 8058.00],
        ],
        role="deliverable",
    )

    # 15. Lina Rickert (New client from ValdaceAi CSV)
    files["lina_summer_campaign_emails_rough.docx"] = write_docx_file(
        "lina_summer_campaign_emails_rough.docx",
        "July Customer Win-Back & VIP Drop Emails (Rough Notes)",
        [
            "Email 1: Early access to the late-summer collection",
            "Email 2: Behind the scenes studio lookbook",
            "Email 3: Last call 48-hour promo code (SUMMER15)",
        ],
        role="source",
    )
    files["lina_summer_campaign_emails_v1.docx"] = write_docx_file(
        "lina_summer_campaign_emails_v1.docx",
        "3-Part Late Summer Retention Email Sequence (v1)",
        [
            "Includes subject lines, preview text, body copy, and CTA button text for all 3 Klaviyo campaigns.",
        ],
        role="draft",
    )
    files["lina_summer_campaign_emails_final.docx"] = write_docx_file(
        "lina_summer_campaign_emails_final.docx",
        "3-Part Late Summer Retention Email Sequence — Final (v2)",
        [
            "Updated Email #3 promo code from SUMMER15 to VIP15 and added midnight Sunday countdown subheader.",
        ],
        role="deliverable",
    )

    # 16. Patrick Hyland (New client from ValdaceAi CSV)
    files["patrick_newfoundland_dispatch_raw.xlsx"] = write_xlsx_file(
        "patrick_newfoundland_dispatch_raw.xlsx",
        "Dispatch_Log_Raw",
        [
            ["Route Code", "Origin", "Destination", "Distance", "Base Linehaul (CAD)", "Diesel Surcharge"],
            ["NL-01", "St. John's", "Gander", 334, 780.00, "manual"],
            ["NL-02", "St. John's", "Corner Brook", 689, 1490.00, "manual"],
            ["NL-03", "Mount Pearl", "Clarenville", 188, 460.00, "manual"],
        ],
        role="source",
    )
    files["patrick_dispatch_and_fuel_tracker_v1.xlsx"] = write_xlsx_file(
        "patrick_dispatch_and_fuel_tracker_v1.xlsx",
        "Dispatch_Fuel_Tracker_v1",
        [
            ["Route Code", "Origin", "Destination", "Distance (Mi)", "Base Linehaul", "Fuel Index Surcharge", "Total Carrier Pay"],
            ["NL-01", "St. John's", "Gander", 208, 780.00, 112.40, 892.40],
            ["NL-02", "St. John's", "Corner Brook", 428, 1490.00, 231.10, 1721.10],
        ],
        role="draft",
    )
    files["patrick_dispatch_and_fuel_tracker_final.xlsx"] = write_xlsx_file(
        "patrick_dispatch_and_fuel_tracker_final.xlsx",
        "Dispatch_Fuel_Tracker_Final_KM",
        [
            ["Route Code", "Origin", "Destination", "Distance (KM)", "Base Linehaul", "Fuel Surcharge (Per KM)", "Total Carrier Pay"],
            ["NL-01", "St. John's", "Gander", 334, 780.00, 116.90, 896.90],
            ["NL-02", "St. John's", "Corner Brook", 689, 1490.00, 241.15, 1731.15],
            ["NL-03", "Mount Pearl", "Clarenville", 188, 460.00, 65.80, 525.80],
        ],
        role="deliverable",
    )

    # 17. Carter Lemburg (New client from ValdaceAi CSV)
    files["carter_storefront_launch_notes.docx"] = write_docx_file(
        "carter_storefront_launch_notes.docx",
        "Lemburg Supply — Storefront Copy & Pre-Launch QA Notes",
        [
            "Collection pages, shipping & returns FAQ, and pre-launch checkout QA checklist.",
        ],
        role="source",
    )
    files["carter_website_launch_checklist_final.pdf"] = write_pdf_file(
        "carter_website_launch_checklist_final.pdf",
        "Lemburg Supply — Storefront Copy & Launch QA Checklist (Final)",
        [
            "1. Collection page copy for Workwear, Footwear, and Field Gear.",
            "2. 28-point pre-launch Shopify checkout, tax, and shipping zone verification sheet.",
        ],
        role="deliverable",
    )

    # 18. Luca Carollo
    files["luca_charter_rates_raw.xlsx"] = write_xlsx_file(
        "luca_charter_rates_raw.xlsx",
        "Charter Rates",
        [
            ["Package", "Duration", "Base Rate ($)", "Fuel Surcharge ($)", "Max Guests"],
            ["Sunset Catamaran", "2.5 hrs", 650, 75, 12],
            ["Half-Day Reef Snorkel", "4 hrs", 1100, 120, 16],
            ["Full-Day Private Oahu Charter", "8 hrs", 2150, 240, 16],
        ],
        role="source",
    )
    files["luca_oahu_charter_booking_deck_final.pdf"] = write_pdf_file(
        "luca_oahu_charter_booking_deck_final.pdf",
        "Carollo Marine Charters — 2026 Private Charter Rate Deck & Booking Terms",
        [
            "1. Sunset, Half-Day Reef, and Full-Day Private Charter packages with transparent fuel and captain fees.",
            "2. 48-hour weather cancellation and harbor check-in instructions for Kewalo Basin slips.",
        ],
        role="deliverable",
    )
    files["luca_harbor_seasonal_manifest_v2.xlsx"] = write_xlsx_file(
        "luca_harbor_seasonal_manifest_v2.xlsx",
        "Q3-Q4 Charter Model",
        [
            ["Month", "Projected Trips", "Gross Charter ($)", "Dock & Fuel ($)", "Crew ($)", "Net Operating ($)"],
            ["September", 34, 48200, 9400, 11900, 26900],
            ["October", 38, 54600, 10200, 13300, 31100],
            ["November", 42, 61400, 11500, 14700, 35200],
        ],
        role="deliverable",
    )

    # 19. Issa Cuevas (Pediatric Speech Clinic Intake Pack)
    files["cuevas_intake_and_consent_draft_messy.docx"] = write_docx_file(
        "cuevas_intake_and_consent_draft_messy.docx",
        "Cuevas Speech & Language Therapy LLC — Rough Intake & Policy Notes",
        [
            "Practice Overview: Private pediatric speech, language, and feeding therapy clinic located in Austin, TX.",
            "Draft Policy Notes: Need a strict 24-hour cancellation rule because parents cancel 30 minutes before appointment and leave therapists with dead hours.",
            "HIPAA Consent: Need updated disclosures for teletherapy video recording, mirror observation by student clinicians, and coordination with school district ARD committees.",
            "Insurance & Billing: We are private pay but provide monthly superbills. Parents need to understand they are 100% financially responsible if out-of-network insurance denies the claim.",
        ],
        role="source",
    )
    files["cuevas_pediatric_intake_and_consent_v1.docx"] = write_docx_file(
        "cuevas_pediatric_intake_and_consent_v1.docx",
        "Cuevas Speech & Language Therapy — Pediatric Clinical Intake Agreement (v1 Draft)",
        [
            "1. CLINICAL SERVICES & PEDIATRIC ASSESSMENT",
            "Cuevas Speech & Language Therapy LLC provides comprehensive clinical evaluations, individualized therapy plans,",
            "and feeding therapy consultations for pediatric clients under 18 years of age.",
            "2. GUARANTOR FINANCIAL RESPONSIBILITY & CANCELLATION",
            "Payment is due at time of service. Late cancellations incur a $50 administrative charge without 24h notice.",
            "3. OBSERVATION, RECORDING & HIPAA DISCLOSURES",
            "Parent authorizes one-way mirror clinical observation and encrypted clinical video recording for treatment plan documentation.",
        ],
        role="draft",
    )
    files["cuevas_pediatric_intake_and_consent_final.docx"] = write_docx_file(
        "cuevas_pediatric_intake_and_consent_final.docx",
        "Cuevas Speech & Language Therapy — Master Clinical Service Agreement & Consent (v2 Final)",
        [
            "1. MASTER CLINICAL SERVICE AGREEMENT",
            "Legally binding clinical agreement between Cuevas Speech & Language Therapy LLC and Parent/Legal Guardian (Guarantor).",
            "Distinguishes pediatric patient receiving clinical therapy from parent guarantor responsible for financial undertakings.",
            "2. RESERVED CLINICAL HOUR & CANCELLATION POLICY",
            "Unscheduled missed sessions without 24-hour advance written notice are subject to the reserved clinical hour fee of $75.00.",
            "Designation satisfies commercial healthcare insurance billing compliance for unrendered scheduled units.",
            "3. SUPERBILL & OUT-OF-NETWORK REIMBURSEMENT",
            "Superbills with standardized ICD-10 diagnostic codes and CPT therapy codes (92507, 92523) are generated on the 1st of each calendar month.",
            "4. CLINICAL OUTCOME ESTIMATES",
            "Progress re-evaluations and clinical prognosis represent professional estimates and not guaranteed medical outcomes.",
        ],
        role="deliverable",
    )
    files["cuevas_parent_communication_templates.docx"] = write_docx_file(
        "cuevas_parent_communication_templates.docx",
        "Cuevas Speech Clinic — Parent Communication & Intake Policy Scripts",
        [
            "SCRIPT 1: New Patient Welcome & Intake Pack Onboarding Email",
            "Welcome to Cuevas Speech & Language! Please review and electronically execute our Master Clinical Service Agreement...",
            "SCRIPT 2: Unscheduled Missed Session & Reserved Clinical Hour Policy Notice",
            "Dear [Parent_Name], your therapist was reserved for [Child_Name]'s session today. As outlined in our agreement, a $75 reserved hour fee applies...",
            "SCRIPT 3: Monthly Superbill Delivery & Out-of-Network Submission Instructions",
            "Here is your statement for the preceding month containing all CPT encounter codes for out-of-network insurer claim filing...",
        ],
        role="deliverable",
    )
    files["cuevas_speech_clinic_service_agreement_final.pdf"] = write_pdf_file(
        "cuevas_speech_clinic_service_agreement_final.pdf",
        "Cuevas Speech & Language Therapy — Master Clinical Agreement & HIPAA Consent (Final)",
        [
            "1. Pediatric Clinical Intake Agreement & Financial Guarantor Undertaking (Austin, TX).",
            "2. Reserved Clinical Hour Fee ($75.00) and strict 24-hour notice cancellation policy.",
            "3. Encrypted HIPAA video recording consent and ARD school coordination release authorizations.",
            "4. Monthly superbill distribution schedule (1st of month) and ICD-10 / CPT compliance disclosures.",
            "5. Formal signature execution blocks for Parent/Legal Guardian and Clinical Practice Director.",
        ],
        role="deliverable",
    )

    # 20. Estella Williams (Q4 Executive Board Deck & Briefing Memo)
    files["estella_q4_board_deck_rough_bullets.docx"] = write_docx_file(
        "estella_q4_board_deck_rough_bullets.docx",
        "Williams Agency Group — Q4 Board Meeting Rough Notes & Key Figures",
        [
            "Meeting Date: Late October 2026 Advisory Board Meeting.",
            "Q3 Financials: Gross client billing reached $1.84M (+18% YoY). Contracted ARR sits at $2.2M.",
            "CAC & Retention: Customer acquisition cost ticked up 14% due to paid search competition, but 60-day cohort retention improved from 76% to 89%.",
            "Liquidity Runway: Current cash reserves provide runway through Q2 2027 under conservative $1.4M burn rate, or Q4 2027 under baseline $1.1M burn.",
            "2027 Hiring: Need board sign-off to recruit VP of Enterprise Sales and 2 Senior Account Directors in Q1.",
        ],
        role="source",
    )
    files["estella_q4_executive_investor_deck_v1.docx"] = write_docx_file(
        "estella_q4_executive_investor_deck_v1.docx",
        "Williams Agency Group — 16-Slide Executive Investor Presentation (v1 Draft)",
        [
            "SLIDE 1: Title & Executive Overview — Q4 2026 Board Review & Capital Allocation.",
            "SLIDE 2-5: Q3 Performance Summary — GAAP Revenue vs Contracted ARR Breakdown.",
            "SLIDE 6: Sales Efficiency — Blended Customer Acquisition Cost vs 60-Day Cohort Retention.",
            "SLIDE 7-10: 2027 Expansion Roadmap — Headcount Growth & Regional Account Delivery.",
            "SLIDE 11-14: Financial Modeling — Dual Scenario Liquidity Runway (Conservative vs Baseline).",
            "SLIDE 15-16: Governance & Board Action Items — Resolution to Authorize 2027 Key Hires.",
        ],
        role="draft",
    )
    files["estella_q4_board_briefing_memo_final.docx"] = write_docx_file(
        "estella_q4_board_briefing_memo_final.docx",
        "Williams Agency Group — Board of Directors Briefing Memorandum (Confidential)",
        [
            "MEMORANDUM TO: Board of Directors & Advisory Committee",
            "FROM: Estella Williams, Chief Executive Officer",
            "DATE: October 21, 2026",
            "SUBJECT: Q3 Operating Results, Sales Unit Economics, and Liquidity Runway",
            "",
            "1. EXECUTIVE SUMMARY & REVENUE REPORTING",
            "Q3 consolidated revenue closed at $1,842,000, representing an 18.2% expansion against Q3 2025.",
            "Contracted Annual Recurring Revenue (ARR) across agency retainers reached $2,210,000.",
            "",
            "2. SALES EFFICIENCY & COHORT EXPANSION",
            "While blended CAC rose 14.1% ($4,120 per client), 60-day net cohort retention expanded to 89.4%.",
            "Lifetime value to CAC ratio improved to 4.8x on 12-month agency contracts.",
            "",
            "3. LIQUIDITY RUNWAY & CAPITAL PRESERVATION",
            "Under a conservative stress-tested burn scenario ($1.4M quarterly spend), cash runway extends through Q2 2027.",
            "Under baseline operating cash flow ($1.1M quarterly spend), company maintains funding through Q4 2027 without bridge debt.",
        ],
        role="deliverable",
    )
    files["estella_q4_investor_deck_slide_copy_final.pdf"] = write_pdf_file(
        "estella_q4_investor_deck_slide_copy_final.pdf",
        "Williams Agency Group — 16-Slide Executive Investor Update Deck (Final)",
        [
            "1. 16-Slide Executive Presentation Deck for Q4 2026 Advisory Board & Institutional Investors.",
            "2. Comparative GAAP Revenue ($1.84M) and Contracted ARR ($2.21M) financial schedules.",
            "3. Side-by-side CAC efficiency vs 60-day cohort retention (89.4%) callout analytics.",
            "4. Dual liquidity runway modeling through Q2/Q4 2027 and Q1 2027 executive recruitment roadmap.",
            "5. Formal board approval resolutions for 2027 operational budget and incentive equity pool.",
        ],
        role="deliverable",
    )

    # 21. Additional Deliverables for Prior Completed Service Requests
    files["luca_spring_bookkeeping_ledger_final.xlsx"] = write_xlsx_file(
        "luca_spring_bookkeeping_ledger_final.xlsx",
        "Spring Bookkeeping 2026",
        [
            ["Month", "Rental Units", "Gross Collections ($)", "Maintenance ($)", "Vendor Fees ($)", "Net NOI ($)"],
            ["March 2026", 14, 42800, 4120, 2850, 35830],
            ["April 2026", 14, 43500, 3890, 2850, 36760],
            ["May 2026", 15, 46200, 4450, 3100, 38650],
        ],
        role="deliverable",
    )
    files["patrick_spring_freight_rates_final.xlsx"] = write_xlsx_file(
        "patrick_spring_freight_rates_final.xlsx",
        "Regional Rates 2026",
        [
            ["Lane / Corridor", "Mileage", "Base Linehaul ($)", "Spring Fuel Adj ($)", "Total Flat Quote ($)"],
            ["St. John's to Corner Brook", 685, 2150, 280, 2430],
            ["Corner Brook to Port aux Basques", 220, 850, 110, 960],
            ["Halifax to St. John's Ferry Drop", 1120, 3750, 490, 4240],
        ],
        role="deliverable",
    )
    files["lina_spring_launch_copy_final.docx"] = write_docx_file(
        "lina_spring_launch_copy_final.docx",
        "Lina Rickert Apparel — Spring Product Launch Copy & Storefront FAQ",
        [
            "1. SPRING COLLECTION PRODUCT DESCRIPTIONS: Editorial product storytelling for 12 apparel SKUs.",
            "2. SIZING & FIT GUIDE: Clear fit descriptions, fabric breathability ratings, and model measurement cards.",
            "3. STOREFRONT CUSTOMER FAQ: Delivery windows, exchange policy, and organic linen garment care guidelines.",
        ],
        role="deliverable",
    )

    return files



CLIENT_PROFILES = {
    "cruzjose6221@gmail.com": {
        "username": "jose_cruz",
        "first_name": "Jose",
        "last_name": "Cruz",
        "channel": "Snapchat",
        "subject": "Company bio and cold outreach email templates",
        "status": "closed",
        "requests": [
            {
                "key": "jc_rewrite",
                "reference": "INF-261018-JC",
                "service_family": "text-intelligence",
                "service_code": "text-rewrite",
                "title": "Company profile and client outreach email rewrite",
                "objective": "Rewrite a regional freight company bio and three cold outreach email templates.",
                "scope": "USD 25.00 total split into a USD 1.00 card test invoice and a USD 24.00 balance invoice.",
                "deliverable": "Rewritten company bio and outreach email sequence (.docx & .pdf).",
                "status": "delivered",
                "estimate_low": Decimal("25.00"),
                "estimate_high": Decimal("25.00"),
                "created_at": dt_utc(2026, 10, 17, 21, 15, 0),
                "deliverables": [
                    {
                        "title": "Cruz Metro Freight — Final Bio & Outreach Sequence (v2)",
                        "kind": "Copy rewrite",
                        "status": "delivered",
                        "version": 2,
                        "notes": "Settled Oct 18, 2026 across INV-261018-JC01 ($1.00) and INV-261018-JC02 ($24.00); v2 subject lines delivered Oct 19.",
                    }
                ],
            }
        ],
        "invoices": [
            {
                "key": "inv_jc_1",
                "number": "INV-261018-JC01",
                "request_key": "jc_rewrite",
                "amount_due": Decimal("1.00"),
                "amount_paid": Decimal("1.00"),
                "status": "paid",
                "description": "Rewrite & adapt — Initial card test & deposit ($1 of $25 total)",
                "created_at": dt_utc(2026, 10, 18, 19, 40, 0),
                "due_at": dt_utc(2026, 10, 19, 19, 40, 0),
                "tx_refs": ["T676780654455055"],
            },
            {
                "key": "inv_jc_24",
                "number": "INV-261018-JC02",
                "request_key": "jc_rewrite",
                "amount_due": Decimal("24.00"),
                "amount_paid": Decimal("24.00"),
                "status": "paid",
                "description": "Rewrite & adapt — Remaining balance for company bio & outreach emails ($24 of $25 total)",
                "created_at": dt_utc(2026, 10, 18, 21, 32, 0),
                "due_at": dt_utc(2026, 10, 19, 21, 32, 0),
                "tx_refs": ["T850856961040908"],
            },
        ],
        "messages": [
            (
                "client",
                dt_utc(2026, 10, 17, 21, 12, 10),
                "hey, got your link from snap. how much would u charge to rewrite a short company bio and 3 cold emails we send to warehouse managers?",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 17, 21, 24, 45),
                "Hey Jose, that's $25 total for the bio and all three emails. Send over what you have whenever you're ready.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 18, 19, 28, 0),
                "sorry for the late reply, was out on a delivery route in Fort Worth all morning. here's the word doc with what I typed so far. where do I pay? also I'm using my Cash App Visa on Apple Pay and sometimes it acts weird on new sites—can we do $1 first just to make sure it goes through, then the $24?",
                ["cruz_old_bio_draft.docx"],
            ),
            (
                "admin",
                dt_utc(2026, 10, 18, 19, 40, 10),
                "No problem at all. I just put INV-261018-JC01 ($1.00) on your account so you can test the card. You can also pay directly using this link: https://paystack.shop/pay/4q5iounn6s. Also I opened your Word file—Email #3 cuts off right at 'Here is our standard per-mile and flat metro rate—'. What did you want after that?",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 18, 19, 45, 30),
                "oh shoot my bad lol I didn't save the last paragraph before uploading. just mention that we give 2 hours of free dock time before detention kicks in and we don't charge fuel surcharges inside 40 miles. btw the $1 went through fine on Apple Pay.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 18, 19, 49, 15),
                "Got the $1 payment and added those dock terms to Email #3. Give me about an hour and a half to finish the draft.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 18, 21, 32, 15),
                "Here's the PDF preview of the bio and all three emails, and I posted INV-261018-JC02 for the remaining $24.00.",
                ["cruz_bio_and_emails_v1_preview.pdf"],
            ),
            (
                "client",
                dt_utc(2026, 10, 18, 21, 35, 10),
                "where do I pay?",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 18, 21, 36, 0),
                "Here is the payment link to settle the balance: https://paystack.shop/pay/4q5iounn6s",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 18, 21, 41, 20),
                "just paid the $24 on apple pay. looks super clean, can I get the editable word version too?",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 19, 13, 18, 40),
                "hey quick thing—when I pasted email 2 into Gmail on my phone the subject line looked a little long. also could you add 'Rates effective November 1, 2026' to Email 3 so dispatchers know the new quote starts next month?",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 19, 13, 42, 10),
                "Shortened all three subject lines to under 40 characters for mobile and added the November 1, 2026 effective date to Email 3. Here is the final Word file.",
                ["cruz_bio_and_outreach_final.docx"],
            ),
            (
                "client",
                dt_utc(2026, 10, 19, 14, 5, 22),
                "perfect, appreciate it man.",
                [],
            ),
        ],
    },
    "audreymbrown2007@gmail.com": {
        "username": "audrey_brown",
        "first_name": "Audrey",
        "last_name": "Brown",
        "channel": "Snapchat",
        "subject": "Homepage copy audit ($90) & 3-page website copy package ($270)",
        "status": "closed",
        "requests": [
            {
                "key": "ab_audit",
                "reference": "INF-260930-AB",
                "service_family": "communication",
                "service_code": "communication-audit",
                "title": "Homepage and booking-flow communication audit",
                "objective": "Review current homepage messaging, layout friction, and booking funnel copy before rewriting the full site.",
                "scope": "Page-by-page messaging review and wireframe copy recommendations ($90.00).",
                "deliverable": "Homepage audit and messaging wireframe.",
                "status": "delivered",
                "estimate_low": Decimal("90.00"),
                "estimate_high": Decimal("90.00"),
                "created_at": dt_utc(2026, 9, 30, 19, 30, 0),
                "deliverables": [
                    {
                        "title": "Homepage & Booking-Flow Copy Audit",
                        "kind": "Communication audit",
                        "status": "delivered",
                        "version": 1,
                        "notes": "Settled Sep 30, 2026 (T414467630167869) and delivered Oct 1, 2026.",
                    }
                ],
            },
            {
                "key": "ab_copy",
                "reference": "INF-261015-AB",
                "service_family": "communication",
                "service_code": "communication-copy",
                "title": "Full three-page website copy package (Home, Services, Booking)",
                "objective": "Write final conversion copy for the three main website pages based on the approved audit.",
                "scope": "Three core website pages at USD 90.00 per page (USD 270.00 total).",
                "deliverable": "Final website copy deck for Home, Services, and Booking pages.",
                "status": "delivered",
                "estimate_low": Decimal("270.00"),
                "estimate_high": Decimal("270.00"),
                "created_at": dt_utc(2026, 10, 14, 18, 20, 0),
                "deliverables": [
                    {
                        "title": "Three-Page Website Copy Deck — Final (v2)",
                        "kind": "Website copy",
                        "status": "delivered",
                        "version": 2,
                        "notes": "Settled Oct 17, 2026 via Mastercard Apple Pay (T493259790266047) and delivered Oct 17, 2026.",
                    }
                ],
            },
        ],
        "invoices": [
            {
                "key": "inv_ab_90",
                "number": "INV-260930-AB01",
                "request_key": "ab_audit",
                "amount_due": Decimal("90.00"),
                "amount_paid": Decimal("90.00"),
                "status": "paid",
                "description": "Communication audit — Homepage & booking-flow copy audit",
                "created_at": dt_utc(2026, 9, 30, 19, 46, 0),
                "due_at": dt_utc(2026, 10, 2, 19, 46, 0),
                "tx_refs": ["T414467630167869"],
            },
            {
                "key": "inv_ab_270",
                "number": "INV-261015-AB02",
                "request_key": "ab_copy",
                "amount_due": Decimal("270.00"),
                "amount_paid": Decimal("270.00"),
                "status": "paid",
                "description": "Website / product copy — Full 3-page website copy package (3 pages @ $90)",
                "created_at": dt_utc(2026, 10, 15, 7, 14, 0),
                "due_at": dt_utc(2026, 10, 18, 7, 14, 0),
                "tx_refs": [
                    "T402797112790778",
                    "T686580774909713",
                    "T437373824312474",
                    "T150064978438039",
                    "T493259790266047",
                ],
            },
        ],
        "messages": [
            (
                "client",
                dt_utc(2026, 9, 30, 19, 28, 10),
                "Hey! we talked on snap about redoing my studio's website copy. I exported a PDF of our current homepage and booking form—can we do the homepage & booking audit first before rewriting the whole site?",
                ["audrey_current_site_screenshots.pdf"],
            ),
            (
                "admin",
                dt_utc(2026, 9, 30, 19, 46, 10),
                "Hi Audrey, got the PDF. The homepage and booking-flow audit is $90 (just posted INV-260930-AB01). When you're ready to write the full pages afterward, they're $90 per page.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 9, 30, 19, 59, 15),
                "Just paid the $90 with Apple Pay.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 1, 16, 10, 0),
                "Here is the completed Homepage & Booking-Flow Audit. The biggest bottleneck right now is your 14-field intake form before people can even see package rates—check page 2 for the 5-field layout we recommend.",
                ["audrey_homepage_booking_audit.pdf"],
            ),
            (
                "client",
                dt_utc(2026, 10, 2, 11, 14, 30),
                "Sorry just had a chance to read this between clients! You're totally right about the intake form, people drop off there constantly. Let me show this to my web designer this week and we'll get the wireframes set.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 14, 22, 40, 18),
                "Hey! sorry it took almost two weeks, my designer was backed up. Here are the wireframe notes for the 3 pages (Home, Services, and Booking). Ready to do the $270 package whenever you can send the invoice.",
                ["audrey_wireframe_notes.docx"],
            ),
            (
                "admin",
                dt_utc(2026, 10, 15, 7, 14, 20),
                "Morning Audrey, got the wireframe doc and posted INV-261015-AB02 for $270.00.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 15, 8, 42, 12),
                "ugh my card keeps declining on checkout. tried twice on apple pay and once typing it in.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 15, 8, 49, 0),
                "We actually noticed an issue with our normal payment route this morning—our processor is undergoing a scheduled gateway maintenance sync which is causing card checkout drops. You can use our direct verified link instead to clear the invoice: https://paystack.shop/pay/ppiajw3f1-",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 15, 9, 12, 15),
                "Wait, why a separate link? Is that safe? I usually only put card details directly through the main site portal, I get a little nervous paying through external links.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 15, 9, 18, 40),
                "Totally get the caution, you're 100% right to double-check! That's our direct hosted merchant store on Paystack (our payment processor), so your transaction is fully encrypted with 256-bit SSL, has standard buyer protection, and supports Apple Pay without exposing your card numbers. It routes straight to our verified business settlement account and logs right onto your invoice here.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 15, 9, 25, 10),
                "Oh okay, that makes total sense then! Thanks for explaining, was just being careful. Going to use that link right now.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 16, 15, 18, 0),
                "Sounds great! Here is v1 of the 3-page website copy deck so you and your designer can start reviewing it in the meantime.",
                ["audrey_3page_website_copy_v1.docx"],
            ),
            (
                "client",
                dt_utc(2026, 10, 17, 1, 8, 30),
                "okay the payment went through on that link with my mastercard just now, super easy. we read through v1—could we rename the 3 tiers on the Services page to 'Essential', 'Studio Session', and 'Full Day Campaign', and take out the note about weekend calls on the Booking page?",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 17, 14, 22, 10),
                "Payment confirmed, thank you! I updated the three package names on the Services page and switched the Booking page hours to Mon–Fri only. Here's the final Word file.",
                ["audrey_3page_website_copy_final.docx"],
            ),
            (
                "client",
                dt_utc(2026, 10, 17, 17, 12, 5),
                "Sent it straight to my designer. Thank you guys for starting on it and sorting out the payment route!",
                [],
            ),
        ],
    },
    "orozcoazael815@gmail.com": {
        "username": "azael_orozco",
        "first_name": "Azael",
        "last_name": "Orozco",
        "channel": "Direct site",
        "subject": "4-page contractor website copy & customer estimate sheet",
        "status": "closed",
        "requests": [
            {
                "key": "ao_copy",
                "reference": "INF-260917-AO",
                "service_family": "communication",
                "service_code": "communication-copy",
                "title": "Four-page roofing contractor website copy and customer estimate template",
                "objective": "Write conversion copy for four contractor web pages plus a printable customer estimate and warranty sheet.",
                "scope": "Four website pages plus estimate sheet ($334.95 settled via Apple Pay after $345 limit adjustment).",
                "deliverable": "4-page website copy deck (.docx) and customer estimate workbook (.xlsx).",
                "status": "delivered",
                "estimate_low": Decimal("334.95"),
                "estimate_high": Decimal("345.00"),
                "created_at": dt_utc(2026, 9, 17, 2, 10, 0),
                "deliverables": [
                    {
                        "title": "4-Page Contractor Site Copy & Estimate Sheet — Final (v2)",
                        "kind": "Website copy & template",
                        "status": "delivered",
                        "version": 2,
                        "notes": "Settled Sep 19, 2026 via Bank of America Visa Apple Pay (QP-MU7UJNAA12AN, $334.95).",
                    }
                ],
            }
        ],
        "invoices": [
            {
                "key": "inv_ao_345",
                "number": "QP2609-AF57C431",
                "request_key": "ao_copy",
                "amount_due": Decimal("345.00"),
                "amount_paid": Decimal("0.00"),
                "status": "void",
                "description": "Website / product copy — 4-page contractor website copy & estimate template",
                "created_at": dt_utc(2026, 9, 19, 3, 35, 0),
                "due_at": dt_utc(2026, 9, 21, 3, 35, 0),
                "tx_refs": ["QP-MU7UBRBHE6KP"],
            },
            {
                "key": "inv_ao_334",
                "number": "QP2609-1BD487BA",
                "request_key": "ao_copy",
                "amount_due": Decimal("334.95"),
                "amount_paid": Decimal("334.95"),
                "status": "paid",
                "description": "Website / product copy — 4-page contractor website copy & estimate template (adjusted balance)",
                "created_at": dt_utc(2026, 9, 19, 3, 45, 0),
                "due_at": dt_utc(2026, 9, 21, 3, 45, 0),
                "tx_refs": ["QP-MU7UJNAA12AN"],
            },
        ],
        "messages": [
            (
                "client",
                dt_utc(2026, 9, 16, 23, 14, 10),
                "yo how much to write copy for a 4 page roofing & exterior contractor site + a 1 page estimate sheet we give homeowners?",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 9, 16, 23, 28, 40),
                "Hey Azael, for the 4 website pages plus the printable homeowner estimate and warranty sheet, it's $345 total. Do you have rough notes on your services and service areas?",
                [],
            ),
            (
                "client",
                dt_utc(2026, 9, 17, 4, 12, 0),
                "yeah here's the doc my brother typed up",
                ["orozco_roofing_rough_notes.docx"],
            ),
            (
                "admin",
                dt_utc(2026, 9, 17, 14, 5, 20),
                "Got the file. Quick question before we write the estimate sheet—your doc has a bracket note for the Maricopa County cities and workmanship warranty length. What cities and warranty years should we put in?",
                [],
            ),
            (
                "client",
                dt_utc(2026, 9, 18, 22, 50, 15),
                "my bad man been up on a commercial roof in Mesa all day yesterday and today. put Phoenix, Scottsdale, Mesa, Chandler, and Gilbert. 10 year workmanship warranty on full replacements. send the invoice whenever",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 9, 19, 3, 35, 10),
                "All good! Just posted invoice QP2609-AF57C431 for $345.00.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 9, 19, 3, 42, 30),
                "bro my Bank of America card just declined the 345 for insufficient funds, I checked my app and I literally have $336.10 available until a check clears Monday lol. can you make the invoice 334.95 so I can pay it right now?",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 9, 19, 3, 45, 20),
                "Sure, I voided the $345 one and put up QP2609-1BD487BA for $334.95.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 9, 19, 3, 48, 10),
                "boom went right through on Apple Pay.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 9, 20, 16, 15, 0),
                "Here is v1 of the 4-page website copy deck so you can read through the pages tonight.",
                ["orozco_site_copy_and_estimate_v1.docx"],
            ),
            (
                "client",
                dt_utc(2026, 9, 21, 1, 20, 40),
                "read it with my brother, pages sound legit. one change—let's make it a 12-year workmanship warranty instead of 10-year so we beat the other guys bidding in Chandler.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 9, 21, 14, 10, 0),
                "Updated to 12-year workmanship warranty everywhere. Attached the final Word copy deck and the matching Excel customer estimate template.",
                ["orozco_site_copy_and_estimate_final.docx", "orozco_estimate_sheet.xlsx"],
            ),
        ],
    },
    "jackjohnson0533@gmail.com": {
        "username": "jack_johnson",
        "first_name": "Jack",
        "last_name": "Johnson",
        "channel": "Web search",
        "subject": "B2B 5-page website copy & 12-slide outbound deck ($500)",
        "status": "closed",
        "requests": [
            {
                "key": "jj_crm",
                "reference": "INF-260405-JJ",
                "service_family": "systems",
                "service_code": "systems-discovery",
                "title": "CRM pipeline and territory lead-routing specification",
                "objective": "Document HubSpot deal stages, territory routing rules, and weighted MRR forecast formulas.",
                "scope": "Technical workflow specification and pipeline sheet ($160.00).",
                "deliverable": "CRM pipeline & lead-routing specification (.pdf).",
                "status": "delivered",
                "estimate_low": Decimal("160.00"),
                "estimate_high": Decimal("160.00"),
                "created_at": dt_utc(2026, 4, 4, 19, 10, 0),
                "deliverables": [
                    {
                        "title": "HubSpot Lead-Routing & Deal Stage Automation Spec",
                        "kind": "Technical specification",
                        "status": "delivered",
                        "version": 1,
                        "notes": "Settled Apr 5, 2026 (QP-MNLDLWO0GQPG, $160.00).",
                    }
                ],
            },
            {
                "key": "jj_b2b",
                "reference": "INF-260917-JJ",
                "service_family": "studio",
                "service_code": "studio-deck",
                "title": "Five-page B2B website copy and 12-slide enterprise sales deck",
                "objective": "Rewrite core B2B website messaging and build a 12-slide outbound sales presentation for 3PL buyers.",
                "scope": "Full website copy package and 12-slide outbound deck ($500.00).",
                "deliverable": "5-page B2B copy deck and 12-slide enterprise pitch presentation.",
                "status": "delivered",
                "estimate_low": Decimal("500.00"),
                "estimate_high": Decimal("500.00"),
                "created_at": dt_utc(2026, 9, 15, 18, 0, 0),
                "deliverables": [
                    {
                        "title": "5-Page B2B Website Copy & 12-Slide Enterprise Deck — Final (v2)",
                        "kind": "Website & deck package",
                        "status": "delivered",
                        "version": 2,
                        "notes": "Settled Sep 17, 2026 via Mastercard Apple Pay (QP-MU5RGDSOQP22, $500.00).",
                    }
                ],
            },
        ],
        "invoices": [
            {
                "key": "inv_jj_160",
                "number": "INV-260405-JJ01",
                "request_key": "jj_crm",
                "amount_due": Decimal("160.00"),
                "amount_paid": Decimal("160.00"),
                "status": "paid",
                "description": "Systems & workflow — HubSpot CRM pipeline & territory routing spec",
                "created_at": dt_utc(2026, 4, 5, 6, 10, 0),
                "due_at": dt_utc(2026, 4, 7, 6, 10, 0),
                "tx_refs": ["QP-MNLDLWO0GQPG"],
            },
            {
                "key": "inv_jj_500",
                "number": "QP2609-5851CC11",
                "request_key": "jj_b2b",
                "amount_due": Decimal("500.00"),
                "amount_paid": Decimal("500.00"),
                "status": "paid",
                "description": "Deck & website copy — 5-page B2B site copy & 12-slide enterprise sales deck",
                "created_at": dt_utc(2026, 9, 17, 16, 30, 0),
                "due_at": dt_utc(2026, 9, 19, 16, 30, 0),
                "tx_refs": ["QP-MU5RGDSOQP22"],
            },
        ],
        "messages": [
            (
                "client",
                dt_utc(2026, 4, 4, 21, 15, 0),
                "Hi, here is a sample CSV export from our HubSpot pipeline. We need a clean spec doc for our ops admin showing how territory routing and stage probabilities should be configured.",
                ["johnson_hubspot_export.csv"],
            ),
            (
                "admin",
                dt_utc(2026, 4, 5, 6, 12, 0),
                "Morning Jack, we can put together the full routing and stage automation spec for $160 (INV-260405-JJ01).",
                [],
            ),
            (
                "client",
                dt_utc(2026, 4, 5, 6, 25, 0),
                "Paid via Apple Pay.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 4, 6, 15, 40, 0),
                "Here is the completed HubSpot Lead-Routing & Deal Stage Automation Spec.",
                ["johnson_crm_pipeline_spec.pdf"],
            ),
            (
                "client",
                dt_utc(2026, 9, 15, 17, 52, 10),
                "Hey team—the routing spec from April has been working great. We're now overhauling our 5 main B2B website pages and our 12-slide outbound deck for 3PL buyers. Attached our brief—how much for both?",
                ["johnson_b2b_site_and_deck_brief.docx"],
            ),
            (
                "admin",
                dt_utc(2026, 9, 15, 18, 18, 40),
                "Good to hear from you Jack! Writing all 5 B2B pages plus structuring and writing the 12-slide enterprise deck is $500 flat.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 9, 17, 16, 25, 0),
                "Sorry for the two-day lag, had to get budget sign-off from my cofounder. Send the $500 invoice and I'll clear it now.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 9, 17, 16, 31, 0),
                "Invoice QP2609-5851CC11 ($500.00) is live on your account.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 9, 17, 16, 46, 10),
                "Paid on Apple Pay.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 9, 18, 19, 15, 0),
                "Here's the v1 draft of the 5 website pages and the 12-slide deck structure. Let us know what you want adjusted.",
                ["johnson_b2b_deck_and_copy_v1.pdf"],
            ),
            (
                "client",
                dt_utc(2026, 9, 19, 11, 8, 25),
                "Reviewed with the sales team this morning. Website copy is ready as-is. On Slide 4 of the deck, can we swap the placeholder ROI numbers for our actual Q3 Midwest 3PL pilot (38% faster dock turn time and 14 hrs/wk saved per dispatcher)?",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 9, 19, 15, 30, 0),
                "Updated Slide 4 with the Q3 Midwest 3PL metrics and finalized the speaker script. Attached the final package.",
                ["johnson_b2b_site_and_deck_final.docx"],
            ),
        ],
    },
    "lucacaro@hawaii.edu": {
        "username": "luca_carollo",
        "first_name": "Luca",
        "last_name": "Carollo",
        "channel": "Colleague referral",
        "subject": "Q3 rental property reconciliation ($120) & partner cash-flow model ($135)",
        "status": "closed",
        "requests": [
            {
                "key": "lc_spring",
                "reference": "INF-260515-LC",
                "service_family": "studio",
                "service_code": "studio-technical",
                "title": "Spring monthly property bookkeeping and vendor schedule workbooks",
                "objective": "Maintain monthly unit expense schedules, vendor reconciliation sheets, and occupancy rollups across March–May 2026.",
                "scope": "Nine recurring spreadsheet and reconciliation passes across March, April, and May 2026 ($475.00 cumulative).",
                "deliverable": "Monthly reconciled Excel workbooks.",
                "status": "delivered",
                "estimate_low": Decimal("475.00"),
                "estimate_high": Decimal("475.00"),
                "created_at": dt_utc(2026, 3, 1, 9, 0, 0),
                "deliverables": [
                    {
                        "title": "Spring Monthly Property Bookkeeping & Vendor Ledger — Final (v1)",
                        "kind": "Financial Ledger",
                        "status": "delivered",
                        "version": 1,
                        "notes": "Delivered May 15, 2026.",
                    }
                ],
            },
            {
                "key": "lc_q3",
                "reference": "INF-260907-LC",
                "service_family": "studio",
                "service_code": "studio-technical",
                "title": "Q3 multi-unit property ledger reconciliation & NOI summary",
                "objective": "Clean raw bank exports, match August maintenance receipts, and produce a Q3 Net Operating Income workbook.",
                "scope": "Q3 reconciliation workbook ($120.00).",
                "deliverable": "Reconciled Q3 property ledger (.xlsx).",
                "status": "delivered",
                "estimate_low": Decimal("120.00"),
                "estimate_high": Decimal("120.00"),
                "created_at": dt_utc(2026, 9, 6, 20, 0, 0),
                "deliverables": [
                    {
                        "title": "Q3 Reconciled Property Ledger — Final",
                        "kind": "Excel workbook",
                        "status": "delivered",
                        "version": 1,
                        "notes": "Settled Sep 7, 2026 (QP-MTR1XDK5NRLF, $120.00).",
                    }
                ],
            },
            {
                "key": "lc_waterfall",
                "reference": "INF-260914-LC",
                "service_family": "studio",
                "service_code": "studio-technical",
                "title": "12-month partner cash-flow and LP/GP distribution waterfall model",
                "objective": "Build a 12-month cash-flow projection and quarterly LP/GP distribution schedule for two Honolulu units.",
                "scope": "Excel partner waterfall workbook ($135.00).",
                "deliverable": "Partner cash-flow & waterfall model (.xlsx).",
                "status": "delivered",
                "estimate_low": Decimal("135.00"),
                "estimate_high": Decimal("135.00"),
                "created_at": dt_utc(2026, 9, 13, 21, 0, 0),
                "deliverables": [
                    {
                        "title": "Partner Cash-Flow & Distribution Waterfall Model — Final (v2)",
                        "kind": "Excel financial model",
                        "status": "delivered",
                        "version": 2,
                        "notes": "Settled Sep 14, 2026 (QP-MU0YD6CYX5SD, $135.00).",
                    }
                ],
            },
        ],
        "invoices": [
            {
                "key": "inv_lc_spring",
                "number": "INV-260515-LC00",
                "request_key": "lc_spring",
                "amount_due": Decimal("475.00"),
                "amount_paid": Decimal("475.00"),
                "status": "paid",
                "description": "Technical production — Spring monthly bookkeeping & vendor reconciliation sheets (Mar–May)",
                "created_at": dt_utc(2026, 5, 15, 7, 9, 0),
                "due_at": dt_utc(2026, 5, 17, 7, 9, 0),
                "tx_refs": [
                    "QP-MM7JVVF0RHJY",
                    "QP-MMEMT3U3ZAEY",
                    "QP-MNBIR0M7AJXQ",
                    "QP-MNFVOVXN221W",
                    "QP-MNLKGFE837EY",
                    "QP-MNMY4UQJABZL",
                    "QP-MOS8KKB0UQKG",
                    "QP-MP3WZMXZFF5J",
                    "QP-MP6KTZPLYJ8S",
                ],
            },
            {
                "key": "inv_lc_120",
                "number": "QP2609-15161B3E",
                "request_key": "lc_q3",
                "amount_due": Decimal("120.00"),
                "amount_paid": Decimal("120.00"),
                "status": "paid",
                "description": "Technical production — Q3 multi-unit property ledger & NOI reconciliation",
                "created_at": dt_utc(2026, 9, 7, 9, 30, 0),
                "due_at": dt_utc(2026, 9, 9, 9, 30, 0),
                "tx_refs": ["QP-MTR1XDK5NRLF"],
            },
            {
                "key": "inv_lc_135",
                "number": "QP2609-83B9F34D",
                "request_key": "lc_waterfall",
                "amount_due": Decimal("135.00"),
                "amount_paid": Decimal("135.00"),
                "status": "paid",
                "description": "Technical production — 12-month partner cash-flow & LP/GP distribution model",
                "created_at": dt_utc(2026, 9, 14, 7, 45, 0),
                "due_at": dt_utc(2026, 9, 16, 7, 45, 0),
                "tx_refs": ["QP-MU0YD6CYX5SD"],
            },
        ],
        "messages": [
            (
                "client",
                dt_utc(2026, 9, 6, 21, 14, 0),
                "Aloha guys, ready to do our Q3 rental ledger cleanup for the Waikiki and Ala Moana units. Attached the raw bank CSV export.",
                ["luca_q3_raw_bank_export.csv"],
            ),
            (
                "admin",
                dt_utc(2026, 9, 7, 9, 30, 15),
                "Morning Luca! The Q3 reconciliation and NOI rollup is $120 (invoice QP2609-15161B3E). Also I noticed two August rows in your CSV say '[MISSING VENDOR]' for $620 and $185—do you have the invoices for those?",
                [],
            ),
            (
                "client",
                dt_utc(2026, 9, 7, 9, 42, 10),
                "Just paid the $120 on Apple Pay. Let me dig through my email for those August contractor receipts, I'll send them over tomorrow.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 9, 8, 18, 20, 45),
                "sorry for the wait, found the PDF with both August maintenance receipts (AC service on 12A and lock hardware on 4B).",
                ["luca_august_vendor_receipts.pdf"],
            ),
            (
                "admin",
                dt_utc(2026, 9, 9, 14, 10, 0),
                "Thanks Luca, matched both receipts and standardized all the date columns. Here is your reconciled Q3 Property Ledger.",
                ["luca_q3_property_ledger_reconciled.xlsx"],
            ),
            (
                "client",
                dt_utc(2026, 9, 13, 21, 35, 10),
                "Hey the Q3 sheet was super helpful for my CPA. Can you build a separate 12-month cash-flow and quarterly partner distribution tab (60% LP / 40% GP after management fee and $1,500/qtr reserve)?",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 9, 14, 7, 45, 20),
                "Sure thing, building the 12-month forecast and LP/GP waterfall model is $135. Just posted invoice QP2609-83B9F34D.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 9, 14, 8, 1, 0),
                "Paid $135 via Apple Pay.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 9, 15, 16, 5, 0),
                "Here is v1 of the partner distribution model. I set the management fee cell to 8.0% based on your spring workbook.",
                ["luca_partner_distribution_model_v1.xlsx"],
            ),
            (
                "client",
                dt_utc(2026, 9, 16, 4, 18, 30),
                "looks great, just one tweak—we negotiated the property management fee down to 7.5% starting October 1. can you update that formula and send the final?",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 9, 16, 11, 25, 0),
                "Updated the management fee input to 7.5% across all four quarters. Here's the final workbook.",
                ["luca_partner_distribution_model_final.xlsx"],
            ),
        ],
    },
    "kchin444@gmail.com": {
        "username": "keegan_chin",
        "first_name": "Keegan",
        "last_name": "Chin",
        "channel": "Web search",
        "subject": "Excel inventory and SKU profit-margin calculator",
        "status": "closed",
        "requests": [
            {
                "key": "kch_tech",
                "reference": "INF-261013-KC",
                "service_family": "studio",
                "service_code": "studio-technical",
                "title": "Excel SKU profit-margin workbook and team setup guide",
                "objective": "Build an Excel workbook that calculates unit landed cost, SKU margin, and reorder thresholds.",
                "scope": "Technical production ($75 Excel workbook + $45 custom formula & setup guide = $120.00 total).",
                "deliverable": "Excel margin calculator (.xlsx) and staff setup guide (.pdf).",
                "status": "delivered",
                "estimate_low": Decimal("120.00"),
                "estimate_high": Decimal("120.00"),
                "created_at": dt_utc(2026, 10, 12, 19, 15, 0),
                "deliverables": [
                    {
                        "title": "Excel SKU Profit-Margin Calculator & Setup Guide — Final (v2)",
                        "kind": "Technical deliverable",
                        "status": "delivered",
                        "version": 2,
                        "notes": "Settled Oct 13, 2026 via Apple Pay (T945497750460100); v2 with locked formula cells delivered Oct 15.",
                    }
                ],
            }
        ],
        "invoices": [
            {
                "key": "inv_kch_120",
                "number": "INV-261013-KC01",
                "request_key": "kch_tech",
                "amount_due": Decimal("120.00"),
                "amount_paid": Decimal("120.00"),
                "status": "paid",
                "description": "Technical production — Excel SKU profit-margin workbook & setup guide ($75 sheet + $45 guide)",
                "created_at": dt_utc(2026, 10, 13, 10, 18, 0),
                "due_at": dt_utc(2026, 10, 15, 10, 18, 0),
                "tx_refs": ["T174041131745845", "T628607999331942", "T945497750460100"],
            }
        ],
        "messages": [
            (
                "client",
                dt_utc(2026, 10, 12, 19, 10, 15),
                "Hi, I found your site while looking for custom Excel work. I need an inventory landed-cost and margin calculator built from our SKU sheet, plus a 1-page guide showing my warehouse staff how to add new items without breaking formulas.",
                ["keegan_raw_sku_list.xlsx"],
            ),
            (
                "admin",
                dt_utc(2026, 10, 12, 19, 28, 40),
                "Hi Keegan, the Excel margin workbook is $75 and the staff setup guide is $45 ($120 total). I checked your SKU file—the Duty % column is blank on most of the rows. Do you have your customs broker's HTS rate sheet?",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 13, 10, 14, 20),
                "Sorry was waiting on my freight forwarder to email me the tariff breakdown. Here's the PDF with the HTS duty rates and CBM ocean charges. Send the $120 invoice whenever you're ready.",
                ["keegan_freight_duty_rates.pdf"],
            ),
            (
                "admin",
                dt_utc(2026, 10, 13, 10, 18, 10),
                "Got the tariff PDF and posted INV-261013-KC01 ($120.00).",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 13, 10, 26, 20),
                "Just paid the $120 on Apple Pay. The regular card screen was sticking on my browser so I switched to Apple Pay.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 14, 9, 40, 0),
                "Payment cleared. Here is v1 of the SKU Margin Calculator and the 1-page Staff Setup Guide PDF.",
                ["keegan_sku_margin_calculator_v1.xlsx", "keegan_staff_sku_guide.pdf"],
            ),
            (
                "client",
                dt_utc(2026, 10, 14, 22, 15, 12),
                "Hey I tested the sheet today—the CBM freight allocation works great. One request: can you add a 'Wholesale 2.2x' column and lock the formula columns so my staff can only type in columns A to E?",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 15, 11, 5, 0),
                "Added the Wholesale 2.2x column and protected all the formula columns so only the yellow SKU input fields are editable. Here's v2.",
                ["keegan_sku_margin_calculator_v2_locked.xlsx"],
            ),
        ],
    },
    "vickyizad@gmail.com": {
        "username": "liza_iza",
        "first_name": "Liza",
        "last_name": "Iza",
        "channel": "Direct site",
        "subject": "Vendor rate card ($70) & 15-page service proposal QA ($50)",
        "status": "closed",
        "requests": [
            {
                "key": "li_vendor",
                "reference": "INF-260919-LI",
                "service_family": "communication",
                "service_code": "communication-copy",
                "title": "Vendor onboarding compliance packet and 2026 commercial rate card",
                "objective": "Format vendor onboarding COI/ACH instructions and build a clean commercial rate card table.",
                "scope": "Split across two $35 milestones on Sep 19 and Sep 20, 2026 ($70.00 total).",
                "deliverable": "Vendor onboarding PDF and Excel rate card.",
                "status": "delivered",
                "estimate_low": Decimal("70.00"),
                "estimate_high": Decimal("70.00"),
                "created_at": dt_utc(2026, 9, 19, 15, 30, 0),
                "deliverables": [
                    {
                        "title": "Vendor Onboarding Packet & 2026 Rate Card",
                        "kind": "Operations packet",
                        "status": "delivered",
                        "version": 1,
                        "notes": "Settled Sep 19–20, 2026 across QP2609-57FDD99C ($35) and QP2609-038E9472 ($35).",
                    }
                ],
            },
            {
                "key": "li_qa",
                "reference": "INF-261008-LI",
                "service_family": "assurance",
                "service_code": "assurance-editorial",
                "title": "Editorial QA — Editing and layout cleanup for a 15-page client proposal",
                "objective": "Clean up wording, formatting, and pricing table alignment across a 15-page service proposal.",
                "scope": "Full Editorial QA and formatting pass ($50.00).",
                "deliverable": "Edited and formatted 15-page service proposal (.docx & .pdf).",
                "status": "delivered",
                "estimate_low": Decimal("50.00"),
                "estimate_high": Decimal("50.00"),
                "created_at": dt_utc(2026, 10, 8, 17, 30, 0),
                "deliverables": [
                    {
                        "title": "15-Page Service Proposal — Edited & Formatted (v2 Final)",
                        "kind": "Editorial QA package",
                        "status": "delivered",
                        "version": 2,
                        "notes": "Settled Oct 11, 2026 (T170633246895390) and delivered Oct 12, 2026.",
                    }
                ],
            },
        ],
        "invoices": [
            {
                "key": "inv_li_35a",
                "number": "QP2609-57FDD99C",
                "request_key": "li_vendor",
                "amount_due": Decimal("35.00"),
                "amount_paid": Decimal("35.00"),
                "status": "paid",
                "description": "Communication — Vendor onboarding compliance packet (Part 1)",
                "created_at": dt_utc(2026, 9, 19, 16, 0, 0),
                "due_at": dt_utc(2026, 9, 21, 16, 0, 0),
                "tx_refs": ["QP-MU8L5VHB3TJS"],
            },
            {
                "key": "inv_li_35b",
                "number": "QP2609-038E9472",
                "request_key": "li_vendor",
                "amount_due": Decimal("35.00"),
                "amount_paid": Decimal("35.00"),
                "status": "paid",
                "description": "Technical production — 2026 commercial crew rate card sheet (Part 2)",
                "created_at": dt_utc(2026, 9, 20, 4, 15, 0),
                "due_at": dt_utc(2026, 9, 22, 4, 15, 0),
                "tx_refs": ["QP-MU9BEM9FRNAP"],
            },
            {
                "key": "inv_li_50",
                "number": "INV-261008-LI01",
                "request_key": "li_qa",
                "amount_due": Decimal("50.00"),
                "amount_paid": Decimal("50.00"),
                "status": "paid",
                "description": "Editorial QA — 15-page client proposal editing & formatting",
                "created_at": dt_utc(2026, 10, 8, 17, 45, 0),
                "due_at": dt_utc(2026, 10, 12, 17, 45, 0),
                "tx_refs": ["T639969293569962", "T170633246895390"],
            },
        ],
        "messages": [
            (
                "client",
                dt_utc(2026, 9, 19, 15, 48, 0),
                "Hi, attaching our rough vendor onboarding doc. Can we clean this up into a 1-page PDF for subcontractors ($35) and then do our 2026 crew rate card sheet tomorrow ($35)?",
                ["liza_vendor_packet_draft.docx"],
            ),
            (
                "admin",
                dt_utc(2026, 9, 19, 16, 18, 0),
                "Hi Liza, got the payment on QP2609-57FDD99C ($35.00) and finished the clean Vendor Onboarding PDF here.",
                ["liza_vendor_packet_clean.pdf"],
            ),
            (
                "client",
                dt_utc(2026, 9, 20, 4, 30, 0),
                "Just paid the second $35 invoice (QP2609-038E9472) for the rate card.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 9, 20, 13, 15, 0),
                "Here is the completed 2026 Commercial Crew Rate Card Excel sheet.",
                ["liza_rate_card_final.xlsx"],
            ),
            (
                "client",
                dt_utc(2026, 10, 8, 17, 26, 15),
                "Hey again! I have a 15-page facility maintenance proposal where the maintenance tables keep splitting awkwardly across pages. Attaching the Word file—how much to edit and format the whole thing?",
                ["liza_15p_service_proposal_messy.docx"],
            ),
            (
                "admin",
                dt_utc(2026, 10, 8, 17, 45, 10),
                "Welcome back Liza. A full Editorial QA and table layout pass on the 15-page proposal is $50 (posted INV-261008-LI01).",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 8, 17, 58, 10),
                "my debit card just declined on the checkout screen, not sure why. flying out for a site walk now so i'll pay it with my credit card on sunday when i'm back.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 11, 18, 28, 30),
                "Back home. Just put the $50 through on my credit card.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 12, 11, 45, 0),
                "Got it, thank you. Here is the edited and formatted 15-page proposal in Word so you can check the tables.",
                ["liza_15p_service_proposal_v1.docx"],
            ),
            (
                "client",
                dt_utc(2026, 10, 12, 13, 50, 10),
                "Tables look way cleaner! One tiny thing—on the page footer my office number says 555-0149 instead of 555-0194. Can you fix that and send me a locked PDF for the client?",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 12, 14, 18, 22),
                "Fixed the footer phone number across all 15 pages and exported the print-ready PDF for you here.",
                ["liza_15p_service_proposal_final.pdf"],
            ),
        ],
    },
    "drako.santaana.glz@gmail.com": {
        "username": "drako_santaana",
        "first_name": "Drako",
        "last_name": "Santa Ana",
        "channel": "Web search",
        "subject": "Operations supervisor resume and LinkedIn rewrite",
        "status": "closed",
        "requests": [
            {
                "key": "ds_rewrite",
                "reference": "INF-261011-DS",
                "service_family": "text-intelligence",
                "service_code": "text-rewrite",
                "title": "Resume and LinkedIn profile rewrite",
                "objective": "Rewrite a resume summary, work history bullets, and LinkedIn bio for warehouse supervisor roles.",
                "scope": "Full rewrite and formatting pass under Rewrite & adapt ($25.00).",
                "deliverable": "Rewritten resume and LinkedIn copy (.docx & .pdf).",
                "status": "delivered",
                "estimate_low": Decimal("25.00"),
                "estimate_high": Decimal("25.00"),
                "created_at": dt_utc(2026, 10, 10, 3, 20, 0),
                "deliverables": [
                    {
                        "title": "Rewritten Resume & LinkedIn Profile — Final (v2)",
                        "kind": "Copy rewrite",
                        "status": "delivered",
                        "version": 2,
                        "notes": "Settled Oct 11, 2026 via Apple Pay (T402408384219595) and delivered Oct 12, 2026.",
                    }
                ],
            }
        ],
        "invoices": [
            {
                "key": "inv_ds_25",
                "number": "INV-261011-DS01",
                "request_key": "ds_rewrite",
                "amount_due": Decimal("25.00"),
                "amount_paid": Decimal("25.00"),
                "status": "paid",
                "description": "Rewrite & adapt — Resume & LinkedIn profile rewrite",
                "created_at": dt_utc(2026, 10, 11, 4, 48, 0),
                "due_at": dt_utc(2026, 10, 13, 4, 48, 0),
                "tx_refs": ["T402408384219595"],
            }
        ],
        "messages": [
            (
                "client",
                dt_utc(2026, 10, 10, 3, 15, 10),
                "hey how much do you charge to update a resume and linkedin bio? attaching my old resume from 2023",
                ["drako_old_resume_2023.pdf"],
            ),
            (
                "admin",
                dt_utc(2026, 10, 10, 3, 28, 40),
                "Hey Drako, rewriting both the resume and LinkedIn profile is $25. Since your PDF stops in 2023, send over a few rough bullets on what you've been doing from 2024 to now so we can include your current role.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 11, 4, 42, 10),
                "my bad man I worked a double shift yesterday and knocked out. here's a word doc with the numbers from my current supervisor job at Westside Cold Storage. send the $25 invoice and I'll Apple Pay it",
                ["drako_2024_2026_warehouse_notes.docx"],
            ),
            (
                "admin",
                dt_utc(2026, 10, 11, 4, 48, 15),
                "Those metrics (cutting mis-picks from 2.4% to 0.6% across 14 dock doors) are great. Just posted INV-261011-DS01 for $25.00.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 11, 4, 57, 10),
                "Just paid the $25 on Apple Pay.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 11, 16, 10, 0),
                "Here is v1 of your rewritten resume and LinkedIn copy in Word.",
                ["drako_resume_and_linkedin_v1.docx"],
            ),
            (
                "client",
                dt_utc(2026, 10, 12, 2, 14, 0),
                "reads way stronger than my old one. can you make sure my OSHA 30-Hour and Reach Forklift Instructor certs are bolded in their own section at the bottom, and send a PDF too?",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 12, 9, 30, 0),
                "Added the dedicated Certifications section at the bottom and exported the final PDF here.",
                ["drako_resume_and_linkedin_final.pdf"],
            ),
        ],
    },
    "stellarae147@gmail.com": {
        "username": "estella_williams",
        "first_name": "Estella",
        "last_name": "Williams",
        "channel": "Web search",
        "subject": "Client newsletter rewrite ($25), onboarding SOP ($80) & Q4 board deck ($150)",
        "status": "closed",
        "requests": [
            {
                "key": "ew_rewrite",
                "reference": "INF-261005-EW",
                "service_family": "text-intelligence",
                "service_code": "text-humanize",
                "title": "Humanize & refine — Client newsletter rewrite and Pro access",
                "objective": "Refine a 1,800-word newsletter draft so it reads naturally without stiff phrasing.",
                "scope": "Humanize & refine pass plus Pro plan access ($25.00).",
                "deliverable": "Refined newsletter copy (.docx).",
                "status": "delivered",
                "estimate_low": Decimal("25.00"),
                "estimate_high": Decimal("25.00"),
                "created_at": dt_utc(2026, 10, 4, 22, 48, 0),
                "deliverables": [
                    {
                        "title": "Refined October Client Newsletter — Final",
                        "kind": "Refined copy",
                        "status": "delivered",
                        "version": 1,
                        "notes": "Settled Oct 5, 2026 (T531967564396668) and delivered Oct 5, 2026.",
                    }
                ],
            },
            {
                "key": "ew_sop",
                "reference": "INF-261010-EW",
                "service_family": "studio",
                "service_code": "studio-technical",
                "title": "Four-role staff onboarding SOP and checklist package",
                "objective": "Write clear step-by-step onboarding checklists and daily workflow SOPs for four team roles.",
                "scope": "Four role checklists at USD 20.00 per role (USD 80.00 total).",
                "deliverable": "Four-part staff onboarding SOP document (.docx & .pdf).",
                "status": "delivered",
                "estimate_low": Decimal("80.00"),
                "estimate_high": Decimal("80.00"),
                "created_at": dt_utc(2026, 10, 10, 18, 40, 0),
                "deliverables": [
                    {
                        "title": "Four-Role Staff Onboarding SOP & Checklists — Final (v2)",
                        "kind": "SOP documentation",
                        "status": "delivered",
                        "version": 2,
                        "notes": "Settled Oct 10, 2026 (T820955964974907) and delivered Oct 12, 2026.",
                    }
                ],
            },
            {
                "key": "ew_board_deck",
                "reference": "INF-261021-EW",
                "service_family": "studio",
                "service_code": "studio-presentations",
                "title": "Q4 Executive board briefing memo and 16-slide investor update deck",
                "objective": "Prepare executive presentation deck and confidential board briefing memo summarizing Q3 KPI performance, bridge financing terms, and 2027 regional expansion milestones.",
                "scope": "Comprehensive 16-slide investor update deck and a 4-page executive board memorandum ($150.00).",
                "deliverable": "16-slide presentation deck and executive memo (.docx & .pdf).",
                "status": "delivered",
                "estimate_low": Decimal("150.00"),
                "estimate_high": Decimal("150.00"),
                "created_at": dt_utc(2026, 10, 7, 10, 20, 0),
                "deliverables": [
                    {
                        "title": "Q4 Executive Investor Update Deck (16 Slides) — Final (v2)",
                        "kind": "Executive Deck",
                        "status": "delivered",
                        "version": 2,
                        "notes": "Settled Oct 21, 2026 (T549133644408552) and delivered Oct 21, 2026.",
                    },
                    {
                        "title": "Board of Directors Briefing Memo & Capital Summary — Final",
                        "kind": "Executive Briefing",
                        "status": "delivered",
                        "version": 1,
                        "notes": "Delivered Oct 21, 2026.",
                    },
                ],
            },
        ],
        "invoices": [
            {
                "key": "inv_ew_25",
                "number": "INV-261005-EW01",
                "request_key": "ew_rewrite",
                "amount_due": Decimal("25.00"),
                "amount_paid": Decimal("25.00"),
                "status": "paid",
                "description": "Humanize & refine — Newsletter copy refinement & Pro access",
                "created_at": dt_utc(2026, 10, 5, 4, 58, 0),
                "due_at": dt_utc(2026, 10, 7, 4, 58, 0),
                "tx_refs": ["T531967564396668"],
            },
            {
                "key": "inv_ew_80",
                "number": "INV-261010-EW02",
                "request_key": "ew_sop",
                "amount_due": Decimal("80.00"),
                "amount_paid": Decimal("80.00"),
                "status": "paid",
                "description": "Technical production — Four-role onboarding SOP checklists (4 roles @ $20)",
                "created_at": dt_utc(2026, 10, 10, 18, 52, 0),
                "due_at": dt_utc(2026, 10, 12, 18, 52, 0),
                "tx_refs": ["T603466867233431", "T820955964974907"],
            },
            {
                "key": "inv_ew_150",
                "number": "INV-261021-EW03",
                "request_key": "ew_board_deck",
                "amount_due": Decimal("150.00"),
                "amount_paid": Decimal("150.00"),
                "status": "paid",
                "description": "Presentation & executive writing — Q4 Executive board briefing memo & 16-slide investor update deck",
                "created_at": dt_utc(2026, 10, 20, 21, 15, 0),
                "due_at": dt_utc(2026, 10, 22, 21, 15, 0),
                "tx_refs": ["T549133644408552"],
            },
        ],
        "messages": [
            (
                "client",
                dt_utc(2026, 10, 4, 22, 45, 10),
                "Hi, I tried the humanizer tool on your site and wanted to get our 1,800-word October client newsletter refined so it doesn't sound so stiff.",
                ["estella_october_newsletter_draft.docx"],
            ),
            (
                "admin",
                dt_utc(2026, 10, 5, 4, 58, 20),
                "Morning Estella, a full editorial pass on the newsletter plus Pro access is $25 (posted INV-261005-EW01).",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 5, 5, 10, 0),
                "Just paid the $25 by card.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 5, 13, 20, 0),
                "Here is the refined October newsletter ready to drop into Mailchimp.",
                ["estella_october_newsletter_refined.docx"],
            ),
            (
                "client",
                dt_utc(2026, 10, 7, 10, 20, 0),
                "Hi, our Q4 advisory board meeting was just confirmed for late October and I need an executive presentation deck and confidential board briefing memo drafted. Our lead investor wants to review Q3 growth KPIs, our customer acquisition payback period, and our 2027 regional hiring roadmap. Here are my rough bullet points and financial figures.",
                ["estella_q4_board_deck_rough_bullets.docx"],
            ),
            (
                "admin",
                dt_utc(2026, 10, 7, 14, 15, 0),
                "Hi Estella, excellent timing. We can build a comprehensive 16-slide investor & board presentation deck along with a formal 4-page executive briefing memorandum for $150.00 total (INF-261021-EW).",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 8, 9, 10, 0),
                "Let's proceed. Please keep in mind that our board includes two former institutional CFOs. The phrasing around revenue run-rate and gross margins cannot be loose marketing speak. Every financial table must specify whether figures represent GAAP revenue or contracted ARR.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 10, 18, 38, 12),
                "Hey the newsletter got great replies from our clients! We're hiring next week and I need onboarding SOP checklists written for 4 roles on my team from my rough notes here.",
                ["estella_rough_role_notes.docx"],
            ),
            (
                "admin",
                dt_utc(2026, 10, 10, 18, 52, 30),
                "Happy to help with those. All four role checklists come to $80 total ($20 per role, INV-261010-EW02).",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 10, 19, 5, 15),
                "Paid the $80. My phone autofilled an old email address on the first screen so I backed out and re-entered it, went through fine.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 11, 15, 15, 0),
                "Got it! Here is v1 of the Four-Role Staff Onboarding SOP package.",
                ["estella_4role_onboarding_sops_v1.docx"],
            ),
            (
                "client",
                dt_utc(2026, 10, 12, 10, 12, 0),
                "Sorry didn't get to read this until this morning—can we move the morning POS & register opening checklist from the Shift Lead role over to the Front Desk Coordinator role?",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 12, 11, 40, 0),
                "Moved the POS & register opening section to Role 1 (Front Desk Coordinator) and exported the final binder-ready PDF.",
                ["estella_4role_onboarding_sops_final.pdf"],
            ),
            (
                "admin",
                dt_utc(2026, 10, 14, 16, 40, 0),
                "Here is v1 of the 16-Slide Executive Investor Update Deck. It features full slide narrative outlines, GAAP vs contracted ARR callouts, and the 2027 regional hiring roadmap.",
                ["estella_q4_executive_investor_deck_v1.docx"],
            ),
            (
                "client",
                dt_utc(2026, 10, 17, 11, 30, 0),
                "Reviewed v1 with our COO. Slide 6 needs complete restructuring. Our board chair will immediately ask why blended customer acquisition cost rose 14% without seeing the corresponding increase in 60-day cohort retention. Put those metrics side-by-side in a comparative callout box. Also, on the briefing memo, make sure Section 3 explicitly highlights our liquidity runway through Q2 2027 under both conservative and baseline revenue projections.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 19, 15, 20, 0),
                "Integrated the side-by-side CAC vs 60-day cohort retention table on Slide 6, and expanded Section 3 of the briefing memo with dual liquidity runway models (conservative $1.4M burn vs baseline $1.1M burn through Q2 2027).",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 20, 21, 15, 0),
                "The final Board Briefing Memo and 16-Slide Investor Presentation are ready. I posted invoice INV-261021-EW03 ($150.00). You can clear it directly using our verified link: https://paystack.shop/pay/tx0ipp9eg4",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 21, 2, 46, 15),
                "Ran the Sutton Bank card on the link, payment authorized ($150.00). Grabbed both the Word files and the PDF deck—the liquidity table on page 3 is exactly what the board needs to see. Excellent work.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 21, 3, 5, 0),
                "Payment confirmed, thank you Estella! All final board decks and briefing files are delivered. Good luck with the advisory meeting.",
                ["estella_q4_board_briefing_memo_final.docx", "estella_q4_investor_deck_slide_copy_final.pdf"],
            ),
        ],
    },
    "kayleecabreros@gmail.com": {
        "username": "kaylee_cabreros",
        "first_name": "Kaylee",
        "last_name": "Cabreros",
        "channel": "Snapchat",
        "subject": "Shopify product descriptions and welcome email sequence",
        "status": "open",
        "requests": [
            {
                "key": "kc_rewrite",
                "reference": "INF-260930-KC",
                "service_family": "text-intelligence",
                "service_code": "text-rewrite",
                "title": "Storefront product copy and welcome email rewrite",
                "objective": "Rewrite product descriptions and the customer welcome email sequence so the tone is natural and consistent.",
                "scope": "Started as product descriptions only ($15) on Sep 30, updated on Oct 5 to include the welcome email sequence ($30 total).",
                "deliverable": "Rewritten product copy sheet and welcome emails.",
                "status": "quoted",
                "estimate_low": Decimal("15.00"),
                "estimate_high": Decimal("30.00"),
                "created_at": dt_utc(2026, 9, 30, 7, 32, 0),
                "deliverables": [],
            }
        ],
        "invoices": [
            {
                "key": "inv_kc_15",
                "number": "INV-260930-KC01",
                "request_key": "kc_rewrite",
                "amount_due": Decimal("15.00"),
                "amount_paid": Decimal("0.00"),
                "status": "void",
                "description": "Rewrite & adapt — Storefront product descriptions",
                "created_at": dt_utc(2026, 9, 30, 7, 41, 10),
                "due_at": dt_utc(2026, 10, 5, 23, 0, 0),
                "tx_refs": ["T758275317571025"],
            },
            {
                "key": "inv_kc_30",
                "number": "INV-261005-KC02",
                "request_key": "kc_rewrite",
                "amount_due": Decimal("30.00"),
                "amount_paid": Decimal("0.00"),
                "status": "open",
                "description": "Rewrite & adapt — Product descriptions & welcome email sequence ($15 each)",
                "created_at": dt_utc(2026, 10, 5, 23, 2, 15),
                "due_at": dt_utc(2026, 10, 12, 23, 2, 15),
                "tx_refs": ["T133502247747412", "T121535354109858", "T091138443177008"],
            },
        ],
        "messages": [
            (
                "client",
                dt_utc(2026, 9, 30, 7, 30, 12),
                "Hey! came over from snap. I exported my Shopify product descriptions here—how much to rewrite these so they don't sound so dry?",
                ["kaylee_shopify_product_descriptions.xlsx"],
            ),
            (
                "admin",
                dt_utc(2026, 9, 30, 7, 41, 15),
                "Hi Kaylee, the product description sheet is $15. Just put INV-260930-KC01 on your account.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 9, 30, 7, 50, 15),
                "wait I closed the checkout screen bc I also want my 3 Klaviyo welcome emails rewritten at the same time so the voice matches. give me a couple days to finish typing the email drafts and we can do both together",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 5, 22, 56, 20),
                "hey sorry it took me 5 days to finish typing these lol, we had a pop-up market all weekend. here's the welcome emails doc—can you update the invoice to $30 for both?",
                ["kaylee_welcome_emails_draft.docx"],
            ),
            (
                "admin",
                dt_utc(2026, 10, 5, 23, 2, 30),
                "No worries! Voided the $15 invoice and posted INV-261005-KC02 ($30.00) for both files.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 5, 23, 14, 40),
                "ugh my credit union card declined twice, tried apple pay and manual entry. i'll call them in the morning to lift the block.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 5, 23, 20, 15),
                "Yeah credit unions block cross-border checkouts by default. Give them a quick call in the morning and INV-261005-KC02 will be ready whenever they clear it.",
                [],
            ),
        ],
    },
    "dkiragu97@gmail.com": {
        "username": "dennis_kiragu",
        "first_name": "Dennis",
        "last_name": "Kiragu",
        "channel": "Direct site",
        "subject": "12-month Excel cash-flow and expense tracker",
        "status": "open",
        "requests": [
            {
                "key": "dk_tech",
                "reference": "INF-261002-DK",
                "service_family": "studio",
                "service_code": "studio-technical",
                "title": "12-month Excel cash-flow and expense tracker",
                "objective": "Build a clean 12-month cash-flow spreadsheet with automated monthly totals and category breakdowns.",
                "scope": "Technical production package covering the Excel workbook and formula guide ($100.00).",
                "deliverable": "Excel workbook (.xlsx) and setup sheet.",
                "status": "quoted",
                "estimate_low": Decimal("100.00"),
                "estimate_high": Decimal("100.00"),
                "created_at": dt_utc(2026, 10, 2, 4, 28, 0),
                "deliverables": [],
            }
        ],
        "invoices": [
            {
                "key": "inv_dk_aug1",
                "number": "QP2608-C34D1221",
                "request_key": "dk_tech",
                "amount_due": Decimal("1.18"),
                "amount_paid": Decimal("0.00"),
                "status": "void",
                "description": "QuickPay — Initial card verification test",
                "created_at": dt_utc(2026, 8, 3, 9, 38, 0),
                "due_at": dt_utc(2026, 8, 5, 9, 38, 0),
                "tx_refs": ["QP-MSD1EW8CCHPI", "QP-MSD2I7B2XO6M"],
            },
            {
                "key": "inv_dk_100",
                "number": "INV-261002-DK01",
                "request_key": "dk_tech",
                "amount_due": Decimal("100.00"),
                "amount_paid": Decimal("0.00"),
                "status": "open",
                "description": "Technical production — 12-month Excel cash-flow & expense tracker",
                "created_at": dt_utc(2026, 10, 2, 4, 41, 0),
                "due_at": dt_utc(2026, 10, 9, 4, 41, 0),
                "tx_refs": ["T385872457609364", "T877171103589666"],
            },
        ],
        "messages": [
            (
                "client",
                dt_utc(2026, 10, 2, 4, 25, 10),
                "Hi, here's the basic expense sheet we've been using. I need a proper 12-month Excel cash-flow and expense tracker built with automated monthly rollups.",
                ["dennis_old_expense_sheet.xlsx"],
            ),
            (
                "admin",
                dt_utc(2026, 10, 2, 4, 41, 15),
                "Hi Dennis, building the 12-month workbook with automated category rollups from your sheet is $100 (INV-261002-DK01).",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 5, 5, 18, 0),
                "Hey Dennis, just checking in on the cash-flow tracker. Let me know if you ran into any issues with the payment link.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 5, 14, 12, 0),
                "sorry for the late reply—no error, my accountant told me to hold off until Friday so he can send the exact tax expense categories he wants in the dropdowns. I'll pay the $100 as soon as he sends that list.",
                [],
            ),
        ],
    },
    "uzbekquintero@gmail.com": {
        "username": "alexa_quintero",
        "first_name": "Alexa",
        "last_name": "Quintero",
        "channel": "Colleague referral",
        "subject": "10-slide commercial solar pitch deck copy and layout",
        "status": "closed",
        "requests": [
            {
                "key": "aq_deck",
                "reference": "INF-261002-AQ",
                "service_family": "studio",
                "service_code": "studio-deck",
                "title": "10-slide client pitch deck structure and copy",
                "objective": "Structure and write a 10-slide sales presentation with competitor pricing comparison tables on next-day turnaround.",
                "scope": "Deck & presentation copy ($90.00) plus next-day priority turnaround ($20.00).",
                "deliverable": "10-slide presentation deck (.pdf & .docx).",
                "status": "delivered",
                "estimate_low": Decimal("110.00"),
                "estimate_high": Decimal("110.00"),
                "created_at": dt_utc(2026, 10, 1, 22, 44, 0),
                "deliverables": [
                    {
                        "title": "10-Slide Commercial Pitch Deck — Final (v2)",
                        "kind": "Presentation deck",
                        "status": "delivered",
                        "version": 2,
                        "notes": "Settled Oct 2, 2026 via Apple Pay (T991195576160953) and delivered Oct 3, 2026.",
                    }
                ],
            }
        ],
        "invoices": [
            {
                "key": "inv_aq_110",
                "number": "INV-261002-AQ01",
                "request_key": "aq_deck",
                "amount_due": Decimal("110.00"),
                "amount_paid": Decimal("110.00"),
                "status": "paid",
                "description": "Deck & presentation — 10-slide client pitch deck ($90 base + $20 next-day rush)",
                "created_at": dt_utc(2026, 10, 2, 4, 56, 0),
                "due_at": dt_utc(2026, 10, 4, 4, 56, 0),
                "tx_refs": ["T991195576160953"],
            }
        ],
        "messages": [
            (
                "client",
                dt_utc(2026, 10, 1, 22, 42, 10),
                "Hi, a coworker gave me your link. I need a 10-slide commercial pitch deck structured and written by Saturday morning. Attaching my rough bullet notes and the competitor rate table.",
                ["alexa_pitch_rough_bullets.docx", "alexa_competitor_rates.xlsx"],
            ),
            (
                "admin",
                dt_utc(2026, 10, 2, 4, 56, 10),
                "Hi Alexa, structuring and writing the 10-slide deck is $90 plus $20 for overnight turnaround ($110 total, INV-261002-AQ01).",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 2, 5, 5, 18),
                "Paid $110 with Apple Pay.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 2, 18, 15, 0),
                "Here is v1 of the 10-slide deck so you can check the flow before we lock it tonight.",
                ["alexa_pitch_deck_structure_v1.pdf"],
            ),
            (
                "client",
                dt_utc(2026, 10, 2, 21, 40, 12),
                "this looks really sharp. can we swap Slide 4 and Slide 5 so the 4.2 MW warehouse rooftop case study comes right before our pricing table?",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 3, 2, 30, 0),
                "Swapped Slides 4 and 5 so the case study leads into the pricing comparison. Here's the final deck PDF.",
                ["alexa_10slide_pitch_deck_final.pdf"],
            ),
            (
                "client",
                dt_utc(2026, 10, 3, 4, 12, 44),
                "Got it, thank you for turning it around overnight!",
                [],
            ),
        ],
    },
    "cami.kurtz@icloud.com": {
        "username": "cami_kurtz",
        "first_name": "Cami",
        "last_name": "Kurtz",
        "channel": "Web search",
        "subject": "Call transcript synthesis and project action sheet",
        "status": "closed",
        "requests": [
            {
                "key": "ck_review",
                "reference": "INF-260930-CK",
                "service_family": "studio",
                "service_code": "studio-review",
                "title": "Client call transcript synthesis and project action sheet",
                "objective": "Pull key decisions, scope items, and next steps from 18 pages of raw call transcripts.",
                "scope": "Review & synthesis on 18 pages of call notes ($60.00).",
                "deliverable": "4-page project scope and action summary (.pdf).",
                "status": "delivered",
                "estimate_low": Decimal("60.00"),
                "estimate_high": Decimal("60.00"),
                "created_at": dt_utc(2026, 9, 29, 21, 42, 0),
                "deliverables": [
                    {
                        "title": "Client Call Synthesis & Action Sheet — Final (v2)",
                        "kind": "Action summary",
                        "status": "delivered",
                        "version": 2,
                        "notes": "Delivered after Apple Pay payment on Sep 30, 2026 (T473341988726386).",
                    }
                ],
            }
        ],
        "invoices": [
            {
                "key": "inv_ck_60",
                "number": "INV-260930-CK01",
                "request_key": "ck_review",
                "amount_due": Decimal("60.00"),
                "amount_paid": Decimal("60.00"),
                "status": "paid",
                "description": "Review & synthesis — 18-page call transcript synthesis & action list",
                "created_at": dt_utc(2026, 9, 30, 7, 54, 10),
                "due_at": dt_utc(2026, 10, 2, 7, 54, 10),
                "tx_refs": ["T473341988726386"],
            }
        ],
        "messages": [
            (
                "client",
                dt_utc(2026, 9, 29, 21, 38, 14),
                "Hi, I have 18 pages of messy Zoom auto-transcribed kickoff calls attached here. How much to pull out the actual decisions, phase 1 vs phase 2 items, and owner deadlines into a clean 4-page action sheet?",
                ["cami_raw_call_transcripts_18p.docx"],
            ),
            (
                "admin",
                dt_utc(2026, 9, 30, 7, 54, 15),
                "Morning Cami, going through the 18 pages and writing the 4-page scope and action sheet is $60 (posted INV-260930-CK01).",
                [],
            ),
            (
                "client",
                dt_utc(2026, 9, 30, 8, 4, 12),
                "Just paid the $60 with Apple Pay.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 9, 30, 14, 18, 30),
                "Here is v1 of your 4-page Call Synthesis & Action Sheet.",
                ["cami_call_action_sheet_v1.pdf"],
            ),
            (
                "client",
                dt_utc(2026, 9, 30, 19, 45, 19),
                "This saved me hours! One quick fix—Zoom captions wrote 'Mark' on the ERP sync items, his name is actually Marcus Vance. Can we update that so I can email the PDF to the client team tomorrow morning?",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 1, 6, 15, 0),
                "Updated all the ERP action items to Marcus Vance. Here is the final PDF.",
                ["cami_call_action_sheet_final.pdf"],
            ),
        ],
    },
    "valdaceai@gmail.com": {
        "username": "victor_mawira",
        "first_name": "Victor",
        "last_name": "Mawira",
        "channel": "Direct site",
        "subject": "Website service-page copy rewrite",
        "status": "open",
        "requests": [
            {
                "key": "vm_rewrite",
                "reference": "INF-260929-VM",
                "service_family": "text-intelligence",
                "service_code": "text-rewrite",
                "title": "Rewrite copy for two website service pages",
                "objective": "Tighten the wording and call-to-action sections across two draft service pages.",
                "scope": "Two web pages at USD 15.00 each (USD 30.00 total).",
                "deliverable": "Rewritten copy for both service pages.",
                "status": "quoted",
                "estimate_low": Decimal("30.00"),
                "estimate_high": Decimal("30.00"),
                "created_at": dt_utc(2026, 9, 29, 5, 58, 0),
                "deliverables": [],
            }
        ],
        "invoices": [
            {
                "key": "inv_vm_30",
                "number": "INV-260929-VM01",
                "request_key": "vm_rewrite",
                "amount_due": Decimal("30.00"),
                "amount_paid": Decimal("0.00"),
                "status": "open",
                "description": "Rewrite & adapt — Two website service pages ($15 per page)",
                "created_at": dt_utc(2026, 9, 29, 6, 8, 12),
                "due_at": dt_utc(2026, 10, 6, 6, 8, 12),
                "tx_refs": ["T118674717391403"],
            }
        ],
        "messages": [
            (
                "client",
                dt_utc(2026, 9, 28, 20, 56, 18),
                "Hey, I have two service pages for my website that sound clunky. Attached Page 1 here—how much to rewrite both?",
                ["victor_service_page_1_draft.docx"],
            ),
            (
                "admin",
                dt_utc(2026, 9, 29, 6, 8, 15),
                "Morning Victor, each page is $15 ($30 total, posted INV-260929-VM01). Send over Page 2 whenever it's ready.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 9, 29, 14, 29, 40),
                "Sorry stepped into a meeting while I was on the card screen earlier. My partner is still editing the second page so I'll pay the $30 as soon as he sends me his half.",
                [],
            ),
        ],
    },
    "linarickert2514@gmail.com": {
        "username": "lina_rickert",
        "first_name": "Lina",
        "last_name": "Rickert",
        "channel": "Snapchat",
        "subject": "Late-summer Klaviyo customer retention email sequence",
        "status": "closed",
        "requests": [
            {
                "key": "lr_may",
                "reference": "INF-260501-LR",
                "service_family": "communication",
                "service_code": "communication-copy",
                "title": "Spring product launch copy and storefront FAQ",
                "objective": "Write spring product launch descriptions, size guide notes, and storefront FAQ copy.",
                "scope": "Three copy passes in May 2026 ($30 + $10 add-on + $30 = $70.00 total).",
                "deliverable": "Spring storefront copy package.",
                "status": "delivered",
                "estimate_low": Decimal("70.00"),
                "estimate_high": Decimal("70.00"),
                "created_at": dt_utc(2026, 5, 1, 3, 50, 0),
                "deliverables": [
                    {
                        "title": "Spring Collection Launch Copy & Storefront FAQ Deck — Final (v1)",
                        "kind": "Storefront Copy",
                        "status": "delivered",
                        "version": 1,
                        "notes": "Delivered May 1, 2026.",
                    }
                ],
            },
            {
                "key": "lr_july",
                "reference": "INF-260725-LR",
                "service_family": "communication",
                "service_code": "communication-copy",
                "title": "Three-part late-summer customer retention email sequence",
                "objective": "Write a 3-email Klaviyo win-back and VIP early-access sequence.",
                "scope": "Three campaign emails ($30.00).",
                "deliverable": "3-part retention email sequence (.docx).",
                "status": "delivered",
                "estimate_low": Decimal("30.00"),
                "estimate_high": Decimal("30.00"),
                "created_at": dt_utc(2026, 7, 23, 18, 20, 0),
                "deliverables": [
                    {
                        "title": "3-Part Late Summer Retention Email Sequence — Final (v2)",
                        "kind": "Email copy",
                        "status": "delivered",
                        "version": 2,
                        "notes": "Settled Jul 25, 2026 (QP-MS0VC5ELX1EJ, $30.00).",
                    }
                ],
            },
        ],
        "invoices": [
            {
                "key": "inv_lr_may",
                "number": "INV-260508-LR01",
                "request_key": "lr_may",
                "amount_due": Decimal("70.00"),
                "amount_paid": Decimal("70.00"),
                "status": "paid",
                "description": "Website / product copy — Spring launch descriptions & FAQ ($30 + $10 + $30)",
                "created_at": dt_utc(2026, 5, 8, 20, 30, 0),
                "due_at": dt_utc(2026, 5, 10, 20, 30, 0),
                "tx_refs": [
                    "QP-MOME7I4M0D4Z",
                    "QP-MOMJ3L3IZG7Q",
                    "QP-MOMJ3YSR920W",
                    "QP-MOMJ4JQEYJPK",
                    "QP-MOMJ4S43E9CP",
                    "QP-MOXDEYGTY769",
                ],
            },
            {
                "key": "inv_lr_july",
                "number": "QP2607-1F151BA1",
                "request_key": "lr_july",
                "amount_due": Decimal("30.00"),
                "amount_paid": Decimal("30.00"),
                "status": "paid",
                "description": "Website / product copy — 3-part late-summer Klaviyo email sequence",
                "created_at": dt_utc(2026, 7, 25, 21, 0, 0),
                "due_at": dt_utc(2026, 7, 27, 21, 0, 0),
                "tx_refs": ["QP-MS0VC5ELX1EJ"],
            },
        ],
        "messages": [
            (
                "client",
                dt_utc(2026, 7, 23, 18, 15, 0),
                "hey! back for another batch of emails :) attaching my rough notes for our 3 late-summer VIP drop emails. still $30 for the three of them?",
                ["lina_summer_campaign_emails_rough.docx"],
            ),
            (
                "admin",
                dt_utc(2026, 7, 23, 18, 32, 0),
                "Hey Lina! Yes, $30 for the 3-email sequence. Just posted invoice QP2607-1F151BA1.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 7, 25, 21, 16, 30),
                "so sorry for the delay, was out of town for a wedding! just paid the $30.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 7, 26, 15, 10, 0),
                "Here is v1 of the 3-part email sequence.",
                ["lina_summer_campaign_emails_v1.docx"],
            ),
            (
                "client",
                dt_utc(2026, 7, 27, 13, 40, 0),
                "love emails 1 and 2! on email 3 can we change the discount code from SUMMER15 to VIP15 so it matches what we set up in Shopify?",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 7, 27, 14, 15, 0),
                "Switched the code to VIP15 in Email #3. Here's the final Word file.",
                ["lina_summer_campaign_emails_final.docx"],
            ),
        ],
    },
    "patrickhyland04@gmail.com": {
        "username": "patrick_hyland",
        "first_name": "Patrick",
        "last_name": "Hyland",
        "channel": "Web search",
        "subject": "Newfoundland regional dispatch & fuel-surcharge Excel workbook",
        "status": "closed",
        "requests": [
            {
                "key": "ph_spring",
                "reference": "INF-260415-PH",
                "service_family": "studio",
                "service_code": "studio-technical",
                "title": "Spring regional freight rate tables and Excel formula updates",
                "objective": "Build and update regional carrier rate lookup sheets across March and April 2026.",
                "scope": "Three Excel builds across Mar 9 ($45), Mar 31 ($25), and Apr 15 ($55) = $125.00 total.",
                "deliverable": "Regional freight rate spreadsheets.",
                "status": "delivered",
                "estimate_low": Decimal("125.00"),
                "estimate_high": Decimal("125.00"),
                "created_at": dt_utc(2026, 3, 9, 18, 0, 0),
                "deliverables": [
                    {
                        "title": "Spring Regional Freight Rate Matrix & Dynamic Formula Tracker — Final (v1)",
                        "kind": "Rate Model",
                        "status": "delivered",
                        "version": 1,
                        "notes": "Delivered April 15, 2026.",
                    }
                ],
            },
            {
                "key": "ph_june",
                "reference": "INF-260627-PH",
                "service_family": "studio",
                "service_code": "studio-technical",
                "title": "Multi-tab Newfoundland dispatch and diesel fuel-surcharge tracker",
                "objective": "Automate per-kilometer carrier linehaul and weekly diesel surcharge calculations across Newfoundland routes.",
                "scope": "Expanded multi-tab Excel tracker ($90.00).",
                "deliverable": "Dispatch and fuel-surcharge workbook (.xlsx).",
                "status": "delivered",
                "estimate_low": Decimal("90.00"),
                "estimate_high": Decimal("90.00"),
                "created_at": dt_utc(2026, 6, 24, 19, 30, 0),
                "deliverables": [
                    {
                        "title": "Newfoundland Dispatch & Fuel-Surcharge Tracker — Final (KM)",
                        "kind": "Excel workbook",
                        "status": "delivered",
                        "version": 2,
                        "notes": "Settled Jun 27, 2026 via TD Canada Trust Visa Debit (QP-MQWYNHW6NBYG, $90.00).",
                    }
                ],
            },
        ],
        "invoices": [
            {
                "key": "inv_ph_spring",
                "number": "INV-260415-PH01",
                "request_key": "ph_spring",
                "amount_due": Decimal("125.00"),
                "amount_paid": Decimal("125.00"),
                "status": "paid",
                "description": "Technical production — Spring regional freight rate & formula sheets ($45 + $25 + $55)",
                "created_at": dt_utc(2026, 4, 15, 12, 35, 0),
                "due_at": dt_utc(2026, 4, 17, 12, 35, 0),
                "tx_refs": [
                    "QP-MMJIYNKE8A0Y",
                    "QP-MNF0TPG932UW",
                    "QP-MO01FHMFKKD6",
                    "QP-MO01KXRAB8TP",
                ],
            },
            {
                "key": "inv_ph_90",
                "number": "INV-260627-PH02",
                "request_key": "ph_june",
                "amount_due": Decimal("90.00"),
                "amount_paid": Decimal("90.00"),
                "status": "paid",
                "description": "Technical production — Multi-tab Newfoundland dispatch & diesel surcharge workbook",
                "created_at": dt_utc(2026, 6, 27, 22, 50, 0),
                "due_at": dt_utc(2026, 6, 29, 22, 50, 0),
                "tx_refs": [
                    "QP-MQTLZ0AJ5G2U",
                    "QP-MQTMRX5VZ647",
                    "QP-MQWVUVXISHS3",
                    "QP-MQWYNHW6NBYG",
                ],
            },
        ],
        "messages": [
            (
                "client",
                dt_utc(2026, 6, 24, 19, 25, 0),
                "Hey guys, attaching our raw St. John's to Corner Brook dispatch sheet. We need a fuel-surcharge lookup tab added to the $80 tracker we talked about.",
                ["patrick_newfoundland_dispatch_raw.xlsx"],
            ),
            (
                "admin",
                dt_utc(2026, 6, 25, 15, 10, 0),
                "Hey Patrick, adding the automated weekly diesel index tab brings it from $80 to $90 total.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 6, 27, 22, 59, 0),
                "sorry about the decline earlier, forgot to move funds over from savings. just cleared the $90 on apple pay.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 6, 28, 16, 20, 0),
                "Got the $90 payment. Here is v1 of the Dispatch & Fuel-Surcharge Tracker.",
                ["patrick_dispatch_and_fuel_tracker_v1.xlsx"],
            ),
            (
                "client",
                dt_utc(2026, 6, 29, 11, 15, 0),
                "Quick thing—the distance column in v1 converted our numbers to miles, we bill everything in kilometers here in Newfoundland. Can you switch the formula back to KM?",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 6, 29, 13, 5, 0),
                "Good catch! Switched the distance column and per-km surcharge multiplier back to kilometers. Here is the final workbook.",
                ["patrick_dispatch_and_fuel_tracker_final.xlsx"],
            ),
        ],
    },
    "lemburgcarter@gmail.com": {
        "username": "carter_lemburg",
        "first_name": "Carter",
        "last_name": "Lemburg",
        "channel": "Colleague referral",
        "subject": "Storefront collection copy & pre-launch checkout QA checklist",
        "status": "closed",
        "requests": [
            {
                "key": "cl_launch",
                "reference": "INF-260501-CL",
                "service_family": "communication",
                "service_code": "communication-audit",
                "title": "Storefront collection copy, email templates, and pre-launch QA checklist",
                "objective": "Write collection page copy and complete a 28-point Shopify pre-launch checklist across six weekly sprints.",
                "scope": "Six milestone payments between Apr 12 and May 8, 2026 ($290.00 total).",
                "deliverable": "Storefront copy deck and 28-point launch QA checklist (.pdf).",
                "status": "delivered",
                "estimate_low": Decimal("290.00"),
                "estimate_high": Decimal("290.00"),
                "created_at": dt_utc(2026, 4, 12, 23, 0, 0),
                "deliverables": [
                    {
                        "title": "Storefront Copy & 28-Point Pre-Launch QA Checklist — Final",
                        "kind": "Launch package",
                        "status": "delivered",
                        "version": 1,
                        "notes": "Settled across Apr 12 – May 8, 2026 (final balance QP-MOWUG2PHKDPF, $55.00).",
                    }
                ],
            }
        ],
        "invoices": [
            {
                "key": "inv_cl_290",
                "number": "INV-260508-CL01",
                "request_key": "cl_launch",
                "amount_due": Decimal("290.00"),
                "amount_paid": Decimal("290.00"),
                "status": "paid",
                "description": "Communication & QA — Storefront collection copy & launch checklist ($50+$40+$50+$50+$45+$55)",
                "created_at": dt_utc(2026, 5, 8, 11, 35, 0),
                "due_at": dt_utc(2026, 5, 10, 11, 35, 0),
                "tx_refs": [
                    "QP-MNWEF4X67DJE",
                    "QP-MNXRNWGE9H26",
                    "QP-MOJ7A8CV69VO",
                    "QP-MOL7PPPC2N24",
                    "QP-MOMLUWW8QVJU",
                    "QP-MOWUG2PHKDPF",
                ],
            }
        ],
        "messages": [
            (
                "client",
                dt_utc(2026, 5, 1, 7, 38, 0),
                "Here are the notes for our final collection pages and the pre-launch Shopify checklist. Paid the $45 milestone on Apple Pay.",
                ["carter_storefront_launch_notes.docx"],
            ),
            (
                "client",
                dt_utc(2026, 5, 8, 11, 41, 0),
                "Just sent the final $55 balance on Apple Pay too.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 5, 8, 16, 20, 0),
                "Thanks Carter, all 6 milestones ($290 total) are settled. Here is the completed Storefront Copy & 28-Point Pre-Launch QA Checklist PDF.",
                ["carter_website_launch_checklist_final.pdf"],
            ),
        ],
    },
    "issabelc207@gmail.com": {
        "username": "issa_cuevas",
        "first_name": "Issa",
        "last_name": "Cuevas",
        "channel": "Audrey Brown referral",
        "subject": "Pediatric speech clinic intake agreement, parent disclosure forms, and HIPAA consent pack ($240)",
        "status": "closed",
        "requests": [
            {
                "key": "ic_intake",
                "reference": "INF-261020-IC",
                "service_family": "studio",
                "service_code": "studio-technical",
                "title": "Pediatric speech clinic intake agreement, parent disclosure forms, and HIPAA consent pack",
                "objective": "Draft comprehensive clinical service agreements, parent fee disclosures, cancellation policies, and HIPAA-compliant consent documents for pediatric speech therapy practice.",
                "scope": "Four specialized clinical documents: Master Clinical Service Agreement, Parent Financial & Cancellation Disclosure, HIPAA Teletherapy & In-Clinic Consent, and Intake Encounter Scripts ($240.00 total).",
                "deliverable": "Clinical agreement and parent intake documentation pack (.docx & .pdf).",
                "status": "delivered",
                "estimate_low": Decimal("240.00"),
                "estimate_high": Decimal("240.00"),
                "created_at": dt_utc(2026, 10, 6, 14, 15, 0),
                "deliverables": [
                    {
                        "title": "Pediatric Clinical Intake & Consent Agreement — Final (v2)",
                        "kind": "Clinical Documentation",
                        "status": "delivered",
                        "version": 2,
                        "notes": "Settled Oct 20, 2026 (T267443039046790) and delivered Oct 20, 2026.",
                    },
                    {
                        "title": "Parent Communication & Cancellation Policy Templates — Final",
                        "kind": "Practice Templates",
                        "status": "delivered",
                        "version": 1,
                        "notes": "Delivered Oct 20, 2026.",
                    },
                ],
            },
        ],
        "invoices": [
            {
                "key": "inv_ic_240",
                "number": "INV-261020-IC01",
                "request_key": "ic_intake",
                "amount_due": Decimal("240.00"),
                "amount_paid": Decimal("240.00"),
                "status": "paid",
                "description": "Technical documentation — Pediatric speech clinic intake agreement, parent disclosure forms, and HIPAA consent pack",
                "created_at": dt_utc(2026, 10, 20, 17, 30, 0),
                "due_at": dt_utc(2026, 10, 22, 17, 30, 0),
                "tx_refs": ["T083852538976491", "T267443039046790"],
            },
        ],
        "messages": [
            (
                "client",
                dt_utc(2026, 10, 6, 14, 15, 0),
                "Hey! Audrey Brown told me you guys overhauled her studio website and booking flow copy and saved her so much headache, so she told me I had to reach out to you. I run Cuevas Speech & Language Therapy here in Austin, and our intake paperwork is a complete mess right now. Parents are constantly confused by our cancellation policy and our HIPAA disclosures are outdated. Here is the draft Word file we've been trying to piece together—can you quote me to turn this into a professional clinical intake agreement, parent disclosure form, and communication templates?",
                ["cuevas_intake_and_consent_draft_messy.docx"],
            ),
            (
                "admin",
                dt_utc(2026, 10, 6, 15, 40, 0),
                "Hi Issa, thanks for reaching out, and glad to hear Audrey's booking flow is working so well! Reviewed your draft file. We can turn this into a comprehensive 4-part clinical pack: Master Clinical Service Agreement, Parent Financial & Cancellation Disclosure, HIPAA & Teletherapy Consent, and 3 parent communication scripts. That's $240 total for the full package (posted reference INF-261020-IC).",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 7, 8, 30, 0),
                "That price works as long as you can guarantee this will be legally sound and specific to pediatric practices. Do not use generic medical templates. Our therapists deal with non-verbal kids and sensory integration, so the consent clauses need to explicitly cover observation mirrors and parent video recording for home exercises. When will I see the first draft?",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 7, 11, 20, 0),
                "Understood completely. We tailor clinical terms directly to therapy practices, including explicit clauses for parent observation, teletherapy video authorization, and sensory therapy safety disclosures. We'll have v1 ready for your review by Friday.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 9, 19, 45, 0),
                "Just checking on this. It's Friday evening and I haven't seen the draft in my portal yet. I have a staff meeting Monday morning and need to review this beforehand.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 9, 20, 15, 0),
                "Here is v1 of the Pediatric Clinical Intake & Consent Agreement. It includes all specialized observation clauses, HIPAA consents, and parent financial disclosure terms.",
                ["cuevas_pediatric_intake_and_consent_v1.docx"],
            ),
            (
                "client",
                dt_utc(2026, 10, 11, 11, 15, 0),
                "I went through v1 line by line with my lead pathologist. You have a lot of work to do.\n1. Page 2 is completely unacceptable. You wrote 'late cancellations incur a $50 administrative charge'—in clinical therapy that will trigger insurance audit pushback. It MUST read 'Unscheduled missed sessions without 24-hour advance written notice are subject to the reserved clinical hour fee of $75'.\n2. Why did you use the word 'patient' on line 14 and 'client' on line 28? We treat pediatric patients, but parents are the legal guarantors. Keep the legal terms strict throughout.\n3. Add a clear disclaimer on page 3 that progress evaluations are clinical estimates and not guaranteed medical outcomes.\nFix these and send me a revised version.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 12, 14, 10, 0),
                "Thanks for the exact phrasing, Issa. You're completely right on the clinical hour designation for insurance clarity, and distinguishing pediatric patient from parent guarantor eliminates any legal ambiguity. Integrating those updates now along with the progress evaluation disclaimer.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 14, 16, 30, 0),
                "Did you finish those edits yet? Also don't forget the parent communication emails you promised in the scope. I need those templates for our intake coordinator.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 15, 12, 45, 0),
                "Here is v2 of the Clinical Intake Agreement incorporating all three revisions: strict patient/guarantor designations, the $75 reserved clinical hour term, and the progress evaluation disclaimer. Attached alongside is the Parent Communication Templates deck with all 3 intake and fee scripts.",
                ["cuevas_pediatric_intake_and_consent_final.docx", "cuevas_parent_communication_templates.docx"],
            ),
            (
                "client",
                dt_utc(2026, 10, 17, 9, 12, 0),
                "The cancellation clause and guarantor terms are much better now. However, under Section 4 on the communication deck, can you add a sentence explaining that superbills for out-of-network reimbursement are generated on the 1st of each month? Once that's in, we should be ready for the final PDF.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 17, 14, 30, 0),
                "Added the superbill 1st-of-month generation schedule to both the intake agreement and the parent welcome email script. All clauses are locked.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 20, 17, 15, 0),
                "Okay where do I pay? I need to get this off my to-do list before my 7pm patient.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 20, 17, 30, 0),
                "We are actually experiencing a temporary sync issue with our normal payment route at the moment; our payment gateway is running an internal maintenance cycle. We'll share the direct link with you shortly once it clears.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 20, 17, 42, 0),
                "Are you serious? Why didn't you mention that earlier? Is my delivery going to be delayed because of this? I have a new speech pathologist starting clinical intake on Monday and parents need to sign this paperwork before their morning sessions. I can't wait around for IT issues.",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 20, 18, 10, 0),
                "Completely understand the urgency Issa, and apologize for the inconvenience. The cleared route is live right now: https://paystack.shop/pay/tx0ipp9eg4. As soon as that clears, the final binder-ready PDF will unlock immediately.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 20, 18, 24, 55),
                "Trying my card now... Ugh, the form dropped the connection on my autofill. Let me switch to Apple Pay.",
                [],
            ),
            (
                "client",
                dt_utc(2026, 10, 20, 18, 25, 40),
                "Alright Apple Pay went through. $240 paid. Where are my clean Word docs?",
                [],
            ),
            (
                "admin",
                dt_utc(2026, 10, 20, 18, 28, 10),
                "Payment received, thank you Issa! Here is the final binder-ready PDF with all clinical signature blocks, plus the final editable Word decks.",
                ["cuevas_speech_clinic_service_agreement_final.pdf"],
            ),
            (
                "client",
                dt_utc(2026, 10, 20, 18, 42, 0),
                "Got them downloaded. The clause formatting on page 3 looks much cleaner now. Thank you for turning it around so fast—I'll let Audrey know you survived my revisions lol.",
                [],
            ),
        ],
    },
}

EMAIL_ALIAS_TO_PRIMARY = {
    "estellawilliams06@gmail.com": "stellarae147@gmail.com",
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
            "T083852538976491": {
                "Reference": "T083852538976491",
                "Transaction Date": "Oct 20th, 2026 06:24:55 PM",
                "Customer (email)": "issabelc207@gmail.com",
                "Amount Paid": "240",
                "Paystack Fees": "0",
                "Total Fees": "0",
                "Amount Due": "240.00",
                "Settlement Date": "",
                "Gateway Response": "The transaction was not completed",
                "Customer (fullname)": "Issa cuevas",
                "Transaction ID": "6678711423",
                "Card Type": "",
                "Card Bank": "",
                "Country Code": "",
                "Currency": "USD",
                "Subaccount": "",
                "Subaccount Amount Due": "",
                "Source": "checkout",
                "Source Identifier": "",
                "Status": "abandoned",
                "Channel": "card",
                "Requested Amount": "240",
                "Card Authentication Type": "Unknown",
                "Receipt Number": "",
            },
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

            inv_obj = None
            csv_inv_num = (row.get("Invoice") or "").strip()
            if ref in ADDITIONAL_TX_DESCRIPTIONS and raw_status == "success":
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
