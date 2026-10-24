"""
estella.py - Estella Williams (Apex Fleet & Logistics) Deliverables
Authentic executive board packs, investor presentations, role onboarding SOPs, newsletters, and financial models.
"""

from platformhub.chat_files import write_docx_file, write_pdf_file, write_pptx_file

def build_estella_deliverables() -> dict[str, dict]:
    files = {}

    # 1. estella_4role_onboarding_sops_v1.docx: Master role onboarding SOPs (v1 working draft)
    files["estella_4role_onboarding_sops_v1.docx"] = write_docx_file(
        "estella_4role_onboarding_sops_v1.docx",
        "Apex Fleet Operations — Master Role Onboarding SOPs (v1 Operational Working Draft)",
        [
            "ORGANIZATION: Apex Logistics & Fleet Systems LLC · Operations Division",
            "EXECUTIVE SPONSOR: Estella Williams, Vice President of Fleet Operations",
            "TERMINAL LOCATIONS: Chicago Hub (HQ), Memphis Multimodal, Dallas-Fort Worth Depot",
            "DOCUMENT: Master Role Onboarding Standard Operating Procedures (4 Core Roles)",
            "VERSION: 1.0 Working Operational Draft",
            "--PAGE-BREAK--",
            "# ROLE 1: SENIOR TERMINAL DISPATCH MANAGER (SOP-DISP-01)",
            "Mission: Direct real-time terminal dispatch, enforce FMCSA Hours of Service (HOS) driver compliance, minimize trailer dwell time, and maximize revenue-per-loaded-mile across regional corridors.",
            "Daily Operating Cadence:",
            "— 05:30 – 06:15: Morning Yard Audit & Equipment Walkthrough. Physically verify that outbound tractors and trailers match Samsara telematics GPS coordinates. Confirm pre-trip electronic vehicle inspection reports (e-DVIR) are cleared by maintenance.",
            "— 06:15 – 08:30: Primary Dispatch Assignment & Driver Briefings. Conduct face-to-face or cab-radio dispatch briefings. Review route turnpikes, forecasted adverse weather, customer delivery appointment windows, and required E-track load bar bracing.",
            "— 08:30 – 12:00: Active Corridor Monitoring & Load-Matching. Monitor McLeod LoadMaster dispatch board. Coordinate cross-dock staging with warehouse shift leads. Re-assign open trailer capacity for backhauls.",
            "— 13:00 – 15:30: Mid-Day HOS Review & Demurrage Auditing. Review driver duty status logs on Samsara ELD. Flag drivers approaching 11-hour driving or 14-hour duty limits. Intervene on deliveries exceeding 90 minutes of dock detention to enforce $75/hr detention billing.",
            "— 16:30 – 17:30: Evening Shift Handover & Next-Day Planning. Stage next-day bills of lading (BOL), verify fuel card limits, and conduct structured handover to Night Dispatch Lead.",
            "--PAGE-BREAK--",
            "# ROLE 2: LEAD COMMERCIAL DIESEL TECHNICIAN (SOP-TECH-02)",
            "Mission: Maintain fleet roadworthiness, execute preventative maintenance (PM) cycles, conduct annual DOT safety inspections, and maintain zero out-of-service (OOS) roadside inspection violations.",
            "Technical Compliance Standards:",
            "— Preventative Maintenance Cycles: Service-A (Oil, lube, fuel filters, brake stroke check) every 15,000 miles. Service-B (Coolant flush, transmission fluid, differential lube, full driveline inspection) every 45,000 miles.",
            "— Tire Safety Standards: Steer tires must maintain minimum 4/32-inch tread depth; drive and trailer tires minimum 2/32-inch. Tire pressures must be checked cold and inflated to 105 PSI.",
            "— Electronic Diagnostics: Utilize Detroit Diesel Diagnostic Link (DDDL) and Cummins INSITE to extract active engine fault codes (SPN/FMI). Clear resolved codes and log technician repair notes into TMW Fleet Maintenance software.",
            "--PAGE-BREAK--",
            "# ROLE 3: CROSS-BORDER SAFETY & REGULATORY COORDINATOR (SOP-SAFE-03)",
            "Mission: Enforce Federal Motor Carrier Safety Regulations (49 CFR Parts 350-399), oversee Driver Qualification (DQ) files, administer DOT random drug and alcohol testing, and manage cargo claims.",
            "Compliance Checklists:",
            "— Driver Qualification (DQ) File Audit: Annually verify motor vehicle records (MVR), commercial driver's license (CDL-A) expiration dates, and current FMCSA Medical Examiner's Certificates (Form MCSA-5876).",
            "— DOT Random Drug & Alcohol Testing: Administer quarterly random testing pools meeting FMCSA minimums (50% drug, 10% alcohol) via Quest Diagnostics SAP network.",
            "— Roadside Inspection Audit: Audit every state police Level 1, 2, and 3 inspection report. Challenge erroneous violations via FMCSA DataQs portal within 14 days of citation.",
            "--PAGE-BREAK--",
            "# ROLE 4: FREIGHT BILLING & DEMURRAGE SPECIALIST (SOP-BILL-04)",
            "Mission: Reconcile completed trip manifests, audit electronic proof-of-delivery (e-POD) documents, calculate detention charges, and execute accurate freight invoicing within 24 hours of delivery.",
            "Invoicing Protocols:",
            "— BOL Verification: Confirm receiver signature, legible date/time stamp, and piece counts against customer rate confirmation sheet.",
            "— Detention Settlement: Compare Samsara geofenced dock entry/exit time stamps against customer appointment windows. Calculate detention charges for time exceeding 120 minutes of free time.",
            "— Fuel Surcharge (FSC) Indexing: Apply current EIA national average diesel fuel index formula to compute weekly fuel adjustment surcharge.",
        ],
        role="draft",
    )

    # 2. estella_rough_role_notes.docx: Working role staffing notes
    files["estella_rough_role_notes.docx"] = write_docx_file(
        "estella_rough_role_notes.docx",
        "Apex Fleet Operations — Terminal Staffing Requirements, Role Descriptions & KPI Benchmarks",
        [
            "AUTHOR: Estella Williams, VP Fleet Operations",
            "RECIPIENT: HR Committee & Terminal General Managers",
            "DATE: October 2026",
            "PURPOSE: Staffing Specifications for 2027 Midwest Network Expansion",
            "--PAGE-BREAK--",
            "# STAFFING GAPS & RECRUITING PRIORITIES",
            "With the launch of our Memphis interchange terminal in Q1 2027, Apex must hire and onboard four key operational roles across each of our three primary logistics hubs:",
            "— Terminal Dispatch Manager: Target 5+ years experience in Class-8 tractor-trailer dispatch using McLeod or TMW software. Compensation: $78k – $92k base + quarterly safety/on-time performance bonus.",
            "— Lead Diesel Mechanic: ASE T2-T8 Master Medium/Heavy Truck certification preferred. Target 7+ years hands-on experience with Detroit DD15 and Cummins X15 platforms. Compensation: $38 – $45 / hour + tool allowance.",
            "— Cross-Border Safety Coordinator: In-depth knowledge of FMCSA CSA scores, FAST card clearance, and Canada-US border customs documentation (ACI eManifest / ACE). Compensation: $68k – $80k base.",
            "— Freight Billing Specialist: High-volume 3PL billing experience with factoring reconciliation and TMS billing integrations. Compensation: $26 – $32 / hour.",
            "--PAGE-BREAK--",
            "# TERMINAL KPI BENCHMARKS",
            [
                ["Role Title", "Primary Key Performance Indicator (KPI)", "Target Operational Standard", "Review Frequency"],
                ["Terminal Dispatch Manager", "On-Time Pickup & Delivery Metric", ">= 98.5% across all regional routes", "Weekly Scorecard"],
                ["Lead Diesel Mechanic", "Fleet Out-of-Service (OOS) Roadside Rate", "< 2.5% (National average is 20.8%)", "Monthly Maintenance Audit"],
                ["Safety Coordinator", "FMCSA BASIC Safety Measurement Score", "< 35% in all 7 measurement categories", "Monthly CSA Dashboard"],
                ["Billing Specialist", "Days Sales Outstanding (DSO) for Freight", "< 28 calendar days from delivery date", "Bi-Weekly Cash Review"],
            ],
        ],
        role="source",
    )

    # 3. estella_october_newsletter_draft.docx: Internal monthly operating dispatch
    files["estella_october_newsletter_draft.docx"] = write_docx_file(
        "estella_october_newsletter_draft.docx",
        "Apex Logistics Monthly Operating Dispatch — October 2026 (Internal Working Draft)",
        [
            "NEWSLETTER: Apex Operating Dispatch · Volume 8, Issue 10 · October 2026",
            "AUDIENCE: 320 Drivers, Mechanics, Dispatchers, and Corporate Staff",
            "EDITOR: Estella Williams, VP Fleet Operations",
            "--PAGE-BREAK--",
            "# 1. EXECUTIVE DISPATCH: RECORD Q3 FREIGHT VOLUMES",
            "Team Apex: Thanks to your extraordinary discipline and dedication, Q3 was the strongest operating quarter in Apex history. We completed 6,840 freight dispatches across our Midwest and Southern corridors while achieving an exceptional 99.1% on-time delivery metric.",
            "Even more impressively, our fleet fuel efficiency improved to 7.42 MPG—saving over $140,000 in corridor diesel expenses through smart routing and reduced idle times.",
            "--PAGE-BREAK--",
            "# 2. DRIVER SAFETY HONOR ROLL: MILLION-MILE COMMENDATIONS",
            "Please join us in celebrating four outstanding professional drivers who crossed the historic milestone of One Million Accident-Free Highway Miles this month:",
            "— Marcus Vance (Chicago Terminal, 12 years with Apex)",
            "— Darrell Jenkins (Memphis Terminal, 9 years with Apex)",
            "— Hector Ramirez (Dallas Terminal, 11 years with Apex)",
            "— Sarah Lindqvist (Chicago Terminal, 8 years with Apex)",
            "Each driver will receive a personalized leather flight jacket, custom gold truck cab badge, and a $2,500 safety achievement bonus at our annual winter banquet.",
            "--PAGE-BREAK--",
            "# 3. WINTER PREPAREDNESS & FLEET MAINTENANCE ADVISORY",
            "With freezing temperatures approaching our northern routes, all company drivers must complete winter tire chain inspection and diesel anti-gel training by November 1.",
            "Maintenance shops are currently installing new engine block heaters and testing cold-cranking amp capacity on all tractor batteries.",
        ],
        role="source",
    )

    # 4. estella_q4_board_deck_rough_bullets.docx: Raw board review bullets from CEO & CFO
    files["estella_q4_board_deck_rough_bullets.docx"] = write_docx_file(
        "estella_q4_board_deck_rough_bullets.docx",
        "Apex Logistics Q4 Executive Board Review — Raw Operational Bullets & Financial Notes",
        [
            "CONFIDENTIAL: Board of Directors Briefing Notes",
            "COMPANY: Apex Logistics & Fleet Systems LLC",
            "SESSION: Q4 Executive Strategy & FY2027 Capital Allocation Review",
            "PREPARED BY: Estella Williams (VP Ops), CEO, and CFO",
            "--PAGE-BREAK--",
            "# SECTION 1: FINANCIAL TRAJECTORY & EBITDA ACCRETION",
            "— Q3 Gross Operating Revenue: $18,420,000 (up 22.4% YoY compared to $15,050,000 in Q3 2025).",
            "— Q3 Adjusted EBITDA: $2,615,640 (14.2% EBITDA margin, expanding 180 basis points YoY).",
            "— Operating Ratio (OR): Improved to 87.8% from 89.6% in the prior-year period.",
            "— Free Cash Flow: $1,420,000 generated in Q3, supporting $8.5M total year-to-date cash reserves.",
            "--PAGE-BREAK--",
            "# SECTION 2: FLEET CAPACITY, UTILIZATION & DRIVER RETENTION",
            "— Active Power Units: 142 Class-8 tractors (100% late-model Freightliner Cascadia and Peterbilt 579).",
            "— Active Trailers: 380 53ft dry van and refrigerated trailers (100% equipped with carrier telematics).",
            "— Fleet Utilization: Reached 94.2% in September, outperforming the ATA industry benchmark of 88.5%.",
            "— Annualized Driver Turnover: Reduced dramatically from 68% in 2024 to 34% in Q3 2026 following our driver compensation restructuring and modern equipment upgrades.",
            "--PAGE-BREAK--",
            "# SECTION 3: 2027 STRATEGIC CAPITAL DEPLOYMENT ROADMAP",
            "— Memphis Multimodal Hub: Board authorization requested for $4.2M capital expenditure to acquire and build out a 24-bay cross-dock facility near BNSF rail interchange in Memphis, TN.",
            "— Fleet Modernization: Commit to leasing 25 new low-emission Freightliner Cascadia tractors with active collision mitigation and automated electric APUs.",
        ],
        role="source",
    )

    # 5. estella_q4_executive_investor_deck_v1.docx: v1 investor deck narrative copy
    files["estella_q4_executive_investor_deck_v1.docx"] = write_docx_file(
        "estella_q4_executive_investor_deck_v1.docx",
        "Apex Fleet & Logistics — Q4 Executive Investor Update Deck (v1 Narrative Copy)",
        [
            "DOCUMENT: Investor Update Slide Copy & Narrative Architecture (v1 Draft)",
            "AUDIENCE: Institutional Debt Partners, Equity Holders & Advisory Board",
            "DATE: October 2026",
            "--PAGE-BREAK--",
            "# SLIDE 1: EXECUTIVE TITLE & INVESTMENT THESIS",
            "Title: Apex Fleet & Logistics — Modern Regional Freight Infrastructure",
            "Subtitle: Q4 2026 Operational Performance & Network Scale Overview",
            "Core Thesis: Capitalizing on the nearshoring boom and cross-border manufacturing growth through asset-backed fleet discipline, proprietary dispatch technology, and industry-leading driver retention.",
            "--PAGE-BREAK--",
            "# SLIDE 2: THE APEX OPERATING ADVANTAGE",
            "Key Pillars: 142 late-model tractors, 380 dry/reefer trailers, 3 regional hubs, and 99.1% on-time service standard. Our asset density across the Midwest-to-Gulf corridor creates unbeatable backhaul economics.",
            "--PAGE-BREAK--",
            "# SLIDE 3: FINANCIAL PERFORMANCE OVERVIEW",
            "Q3 2026 Revenue reached $18.42M (+22.4% YoY) with Adjusted EBITDA of $2.62M (14.2% margin). Operating Ratio tightened to 87.8%. Full-year 2026 revenue is on track to surpass $72M.",
            "--PAGE-BREAK--",
            "# SLIDE 4: NETWORK MAP & TERMINAL CAPACITY",
            "Strategic coverage across Chicago (Northern Gateway), Dallas-Fort Worth (Texas Corridor), and incoming Memphis (Mid-South Rail Interchange).",
            "--PAGE-BREAK--",
            "# SLIDE 5: 2027 GROWTH CATALYSTS & CAPITAL ALLOCATION",
            "Deploying $4.2M in Memphis hub build-out, expanding dedicated customer fleets, and scaling logistics technology to reach $100M ARR by 2028.",
        ],
        role="draft",
    )

    # 6. estella_q4_investor_deck_slide_copy_final.pdf: 4-page investor deck executive companion PDF
    files["estella_q4_investor_deck_slide_copy_final.pdf"] = write_pdf_file(
        "estella_q4_investor_deck_slide_copy_final.pdf",
        "Apex Logistics — Q4 Executive Investor Deck Companion & Financial Memorandum (Final)",
        [
            "# 1. EXECUTIVE INVESTMENT MEMORANDUM",
            "Apex Logistics & Fleet Systems LLC presents this executive briefing companion to the Q4 2026 Investor Deck for debt partners, institutional equity holders, and the Board of Directors.",
            "FY2026 Financial Highlights: Full-year operating revenue projected at $72.8M, representing 24.1% year-over-year expansion with Adjusted EBITDA of $10.3M (14.1% margin).",
            "--PAGE-BREAK--",
            "# 2. KEY OPERATING & FINANCIAL METRICS BENCHMARK",
            [
                ["Operating Metric", "Q3 2025 Actual", "Q3 2026 Actual", "YoY Change %", "FY2026 Forecast"],
                ["Gross Operating Revenue", "$15,050,000", "$18,420,000", "+22.4%", "$72,800,000"],
                ["Adjusted EBITDA", "$1,866,200", "$2,615,640", "+40.2%", "$10,265,000"],
                ["Adjusted EBITDA Margin", "12.4%", "14.2%", "+180 bps", "14.1%"],
                ["Operating Ratio (OR)", "89.6%", "87.8%", "-180 bps", "87.5%"],
                ["Active Class-8 Power Units", "118 tractors", "142 tractors", "+20.3%", "150 tractors"],
                ["Fleet Capacity Utilization", "89.2%", "94.2%", "+500 bps", "93.5%"],
                ["Annualized Driver Turnover", "62.4%", "34.1%", "-2,830 bps", "< 35.0%"],
            ],
            "--PAGE-BREAK--",
            "# 3. SLIDE-BY-SLIDE INVESTOR PRESENTATION STRUCTURE",
            "— Slide 1: Executive Title & Corporate Investment Thesis.",
            "— Slide 2: Core Operating Footprint & Corridor Network Scale.",
            "— Slide 3: Financial Trajectory: Q3 Revenue & EBITDA Accretion.",
            "— Slide 4: Cost Optimization & Telematics-Driven Fuel Savings.",
            "— Slide 5: Fleet Utilization & Driver Retention Advantage.",
            "— Slide 6: Contracted Dedicated Carrier Relationships.",
            "— Slide 7: Regulatory Safety Record (FMCSA BASIC Compliance).",
            "— Slide 8: Technology Infrastructure (Samsara + McLeod TMS).",
            "— Slide 9: Memphis Terminal Expansion & CapEx Plan.",
            "— Slide 10: 2027 Financial Guidance & Long-Term Milestones.",
            "--PAGE-BREAK--",
            "# 4. CAPITAL ALLOCATION & 2027 EXPANSION GUIDANCE",
            "— Memphis Cross-Dock Acquisition: $4.2M CapEx funded via operational cash flow and revolving credit facility.",
            "— Fleet Leases: 25 new Freightliner Cascadia units scheduled for Q1 delivery with full manufacturer warranty.",
            "— Senior Leadership Sign-Off: Estella Williams, Vice President of Fleet Operations · October 2026.",
        ],
        role="deliverable",
        subtitle="4-Page Investor Presentation Companion & Strategic Financial Memorandum",
        meta_tag="Apex Fleet & Logistics · Investor Relations Dossier",
    )

    return files
