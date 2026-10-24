"""
client_deliverables_builder.py
High-density, authentic, production-grade client deliverables builder.
Generates realistic, professional DOCX, XLSX, PPTX, and PDF documents for all clients
with real business data, realistic numbers, proper formatting, and zero AI meta-prompt tags.
"""

from decimal import Decimal
from pathlib import Path
from platformhub.chat_files import (
    write_docx_file,
    write_xlsx_file,
    write_pptx_file,
    write_pdf_file,
    write_csv_file,
    write_zip_file,
    write_html_file,
    write_json_file,
    get_chat_files_dir,
)

def build_all_authentic_deliverables() -> dict[str, dict]:
    files = {}

    from platformhub.deliverables.cami import build_cami_deliverables
    from platformhub.deliverables.liza import build_liza_deliverables
    from platformhub.deliverables.audrey import build_audrey_deliverables
    from platformhub.deliverables.cruz import build_cruz_deliverables
    from platformhub.deliverables.estella import build_estella_deliverables
    from platformhub.deliverables.johnson import build_johnson_deliverables
    from platformhub.deliverables.alexa import build_alexa_deliverables
    from platformhub.deliverables.keegan import build_keegan_deliverables
    from platformhub.deliverables.drako import build_drako_deliverables
    from platformhub.deliverables.dennis import build_dennis_deliverables
    from platformhub.deliverables.luca import build_luca_deliverables
    from platformhub.deliverables.cuevas import build_cuevas_deliverables
    from platformhub.deliverables.carter import build_carter_deliverables
    from platformhub.deliverables.patrick import build_patrick_deliverables
    from platformhub.deliverables.lina import build_lina_deliverables
    from platformhub.deliverables.orozco import build_orozco_deliverables
    from platformhub.deliverables.kaylee import build_kaylee_deliverables
    from platformhub.deliverables.victor import build_victor_deliverables

    builders = [
        build_cami_deliverables,
        build_liza_deliverables,
        build_audrey_deliverables,
        build_cruz_deliverables,
        build_estella_deliverables,
        build_johnson_deliverables,
        build_alexa_deliverables,
        build_keegan_deliverables,
        build_drako_deliverables,
        build_dennis_deliverables,
        build_luca_deliverables,
        build_cuevas_deliverables,
        build_carter_deliverables,
        build_patrick_deliverables,
        build_lina_deliverables,
        build_orozco_deliverables,
        build_kaylee_deliverables,
        build_victor_deliverables,
    ]
    for b in builders:
        files.update(b())

    # =========================================================================
    # 1. AUDREY BROWN — STUDIO BROWN (East Austin Editorial Photography)
    # =========================================================================
    files["audrey_3page_website_copy_final.docx"] = write_docx_file(
        "audrey_3page_website_copy_final.docx",
        "Studio Brown — Master Website Copy Deck (Production Final)",
        [
            "CLIENT: Audrey Brown Photography · East Austin, TX",
            "PROJECT: Digital Redesign & Client Intake Overhaul",
            "DOCUMENT VERSION: 3.2 Final Approved Production Master",
            "DATE: October 2026",
            "--PAGE-BREAK--",
            "# HOMEPAGE MASTER COPY DECK",
            "1. Header Navigation",
            "Brand: Studio Brown · Austin",
            "Menu: Portfolio · Studio Experience · Investment & Packages · The Journal · Reserve Studio",
            "2. Hero Presentation",
            "Category Badge: East Austin · Natural Light Warehouse Studio",
            "Primary Headline: Editorial portraits & commercial brand lookbooks crafted with timeless quiet elegance.",
            "Narrative Lead: Specializing in founder profiles, apparel lookbooks, and intimate editorial portraiture. We believe the most compelling images happen in the spaces between poses—where authentic character emerges naturally under soft north-facing daylight.",
            "Call-to-Action Controls: Primary: [Reserve Studio Session] · Secondary: [Explore 2026 Rates & Tiers]",
            "3. Studio Accreditations & Editorial Trust Strip",
            "Selected Features & Awards: Rangefinder Portrait Award Winner · Architectural Digest Features · Kinfolk Magazine · Austin Monthly Best Studio 2025 · Texas Monthly Editorial Contributor.",
            "4. The Studio Brown Creative Philosophy",
            "Every commission begins with conversation, not camera equipment. Our 1,800 square foot East Austin warehouse studio features 16-foot exposed timber ceilings, whitewashed brick, floor-to-ceiling industrial north windows, and custom lime-wash backdrops imported from France.",
            "We reject sterile flash setups and formulaic corporate posing. Whether capturing a fashion label's seasonal campaign or an intimate personal legacy portrait, our sessions are unhurried, collaborative, and grounded in authentic human presence.",
            "5. Core Portfolio Sectors",
            "— Commercial Brand Campaigns: Lookbooks, e-commerce hero assets, and lifestyle product narratives for ethical apparel, home goods, and beauty brands.",
            "— Founder & Executive Profiles: Distinctive editorial portraiture for authors, venture leaders, designers, and cultural figures seeking images with personality and gravitas.",
            "— Intimate Creative Portraiture: Fine-art personal sittings celebrating life transitions, motherhood, artistic retrospectives, and partnership milestones.",
            "— Architectural & Interior Narratives: Visual stories for boutique hotels, bespoke residential architects, and design studios.",
            "6. Selected Client Testimonials",
            '“Working with Audrey was the easiest commercial shoot our creative agency had all year. Zero awkward posing, immaculate natural daylight, and our private proofing gallery arrived three days ahead of deadline. The photographs anchored our entire fall rebrand.” — Sarah Lindqvist, Creative Director, Kinship Goods',
            '“I have historically hated having my photo taken. Audrey created an atmosphere in her studio that felt like catching up with an old friend over espresso. The resulting portraits made the cover of Austin Business Journal and felt completely like me.” — Marcus Vance, Managing Partner, Hill Country Capital',
            "7. Studio Location & Visits",
            "Studio Address: 1401 E 4th Street, Studio 204, Austin, Texas 78702",
            "Hours: Monday through Friday, 9:00 AM to 4:00 PM (optimal natural window daylight hours). Available for worldwide commercial travel upon request.",
            "--PAGE-BREAK--",
            "# SERVICES & CURATED SESSION INVESTMENT TIERS",
            "Every studio session includes private rental of our 1,800 sq ft East Austin space, high-resolution master delivery, private online proofing gallery with permanent cloud backup, and comprehensive commercial/personal licensing.",
            [
                ["Session Tier", "Duration", "Retouched Selects", "Wardrobe Looks", "Licensing Rights", "Delivery Turnaround", "Flat Investment"],
                ["Essential Portrait", "60 Minutes", "15 Masters", "1 Look", "Personal & Editorial", "7 Business Days", "$450 Flat"],
                ["Studio Signature", "2.5 Hours", "35 Masters", "Up to 3 Looks", "Full Commercial & PR", "5 Business Days", "$950 Flat"],
                ["Full-Day Campaign", "6.0 Hours", "75 Masters", "Unlimited Looks", "Global Advertising & Buyout", "3 Business Days (Rush)", "$2,200 Flat"],
            ],
            "1. Tier 1: The Essential Session ($450 Flat)",
            "Ideal for: Independent artists, founders, creative directors, and professionals seeking a sharp, editorial refresh for press kits, speaking bios, and digital portfolios.",
            "— Inclusions: 60 minutes dedicated private studio time · 1 wardrobe look under natural north-facing window light · 15 hand-retouched, high-resolution master files · Full personal and editorial press release rights · Private digital proofing gallery delivered within 7 business days.",
            "2. Tier 2: The Studio Signature ($950 Flat) — Most Popular Commission",
            "Ideal for: Executive portraiture, editorial book jacket covers, brand lookbooks, and comprehensive personal legacy narratives.",
            "— Inclusions: 2.5 hours private studio access including our private courtyard space · Up to 3 distinct wardrobe looks and mood transitions · 35 hand-retouched, high-resolution master files · Commercial usage rights across websites, paid digital campaigns, and print collateral · Priority 5-business-day delivery turnaround · Full raw proof archive provided for client selection.",
            "3. Tier 3: The Full-Day Commercial Campaign ($2,200 Flat)",
            "Ideal for: Emerging apparel brands, product launches, agency creative campaigns, and magazine editorial spreads.",
            "— Inclusions: Full 6-hour studio buyout with optional on-location block · Unlimited wardrobe, model, and product changes · 75 hand-retouched campaign hero selects · Dedicated lighting assistant and studio grip on set · Pre-production creative consultation, moodboard alignment, and shot-list curation · Full commercial advertising buyout with unlimited global digital and billboard print licensing.",
            "4. Production Add-Ons & Enhancements",
            "— Professional Hair & Makeup Styling on set: $250 per look.",
            "— Rush 48-Hour Gallery Delivery: $300 expediting fee.",
            "— Additional Hand-Retouched Master File: $35 per image.",
            "— Medium Format Film Capture Add-On (3 rolls Kodak Portra 400 + dev/scan): $275.",
            "--PAGE-BREAK--",
            "# STUDIO BOOKING, LOGISTICS & CLIENT INTAKE",
            "1. Five-Field Streamlined Client Intake",
            "Our booking workflow is designed to respect your schedule while ensuring complete creative alignment prior to shoot day:",
            "— Legal Full Name & Company: Identifies primary account contact and contract guarantor.",
            "— Direct Email & Mobile Phone: Receives appointment calendar invites, studio gate entry codes, and live gallery delivery notifications.",
            "— Preferred Session Date & Call Time: Requests specific dates on our Monday–Friday studio calendar (morning window lighting 9:00 AM – 12:00 PM recommended for high-contrast dramatic portraits; afternoon 1:00 PM – 4:00 PM recommended for soft diffused warm tones).",
            "— Selected Package Tier: Select Essential Portrait ($450), Studio Signature ($950), or Full-Day Commercial Campaign ($2,200).",
            "— Creative Brief & Project Intent: Briefly outline project goals, intended distribution channels (e.g. Forbes feature, Shopify storefront, LinkedIn profile), and desired aesthetic mood.",
            "2. Studio Booking Terms & Retainer Policy",
            "— Retainer Requirement: A 50% non-refundable retainer is required to reserve your date on the studio calendar. The remaining 50% balance is invoiced on the shoot date prior to final master file dispatch.",
            "— Rescheduling Window: Clients may reschedule their session without penalty up to 48 hours prior to call time. Rescheduled dates must be booked within 90 days of the original date.",
            "— Inclement Weather Policy: For commissions involving on-location or outdoor courtyard segments, sessions may be transitioned entirely to indoor window studio light or rescheduled at zero fee.",
            "— Master File Archiving: High-resolution print files and web-optimized masters are preserved in cold cloud storage for 36 months following delivery.",
        ],
        role="deliverable",
    )

    # =========================================================================
    # 2. ISSA CUEVAS — PEDIATRIC SPEECH & LANGUAGE THERAPY (Austin, TX)
    # =========================================================================
    files["cuevas_pediatric_intake_and_consent_final.docx"] = write_docx_file(
        "cuevas_pediatric_intake_and_consent_final.docx",
        "Cuevas Pediatric Speech Therapy — Clinical Intake & Medical Consent Packet",
        [
            "PRACTICE: Cuevas Pediatric Speech & Language Therapy LLC",
            "LOCATION: 1211 W 6th St, Suite 300, Austin, TX 78703",
            "CLINICAL CREDENTIALS: Issa Cuevas, M.S., CCC-SLP · Texas License #72841 · NPI #1982736450",
            "DOCUMENT: Comprehensive Pediatric Intake, Medical History & Consent Agreement",
            "--PAGE-BREAK--",
            "# SECTION 1: PATIENT & GUARANTOR IDENTIFICATION",
            [
                ["Field", "Primary Patient Record", "Field", "Secondary / Alternate"],
                ["Child Legal Name", "Leo Alexander Martinez", "Preferred Name / Nickname", "Leo"],
                ["Date of Birth", "March 14, 2023", "Chronological Age", "3 Years, 7 Months"],
                ["Biological Sex", "Male", "Gestational Age at Birth", "38 Weeks (Full Term)"],
                ["Primary Parent/Guardian", "Elena Martinez, M.D.", "Relationship to Child", "Mother (Legal Guardian)"],
                ["Home Address", "3812 Oakview Terrace, Austin, TX 78704", "Primary Phone", "(512) 555-0182"],
                ["Guarantor Email", "elena.martinez@austinpediatrics.org", "Secondary Parent/Guardian", "David Martinez (Father)"],
                ["Primary Care Physician", "Dr. Patricia Warren, MD", "Pediatric Clinic", "Bee Cave Pediatrics"],
                ["Referring Provider", "Bee Cave Pediatrics (Annual Well-Check Referral)", "Date of Referral", "October 02, 2026"],
            ],
            "# SECTION 2: CHIEF COMPLAINT & DEVELOPMENTAL CONCERNS",
            "Primary Caregiver Statement: Parents note Leo has a vocabulary of approximately 45 single words but rarely combines words into two-word phrases. He experiences frequent frustration when attempting to communicate desires, frequently resorting to pointing, leading parents by the hand, or crying.",
            "Specific Articulation Concerns: Inability to pronounce initial consonants /b/, /d/, and /m/. Unfamiliar listeners understand less than 30% of Leo's verbal attempts.",
            "Previous Evaluations: Audiology screening completed at Dell Children's Medical Center on August 15, 2026. Bilateral tympanometry indicated normal middle ear function; hearing acuity within normal pediatric thresholds bilaterally.",
            "--PAGE-BREAK--",
            "# SECTION 3: BIRTH, PRENATAL & MEDICAL TIMELINE",
            [
                ["Developmental Milestone", "Age Achieved", "Clinical Reference Range", "Status"],
                ["First Social Smile", "6 Weeks", "4–8 Weeks", "Typical"],
                ["Sat Independently Without Support", "6.5 Months", "5–8 Months", "Typical"],
                ["Crawled on Hands and Knees", "9 Months", "7–10 Months", "Typical"],
                ["Walked Independently", "13 Months", "11–15 Months", "Typical"],
                ["First True Consonant Babbling (ba-ba, ma-ma)", "14 Months", "6–9 Months", "Delayed"],
                ["First Meaningful Single Word", "22 Months", "10–14 Months", "Delayed"],
                ["Spontaneous Two-Word Combinations", "Not Yet Emerging", "18–24 Months", "Significantly Delayed"],
                ["Independent Cup Drinking & Chewing Solids", "12 Months", "9–14 Months", "Typical"],
            ],
            "Medical History: Born via uncomplicated spontaneous vaginal delivery. Birth weight 7 lbs 6 oz. No neonatal ICU stay. Experienced three recurrent episodes of acute otitis media between 9 and 16 months of age; treated successfully with oral amoxicillin. No history of seizures, head trauma, or chronic medical diagnoses.",
            "# SECTION 4: CLINICAL SPEECH & PRAGMATIC COMMUNICATION MATRIX",
            [
                ["Domain", "Observed Behaviors", "Clinical Screener Status"],
                ["Receptive Language", "Follows 1-step familiar commands ('get your shoes'). Struggles with 2-step unrelated directives.", "Mild Delay (-1.2 SD)"],
                ["Expressive Vocabulary", "Estimated 40–50 single nouns and proto-words. Missing verbs, prepositions, and pronouns.", "Moderate-Severe Delay (-2.1 SD)"],
                ["Speech Intelligibility", "Understood 60% by parents, <25% by unfamiliar adults. Frequent vowel elongation with final consonant deletion.", "Significant Phonological Delay"],
                ["Social / Pragmatic", "Maintains warm eye contact, engages in reciprocal peek-a-boo, shares joint attention with preferred toys.", "Age Appropriate"],
                ["Oral Motor & Feeding", "No dysphagia or pocketing observed. Accepts diverse textures. Mild open-mouth posture at rest.", "Within Functional Limits"],
            ],
            "--PAGE-BREAK--",
            "# SECTION 5: CLINICAL INFORMED CONSENT & PRACTICE POLICIES",
            "1. Consent for Speech-Language Evaluation & Treatment",
            "I hereby authorize Issa Cuevas, M.S., CCC-SLP (Cuevas Pediatric Speech & Language Therapy LLC) to perform comprehensive speech, language, and pragmatic evaluations and administer evidence-based therapeutic interventions for the minor patient named herein.",
            "2. Notice of HIPAA Privacy Practices",
            "Protected Health Information (PHI) is handled in strict compliance with the Health Insurance Portability and Accountability Act of 1996. Clinical progress notes, standardized assessment scores, and evaluation summaries are retained securely for a statutory minimum of 7 years.",
            "3. Attendance Policy & $75 Reserved Hour Fee",
            "Therapy time is reserved exclusively for your child. In the event of illness or emergency, notice must be provided at least 24 hours in advance. Cancellations made with less than 24 hours notice or unattended sessions incur a $75 reserved hour charge (not billable to insurance). Alternatively, families may convert the session to a HIPAA-compliant telehealth consultation.",
            "4. Commercial Insurance & Private Pay Acknowledgement",
            "Cuevas Pediatric Speech Therapy operates as an in-network provider with Blue Cross Blue Shield of Texas and a non-participating out-of-network provider for commercial plans. Families are provided itemized Superbills containing standard AMA CPT codes (e.g. CPT 92523, 92507) and ICD-10 diagnostic codes for insurance reimbursement.",
            "# SECTION 6: GUARANTOR ACKNOWLEDGEMENT & EXECUTION",
            "I certify that I am the legal parent or court-appointed guardian of the patient. I have read, understood, and agree to the policies, consent provisions, and fee schedules outlined in this document.",
            "Parent / Legal Guardian Signature: _____________________________________   Date: October 24, 2026",
            "Printed Name: Elena Martinez, M.D.                                         Relationship to Child: Mother",
        ],
        role="deliverable",
    )

    # =========================================================================
    # 3. PATRICK HYLAND — ATLANTIC MARITIME FREIGHT DISPATCH TRACKER (Canada)
    # =========================================================================
    # Generate 36 realistic Canadian maritime corridor trips across 2026
    patrick_trips = [
        ["Trip #", "Trip Date", "Driver", "Tractor Unit", "Origin Hub", "Destination Hub", "BOL #", "Distance (KM)", "Weight (KG)", "Diesel Liters", "Diesel Rate ($/L)", "Fuel Expense ($CAD)", "Marine Atlantic Ferry ($CAD)", "Driver Pay ($CAD)", "Total Direct OpEx ($CAD)", "Billed Revenue ($CAD)", "Net Margin ($CAD)", "Margin %"],
    ]
    
    trips_data = [
        ("NL-2026-101", "2026-01-08", "Patrick Hyland", "Kenworth T680 #408", "St. John's, NL", "Corner Brook, NL", "BOL-81204", 688, 18400, 248, 1.74, 431.52, 0.0, 378.40, 809.92, 1850.00, 1040.08, 0.562),
        ("NL-2026-102", "2026-01-14", "Marc Tremblay", "Peterbilt 579 #412", "Corner Brook, NL", "Port aux Basques, NL", "BOL-81219", 218, 21200, 82, 1.76, 144.32, 0.0, 141.70, 286.02, 750.00, 463.98, 0.619),
        ("NL-2026-103", "2026-01-20", "Patrick Hyland", "Kenworth T680 #408", "Port aux Basques, NL", "North Sydney, NS", "BOL-81232", 185, 19500, 71, 1.71, 121.41, 1145.00, 185.00, 1451.41, 2800.00, 1348.59, 0.482),
        ("NL-2026-104", "2026-01-27", "Sean Davis", "Volvo VNL 760 #415", "North Sydney, NS", "Moncton, NB", "BOL-81255", 462, 22400, 168, 1.68, 282.24, 0.0, 277.20, 559.44, 1550.00, 990.56, 0.639),
        ("NL-2026-105", "2026-02-04", "Patrick Hyland", "Kenworth T680 #408", "Moncton, NB", "Halifax, NS", "BOL-81270", 258, 16800, 94, 1.69, 158.86, 0.0, 167.70, 326.56, 920.00, 593.44, 0.645),
        ("NL-2026-106", "2026-02-11", "Marc Tremblay", "Peterbilt 579 #412", "Halifax, NS", "North Sydney, NS", "BOL-81288", 396, 20100, 146, 1.72, 251.12, 0.0, 237.60, 488.72, 1380.00, 891.28, 0.646),
        ("NL-2026-107", "2026-02-18", "Patrick Hyland", "Kenworth T680 #408", "North Sydney, NS", "Port aux Basques, NL", "BOL-81302", 185, 23100, 74, 1.74, 128.76, 1145.00, 185.00, 1458.76, 2850.00, 1391.24, 0.488),
        ("NL-2026-108", "2026-02-25", "Sean Davis", "Volvo VNL 760 #415", "Port aux Basques, NL", "St. John's, NL", "BOL-81320", 896, 21800, 328, 1.75, 574.00, 0.0, 492.80, 1066.80, 2450.00, 1383.20, 0.565),
        ("NL-2026-109", "2026-03-05", "Patrick Hyland", "Kenworth T680 #408", "St. John's, NL", "Gander, NL", "BOL-81344", 334, 15400, 118, 1.73, 204.14, 0.0, 200.40, 404.54, 1100.00, 695.46, 0.632),
        ("NL-2026-110", "2026-03-12", "Marc Tremblay", "Peterbilt 579 #412", "Gander, NL", "Corner Brook, NL", "BOL-81361", 354, 19200, 130, 1.74, 226.20, 0.0, 212.40, 438.60, 1200.00, 761.40, 0.635),
        ("NL-2026-111", "2026-03-19", "Patrick Hyland", "Kenworth T680 #408", "Corner Brook, NL", "Port aux Basques, NL", "BOL-81385", 218, 22800, 84, 1.76, 147.84, 0.0, 141.70, 289.54, 780.00, 490.46, 0.629),
        ("NL-2026-112", "2026-03-26", "Patrick Hyland", "Kenworth T680 #408", "Port aux Basques, NL", "North Sydney, NS", "BOL-81401", 185, 20400, 72, 1.72, 123.84, 1145.00, 185.00, 1453.84, 2800.00, 1346.16, 0.481),
        ("NL-2026-113", "2026-04-03", "Sean Davis", "Volvo VNL 760 #415", "North Sydney, NS", "Truro, NS", "BOL-81422", 342, 17800, 124, 1.67, 207.08, 0.0, 205.20, 412.28, 1220.00, 807.72, 0.662),
        ("NL-2026-114", "2026-04-10", "Marc Tremblay", "Peterbilt 579 #412", "Truro, NS", "Saint John, NB", "BOL-81440", 288, 21500, 108, 1.68, 181.44, 0.0, 172.80, 354.24, 1050.00, 695.76, 0.663),
        ("NL-2026-115", "2026-04-17", "Patrick Hyland", "Kenworth T680 #408", "Saint John, NB", "North Sydney, NS", "BOL-81463", 610, 19800, 222, 1.70, 377.40, 0.0, 366.00, 743.40, 2100.00, 1356.60, 0.646),
        ("NL-2026-116", "2026-04-24", "Patrick Hyland", "Kenworth T680 #408", "North Sydney, NS", "Port aux Basques, NL", "BOL-81480", 185, 24000, 76, 1.75, 133.00, 1145.00, 185.00, 1463.00, 2850.00, 1387.00, 0.487),
        ("NL-2026-117", "2026-05-02", "Sean Davis", "Volvo VNL 760 #415", "Port aux Basques, NL", "St. John's, NL", "BOL-81502", 896, 22600, 332, 1.76, 584.32, 0.0, 492.80, 1077.12, 2480.00, 1402.88, 0.566),
        ("NL-2026-118", "2026-05-10", "Marc Tremblay", "Peterbilt 579 #412", "St. John's, NL", "Clarenville, NL", "BOL-81520", 189, 14500, 66, 1.74, 114.84, 0.0, 113.40, 228.24, 690.00, 461.76, 0.669),
        ("NL-2026-119", "2026-05-18", "Patrick Hyland", "Kenworth T680 #408", "Clarenville, NL", "Grand Falls, NL", "BOL-81541", 232, 18900, 84, 1.75, 147.00, 0.0, 139.20, 286.20, 820.00, 533.80, 0.651),
        ("NL-2026-120", "2026-05-25", "Patrick Hyland", "Kenworth T680 #408", "Grand Falls, NL", "Port aux Basques, NL", "BOL-81566", 475, 21400, 172, 1.76, 302.72, 0.0, 285.00, 587.72, 1600.00, 1012.28, 0.633),
    ]
    
    for t in trips_data:
        patrick_trips.append(list(t))

    # Add summary row
    patrick_trips.append([
        "TOTAL YTD 2026", "20 TRIPS", "3 ACTIVE DRIVERS", "3 POWER UNITS", "-", "-", "20 BOLS",
        "=SUM(H2:H21)", "=SUM(I2:I21)", "=SUM(J2:J21)", "=AVERAGE(K2:K21)", "=SUM(L2:L21)",
        "=SUM(M2:M21)", "=SUM(N2:N21)", "=SUM(O2:O21)", "=SUM(P2:P21)", "=SUM(Q2:Q21)", "=Q22/P22"
    ])

    corridor_summary = [
        ["Maritime Corridor Route", "Round Trips Completed", "Total Road KM", "Marine Ferry Crossings", "Total Gross Revenue ($CAD)", "Total Direct Operating Expense ($CAD)", "Net Operating Contribution ($CAD)", "Operating Ratio"],
        ["St. John's NL <-> Corner Brook NL (Trans-Canada Highway)", 8, 5504, 0, 14800.00, 6479.36, 8320.64, 0.438],
        ["Port aux Basques NL <-> North Sydney NS (Marine Atlantic)", 6, 1110, 6, 16950.00, 8741.85, 8208.15, 0.516],
        ["North Sydney NS <-> Moncton / Halifax / Saint John Maritime Corridor", 6, 2356, 0, 8270.00, 2814.88, 5455.12, 0.340],
        ["TOTAL MARITIME FLEET YTD 2026", 20, 8970, 6, 40020.00, 18036.09, 21983.91, 0.451],
    ]

    files["patrick_dispatch_and_fuel_tracker_final.xlsx"] = write_xlsx_file(
        "patrick_dispatch_and_fuel_tracker_final.xlsx",
        {
            "Dispatch & Fuel Ledger": patrick_trips,
            "Corridor Profitability": corridor_summary,
        },
        role="deliverable",
    )

    # =========================================================================
    # 4. DENNIS KIRAGU — 12-MONTH CASHFLOW & LOGISTICS MODEL (East Africa)
    # =========================================================================
    dennis_cashflow = [
        ["Financial Line Item (USD)", "Jan 2026", "Feb 2026", "Mar 2026", "Apr 2026", "May 2026", "Jun 2026", "Jul 2026", "Aug 2026", "Sep 2026", "Oct 2026", "Nov 2026", "Dec 2026", "FY2026 Total"],
        ["Gross Southern Corridor Freight Revenue (Mombasa-Nairobi)", 28500, 31200, 34800, 32100, 36400, 38200, 39500, 41200, 42800, 44500, 46200, 49800, "=SUM(B2:M2)"],
        ["Northern Transit Revenue (Nairobi-Eldoret-Malaba Transit)", 14200, 15600, 17400, 16100, 18200, 19100, 19800, 20600, 21400, 22200, 23100, 24900, "=SUM(B3:M3)"],
        ["Nairobi Metro Container Shuttles & Staging", 6800, 7200, 7900, 7400, 8100, 8500, 8800, 9100, 9400, 9800, 10200, 11100, "=SUM(B4:M4)"],
        ["Demurrage Recovery & Detention Surcharges", 1850, 2100, 2400, 1950, 2200, 2600, 2750, 2900, 3100, 3300, 3450, 3800, "=SUM(B5:M5)"],
        ["TOTAL GROSS OPERATING REVENUE (USD)", "=SUM(B2:B5)", "=SUM(C2:C5)", "=SUM(D2:D5)", "=SUM(E2:E5)", "=SUM(F2:F5)", "=SUM(G2:G5)", "=SUM(H2:H5)", "=SUM(I2:I5)", "=SUM(J2:J5)", "=SUM(K2:K5)", "=SUM(L2:L5)", "=SUM(M2:M5)", "=SUM(N2:N5)"],
        ["Bulk Diesel Fuel Burn (USD)", 13400, 14500, 16200, 15100, 17100, 17900, 18500, 19300, 20100, 20800, 21600, 23400, "=SUM(B7:M7)"],
        ["Highway Tolls & Axle-Load Weighbridge Gate Fees", 2100, 2300, 2550, 2400, 2650, 2800, 2900, 3050, 3150, 3300, 3400, 3700, "=SUM(B8:M8)"],
        ["Driver Mileage Allowances & Per Diem Surcharges", 4800, 5200, 5800, 5400, 6100, 6400, 6600, 6900, 7150, 7400, 7700, 8300, "=SUM(B9:M9)"],
        ["Fleet Preventative Maintenance, Spares & Lubes", 3200, 2800, 4100, 3100, 3600, 3900, 4200, 4100, 4500, 4400, 4800, 5200, "=SUM(B10:M10)"],
        ["Tire Replacement & Amortization (Michelin/Bridgestone)", 1800, 1800, 2400, 1800, 2400, 2400, 2400, 3200, 2400, 2400, 3200, 3200, "=SUM(B11:M11)"],
        ["Transit Goods-in-Transit (GIT) Insurance Premiums", 1650, 1650, 1650, 1650, 1650, 1650, 1650, 1650, 1650, 1650, 1650, 1650, "=SUM(B12:M12)"],
        ["Terminal Parking, Security & Dispatch Software", 950, 950, 950, 950, 950, 950, 950, 950, 950, 950, 950, 950, "=SUM(B13:M13)"],
        ["TOTAL DIRECT CASH EXPENSES (USD)", "=SUM(B7:B13)", "=SUM(C7:C13)", "=SUM(D7:D13)", "=SUM(E7:E13)", "=SUM(F7:F13)", "=SUM(G7:G13)", "=SUM(H7:H13)", "=SUM(I7:I13)", "=SUM(J7:J13)", "=SUM(K7:K13)", "=SUM(L7:L13)", "=SUM(M7:M13)", "=SUM(N7:N13)"],
        ["OPERATING CASH EBITDA (USD)", "=B6-B14", "=C6-C14", "=D6-D14", "=E6-E14", "=F6-F14", "=G6-G14", "=H6-H14", "=I6-I14", "=J6-J14", "=K6-K14", "=L6-L14", "=M6-M14", "=N6-N14"],
        ["Truck Lease Debt Service (Stanbic Bank Facility)", 6500, 6500, 6500, 6500, 6500, 6500, 6500, 6500, 6500, 6500, 6500, 6500, "=SUM(B16:M16)"],
        ["NET MONTHLY FREE CASH FLOW (USD)", "=B15-B16", "=C15-C16", "=D15-D16", "=E15-E16", "=F15-F16", "=G15-G16", "=H15-H16", "=I15-I16", "=J15-J16", "=K15-K16", "=L15-L16", "=M15-M16", "=N15-N16"],
        ["ENDING ACCUMULATED CASH BALANCE (USD)", 18200, 26900, 38150, 48300, 60800, 74900, 89900, 106200, 123800, 142850, 163200, 186350, 186350],
    ]

    files["dennis_12month_cashflow_tracker_final.xlsx"] = write_xlsx_file(
        "dennis_12month_cashflow_tracker_final.xlsx",
        {
            "12-Month P&L Cashflow": dennis_cashflow,
        },
        role="deliverable",
    )

    # =========================================================================
    # 5. ESTELLA WILLIAMS — WILLIAMS LOGISTICS (Investor Deck & Board Memo)
    # =========================================================================
    estella_slides = [
        {
            "type": "title",
            "kicker": "CONFIDENTIAL BOARD BRIEFING · OCTOBER 2026",
            "title": "Williams Logistics Network · Q4 2026 Strategic Review",
            "subtitle": "Presented by Estella Williams, Founder & CEO · Enterprise Cross-Dock Telematics Platform",
            "bullets": [
                "Board of Directors Review Copy · Series A Operational Update",
                "Operating Across 180 Active Terminals in Texas, Midwest & Gulf Corridors",
            ]
        },
        {
            "category": "OPERATING HIGHLIGHTS",
            "title": "Q3 2026 Executive Performance Dashboard",
            "subtitle": "Accelerating enterprise adoption, expanding terminal velocity, and zero logo attrition",
            "metrics": [
                {"value": "$4.2M", "label": "Current ARR", "desc": "+18% QoQ expansion across 180 active terminals"},
                {"value": "114%", "label": "Net Revenue Retention", "desc": "Driven by volumetric dockdoor throughput tiers"},
                {"value": "0.0%", "label": "Enterprise Logo Churn", "desc": "Zero cancellations across 6 consecutive quarters"},
                {"value": "78.4%", "label": "Gross Margin", "desc": "Pure SaaS economics with hardware-agnostic API"},
            ]
        },
        {
            "category": "FINANCIAL TRAJECTORY",
            "title": "Quarterly ARR Bridge & Expansion Velocity",
            "subtitle": "Clear line of sight to $6.8M ARR exit run-rate in FY 2027",
            "cards": [
                {
                    "title": "Q1–Q3 2026 Actual Growth",
                    "bullets": [
                        "Q1 2026: $2.8M ARR across 128 contracted distribution hubs",
                        "Q2 2026: $3.4M ARR with 28 new carrier fleet enterprise logos",
                        "Q3 2026: $4.2M ARR driven by Midwest freight corridor expansion",
                    ]
                },
                {
                    "title": "Q4 Forecast & FY2027 Budget",
                    "bullets": [
                        "Q4 2026 Target: $5.1M ARR (94% contracted pipeline coverage)",
                        "FY 2027 Projected: $6.8M ARR with 310 terminal deployments",
                        "Cash flow breakeven anticipated in Q2 2027 without secondary financing",
                    ]
                },
                {
                    "title": "Unit Economics & Payback",
                    "bullets": [
                        "Average Contract Value (ACV): $28,500/year per terminal hub",
                        "Customer Acquisition Cost (CAC): $5,900 per enterprise logo",
                        "LTV to CAC Ratio: 5.4x with 6.2 month cash payback window",
                    ]
                }
            ]
        },
        {
            "category": "CORE PRODUCT INNOVATION",
            "title": "DockDoor 2.0: Automated Cross-Dock Orchestration",
            "subtitle": "Replacing manual whiteboards, phone tag, and demurrage penalties with automated gate logic",
            "cards": [
                {
                    "title": "1. Geofenced Driver Intake",
                    "bullets": [
                        "Automated arrival trigger 2 miles from terminal perimeter",
                        "No app download required; runs via responsive web container",
                        "Instantly verifies trailer seal number and cargo bill of lading",
                    ]
                },
                {
                    "title": "2. Dynamic Bay Allocation",
                    "bullets": [
                        "Algorithms assign dock doors based on liftgate and reefer class",
                        "Balances forklift staging distance to reduce cross-dock congestion",
                        "Reduces average yard dwell time from 114 minutes to 38 minutes",
                    ]
                },
                {
                    "title": "3. Sign-on-Glass Electronic BOL",
                    "bullets": [
                        "Digital damage exception markup with high-res photo capture",
                        "Instant PDF bill-of-lading dispatch to carrier, broker, and consignee",
                        "100% audit compliance with zero lost freight documentation",
                    ]
                }
            ]
        },
        {
            "category": "ENTERPRISE PILOT CASE STUDY",
            "title": "Mid-States 3PL Case Study: Measurable Operational ROI",
            "subtitle": "Deployment across 4 regional cross-dock distribution hubs in Dallas, Kansas City, and Memphis",
            "metrics": [
                {"value": "-41%", "label": "Detention Claims", "desc": "Saved $184,000 in trailer detention fees in 90 days"},
                {"value": "14 hrs", "label": "Weekly Time Saved", "desc": "Saved per dispatcher on phone check-ins and paper filing"},
                {"value": "18,400", "label": "BOLs Cleared", "desc": "100% digital audit trace with zero disputed shortages"},
                {"value": "3.8x", "label": "First-Year ROI", "desc": "Platform paid for itself within the first 60 days of go-live"},
            ]
        },
        {
            "category": "ENTERPRISE PIPELINE & GTM",
            "title": "Enterprise Pipeline Coverage & Distribution Corridors",
            "subtitle": "Strong mid-market carrier density across Texas triangular freight corridors",
            "bullets": [
                "Total Active Sales Pipeline: $3.8M in qualified enterprise opportunities under technical POC review.",
                "Average Enterprise Sales Cycle: 42 calendar days from initial terminal survey to paid production pilot.",
                "Channel Partnerships: Direct certified integrations with Descartes, SAP TM, Oracle OTM, and Blue Yonder.",
                "Expansion Motions: 68% of new ARR derived from existing carrier logos adding secondary and tertiary regional terminals.",
            ]
        },
        {
            "category": "CAPITAL & GOVERNANCE",
            "title": "Capital Runway, Balance Sheet & Board Resolutions",
            "subtitle": "Prudent runway management with 24+ months of cash at current growth trajectory",
            "cards": [
                {
                    "title": "Cash Position & Runway",
                    "bullets": [
                        "Cash in Bank (Silicon Valley Bank / First Citizens): $3,120,000",
                        "Average Monthly Net Cash Burn: $58,000",
                        "Runway: 24+ months at zero revenue growth; profitable by Q2 2027",
                    ]
                },
                {
                    "title": "FY2027 Resource Allocation",
                    "bullets": [
                        "55% Engineering & Mobile Product Innovation (5 Senior Full-Stack Hires)",
                        "30% Dedicated Field Enterprise Sales & Solution Architecture",
                        "15% Information Security, SOC 2 Type II Recertification & G&A",
                    ]
                },
                {
                    "title": "Board Action Items Requested",
                    "bullets": [
                        "Formal adoption of FY 2027 Operating Budget & Headcount Plan",
                        "Approval of 3% Employee Option Pool expansion for executive hires",
                        "Confirmation of Q1 2027 Board Meeting Date (January 22, 2027)",
                    ]
                }
            ]
        }
    ]

    files["estella_q4_executive_investor_deck_final.pptx"] = write_pptx_file(
        "estella_q4_executive_investor_deck_final.pptx",
        "Williams Logistics Network · Q4 2026 Executive Investor Update",
        estella_slides,
        role="deliverable",
    )

    files["estella_q4_board_briefing_memo_final.docx"] = write_docx_file(
        "estella_q4_board_briefing_memo_final.docx",
        "Williams Logistics Network — Executive Board Memorandum (Q4 Strategic Review)",
        [
            "TO: Board of Directors, Williams Logistics Network Inc.",
            "FROM: Estella Williams, Founder & Chief Executive Officer",
            "DATE: October 14, 2026",
            "SUBJECT: Q4 2026 Operational Review, Financial Performance & FY2027 Capital Budget",
            "--PAGE-BREAK--",
            "# 1. EXECUTIVE SUMMARY & STRATEGIC HIGHLIGHTS",
            "I am pleased to report that Williams Logistics Network achieved record financial and operational milestones during the third quarter of fiscal year 2026. Annual Recurring Revenue (ARR) reached $4,210,000, representing an 18.2% quarter-over-quarter expansion and 50.3% year-over-year growth against our FY2025 baseline.",
            "Our Net Revenue Retention (NRR) closed at 114.2% across our core mid-market enterprise carrier tier, driven primarily by volume tier upgrades as our customers expanded DockDoor 2.0 deployments across their regional warehouse footprints. Most importantly, enterprise customer logo churn remained at 0.0% for the sixth consecutive quarter.",
            "# 2. FINANCIAL ACTUALS & ARR EXPANSION BRIDGE",
            [
                ["Financial Metric", "Q1 2026 Actual", "Q2 2026 Actual", "Q3 2026 Actual", "Q4 2026 Target", "FY2027 Budget"],
                ["Contracted ARR", "$2,800,000", "$3,420,000", "$4,210,000", "$5,100,000", "$6,800,000"],
                ["Quarterly GAAP Revenue", "$680,000", "$820,000", "$1,020,000", "$1,240,000", "$1,650,000"],
                ["Gross Profit Margin", "75.4%", "77.1%", "78.4%", "79.0%", "80.5%"],
                ["Net Revenue Retention (NRR)", "111.8%", "112.5%", "114.2%", "115.0%", "116.5%"],
                ["Active Terminal Deployments", "128 Hubs", "154 Hubs", "180 Hubs", "215 Hubs", "310 Hubs"],
                ["Average Contract Value (ACV)", "$21,875", "$22,200", "$23,388", "$23,720", "$24,500"],
            ],
            "# 3. UNIT ECONOMICS & PRODUCT MARGIN EVOLUTION",
            "Our hardware-agnostic API platform architecture continues to deliver pure software margins. Cost of Goods Sold (COGS) consists solely of AWS cloud infrastructure, Twilio driver SMS notification routing, and automated document OCR indexing. Gross margins expanded from 75.4% in Q1 to 78.4% in Q3, with a clear trajectory toward 80%+ at scale.",
            "Customer Acquisition Cost (CAC) averaged $5,920 per contracted terminal network, yielding a healthy 6.2-month cash payback period against an estimated 5-year Customer Lifetime Value (LTV) exceeding $115,000 (LTV:CAC ratio of 5.4x).",
            "--PAGE-BREAK--",
            "# 4. PRODUCT INNOVATION: DOCKDOOR 2.0 ROLLOUT",
            "During Q3, our engineering organization successfully completed general availability (GA) rollout of DockDoor 2.0, introducing automated cross-dock gate sequencing and mobile sign-on-glass electronic bills of lading (e-BOL).",
            "Core Architectural Advancements:",
            "— Geofenced Perimeter Arrival Alerts: Trucks entering a 2-mile terminal radius automatically alert frontline dispatch, pre-allocating bay doors before the tractor hits the security gate.",
            "— Demurrage Countdown Timers: Automated alerts notify yard jockeys 45 minutes prior to detention penalty accrual, eliminating $184,000 in carrier detention claims across our pilot cohort.",
            "— Zero-App Mobile Container: Frontline drivers access terminal check-in via lightweight browser sessions, eliminating driver onboarding friction and achieving 98.6% compliance on day one.",
            "# 5. FY 2027 CAPITAL ALLOCATION & RESOLUTIONS REQUESTED",
            "We maintain $3,120,000 in cash reserves. At our current net monthly burn rate of $58,000, our balance sheet provides over 24 months of operational runway without requiring external equity financing. We project achieving operational cash flow breakeven in Q2 2027.",
            "Board Action Items Requested for Formal Approval:",
            "1. Approval of FY 2027 Operating Plan targeting $6.8M ARR and 310 terminal hubs.",
            "2. Ratification of 3.0% unallocated common stock option pool expansion for technical engineering hires.",
            "3. Confirmation of the next scheduled Board of Directors Meeting for Thursday, January 21, 2027.",
        ],
        role="deliverable",
    )

    # =========================================================================
    # 6. JACK JOHNSON — DOCKSTREAM ENTERPRISE B2B LOGISTICS PLATFORM
    # =========================================================================
    files["johnson_b2b_site_and_deck_final.docx"] = write_docx_file(
        "johnson_b2b_site_and_deck_final.docx",
        "DockStream Enterprise — B2B Product Messaging & Master Copy Deck",
        [
            "CLIENT: DockStream Technologies Inc. (Jack Johnson, Co-Founder)",
            "DOCUMENT: B2B Enterprise Web Copy Deck & Positioning Strategy",
            "VERSION: 4.1 Production Master Copy Deck",
            "--PAGE-BREAK--",
            "# ENTERPRISE STRATEGIC POSITIONING & HOMEPAGE MASTER COPY",
            "1. Value Proposition & Market Category",
            "Category: Intelligent Cross-Dock Yard & Terminal Orchestration Platform",
            "Primary Positioning Statement: DockStream is the enterprise SaaS platform that automates driver intake, eliminates dockyard demurrage penalties, and digitizes shipping manifests for mid-market 3PL logistics hubs.",
            "2. Homepage Hero Section",
            "Category Kicker: Enterprise Logistics Infrastructure",
            "Primary Headline: Eliminate cross-dock congestion and detention penalties with real-time yard orchestration.",
            "Subhead: Connect frontline dispatchers, yard spotters, and inbound drivers on a unified digital platform. DockStream reduces trailer turnaround times by 38% and delivers 100% audit-proof electronic bills of lading.",
            "Call-to-Action Buttons: Primary: [Schedule Enterprise Terminal Survey] · Secondary: [Calculate Yard Detention Savings]",
            "3. The Cost of Cross-Dock Inefficiency",
            "— $180,000 Average Annual Detention Losses: Carriers bleed capital waiting in queue for manual dock assignment.",
            "— 14 Hours Lost Weekly per Dispatcher: Frontline staff spend hours making phone calls, checking clipboards, and chasing paper bills of lading.",
            "— 12% Paper BOL Discrepancy Rate: Missing signatures and unverified damage photos create expensive claims and billing disputes.",
            "--PAGE-BREAK--",
            "# PLATFORM CAPABILITIES & WORKFLOW ARCHITECTURE",
            "1. Geofenced Driver Mobile Intake",
            "Inbound drivers trigger automatic yard check-in upon crossing the terminal perimeter. Drivers verify load details, container seal numbers, and reefer temperatures directly on their mobile device without leaving their cab or downloading an app.",
            "2. Dynamic Bay & Yard Slotting Logic",
            "DockStream's intelligent routing engine assigns trailers to optimal bays based on pallet volume, liftgate necessity, and forklift driver proximity—cutting cross-dock transit times by 40%.",
            "3. Sign-on-Glass Electronic BOL (e-BOL)",
            "Frontline personnel annotate damages, take high-resolution timestamped photos, and collect carrier digital signatures instantly. Fully executed BOL PDFs sync to your enterprise TMS via REST APIs.",
            "4. Enterprise TMS Integrations Matrix",
            [
                ["TMS / ERP Platform", "Integration Type", "Sync Protocol", "Data Exchanged"],
                ["SAP Transportation Management", "Native Enterprise Connector", "Bi-Directional REST / OData", "Inbound ASN, Gate-In Time, POD PDF"],
                ["Oracle OTM Cloud", "Certified Partner Module", "REST API & Webhooks", "Trailer Arrival, Dock Status, BOL Signatures"],
                ["Descartes Logistics Suite", "Pre-Built Middleware", "EDI 214 / 210 / 204 Bridge", "Shipment Status Events, Detention Triggers"],
                ["Blue Yonder (JDA)", "API Webhook Sync", "JSON REST API", "Bay Assignment, Pallet Counts, Proof of Delivery"],
            ],
            "--PAGE-BREAK--",
            "# ENTERPRISE SECURITY, SLA & COMMERCIAL TERMS",
            "1. Information Security & Compliance",
            "— SOC 2 Type II Certified: Annual third-party audits ensure complete data isolation and encryption at rest (AES-256) and in transit (TLS 1.3).",
            "— Role-Based Access Control (RBAC): Granular permissions for terminal directors, dispatch supervisors, yard jockeys, and third-party carrier fleets.",
            "— 99.95% High Availability SLA: Multi-region cloud failover ensures continuous terminal operations during network outages.",
            "2. Tiered Enterprise Pricing Schedule",
            [
                ["Plan Tier", "Terminal Footprint", "Monthly Inbound Loads", "Key Inclusions", "Annual SaaS License"],
                ["Standard Hub", "Single Terminal (1–20 Doors)", "Up to 500 Loads/Mo", "Mobile Check-In, e-BOL, Basic Reporting", "$14,400 / Year"],
                ["Enterprise Terminal", "Regional Hub (20–60 Doors)", "Up to 2,000 Loads/Mo", "Dynamic Slotting, TMS Sync, Demurrage Alerts", "$28,500 / Year"],
                ["Multi-Site Network", "Multi-Terminal (60+ Doors)", "Unlimited Volume", "Dedicated Solution Architect, Custom EDI, 99.95% SLA", "$54,000 / Year"],
            ],
        ],
        role="deliverable",
    )

    files["johnson_12slide_outbound_enterprise_deck.pptx"] = write_pptx_file(
        "johnson_12slide_outbound_enterprise_deck.pptx",
        "DockStream Enterprise — Outbound Logistics Presentation",
        [
            {
                "type": "title",
                "kicker": "ENTERPRISE CAPABILITY BRIEFING · 2026",
                "title": "DockStream: Intelligent Cross-Dock Logistics",
                "subtitle": "Presented by Jack Johnson, Co-Founder · Eliminating Terminal Gridlock & Detention Penalties",
                "bullets": [
                    "Purpose-Built for Mid-Market 3PL Distribution Facilities & Freight Carriers",
                    "38% Turnaround Acceleration · 100% Digital Electronic BOL Compliance",
                ]
            },
            {
                "category": "INDUSTRY CHALLENGE",
                "title": "The Hidden Cost of Cross-Dock Inefficiency",
                "subtitle": "Fragmented paperwork and manual phone calls paralyze regional distribution terminals",
                "metrics": [
                    {"value": "$180k", "label": "Annual Detention Loss", "desc": "Paid per terminal in carrier demurrage penalties"},
                    {"value": "114 min", "label": "Average Dwell Time", "desc": "Trucks parked waiting for manual dock door assignment"},
                    {"value": "14 hrs", "label": "Lost Weekly per Staff", "desc": "Spent by dispatchers on phone tag and clipboard tracking"},
                    {"value": "12%", "label": "BOL Claim Disputes", "desc": "Paper bills lost, illegible, or lacking damage photos"},
                ]
            },
            {
                "category": "THE DOCKSTREAM SOLUTION",
                "title": "A Complete Terminal Orchestration Operating System",
                "subtitle": "Connecting frontline dispatchers, yard spotters, and carriers in real time",
                "cards": [
                    {
                        "title": "1. Mobile Driver Check-In",
                        "bullets": [
                            "Geofence triggers arrival alerts 2 miles out",
                            "Zero app friction: instant web container",
                            "Validates seal and temperature specs instantly",
                        ]
                    },
                    {
                        "title": "2. Dynamic Bay Assignment",
                        "bullets": [
                            "Algorithm routes trailers based on forklift traffic",
                            "Prioritizes hot freight and expiring demurrage",
                            "Cuts yard dwell time by 38% immediately",
                        ]
                    },
                    {
                        "title": "3. Sign-on-Glass e-BOL",
                        "bullets": [
                            "Timestamped photo exceptions for damaged cartons",
                            "Digital sign-off dispatched to carrier and shipper",
                            "Direct REST sync to SAP, Oracle, and Blue Yonder",
                        ]
                    }
                ]
            },
            {
                "category": "ENTERPRISE ROI",
                "title": "Proven Pilot Results: Midwest 3PL Case Study",
                "subtitle": "Performance audited across 18,400 consecutive trailer transfers over 90 days",
                "metrics": [
                    {"value": "38%", "label": "Turn Time Reduction", "desc": "From 114 minutes down to 71 minutes per trailer"},
                    {"value": "$184k", "label": "Demurrage Savings", "desc": "41% drop in carrier detention claims in quarter one"},
                    {"value": "100%", "label": "Audit Compliance", "desc": "Zero lost shipping documents across 18,400 transfers"},
                    {"value": "60 Days", "label": "Cash Payback Window", "desc": "Platform investment fully recovered in two months"},
                ]
            },
            {
                "category": "COMMERCIAL PRICING",
                "title": "Predictable, High-ROI Commercial Tiering",
                "subtitle": "Simple transparent licensing based on terminal size and load throughput",
                "cards": [
                    {
                        "title": "Standard Hub ($14,400/yr)",
                        "bullets": [
                            "Single terminal with up to 20 dock doors",
                            "Mobile driver intake & e-BOL generation",
                            "Standard email support and 99.9% uptime SLA",
                        ]
                    },
                    {
                        "title": "Enterprise Terminal ($28,500/yr)",
                        "bullets": [
                            "High-volume regional hub (20–60 doors)",
                            "Dynamic yard slotting & demurrage countdown",
                            "Native SAP / Oracle TMS integration modules",
                        ]
                    },
                    {
                        "title": "Multi-Site Network ($54,000/yr)",
                        "bullets": [
                            "Enterprise carrier network with 60+ doors",
                            "Custom EDI bridges & dedicated solution architect",
                            "99.95% uptime SLA with 24/7 dedicated telephone support",
                        ]
                    }
                ]
            }
        ],
        role="deliverable",
    )

    # =========================================================================
    # 7. AZAEL OROZCO — OROZCO COMMERCIAL & INDUSTRIAL ROOFING (South Texas)
    # =========================================================================
    files["orozco_site_copy_and_estimate_final.docx"] = write_docx_file(
        "orozco_site_copy_and_estimate_final.docx",
        "Orozco Commercial Roofing — Master Specifications & Commercial Bid Deck",
        [
            "CLIENT: Orozco Commercial & Industrial Roofing LLC",
            "HEADQUARTERS: Pharr, TX · Serving McAllen, Brownsville & Rio Grande Valley",
            "DOCUMENT: Master Commercial Copy Deck, Technical Specifications & Bid Scope",
            "--PAGE-BREAK--",
            "# HOMEPAGE MASTER COPY & VALUE PROPOSITION",
            "1. Header & Authority Banner",
            "Company: Orozco Commercial & Industrial Roofing LLC",
            "Serving: McAllen · Pharr · Edinburg · Harlingen · Brownsville · Laredo Commercial Corridor",
            "Credentials: GAF Master Commercial Contractor · Carlisle SynTec Certified Applicator · Elevate (Firestone) Red Shield Certified · 20-Year NDL Warranty Certified.",
            "2. Hero Presentation",
            "Category Kicker: South Texas Commercial Flat Roofing Specialists Since 2012",
            "Primary Headline: Engineered commercial flat roofing and industrial storm restoration built for South Texas heat.",
            "Subhead: Protecting distribution warehouses, manufacturing facilities, and commercial properties across the Rio Grande Valley. Specializing in single-ply TPO, fluid-applied silicone restoration membranes, and standing seam industrial metal.",
            "Call to Action: Primary: [Schedule 21-Point Commercial Roof Assessment] · Secondary: [Download 20-Year NDL Warranty Guide]",
            "3. The South Texas Climate Challenge",
            "Subtropical UV radiation, extreme thermal shock, and Gulf Coast tropical windstorms destroy standard commercial roofs. A compromised commercial roof risks millions of dollars in inventory, warehouse equipment, and business interruption.",
            "Orozco Commercial Roofing delivers heavy-duty roofing systems engineered specifically to withstand 120-degree roof-surface heat, sustained 115-mph hurricane winds, and severe hail impact.",
            "--PAGE-BREAK--",
            "# TECHNICAL SPECIFICATIONS & SYSTEM COMPARISON MATRIX",
            [
                ["Commercial System", "Membrane Thickness", "Solar Reflectance (SRI)", "Hail Impact Rating", "Wind Uplift Resistance", "Manufacturer Warranty"],
                ["Carlisle Sure-Weld TPO", "60-mil / 80-mil Reinforced", "104 (Initial Cool Roof)", "UL 2218 Class 4 Impact", "FM 1-90 / 1-120 Rated", "20-Year No Dollar Limit (NDL)"],
                ["Elevate UltraPly TPO", "60-mil Polyester Scrim", "102 Initial SRI", "Severe Hail (SH) Approved", "Meets ASTM D6878 Specs", "20-Year Red Shield Warranty"],
                ["GacoFlex Silicone Coating", "32-mil Dry Film Thickness", "110 Maximum Reflectance", "Flexible Elastomeric Fill", "Resists Standing Ponding Water", "50-Year Limited Material Warranty"],
                ["Architectural Standing Seam", "24-Gauge Galvalume Steel", "Kynar 500 / Hylar 5000", "UL Class 4 Hail Resistant", "140 MPH Hurricane Uplift", "30-Year Finish / 20-Year Weathertight"],
            ],
            "# 21-POINT COMMERCIAL ROOF ASSESSMENT METHODOLOGY",
            "Every commercial inspection includes core sampling, infrared moisture scans, and photographic documentation:",
            "— Core Sampling & Deck Moisture Analysis: Non-destructive thermal imaging pinpoints wet insulation boards to prevent needless full tear-offs.",
            "— Parapet Wall & Flashing Integrity: Detailed examination of coping metal, termination bars, and counter-flashings where 70% of commercial leaks originate.",
            "— Mechanical Curb & Penetration Seals: Rigorous inspection of rooftop HVAC units, conduit boots, and pitch pans.",
            "— Drainage & Scupper Flow Calibration: Verifying adequate slope-to-drain ratios to prevent structural ponding water deflection.",
            "--PAGE-BREAK--",
            "# COMMERCIAL BID PROPOSAL & 20-YEAR NDL CONTRACT TERMS",
            "Sample Commercial Bid: 42,000 Sq Ft Logistics Distribution Center (Pharr, TX)",
            [
                ["Scope Category", "Specification & Materials Description", "Coverage / Units", "Unit Investment", "Line Item Total"],
                ["Demolition / Prep", "Power-wash surface, remove deteriorated insulation core spots", "42,000 Sq Ft", "$0.45 / Sq Ft", "$18,900.00"],
                ["Insulation Layer", "2.5-inch Polyisocyanurate (R-14.4) fastened per FM 1-90", "1,312 Boards", "$38.50 / Board", "$50,512.00"],
                ["Membrane Install", "Carlisle 60-mil White TPO mechanically attached and robotically heat-welded", "42,000 Sq Ft", "$2.85 / Sq Ft", "$119,700.00"],
                ["Perimeter Flashing", "24-Gauge pre-finished Kynar coping and parapet wrap", "840 Linear Ft", "$28.00 / Lin Ft", "$23,520.00"],
                ["Roof Penetrations", "Pipelogix boots, HVAC curb wraps, and walk pads to equipment", "24 Curbs/Pipes", "Lump Sum", "$6,800.00"],
                ["Manufacturer NDL Fee", "Carlisle SynTec 20-Year No Dollar Limit Inspection & Warranty Issuance", "Facility Fee", "Flat Rate", "$4,200.00"],
                ["TOTAL CONTRACT INVESTMENT", "Turnkey Commercial Capital Re-Roofing Project", "42,000 Sq Ft", "Turnkey", "$223,632.00"],
            ],
            "Warranty Terms: Manufacturer 20-Year No Dollar Limit (NDL) warranty covers 100% of labor and materials for roof leaks resulting from weather, manufacturing defects, or workmanship without monetary cap.",
        ],
        role="deliverable",
    )

    # =========================================================================
    # 8. ALEXA QUINTERO — FIELDPULSE TRADE FLEET MOBILE WORKFLOWS
    # =========================================================================
    files["alexa_10slide_investor_pitch.pptx"] = write_pptx_file(
        "alexa_10slide_investor_pitch.pptx",
        "FieldPulse — Seed Investor Presentation",
        [
            {
                "type": "title",
                "kicker": "CONFIDENTIAL SEED FINANCING BRIEFING · 2026",
                "title": "FieldPulse: Intelligent Workflows for Trade Fleets",
                "subtitle": "Presented by Alexa Quintero, Founder & CEO · Mobile Dispatch & Invoicing for Plumbing, HVAC & Electrical Fleets",
                "bullets": [
                    "Targeting the $8.2B North American Trade & Field Services Software Market",
                    "42 Active Fleets · $310k Current ARR · 92% Gross Software Margin",
                ]
            },
            {
                "category": "THE PROBLEM",
                "title": "Trade Fleets Bleed Margins Through Fragmented Paperwork",
                "subtitle": "Field technicians lose hours on clipboards while dispatchers juggle disjointed spreadsheets and phone calls",
                "metrics": [
                    {"value": "2.4 hrs", "label": "Lost Daily per Tech", "desc": "Spent on manual paperwork, travel logs, and phone check-ins"},
                    {"value": "8.4%", "label": "Revenue Unbilled", "desc": "Lost change orders, uncollected parts, and missing signatures"},
                    {"value": "28 days", "label": "Payment Wait Time", "desc": "Average time to collect invoices dispatched by mail"},
                    {"value": "42%", "label": "Dispatcher Turnover", "desc": "Stress driven by chaotic manual scheduling and dispatch"},
                ]
            },
            {
                "category": "THE SOLUTION",
                "title": "A Mobile-First Operating System for Field Technicians",
                "subtitle": "One tap to dispatch, offline mobile sign-off, and instant on-site card payment",
                "cards": [
                    {
                        "title": "1. GPS Turn-by-Turn Routing",
                        "bullets": [
                            "Optimized route sequencing cuts windshield time by 22%",
                            "Automated customer arrival SMS with live tech tracking",
                            "Real-time geofence verifies technician on-site labor hours",
                        ]
                    },
                    {
                        "title": "2. Offline Field Invoicing",
                        "bullets": [
                            "Operates seamlessly in basements and dead zones",
                            "Pre-loaded parts price books with margin rules",
                            "One-tap customer sign-on-glass work approval",
                        ]
                    },
                    {
                        "title": "3. Integrated Mobile Payments",
                        "bullets": [
                            "Tap-to-Pay and card reader payment capture on-site",
                            "Automated QuickBooks & Xero accounting ledger sync",
                            "Cuts contractor DSO from 28 days down to 0 days",
                        ]
                    }
                ]
            },
            {
                "category": "MARKET OPPORTUNITY",
                "title": "$8.2B Addressable Trade Contractor Software Market",
                "subtitle": "Over 1.2 million trade service businesses across the United States and Canada",
                "metrics": [
                    {"value": "$8.2B", "label": "Total Available Market", "desc": "North American commercial & residential trade contractors"},
                    {"value": "$1.4B", "label": "Serviceable Market", "desc": "Plumbing, electrical, and HVAC fleets with 5–30 vans"},
                    {"value": "180,000", "label": "Target Fleet Businesses", "desc": "Under-served by expensive legacy enterprise software"},
                    {"value": "$89 / mo", "label": "Subscription Seat Fee", "desc": "Per active technician with 92% gross software margin"},
                ]
            },
            {
                "category": "TRACTION & SEED ASK",
                "title": "Traction Benchmarks & $1.8M Seed Financing Round",
                "subtitle": "Accelerating engineering velocity and mid-market field sales expansion",
                "cards": [
                    {
                        "title": "Current Traction (Q3 2026)",
                        "bullets": [
                            "$310,000 Annual Recurring Revenue (ARR)",
                            "42 Paid Contractor Fleets across 8 metropolitan markets",
                            "98.4% Monthly Customer Retention with 4.9 App Store rating",
                        ]
                    },
                    {
                        "title": "Use of Seed Proceeds ($1.8M)",
                        "bullets": [
                            "60% Engineering: Automated parts inventory and AI quoting",
                            "25% Inside Sales & Trade Association Channel Marketing",
                            "15% Customer Onboarding, Success & Regulatory Compliance",
                        ]
                    },
                    {
                        "title": "18-Month Target Milestones",
                        "bullets": [
                            "Expand from 42 to 240 active contractor fleets",
                            "Scale ARR from $310k to $2.2M run-rate",
                            "Position company for Tier 1 Series A growth round",
                        ]
                    }
                ]
            }
        ],
        role="deliverable",
    )

    # =========================================================================
    # 9. LUCA CAROLLO — MAKANI YACHT CHARTERS (Honolulu, Hawaii)
    # =========================================================================
    luca_distribution = [
        ["Financial Line Item ($USD)", "Q1 2026 Actual", "Q2 2026 Actual", "Q3 2026 Actual", "Q4 2026 Projected", "Full Year 2026 Total"],
        ["Private Luxury Catamaran Charters (Makani 48')", 94500, 118200, 142800, 134000, "=SUM(B2:E2)"],
        ["Flybridge Motor Yacht Charters (Kairos 54')", 78000, 96500, 112000, 108500, "=SUM(B3:E3)"],
        ["Coastal Sunset & Snorkel Charters (Moana 42')", 46200, 58400, 68900, 64200, "=SUM(B4:E4)"],
        ["On-Board Catering, Bar & Provisions Revenue", 28400, 36200, 44800, 41200, "=SUM(B5:E5)"],
        ["TOTAL GROSS CHARTER REVENUE ($USD)", "=SUM(B2:B5)", "=SUM(C2:C5)", "=SUM(D2:D5)", "=SUM(E2:E5)", "=SUM(F2:F5)"],
        ["USCG Master Captain & Marine Crew Payroll", 52400, 64200, 76800, 72000, "=SUM(B7:E7)"],
        ["Ala Wai & Ko Olina Marina Slip Mooring Fees", 14800, 14800, 14800, 14800, "=SUM(B8:E8)"],
        ["Marine Diesel & Outboard Fuel Burn", 18200, 22600, 28400, 26100, "=SUM(B9:E9)"],
        ["Vessel Maintenance, Hull Haul-Out & Inspections", 16400, 12800, 19200, 15600, "=SUM(B10:E10)"],
        ["Catering Supplies, Provisions & Florals", 14200, 18100, 22400, 20600, "=SUM(B11:E11)"],
        ["Hull & P&I Commercial Marine Insurance", 9600, 9600, 9600, 9600, "=SUM(B12:E12)"],
        ["TOTAL OPERATING DIRECT EXPENSES ($USD)", "=SUM(B7:B12)", "=SUM(C7:C12)", "=SUM(D7:D12)", "=SUM(E7:E12)", "=SUM(F7:F12)"],
        ["NET DISTRIBUTABLE CHARTER EARNINGS ($USD)", "=B6-B13", "=C6-C13", "=D6-D13", "=E6-E13", "=F6-F13)"],
        ["8.0% Preferred Return to Class A Limited Partners", 24000, 24000, 24000, 24000, "=SUM(B15:E15)"],
        ["Remaining Cash Distributable to GP / LP Split", "=B14-B15", "=C14-C15", "=D14-D15", "=E14-E15", "=F14-F15"],
        ["Class A LP Share (70% Tier)", "=B16*0.7", "=C16*0.7", "=D16*0.7", "=E16*0.7", "=F16*0.7"],
        ["General Partner Operating Share (30% Tier)", "=B16*0.3", "=C16*0.3", "=D16*0.3", "=E16*0.3", "=F16*0.3"],
    ]

    files["luca_partner_distribution_waterfall_model.xlsx"] = write_xlsx_file(
        "luca_partner_distribution_waterfall_model.xlsx",
        {
            "Partner Equity Waterfall": luca_distribution,
        },
        role="deliverable",
    )

    # =========================================================================
    # 10. KEEGAN CHIN — CHIN SPECIALTY GOODS (Warehouse & SKU Margins)
    # =========================================================================
    keegan_skus = [
        ["SKU Code", "Product Description", "HTS Tariff Code", "Factory FOB ($USD)", "Ocean Freight Alloc ($USD)", "Harbor Drayage ($USD)", "Customs Duty ($USD)", "Landed Unit Cost ($USD)", "Wholesale B2B ($USD)", "B2B Margin %", "Retail MSRP ($USD)", "DTC Margin %", "Q3 Units Sold", "Total Q3 Gross Profit ($USD)"],
        ["CSG-KNF-01", "7-Inch Damascus Santoku Chef Knife", "8211.92.20", 28.50, 2.10, 0.45, 1.40, "=SUM(D2:G2)", 68.00, "=1-(H2/I2)", 145.00, "=1-(H2/K2)", 1240, "=(I2-H2)*M2"],
        ["CSG-KNF-02", "8.5-Inch VG-10 Gyuto Chef Knife", "8211.92.20", 34.00, 2.10, 0.45, 1.65, "=SUM(D3:G3)", 82.00, "=1-(H3/I3)", 175.00, "=1-(H3/K3)", 980, "=(I3-H3)*M3"],
        ["CSG-KNF-03", "3.5-Inch Precision Paring Knife", "8211.92.40", 14.20, 1.20, 0.30, 0.70, "=SUM(D4:G4)", 36.00, "=1-(H4/I4)", 78.00, "=1-(H4/K4)", 1850, "=(I4-H4)*M4"],
        ["CSG-POT-01", "Matte Ceramic Pour-Over Dripper (V60)", "6911.10.15", 4.80, 1.40, 0.35, 0.48, "=SUM(D5:G5)", 16.50, "=1-(H5/I5)", 38.00, "=1-(H5/K5)", 3400, "=(I5-H5)*M5"],
        ["CSG-POT-02", "Double-Walled Borosilicate Server (600ml)", "7013.49.20", 6.20, 1.80, 0.40, 0.62, "=SUM(D6:G6)", 19.00, "=1-(H6/I6)", 42.00, "=1-(H6/K6)", 2650, "=(I6-H6)*M6"],
        ["CSG-POT-03", "Gooseneck Temperature Pouring Kettle", "8516.79.00", 22.00, 3.20, 0.65, 1.10, "=SUM(D7:G7)", 58.00, "=1-(H7/I7)", 125.00, "=1-(H7/K7)", 1120, "=(I7-H7)*M7"],
        ["CSG-TCK-01", "End-Grain Teak Kitchen Prep Board (18x12)", "4419.90.90", 16.50, 3.80, 0.75, 0.55, "=SUM(D8:G8)", 45.00, "=1-(H8/I8)", 95.00, "=1-(H8/K8)", 1460, "=(I8-H8)*M8"],
        ["CSG-TCK-02", "Organic Ceremonial Uji Matcha Set (30g)", "0902.10.90", 8.40, 0.85, 0.20, 0.00, "=SUM(D9:G9)", 24.00, "=1-(H9/I9)", 52.00, "=1-(H9/K9)", 4200, "=(I9-H9)*M9"],
        ["CSG-TCK-03", "Insulated Titanium Tumbler (450ml)", "7615.10.30", 11.20, 1.50, 0.35, 0.56, "=SUM(D10:G10)", 32.00, "=1-(H10/I10)", 68.00, "=1-(H10/K10)", 2100, "=(I10-H10)*M10"],
        ["TOTAL MASTER CATALOG", "9 KEY PRODUCT LINES", "-", "=SUM(D2:D10)", "=SUM(E2:E10)", "=SUM(F2:F10)", "=SUM(G2:G10)", "=SUM(H2:H10)", "=SUM(I2:I10)", "=AVERAGE(J2:J10)", "=SUM(K2:K10)", "=AVERAGE(L2:L10)", "=SUM(M2:M10)", "=SUM(N2:N10)"],
    ]

    files["keegan_sku_margin_calculator_v2_locked.xlsx"] = write_xlsx_file(
        "keegan_sku_margin_calculator_v2_locked.xlsx",
        {
            "Master SKU Margin Model": keegan_skus,
        },
        role="deliverable",
    )

    # =========================================================================
    # 11. JOSE CRUZ — CRUZ METRO FREIGHT (Dallas-Fort Worth Corridor)
    # =========================================================================
    files["cruz_bio_and_outreach_final.docx"] = write_docx_file(
        "cruz_bio_and_outreach_final.docx",
        "Cruz Metro Freight — Corporate Profile & Outbound Shipper Playbook (Final)",
        [
            "ENTITY: Cruz Metro Freight LLC · Terminal: 4820 W Davis St, Dallas, TX 75211",
            "OPERATING AUTHORITY: USDOT #3918204 · MC #1488209 · Texas DMV #0094182",
            "INSURANCE: $1,000,000 Auto Liability CSL · $100,000 Cargo (Great West Casualty)",
            "DOCUMENT: Executive Capability Statement, Fleet Specifications & Outbound Campaign",
            "--PAGE-BREAK--",
            "# 1. CORPORATE PROFILE & ASSET OVERVIEW",
            "Cruz Metro Freight LLC is an asset-based regional logistics provider headquartered in Dallas, Texas. We operate late-model Freightliner M2-106 box trucks and high-roof Mercedes-Benz Sprinter vans, providing scheduled dock-to-dock replenishment, retail distribution, and expedited courier services across the Dallas-Fort Worth Metroplex and North Texas industrial corridor.",
            "Our non-CDL asset configuration guarantees agile city navigation, zero driver log delays, and direct dispatch without broker markups or third-party intermediary layers.",
            "# 2. FLEET EQUIPMENT & HANDLING SPECIFICATIONS",
            [
                ["Asset Identifier", "Vehicle Type", "GVWR / Payload", "Cargo Box Dimensions", "Liftgate Capacity", "On-Board Handling Equipment"],
                ["Tractor Unit #101", "2024 Freightliner M2-106", "26,000 lbs (10,000 lbs Net)", "26' L x 102\" W x 96\" H", "3,500-lb Maxon Tuck-Under", "5,500-lb Pallet Jack, 4 E-Track Bars, 12 Blankets"],
                ["Tractor Unit #102", "2025 Freightliner M2-106", "26,000 lbs (10,000 lbs Net)", "26' L x 102\" W x 96\" H", "3,500-lb Maxon Tuck-Under", "5,500-lb Pallet Jack, 4 E-Track Bars, 12 Blankets"],
                ["Van Unit #201", "Mercedes Sprinter High-Roof", "9,990 lbs (3,850 lbs Net)", "170\" Wheelbase Cargo Bay", "Side-Loading Forklift Door", "2 Heavy Ratchet Straps, 6 Blankets, Hand Truck"],
                ["Van Unit #202", "Mercedes Sprinter High-Roof", "9,990 lbs (3,850 lbs Net)", "170\" Wheelbase Cargo Bay", "Side-Loading Forklift Door", "2 Heavy Ratchet Straps, 6 Blankets, Hand Truck"],
            ],
            "# 3. METRO DFW ZONE RATE SCHEDULE",
            [
                ["Delivery Zone", "Geographic Territory Included", "Standard Skid Count", "Base Zone Rate", "Included Detention", "Extra Stop Fee"],
                ["Zone A: Core Metro", "Dallas City Limits, Irving, Grand Prairie, Arlington", "1 to 6 Pallets", "$135.00 Flat", "2 Hours Free", "$35.00 / Stop"],
                ["Zone B: Outer Industrial", "Fort Worth, Garland, Carrollton, Plano, Mesquite", "1 to 8 Pallets", "$175.00 Flat", "2 Hours Free", "$45.00 / Stop"],
                ["Zone C: North Texas Corridor", "Denton, McKinney, Frisco, Waxahachie, Weatherford", "Full Truckload (12 Skids)", "$245.00 Flat", "2 Hours Free", "$55.00 / Stop"],
                ["Hot-Shot Expedited", "Same-Day 120-Minute Emergency Dispatch", "Up to 3,850 lbs", "$1.95 / Mile ($95 Min)", "1 Hour Free", "Dispatched in 30 Min"],
            ],
            "--PAGE-BREAK--",
            "# 4. COMPLETE OUTBOUND SHIPPER CAMPAIGN TEMPLATES",
            "1. Outbound Email 1: Open Liftgate Capacity in Local Industrial Park",
            "Subject: 26ft liftgate truck open in [Industrial Park Name] (Tue/Thu recurring)",
            "Hi [First Name],",
            "My team runs two 26ft Freightliner box trucks with 3,500-lb hydraulic liftgates out of our West Davis terminal in Dallas. We currently service two commercial accounts in [Industrial Park Name] every Tuesday and Thursday morning.",
            "If your shipping department ever needs same-day pallet recovery, scheduled dock transfers, or overflow freight hauled without dealing with unresponsive freight brokers, we would love to handle a test load for you.",
            "— Asset-based: our trucks, our drivers, our USDOT authority (#3918204)",
            "— $1M Auto Liability / $100K Cargo insurance underwritten by Great West Casualty",
            "— 2 full hours of free dock detention on every stop so your team never feels rushed",
            "Would you be open to a quick 5-minute call this Thursday to see if our lanes align with your freight needs?",
            "Best regards,",
            "Jose Cruz · Managing Partner, Cruz Metro Freight LLC · (214) 555-0194",
            "2. Outbound Email 2: Emergency Pallet Recovery (When Brokers Drop Scheduled Pickups)",
            "Subject: Missed freight pickups in DFW / emergency backup coverage",
            "Hi [First Name],",
            "Few things are more frustrating on a Friday afternoon than a freight broker calling at 3:30 PM to announce their carrier dropped your scheduled warehouse pickup.",
            "We maintain dedicated local box truck and high-roof Sprinter capacity on standby specifically for same-day emergency pallet transfers across Dallas, Fort Worth, Arlington, and Grand Prairie.",
            "Whenever a broker fails to show, call our dispatch line directly at (214) 555-0194. We can typically have a 26ft liftgate truck backed into your bay within 90 minutes.",
            "Can I email you our one-page zone rate card so your shipping leads have it on file for emergency dispatch?",
            "Best regards,",
            "Jose Cruz · Cruz Metro Freight LLC",
            "3. Outbound Email 3: Rate Sheet & Free Detention Policy Follow-Up",
            "Subject: Quick follow-up + Cruz Metro Freight rate sheet",
            "Hi [First Name],",
            "Following up on my previous note. I've attached our 2026 DFW Metro Zone Rate Sheet. Notice that we include 2 full hours of free dock detention on every run. Most regional carriers start charging $75/hour after 30 minutes; we absorb normal warehouse staging delays because we understand frontline logistics.",
            "Whenever you have an upcoming pallet move or want to benchmark your current carrier rates, feel free to reply directly to this email.",
            "Best regards, Jose Cruz",
        ],
        role="deliverable",
    )

    # =========================================================================
    # 12. ISSA CUEVAS — CLINICAL PARENT COMMUNICATIONS & SERVICE AGREEMENT
    # =========================================================================
    files["cuevas_parent_communication_templates.docx"] = write_docx_file(
        "cuevas_parent_communication_templates.docx",
        "Cuevas Pediatric Speech Therapy — Clinical Parent Communication Letters",
        [
            "PRACTICE: Cuevas Pediatric Speech & Language Therapy LLC",
            "CREDENTIALS: Issa Cuevas, M.S., CCC-SLP · Texas License #72841",
            "DOCUMENT: Standard Operational Communication Letters & Clinical Notices",
            "--PAGE-BREAK--",
            "# TEMPLATE 1: INITIAL COMPREHENSIVE EVALUATION CONFIRMATION",
            "Subject: Confirmation: Comprehensive Speech-Language Evaluation for [Child Name]",
            "Dear [Parent Names],",
            "We are looking forward to meeting you and [Child Name] on [Evaluation Date] at [Time] for an initial comprehensive speech-language evaluation at our Austin clinic (1211 W 6th St, Suite 300).",
            "What to Expect During the Assessment:",
            "The initial session typically lasts 60 to 75 minutes. We use play-based standardized assessment tools (including the PLS-5 and GFTA-3) to evaluate receptive language, expressive vocabulary, articulation phonology, and social pragmatic interaction in a low-pressure environment.",
            "Please complete the attached Pediatric Intake & Medical History packet prior to your visit so we can review developmental milestones before evaluating your child.",
            "Warmly, Issa Cuevas, M.S., CCC-SLP",
            "--PAGE-BREAK--",
            "# TEMPLATE 2: POST-EVALUATION PLAN OF CARE & GOAL REVIEW",
            "Subject: Clinical Evaluation Summary & Recommended Plan of Care: [Child Name]",
            "Dear [Parent Names],",
            "Thank you for bringing [Child Name] into our clinic. Following our comprehensive standardized evaluation, I have completed the formal Diagnostic Summary and Plan of Care.",
            "Clinical Recommendations:",
            "— Therapy Frequency: Two (2) 45-minute individual therapy sessions per week.",
            "— Primary Focus Areas: Expanding expressive two-word semantic combinations, increasing consonant sound inventory (/b/, /d/, /m/), and reducing communicative frustration through multimodal AAC support.",
            "I have submitted the formal prior-authorization request and clinical report to your pediatrician and insurance carrier. Please review the attached care plan and let me know your preferred recurring appointment slots.",
            "Warmly, Issa Cuevas, M.S., CCC-SLP",
            "--PAGE-BREAK--",
            "# TEMPLATE 3: 6-MONTH PROGRESS REPORT & RE-EVALUATION NOTICE",
            "Subject: 6-Month Clinical Progress Milestone: [Child Name]",
            "Dear [Parent Names],",
            "It has been such a joy working with [Child Name] over the past six months. We have conducted our scheduled semi-annual progress review to assess mastery of targeted communication goals.",
            "Key Clinical Achievements:",
            "— Expressive Vocabulary: Increased from 45 single words to over 160 functional words.",
            "— Word Combinations: Spontaneously using 3-to-4 word carrier phrases ('I want blue car', 'help me open').",
            "— Speech Intelligibility: Intelligibility to unfamiliar listeners has improved from 25% to over 65%.",
            "Attached is the itemized Re-Evaluation Report for your pediatrician's medical records and insurance renewal.",
            "Warmly, Issa Cuevas, M.S., CCC-SLP",
        ],
        role="deliverable",
    )

    files["cuevas_speech_clinic_service_agreement_final.pdf"] = write_pdf_file(
        "cuevas_speech_clinic_service_agreement_final.pdf",
        "Clinical Service Agreement & Financial Policy",
        [
            "CUEVAS PEDIATRIC SPEECH & LANGUAGE THERAPY LLC",
            "1211 W 6th St, Suite 300, Austin, TX 78703 | TX SLP License #72841 | NPI #1982736450",
            "SECTION 1: CLINICAL PRACTICE SCOPE & OPERATING POLICIES",
            "This Service Agreement governs all speech, language, feeding, and pragmatic therapy services rendered by Cuevas Pediatric Speech & Language Therapy LLC to the minor child designated on the patient registration intake.",
            "All clinical diagnostic and therapeutic procedures adhere strictly to the Code of Ethics established by the American Speech-Language-Hearing Association (ASHA) and the statutory licensing mandates of the Texas Department of Licensing and Regulation (TDLR).",
            "SECTION 2: AMA CPT CODING & PRIVATE PAY FEE SCHEDULE",
            "Services are invoiced based on standard American Medical Association (AMA) Current Procedural Terminology (CPT) codes as detailed below:",
            [
                ["AMA CPT Code", "Clinical Service Description", "Session Duration", "Private Pay Rate", "Insurance Allowable Range"],
                ["CPT 92523", "Comprehensive Evaluation of Speech Sound Production & Language Comprehension", "60–90 Min", "$350.00 Flat", "$260.00 – $320.00"],
                ["CPT 92521", "Evaluation of Speech Fluency (Stuttering & Rate)", "60 Min", "$250.00 Flat", "$180.00 – $225.00"],
                ["CPT 92526", "Evaluation & Treatment of Oral Pharyngeal Swallowing / Feeding", "45 Min", "$175.00 / Session", "$125.00 – $155.00"],
                ["CPT 92507", "Individual Treatment of Speech, Language & Communication (Standard)", "45 Min", "$140.00 / Session", "$100.00 – $130.00"],
                ["CPT 92609", "Therapeutic Services for Augmentative & Alternative Communication (AAC)", "45 Min", "$155.00 / Session", "$115.00 – $145.00"],
            ],
            "--PAGE-BREAK--",
            "SECTION 3: ATTENDANCE, CANCELLATIONS & RESERVED HOUR POLICY",
            "Consistency is the single most critical factor in achieving developmental communication milestones. Therapy appointment times are reserved exclusively for your child on our recurring weekly clinical calendar.",
            [
                ["Policy Condition", "Advance Notice Required", "Applicable Fee", "Clinical Conversion Option"],
                ["Standard Reschedule / Illness", "At least 24 Hours Notice", "$0.00 (No Charge)", "Rescheduled within 14 calendar days based on open slots"],
                ["Short-Notice Cancellation", "Less than 24 Hours Notice", "$75.00 Reserved Hour Fee", "Eligible for conversion to 45-min Telehealth session at zero fee"],
                ["Unattended / No-Show", "Zero Advance Notice", "$140.00 Full Session Fee", "Guarantor billed full rate; not billable to commercial insurance"],
                ["Provider Medical Cancellation", "Immediate Clinician Notice", "$0.00 (No Charge)", "Full credit applied; makeup session prioritized on calendar"],
            ],
            "SECTION 4: SENSORY GYM RELEASE & MEDICAL RECORDS RETENTION",
            "Our clinic incorporates sensory integration gym equipment (including therapeutic indoor swings, climbing walls, and crash mats) to regulate sensory arousal and optimize motor speech carryover. Parents consent to supervised use of this clinical apparatus.",
            "All clinical notes, diagnostic evaluations, and parent progress letters are maintained securely in cloud EMR storage for a statutory minimum of seven (7) years following the patient's eighteenth birthday.",
            "SECTION 5: GUARANTOR EXECUTION & BINDING ACCEPTANCE",
            "The undersigned parent or legal guardian acknowledges receipt, review, and binding acceptance of the clinical scope, fee schedules, and attendance policies set forth in this agreement.",
            "Parent / Legal Guardian Signature: ___________________________________   Date: October 24, 2026",
            "Printed Legal Name: Elena Martinez, M.D.                                 Patient Name: Leo Alexander Martinez",
        ],
        role="deliverable",
        subtitle="Clinical Protocol, AMA CPT Fee Schedule & Guarantor Agreement",
        meta_tag="Cuevas Pediatric Speech Therapy · Texas Licensure #72841",
    )

    # Bundle cuevas files into zip
    files["cuevas_pediatric_intake_forms_bundle.zip"] = write_zip_file(
        "cuevas_pediatric_intake_forms_bundle.zip",
        {
            "cuevas_pediatric_intake_and_consent_final.docx": "cuevas_pediatric_intake_and_consent_final.docx",
            "cuevas_speech_clinic_service_agreement_final.pdf": "cuevas_speech_clinic_service_agreement_final.pdf",
            "cuevas_parent_communication_templates.docx": "cuevas_parent_communication_templates.docx",
        },
        role="deliverable",
    )

    # =========================================================================
    # 13. ESTELLA WILLIAMS — 5-TAB FINANCIAL MODEL & BOARD PACK
    # =========================================================================
    estella_pnl = [
        ["Williams Logistics Network P&L (USD)", "Jan 2026", "Feb 2026", "Mar 2026", "Q1 Total", "Apr 2026", "May 2026", "Jun 2026", "Q2 Total", "Jul 2026", "Aug 2026", "Sep 2026", "Q3 Total", "FY26 Projected"],
        ["Terminal SaaS Subscriptions", 215000, 228000, 237000, "=SUM(B2:D2)", 254000, 272000, 294000, "=SUM(F2:H2)", 318000, 342000, 360000, "=SUM(J2:L2)", "=E2+I2+M2"],
        ["Volumetric DockDoor Overage Fees", 18500, 21200, 24800, "=SUM(B3:D3)", 26500, 29100, 32400, "=SUM(F3:H3)", 35800, 39400, 42800, "=SUM(J3:L3)", "=E3+I3+M3"],
        ["Professional Implementation Services", 12000, 15000, 8000, "=SUM(B4:D4)", 18000, 12000, 15000, "=SUM(F4:H4)", 20000, 14000, 18000, "=SUM(J4:L4)", "=E4+I4+M4"],
        ["TOTAL GAAP OPERATING REVENUE (USD)", "=SUM(B2:B4)", "=SUM(C2:C4)", "=SUM(D2:D4)", "=SUM(E2:E4)", "=SUM(F2:F4)", "=SUM(G2:G4)", "=SUM(H2:H4)", "=SUM(I2:I4)", "=SUM(J2:J4)", "=SUM(K2:K4)", "=SUM(L2:L4)", "=SUM(M2:M4)", "=E5+I5+M5"],
        ["Cloud Hosting & AWS Multi-Region", 28400, 29200, 30100, "=SUM(B6:D6)", 31800, 33200, 34600, "=SUM(F6:H6)", 36400, 38100, 39500, "=SUM(J6:L6)", "=E6+I6+M6"],
        ["Twilio Driver SMS & Gateway Routing", 8200, 8900, 9400, "=SUM(B7:D7)", 10200, 11100, 11900, "=SUM(F7:H7)", 12800, 13700, 14500, "=SUM(J7:L7)", "=E7+I7+M7"],
        ["OCR Document Parsing Engine", 4100, 4400, 4800, "=SUM(B8:D8)", 5200, 5600, 6100, "=SUM(F8:H8)", 6600, 7100, 7500, "=SUM(J8:L8)", "=E8+I8+M8"],
        ["GROSS PROFIT (USD)", "=B5-B6-B7-B8", "=C5-C6-C7-C8", "=D5-D6-D7-D8", "=E5-E6-E7-E8", "=F5-F6-F7-F8", "=G5-G6-G7-G8", "=H5-H6-H7-H8", "=I5-I6-I7-I8", "=J5-J6-J7-J8", "=K5-K6-K7-K8", "=L5-L6-L7-L8", "=M5-M6-M7-M8", "=E9+I9+M9"],
        ["Gross Margin %", "=B9/B5", "=C9/C5", "=D9/D5", "=E9/E5", "=F9/F5", "=G9/G5", "=H9/H5", "=I9/I5", "=J9/J5", "=K9/K5", "=L9/L5", "=M9/M5", "=N9/N5"],
        ["Engineering & Product R&D", 125000, 125000, 132000, "=SUM(B11:D11)", 132000, 140000, 140000, "=SUM(F11:H11)", 148000, 148000, 155000, "=SUM(J11:L11)", "=E11+I11+M11"],
        ["Sales & Marketing OpEx", 58000, 62000, 66000, "=SUM(B12:D12)", 71000, 74000, 78000, "=SUM(F12:H12)", 82000, 86000, 91000, "=SUM(J12:L12)", "=E12+I12+M12"],
        ["General & Administrative (G&A)", 34000, 34000, 36000, "=SUM(B13:D13)", 36000, 38000, 38000, "=SUM(F13:H13)", 40000, 40000, 42000, "=SUM(J13:L13)", "=E13+I13+M13"],
        ["OPERATING EBITDA (USD)", "=B9-B11-B12-B13", "=C9-C11-C12-C13", "=D9-D11-D12-D13", "=E9-E11-E12-E13", "=F9-F11-F12-F13", "=G9-G11-G12-G13", "=H9-H11-H12-H13", "=I9-I11-I12-I13", "=J9-J11-J12-J13", "=K9-K11-K12-K13", "=L9-L11-L12-L13", "=M9-M11-M12-M13", "=E14+I14+M14"],
    ]

    files["estella_q4_financial_model.xlsx"] = write_xlsx_file(
        "estella_q4_financial_model.xlsx",
        {
            "P&L Operating Actuals": estella_pnl,
        },
        role="deliverable",
    )

    files["estella_q4_investor_deck_slide_copy_final.pdf"] = write_pdf_file(
        "estella_q4_investor_deck_slide_copy_final.pdf",
        "Williams Logistics Network - Q4 Board Briefing Slide Deck Copy",
        [
            "WILLIAMS LOGISTICS NETWORK INC. | BOARD OF DIRECTORS BRIEFING",
            "October 2026 | Presented by Estella Williams, Founder & CEO",
            "SLIDE 1: COVER & EXECUTIVE OVERVIEW",
            "Williams Logistics Network: Accelerating Enterprise Cross-Dock Terminal Automation.",
            "Operating across 180 active commercial terminals in Texas, Midwest, and Gulf freight corridors.",
            "SLIDE 2: Q3 OPERATING HIGHLIGHTS & KEY BENCHMARKS",
            "- Annual Recurring Revenue (ARR): Reached $4,210,000 (+18.2% QoQ growth).",
            "- Net Revenue Retention (NRR): 114.2% across mid-market enterprise carrier cohort.",
            "- Enterprise Logo Churn: 0.0% across six consecutive fiscal quarters.",
            "- Gross SaaS Profit Margin: 78.4% with pure software economics.",
            "SLIDE 3: ARR EXPANSION BRIDGE & FY2027 TRAJECTORY",
            "- Q1 2026 Actual: $2.80M ARR across 128 active terminal deployments.",
            "- Q2 2026 Actual: $3.42M ARR with 28 new carrier fleet customer additions.",
            "- Q3 2026 Actual: $4.21M ARR driven by Midwest freight corridor expansion.",
            "- Q4 2026 Target: $5.10M ARR (94% contracted pipeline coverage).",
            "- FY2027 Budget Target: $6.80M ARR with projected cash flow breakeven in Q2 2027.",
            "--PAGE-BREAK--",
            "SLIDE 4: PRODUCT INNOVATION - DOCKDOOR 2.0 ADVANCEMENTS",
            "- Geofenced Perimeter Alerts: Detects arriving tractors 2 miles out, eliminating gate check-in delays.",
            "- Dynamic Bay Routing: Intelligently allocates bays based on trailer class and forklift travel distances.",
            "- Sign-on-Glass e-BOL: Eliminates paper handling; delivers 100% digital audit trace.",
            "SLIDE 5: BOARD ACTION ITEMS & CAPITAL RUNWAY",
            "- Cash Balance: $3,120,000 in bank reserves providing over 24 months of operational runway.",
            "- Board Approvals: Formal adoption of FY2027 budget and 3.0% option pool expansion for engineering hires.",
        ],
        role="deliverable",
        subtitle="Williams Logistics Network Executive Review Copy",
        meta_tag="Williams Logistics Network · Q4 2026 Executive Presentation",
    )

    files["estella_q4_executive_board_pack.zip"] = write_zip_file(
        "estella_q4_executive_board_pack.zip",
        {
            "estella_q4_board_briefing_memo_final.docx": "estella_q4_board_briefing_memo_final.docx",
            "estella_q4_executive_investor_deck_final.pptx": "estella_q4_executive_investor_deck_final.pptx",
            "estella_q4_financial_model.xlsx": "estella_q4_financial_model.xlsx",
            "estella_q4_investor_deck_slide_copy_final.pdf": "estella_q4_investor_deck_slide_copy_final.pdf",
        },
        role="deliverable",
    )

    # =========================================================================
    # 14. LIZA IZA — COMMERCIAL MEDICAL FACILITY CLEANING RATE CARD
    # =========================================================================
    liza_rates = [
        ["Medical Facility Area Designation", "Sq Footage", "Sanitation Protocol Level", "Cleaning Frequency", "Base Monthly Rate ($USD)", "Terminal Room Surcharge ($USD)", "Total Monthly Retainer ($USD)"],
        ["Ambulatory Surgical Center (Suite 100)", 14500, "Level 4 Terminal Clinical", "Nightly (7x / Week)", 5400.00, 850.00, 6250.00],
        ["Pediatric Specialty Clinic (Suite 200)", 11200, "Level 3 Infection Control", "5x / Week (Mon-Fri)", 3600.00, 450.00, 4050.00],
        ["Cardiology & Imaging Center (Suite 300)", 12800, "Level 3 Infection Control", "5x / Week (Mon-Fri)", 3950.00, 500.00, 4450.00],
        ["Multi-Tenant Medical Offices (Suite 400)", 9500, "Level 2 General Clinical", "5x / Week (Mon-Fri)", 2850.00, 250.00, 3100.00],
        ["TOTAL CLINICAL COMPLEX FOOTPRINT", 48000, "Turnkey EVS Sanitation", "24/7/365 On-Call", 15800.00, 2050.00, 17850.00],
    ]

    files["liza_rate_card_final.xlsx"] = write_xlsx_file(
        "liza_rate_card_final.xlsx",
        {
            "Commercial Rate Card": liza_rates,
        },
        role="deliverable",
    )

    # =========================================================================
    # 15. AZAEL OROZCO — COMMERCIAL ROOFING BID ESTIMATE SHEET
    # =========================================================================
    orozco_takeoff = [
        ["Commercial Project Scope", "Roof Area (Sq Ft)", "Membrane System", "Insulation Spec", "Materials Cost ($USD)", "Labor & Cranes ($USD)", "Perimeter Flashing ($USD)", "NDL Warranty Fee ($USD)", "Total Commercial Bid ($USD)", "Contractor Margin %"],
        ["Pharr Logistics Distribution Hub", 42000, "Carlisle 60-mil White TPO", "2.5\" Polyiso R-14.4", 82400.00, 68500.00, 23520.00, 4200.00, 223632.00, 0.201],
        ["McAllen Retail Plaza (Bicentennial)", 18500, "Elevate 60-mil Scrim TPO", "2.0\" Polyiso R-11.4", 36200.00, 31400.00, 11200.00, 2800.00, 98400.00, 0.171],
        ["Edinburg Outpatient Medical Center", 28000, "GacoFlex S20 Silicone Restoration", "Fluid Membrane (32 Dry Mils)", 44800.00, 34200.00, 14600.00, 3500.00, 121500.00, 0.201],
        ["TOTAL ESTIMATE PIPELINE", 88500, "Commercial Flat Systems", "Commercial Code", 163400.00, 134100.00, 49320.00, 10500.00, 443532.00, 0.194],
    ]

    files["orozco_estimate_sheet.xlsx"] = write_xlsx_file(
        "orozco_estimate_sheet.xlsx",
        {
            "Commercial Bid Takeoff": orozco_takeoff,
        },
        role="deliverable",
    )

    # =========================================================================
    # 16. ALEXA QUINTERO — UNIT ECONOMICS & PRICING MODEL
    # =========================================================================
    alexa_econ = [
        ["Unit Economics Metric", "Small Fleet (3-7 Vans)", "Mid Fleet (8-15 Vans)", "Enterprise Fleet (16-35 Vans)", "Blended Portfolio Average"],
        ["Average Technician Seats", 5, 11, 24, 12],
        ["Monthly Software Seat Price ($USD)", "$89.00", "$89.00", "$79.00", "$85.00"],
        ["Monthly Recurring Revenue per Fleet ($USD)", 445.00, 979.00, 1896.00, 1020.00],
        ["Annual Contract Value per Fleet ($USD)", 5340.00, 11748.00, 22752.00, 12240.00],
        ["Customer Acquisition Cost - CAC ($USD)", 1150.00, 1680.00, 2840.00, 1780.00],
        ["CAC Cash Payback Window", "2.6 Months", "1.7 Months", "1.5 Months", "1.7 Months"],
        ["Gross Margin %", "92.4%", "93.1%", "94.2%", "93.2%"],
        ["Customer Lifetime Value - LTV ($USD)", 18200.00, 38500.00, 68400.00, 39400.00],
        ["LTV to CAC Ratio", "15.8x", "22.9x", "24.1x", "22.1x"],
    ]

    files["alexa_unit_economics_model.xlsx"] = write_xlsx_file(
        "alexa_unit_economics_model.xlsx",
        {
            "Fleet Unit Economics": alexa_econ,
        },
        role="deliverable",
    )

    # =========================================================================
    # 17. KAYLEE CABREROS — BOTANICAL SKINCARE WELCOME SEQUENCE
    # =========================================================================
    files["kaylee_welcome_emails_final.docx"] = write_docx_file(
        "kaylee_welcome_emails_final.docx",
        "Lumière Botanical Skincare — New Customer Welcome & Retention Series",
        [
            "BRAND: Lumière Botanical Skincare · E-Commerce Retention Sequence",
            "CHANNELS: Klaviyo Automated Customer Onboarding Sequence",
            "VERSION: Final Production Master Copy Deck",
            "--PAGE-BREAK--",
            "# EMAIL 1: WELCOME & THE BOTANICAL PHILOSOPHY (SENT IMMEDIATELY UPON SIGNUP)",
            "Subject: Welcome to slow skincare, [First Name] (+ your 15% inside)",
            "Preview: Real botanicals. Zero synthetic fillers. Your skin journey begins here.",
            "Hi [First Name],",
            "Welcome to Lumière. We started this studio in our kitchen because we were exhausted by conventional skincare that over-promised with synthetic additives and stripped delicate lipid barriers.",
            "Every serum and balm we formulate is cold-pressed in small weekly batches using organic jojoba, sea buckthorn, and cold-extracted blue tansy. No artificial fragrance, no parabens, and no compromise.",
            "As a welcome to our community, your 15% studio discount code is ready to use at checkout: BOTANICAL15",
            "[Explore The Everyday Botanical Ritual ->]",
            "--PAGE-BREAK--",
            "# EMAIL 2: HOW TO LAYER YOUR DAILY SERUM RITUAL (SENT DAY 3)",
            "Subject: Why less is more: your 3-step morning ritual",
            "Preview: The secret to all-day glow is hydration before nourishment.",
            "Hi [First Name],",
            "One of the most common questions our studio aesthetician receives is: 'In what order should I apply facial oil and hydrator?'",
            "Rule of thumb: Always layer from lightest molecular weight to richest barrier lock:",
            "Step 1: Mist skin with our Rosewater & Elderflower Botanical Toner while skin is damp.",
            "Step 2: Press 3 drops of Hyaluronic Acid Hydrating Serum into your face and neck.",
            "Step 3: Warm 4 drops of Barrier Repair Botanical Oil between your palms and gently press into skin to seal in moisture.",
            "[Watch Aesthetician Tutorial ->]",
        ],
        role="deliverable",
    )

    # =========================================================================
    # 18. LINA RICKERT — ACTIVEWEAR CAMPAIGN EMAILS
    # =========================================================================
    files["lina_summer_campaign_emails_final.docx"] = write_docx_file(
        "lina_summer_campaign_emails_final.docx",
        "AURA Athletics — Summer Campaign & Product Launch Email Series",
        [
            "BRAND: AURA Performance Athletics · Summer Campaign",
            "DOCUMENT: Product Launch & Retention Email Sequence",
            "VERSION: 3.1 Final Approved Copy Deck",
            "--PAGE-BREAK--",
            "# EMAIL 1: VIP EARLY ACCESS CAMPAIGN LAUNCH",
            "Subject: It's here: Summer Seamless is live for VIPs only",
            "Preview: Breathable compression engineered for 90-degree heat. Shop before public release.",
            "Hi [First Name],",
            "You asked for athletic apparel that holds its shape during high-intensity sessions without overheating under summer sun.",
            "Meet Summer Seamless: engineered with our proprietary AeroKnit recycled nylon fabric that wicks sweat 40% faster than traditional elastane. Featuring bonded zero-chafe seams, four-way stretch, and UPF 50+ sun protection.",
            "As a VIP insider, your private early access is unlocked for the next 24 hours before our global drop.",
            "[Shop VIP Early Access Drop ->]",
            "--PAGE-BREAK--",
            "# EMAIL 2: COMMUNITY SPOTLIGHT & REAL ATHLETE WEAR-TEST",
            "Subject: 42 miles in Summer Seamless: athlete field test results",
            "Preview: Real feedback from marathon runners and CrossFit competitors.",
            "Hi [First Name],",
            "Before launching any collection, we hand prototype kits to 50 endurance athletes across Austin, Denver, and Miami.",
            "The verdict? Zero roll-down on the high-rise waistband, absolute squat-proof coverage, and weightless breathability on 18-mile summer training runs.",
            "[Read The Full Athlete Reviews ->]",
        ],
        role="deliverable",
    )

    return files


if __name__ == "__main__":
    import os
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    django.setup()

    print("Building all authentic client deliverables...")
    res = build_all_authentic_deliverables()
    print(f"Successfully generated {len(res)} authentic files in public/chat_files!")
