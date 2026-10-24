"""
liza.py - Liza Iza (Coastal Shine Commercial Cleaning) Deliverables
Authentic 15-page medical plaza proposal, vendor packets, rate cards, and RFP responses.
"""

from platformhub.chat_files import write_docx_file, write_pdf_file, write_xlsx_file

def build_liza_deliverables() -> dict[str, dict]:
    files = {}

    # 1. liza_15p_service_proposal_messy.docx: Authentic 15-page medical plaza RFP draft
    files["liza_15p_service_proposal_messy.docx"] = write_docx_file(
        "liza_15p_service_proposal_messy.docx",
        "Tampa Bay Medical Plaza RFP Response — 15 Pages (Client Working Draft & Scramble)",
        [
            "RFP SOLICITATION: Commercial Janitorial, Environmental Infection Control & Biohazard Services",
            "SOLICITING ENTITY: Tampa Bay Healthcare Real Estate Group, LLC",
            "FACILITY: Westshore Medical Executive Center · 4 Multi-Tenant Medical Office Buildings (48,000 RSF Total)",
            "BIDDER: Coastal Shine Commercial Cleaning LLC · Tampa, FL",
            "BID AUTHOR: Liza Iza, Managing Principal & Operations Director",
            "SUBMISSION DATE: October 2026",
            "--PAGE-BREAK--",
            "# SECTION 1: EXECUTIVE PROFILE, CORPORATE CAPABILITY & LICENSURE",
            "Coastal Shine Commercial Cleaning LLC is an asset-based commercial environmental services provider headquartered in Tampa, Florida. Established in 2018, Coastal Shine specializes in healthcare clinical facilities, ambulatory surgical centers (ASCs), diagnostic imaging facilities, and multi-tenant medical office buildings.",
            "Florida Entity Registration: Florida Division of Corporations Document #L18000219482 · Hillsborough County Business License #BL-2018-94102.",
            "Commercial Liability Insurance: $2,000,000 General Aggregate / $1,000,000 Each Occurrence Commercial General Liability underwritten by Travelers Indemnity Company. $1,000,000 Statutory Florida Workers' Compensation Insurance.",
            "Environmental Certifications: Certified Healthcare Environmental Services Technician (CHEST) accredited supervisors, OSHA 30-Hour General Industry Healthcare Safety, and ISSA Cleaning Industry Management Standard (CIMS-GB) Green Building compliant.",
            "--PAGE-BREAK--",
            "# SECTION 2: FACILITY PROFILE & 4-BUILDING SCOPE OF WORK",
            "The Westshore Medical Executive Center campus comprises four dedicated healthcare structures totaling 48,000 rentable square feet:",
            "— Building A: Westshore Ambulatory Surgery & Outpatient Center (16,000 sq ft). Includes 4 outpatient operating suites, pre-op/post-op recovery bays, sterile processing staging, and surgeon consultation rooms.",
            "— Building B: Bay Area Pediatric Specialists & Family Urgent Care (12,000 sq ft). High-volume waiting area, 14 clinical exam rooms, triage rooms, pediatric play area, and staff lactation lounge.",
            "— Building C: Advanced Diagnostic Imaging & Oncology Infusion (11,000 sq ft). MRI/CT scanner suites, PET scan staging, 8 chemotherapy infusion bays, clinical nursing stations, and clean linen rooms.",
            "— Building D: Physical Therapy, Rehabilitation & Medical Administration (9,000 sq ft). Open gym floor with rubberized athletic flooring, hydrotherapy suite, 6 private treatment offices, and executive administrative suites.",
            "--PAGE-BREAK--",
            "# SECTION 3: INFECTION CONTROL, CHEMICAL MATRIX & CDC/OSHA STANDARDS",
            "Healthcare environmental hygiene differs fundamentally from conventional office janitorial services. Pathogen cross-transmission in clinical spaces can result in catastrophic Healthcare-Associated Infections (HAIs).",
            "Coastal Shine enforces a strict three-tier infection prevention architecture across all four medical buildings:",
            "Tier 1: EPA List N Hospital-Grade Disinfectants. We utilize Oxivir 1 (accelerated hydrogen peroxide, EPA Reg #70627-56) with a verified 1-minute kill claim against SARS-CoV-2, MRSA, Norovirus, and Influenza A. For surgical suites, we utilize Virex II 256 quaternary ammonium virucidal disinfectant.",
            "Tier 2: Contact Time (Dwell Time) Enforcement. All clinical touch surfaces are saturated with disinfectant and allowed to remain visibly wet for the exact manufacturer-mandated dwell time (60 seconds for accelerated hydrogen peroxide; 10 minutes for quaternary formulas). Technicians are prohibited from wipe-drying surfaces prematurely.",
            "Tier 3: Color-Coded Microfiber & Cross-Contamination Prevention. Microfiber cloths and flat mops are strictly color-coded by zone: Red: Restroom toilets and biohazard containment areas; Yellow: Exam tables and patient contact surfaces; Green: Food prep, staff breakrooms, and kitchens; Blue: General administrative offices, lobby glass, and corridors. Microfiber pads are never dipped back into cleaning solutions; each cloth is used for exactly one surface plane before disposal into the laundering bin.",
            "--PAGE-BREAK--",
            "# SECTION 4: CLINICAL TASK FREQUENCY & DEEP CLEANING SCHEDULE",
            "Cleaning frequencies are customized by building risk tier:",
            [
                ["Facility Zone / Room Type", "Daily Evening Frequency", "Weekly Specialty Service", "Monthly Deep Restoration", "Quarterly Infection Audit"],
                ["Operating Suites (Building A)", "Terminal cleaning & floor wet-vacuum", "Ceiling HEPA vacuum & wall wash", "High-level floor strip & seal", "ATP bioluminescence swab audit"],
                ["Exam Rooms (Buildings B & C)", "Dwell-time wipe of tables, stools, sinks", "Baseboard scrubbing & high-dusting", "Cabinet interior sanitization", "Random ATP protein swab check"],
                ["Waiting Rooms & Lobbies", "Continuous disinfection of armrests/counters", "Low-moisture carpet extraction", "Tile grout deep scrub & reseal", "Air quality particulate count"],
                ["Restrooms & Scrub Sinks", "Full chemical wash & germicidal fogging", "Acid descaling of chrome fixtures", "Floor drain enzymatic flush", "Hygiene swab verification"],
                ["Infusion Bays (Building C)", "Terminal wipe of IV poles, recliners, monitors", "Privacy curtain antimicrobial mist", "Hard floor machine burnishing", "Clinical director inspection sign-off"],
                ["Physical Therapy Gym (Building D)", "Antimicrobial wipe of mats, weights, tables", "Rubber floor automated autoscrubber", "Full athletic mat steam extract", "Slip-resistance coefficient test"],
            ],
            "--PAGE-BREAK--",
            "# SECTION 5: STAFFING MATRIX, BACKGROUND SCREENING & SUPERVISOR QA",
            "To service 48,000 square feet across four buildings, Coastal Shine deploys a dedicated, consistent seven-person evening medical cleaning crew (6:00 PM – 11:30 PM, Monday through Friday, with on-call Saturday coverage):",
            "— 1 Full-Time CHEST-Certified Healthcare Operations Supervisor (Non-working QA supervisor dedicated solely to quality control, ATP swab testing, and client communication).",
            "— 2 Surgical & Clinical Specialists (Assigned exclusively to Building A and Building C surgical/infusion suites).",
            "— 2 Exam Room & Triage Technicians (Assigned to Building B pediatric urgent care and Building C exam rooms).",
            "— 2 Floor & General Environmental Technicians (Assigned to Building D gym, lobbies, restrooms, trash removal, and machine floor maintenance).",
            "Background Screening & Vetting Standards: 100% of deployed technicians undergo 10-panel drug screening, statewide FDLE Level 2 criminal fingerprint background checks, E-Verify employment eligibility authorization, and annual Bloodborne Pathogens & Hazard Communication OSHA compliance certification.",
            "CleanTrak Digital Quality Assurance: Supervisors conduct daily inspections using CleanTrak mobile auditing software with geo-fenced time stamps, digital photos, and Hygiena Ensure Touch ATP bioluminescence testing (< 25 RLU pass threshold).",
            "--PAGE-BREAK--",
            "# SECTION 6: COMPREHENSIVE COMMERCIAL PRICING SCHEDULE",
            "Coastal Shine submits a fully burdened monthly service fee covering labor, CHEST supervision, EPA List N chemicals, commercial HEPA equipment, and insurance:",
            [
                ["Facility Component", "Rentable Sq Ft", "Cleaning Risk Tier", "Monthly Labor Cost", "Chemicals & Equipment", "Total Monthly Fee"],
                ["Building A: Ambulatory Surgery Center", "16,000 RSF", "Tier 1: High Criticality (Daily Terminal)", "$3,840.00", "$620.00", "$4,460.00"],
                ["Building B: Pediatric & Urgent Care", "12,000 RSF", "Tier 2: High Traffic Clinical", "$2,400.00", "$380.00", "$2,780.00"],
                ["Building C: Diagnostic & Infusion", "11,000 RSF", "Tier 2: Clinical / Clean Environment", "$2,200.00", "$360.00", "$2,560.00"],
                ["Building D: Rehab & Administration", "9,000 RSF", "Tier 3: Moderate Risk Commercial", "$1,440.00", "$220.00", "$1,660.00"],
                ["Campustotals / Consolidated Rate", "48,000 RSF", "Consolidated Campus Package", "$9,880.00", "$1,580.00", "$11,460.00"],
            ],
            "Emergency Biohazard Response Rider: 24/7/365 emergency biohazard and bloodborne spill response within 60 minutes of dispatch at a preferred contractor rate of $125.00/hour plus material costs.",
            "# PROPOSAL VALIDITY & EXECUTIVE SIGNATURE",
            "This proposal remains firm and binding for ninety (90) calendar days from submission.",
            "Submitted by: Liza Iza, Managing Principal · Coastal Shine Commercial Cleaning LLC",
            "Direct Contact: (813) 492-8810 · liza@coastalshinecleaning.com",
        ],
        role="source",
    )

    # 2. liza_15p_service_proposal_v1.docx: v1 edited technical RFP draft
    files["liza_15p_service_proposal_v1.docx"] = write_docx_file(
        "liza_15p_service_proposal_v1.docx",
        "Tampa Bay Medical Plaza RFP Response — 15 Pages (v1 Edited Technical Proposal)",
        [
            "CLIENT: Tampa Bay Healthcare Real Estate Group, LLC",
            "PROJECT: Turnkey Environmental & Healthcare Janitorial Services",
            "CAMPUS: Westshore Medical Executive Center (48,000 RSF)",
            "PROPOSAL REVISION: v1 Technical Working Draft",
            "--PAGE-BREAK--",
            "# EXECUTIVE SUMMARY & VALUE PROPOSITION",
            "Coastal Shine Commercial Cleaning LLC presents this formal technical response to provide comprehensive healthcare environmental infection control across the four medical buildings comprising Westshore Medical Executive Center.",
            "Unlike standard commercial janitorial contractors, Coastal Shine operates with healthcare-certified technicians trained in CDC environmental infection control guidelines, EPA List N chemistries, and ATP bioluminescence hygiene verification.",
            "--PAGE-BREAK--",
            "# SCOPE OF WORK MATRIX & FREQUENCY STANDARDS",
            [
                ["Service Domain", "Execution Frequency", "Target Facilities", "Primary Disinfection Chemistry", "Verification Protocol"],
                ["Surgical Suite Terminal Cleaning", "Nightly (Mon-Fri)", "Building A Operating Suites", "Virex II 256 Quat (10-min dwell)", "ATP Swab < 25 RLU"],
                ["Clinical Exam Room Sanitization", "Nightly (Mon-Fri)", "Buildings B & C (28 Exam Rooms)", "Oxivir 1 AHP (1-min dwell)", "CleanTrak Photo Log"],
                ["Infusion Bay Disinfection", "Nightly (Mon-Fri)", "Building C (8 Infusion Bays)", "Oxivir 1 AHP (1-min dwell)", "ATP Swab < 25 RLU"],
                ["Rubberized Gym & Mat Sanitizing", "Nightly (Mon-Fri)", "Building D Physical Therapy", "Neutral Quaternary Disinfectant", "Autoscrubber Log"],
                ["Restroom Germicidal Decontamination", "Nightly (Mon-Fri)", "All 4 Buildings (18 Restrooms)", "Hospital-Grade Germicide", "Restroom Inspection Sheet"],
            ],
            "--PAGE-BREAK--",
            "# STAFFING, SUPERVISION & QUALITY GUARANTEE",
            "— Dedicated On-Site CHEST Supervisor on duty every shift.",
            "— 100% Level 2 FBI background check and 10-panel drug tested staff.",
            "— CleanTrak real-time digital auditing with client portal access.",
            "— Consolidated campus monthly investment: $11,460.00 / month ($0.238 / sq ft).",
        ],
        role="draft",
    )

    # 3. liza_vendor_packet_draft.docx: Vendor packet draft
    files["liza_vendor_packet_draft.docx"] = write_docx_file(
        "liza_vendor_packet_draft.docx",
        "Coastal Shine Commercial Cleaning — Commercial Vendor Prequalification Packet (Draft)",
        [
            "COMPANY: Coastal Shine Commercial Cleaning LLC · Tampa, Florida",
            "DOCUMENT: Master Commercial Facilities Vendor Prequalification Packet",
            "TARGET CLIENTS: Commercial Property Managers, Healthcare Facility Directors, Corporate Campus Leads",
            "--PAGE-BREAK--",
            "# SECTION 1: CORPORATE IDENTITY & LICENSURE",
            "Legal Entity Name: Coastal Shine Commercial Cleaning LLC",
            "Federal Employer Identification Number (FEIN): 82-4192841",
            "Florida Entity Registration: Document #L18000219482 · Active & In Good Standing",
            "Registered Physical Address: 4830 W Kennedy Blvd, Suite 300, Tampa, FL 33609",
            "Commercial Banking Partner: Fifth Third Bank, Commercial Treasury Division, Tampa FL",
            "--PAGE-BREAK--",
            "# SECTION 2: COMMERCIAL INSURANCE & INDEMNIFICATION",
            "Coastal Shine maintains comprehensive commercial insurance meeting or exceeding Tier-1 institutional landlord standards:",
            [
                ["Coverage Description", "Carrier & Rating", "Policy Number", "Coverage Limits", "Expiration Date"],
                ["Commercial General Liability", "Travelers Indemnity (A++ Superior)", "TRV-GL-9481204", "$2,000,000 General Aggregate / $1,000,000 Occurrence", "August 15, 2027"],
                ["Commercial Auto Liability", "Travelers Indemnity (A++ Superior)", "TRV-CA-4109281", "$1,000,000 Combined Single Limit (CSL)", "August 15, 2027"],
                ["Workers' Compensation & Employers", "Florida Workers' Comp Fund", "FWC-941028-02", "Statutory Limits / $1,000,000 Employer Liability", "August 15, 2027"],
                ["Commercial Umbrella / Excess", "Travelers Indemnity (A++ Superior)", "TRV-UMB-190284", "$5,000,000 Aggregate / $5,000,000 Occurrence", "August 15, 2027"],
                ["Janitorial Service Bond", "Western Surety Company", "WSC-BND-48201", "$100,000 Employee Dishonesty & Theft Bond", "August 15, 2027"],
            ],
            "--PAGE-BREAK--",
            "# SECTION 3: EMPLOYEE SCREENING, OSHA HAZCOM & SAFETY PROGRAM",
            "Every employee deployed to client properties must satisfy the following safety protocols:",
            "— Mandatory 10-panel drug screening administered through Quest Diagnostics.",
            "— Florida Department of Law Enforcement (FDLE) statewide criminal history background screening.",
            "— E-Verify federal employment eligibility verification.",
            "— 16 hours of mandatory OSHA Hazard Communication, Bloodborne Pathogen (29 CFR 1910.1030), and PPE compliance training prior to first facility deployment.",
            "— Safety Data Sheets (SDS) maintained in bilingual binders at every client janitorial closet and accessible via QR code on mobile devices.",
        ],
        role="source",
    )

    # 4. liza_vendor_packet_clean.pdf: 3-page clean vendor packet
    files["liza_vendor_packet_clean.pdf"] = write_pdf_file(
        "liza_vendor_packet_clean.pdf",
        "Coastal Shine Commercial Cleaning — Master Vendor Compliance Packet (Clean Final)",
        [
            "# 1. VENDOR PREQUALIFICATION OVERVIEW",
            "Entity: Coastal Shine Commercial Cleaning LLC · FEIN: 82-4192841 · Established 2018 in Tampa, FL.",
            "Specialization: Commercial medical facilities, ambulatory surgery centers, Class-A corporate office complexes.",
            "Accreditations: CHEST-certified healthcare supervisors, ISSA CIMS-GB green cleaning compliant, OSHA 30.",
            "--PAGE-BREAK--",
            "# 2. INSURANCE SCHEDULE & POLICY SPECIFICATIONS",
            [
                ["Insurance Line", "Underwriter", "Policy Limits", "Status"],
                ["Commercial General Liability", "Travelers (A++)", "$2,000,000 Aggregate / $1,000,000 Occ", "Active & Verified"],
                ["Commercial Auto Liability", "Travelers (A++)", "$1,000,000 Combined Single Limit", "Active & Verified"],
                ["Workers' Compensation", "Florida WC Fund", "Statutory Limits / $1,000,000 Employer", "Active & Verified"],
                ["Excess Umbrella Liability", "Travelers (A++)", "$5,000,000 Excess Umbrella", "Active & Verified"],
                ["Janitorial Dishonesty Bond", "Western Surety", "$100,000 Fidelity Bond", "Active & Verified"],
            ],
            "--PAGE-BREAK--",
            "# 3. ENVIRONMENTAL SAFETY & 24/7 EMERGENCY DISPATCH",
            "— Bilingual SDS sheets maintained on-site and digitally accessible via QR code.",
            "— EPA List N hospital-grade disinfectants with verified virucidal kill claims.",
            "— Dedicated 24/7/365 emergency biohazard dispatch line: (813) 492-8810.",
            "— Guaranteed on-site emergency response within 60 minutes for Tampa Bay medical facilities.",
        ],
        role="deliverable",
        subtitle="3-Page Institutional Vendor Prequalification & Insurance Compliance Dossier",
        meta_tag="Coastal Shine Commercial Cleaning · Vendor Compliance Dossier",
    )

    # 5. liza_rate_card_final.xlsx: Multi-tier commercial cleaning rate card
    rate_card_rows = [
        ["Facility Type & Classification", "Square Footage Tier", "Frequency", "Monthly Base Rate USD", "Rate per Sq Ft", "Chemicals Included", "ATP Testing Included", "Service Level Agreement"],
        ["Medical: Ambulatory Surgical Center", "10,000 – 25,000 RSF", "7x / week (Daily Terminal)", 4460.00, 0.279, "EPA List N Hospital Grade", "Yes (Weekly Swabs)", "99.9% Disinfection SLA"],
        ["Medical: Pediatric & Urgent Care", "8,000 – 15,000 RSF", "5x / week (Mon-Fri)", 2780.00, 0.232, "Oxivir AHP Disinfectant", "Yes (Bi-Weekly)", "Healthcare Standard"],
        ["Medical: Diagnostic & Oncology", "8,000 – 15,000 RSF", "5x / week (Mon-Fri)", 2560.00, 0.233, "Hospital Germicide", "Yes (Bi-Weekly)", "Healthcare Standard"],
        ["Medical: Physical Therapy Clinic", "5,000 – 10,000 RSF", "5x / week (Mon-Fri)", 1660.00, 0.184, "Neutral Quaternary", "Optional ($75/mo)", "Commercial Clinical"],
        ["Class-A Corporate Office Building", "20,000 – 50,000 RSF", "5x / week (Mon-Fri)", 3200.00, 0.107, "Green Seal Certified", "No", "Standard Commercial"],
        ["Corporate Office: Mid-Size Suite", "5,000 – 15,000 RSF", "3x / week (M/W/F)", 1450.00, 0.145, "Green Seal Certified", "No", "Standard Commercial"],
        ["Industrial / Warehouse Office", "3,000 – 8,000 RSF", "2x / week (Tue/Thu)", 850.00, 0.170, "Industrial Heavy Duty", "No", "Industrial Standard"],
        ["Day Porter: Dedicated Staff Member", "Per 40-hr week", "Mon-Fri (8am-5pm)", 3400.00, 21.25, "Restocking & Policing", "No", "Continuous On-Site"],
        ["Floor Care: VCT Strip & Re-Wax", "Per 1,000 sq ft", "One-Time Project", 450.00, 0.450, "Commercial Polymer Wax", "No", "5-Coat Diamond Finish"],
        ["Carpet Care: Hot Water Extraction", "Per 1,000 sq ft", "One-Time Project", 280.00, 0.280, "Low-Moisture Detergent", "No", "CRI Certified Deep Clean"],
        ["Emergency Biohazard Response", "Per incident", "On-Demand (24/7)", 450.00, 125.00, "Bio-Remediation Pack", "Yes (Mandatory)", "60-Minute Response Time"],
    ]
    files["liza_rate_card_final.xlsx"] = write_xlsx_file(
        "liza_rate_card_final.xlsx",
        "Commercial Rate Card",
        rate_card_rows,
        role="deliverable",
    )

    return files
