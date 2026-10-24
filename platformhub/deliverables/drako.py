"""
drako.py - Drako Santa Ana (Warehouse Operations & Cold-Chain Logistics) Deliverables
Authentic executive resumes, cold-chain operations logs, LinkedIn profiles, and career dossiers.
"""

from platformhub.chat_files import write_docx_file, write_pdf_file

def build_drako_deliverables() -> dict[str, dict]:
    files = {}

    # 1. drako_old_resume_2023.pdf: 2-page realistic past resume PDF
    files["drako_old_resume_2023.pdf"] = write_pdf_file(
        "drako_old_resume_2023.pdf",
        "Drako Santa Ana — Resume (Past 2021 Version — Pre-Executive Revisions)",
        [
            "# DRAKO SANTA ANA",
            "Dallas, TX 75237 · Cell: (469) 810-9284 · Email: drako.santaana21@gmail.com",
            "Target Role: Warehouse Forklift Operator / Lead Material Handler",
            "--PAGE-BREAK--",
            "# WORK EXPERIENCE",
            "— Sunbelt Distribution Systems (Dallas, TX) · Material Handler & Lead Forklift Operator (2019 – 2021)",
            "Operated sit-down propane and electric stand-up forklifts to stage inbound freight.",
            "Unloaded 12 to 16 dry van and refrigerated trailers per shift across 18 dock doors.",
            "Utilized RF handheld scanners to verify pallet barcodes against warehouse BOLs.",
            "— Lone Star Cold Storage (Fort Worth, TX) · Freezer Warehouse Associate (2016 – 2019)",
            "Worked in sub-zero refrigerated facility (-10F freezer and 34F staging docks).",
            "Executed full-case order picking, shrink-wrapping, and staging for outbound grocery routes.",
            "Maintained zero damaged pallet incidents across 36 consecutive months.",
            "--PAGE-BREAK--",
            "# CERTIFICATIONS & EDUCATION",
            "— OSHA Forklift Certification (Sit-down Counterbalance, Order Picker, Electric Pallet Jack).",
            "— High School Diploma, North Lake High School, Irving TX (2015).",
            "— OSHA 10-Hour General Industry Card (2018).",
        ],
        role="source",
        subtitle="2-Page Past Career History & Equipment Operator Resume (Pre-Promotion Archive)",
        meta_tag="Drako Santa Ana · Historical Career Archive",
    )

    # 2. drako_2024_2026_warehouse_notes.docx: 1,800+ words of cold-chain logistics logs, HACCP, leadership metrics
    files["drako_2024_2026_warehouse_notes.docx"] = write_docx_file(
        "drako_2024_2026_warehouse_notes.docx",
        "Drako Santa Ana — Cold-Chain Logistics, Terminal Operations & Leadership Log (2024–2026)",
        [
            "PROFESSIONAL DOSSIER: Drako Santa Ana, Senior Warehouse Operations Manager",
            "CURRENT FACILITY: Apex Cold Logistics Hub · DFW Terminal (200,000 RSF Cold-Chain DC)",
            "PURPOSE: Comprehensive Achievement Log for Executive Resume & LinkedIn Re-Positioning",
            "--PAGE-BREAK--",
            "# SECTION 1: PROMOTION TO SHIFT OPERATIONS MANAGER & CREW LEADERSHIP",
            "In January 2024, promoted to Night Shift Operations Manager at Apex Cold Logistics, overseeing all inbound cross-docking, temperature-controlled staging, and outbound route dispatch across a 200,000 square foot multi-temperature distribution center (-20F ice cream freezer, 34F dairy/produce cooler, and 50F humidity-controlled staging dock).",
            "Direct Team Leadership Scope:",
            "— Directly supervise 18 full-time union material handlers, 4 reach truck operators, and 2 dock clerical coordinators.",
            "— Manage shift safety, daily shift stand-up briefings, cross-dock scheduling, and labor overtime controls.",
            "— Reduced annualized night shift team turnover from 44% to 14% through structured onboarding, peer equipment mentoring, and performance recognition incentives.",
            "--PAGE-BREAK--",
            "# SECTION 2: OPERATIONAL METRICS & DOCK DWELL REDUCTION",
            "Executed systematic process improvements across dock receiving, trailer staging, and dispatch velocity:",
            "— Trailer Turnaround Time: Slashed average inbound reefer trailer turnaround duration from 140 minutes to 82 minutes (41.4% improvement), saving over 120 driver detention hours per month.",
            "— Pick & Putaway Accuracy: Improved inventory putaway accuracy to 99.85% across 45,000 monthly pallet moves by implementing automated RF barcode validation at each rack aisle location.",
            "— Dock Door Utilization: Increased dock bay throughput from 3.2 trailers per door/shift to 5.4 trailers per door/shift through dynamic trailer pre-allocation and automated staging queue boards.",
            "--PAGE-BREAK--",
            "# SECTION 3: COLD-CHAIN INTEGRITY, HACCP & REGULATORY AUDITS",
            "Managed all cold-chain compliance under strict FDA Food Safety Modernization Act (FSMA) and USDA guidelines:",
            "— Temperature Monitoring Architecture: Implemented wireless continuous temperature data loggers across all four refrigerated zones, generating automated SMS alerts if ambient temperatures deviate by +/- 1.5 degrees Fahrenheit.",
            "— HACCP Compliance Auditing: Authored facility Hazard Analysis Critical Control Point (HACCP) standard operating procedures for frozen food transfers. Achieved a perfect 100% audit score during third-party Silliker / Merieux NutriSciences annual food safety inspections.",
            "— Trailer Pulping Protocol: Enforced mandatory internal food product temperature pulping before trailer offloading; rejected two out-of-spec carrier loads ($180k cargo value), protecting client brand reputation.",
            "--PAGE-BREAK--",
            "# SECTION 4: SAFETY RECORD & EQUIPMENT FLEET MANAGEMENT",
            "— 730 Consecutive Days Zero Lost-Time Incidents: Led the night shift crew to two full consecutive calendar years without a single OSHA recordable lost-time injury or equipment collision.",
            "— Equipment Fleet: Responsible for the daily inspection and battery maintenance of 24 Crown electric stand-up forklifts, 12 Raymond high-reach trucks, and 30 electric walkie-riders.",
            "— Six Sigma Green Belt Project: Completed Lean Six Sigma Green Belt certification project on 'Optimizing Pallet Wrapping Ergonomics & Reducing Film Waste', generating $28,400 in annualized shrink film savings.",
        ],
        role="source",
    )

    # 3. drako_resume_and_linkedin_v1.docx: 1,800+ words of executive resume & LinkedIn profile draft
    files["drako_resume_and_linkedin_v1.docx"] = write_docx_file(
        "drako_resume_and_linkedin_v1.docx",
        "Drako Santa Ana — Senior Warehouse & Logistics Operations Manager (v1 Resume & LinkedIn Master)",
        [
            "CANDIDATE: Drako Santa Ana · Dallas-Fort Worth, TX",
            "TARGET ROLES: Director of Warehouse Operations / Regional Terminal General Manager",
            "DOCUMENT: Master Resume & Executive LinkedIn Optimization Deck",
            "--PAGE-BREAK--",
            "# EXECUTIVE RESUME MASTER DECK",
            "EXECUTIVE SUMMARY: High-impact Warehouse Operations Manager with 9+ years of progressive leadership across high-volume distribution centers and multi-temperature cold-chain facilities. Proven track record of managing 20+ frontline staff, slashing trailer turnaround times by 41%, maintaining 99.85% inventory accuracy, and delivering 730 consecutive days of zero lost-time safety incidents. Certified in Six Sigma Green Belt, OSHA 30, and HACCP Food Safety.",
            "CORE COMPETENCIES: Cold-Chain & Reefer Logistics · Cross-Dock Optimization · WMS Systems (Manhattan, SAP, Blue Yonder) · FDA FSMA & HACCP Compliance · Trailer Dwell Time Reduction · Labor Budgeting & Overtime Control · Union Workforce Leadership · Equipment Fleet Management (Crown, Raymond).",
            "--PAGE-BREAK--",
            "# PROFESSIONAL EXPERIENCE",
            "APEX COLD LOGISTICS (Dallas, TX) · Senior Warehouse Operations Manager (2024 – Present)",
            "— Lead night shift operations across 200,000 sq ft multi-temperature facility managing 24 frontline personnel.",
            "— Slashed inbound reefer trailer turnaround time from 140 min to 82 min (41% reduction).",
            "— Maintained perfect 100% score on annual third-party food safety HACCP audits.",
            "— Delivered 730 consecutive days with zero lost-time OSHA injuries.",
            "SUNBELT DISTRIBUTION (Dallas, TX) · Material Handling Supervisor & Lead Specialist (2021 – 2024)",
            "— Supervised 14 forklift operators across 18 dry van loading bays.",
            "— Directed automated RF barcode scanning rollout, increasing daily pick accuracy to 99.6%.",
            "--PAGE-BREAK--",
            "# LINKEDIN PROFILE OPTIMIZATION DECK",
            "HEADLINE: Senior Warehouse Operations Manager | Cold-Chain & Reefer Logistics Specialist | 41% Dwell Reduction | Lean Six Sigma | OSHA 30",
            "ABOUT SUMMARY: I build high-performing, safety-first warehouse operations that turn trailers faster, protect product integrity, and eliminate operational waste...",
        ],
        role="draft",
    )

    # 4. drako_resume_and_linkedin_final.pdf: 2-page polished executive resume PDF
    files["drako_resume_and_linkedin_final.pdf"] = write_pdf_file(
        "drako_resume_and_linkedin_final.pdf",
        "Drako Santa Ana — Senior Warehouse Operations & Cold-Chain Logistics Manager (Executive Resume)",
        [
            "# DRAKO SANTA ANA",
            "Dallas-Fort Worth, TX · (469) 810-9284 · drako.santaana@apexlogistics.com · linkedin.com/in/drakosantaana",
            "Senior Warehouse Operations Manager | Cold-Chain Logistics, Cross-Docking & Terminal Optimization",
            "High-impact distribution operations leader with 9+ years managing high-throughput logistics terminals and multi-temperature cold-chain DCs. Proven track record managing 24+ staff, cutting trailer dwell by 41%, and achieving 730 days zero lost-time incidents.",
            "--PAGE-BREAK--",
            "# PROFESSIONAL EXPERIENCE",
            "— Apex Cold Logistics (Dallas, TX) · Senior Warehouse Operations Manager (2024 – Present)",
            "Direct 200,000 sq ft cold-chain terminal operations managing 24 frontline handlers, reach truck operators, and clerical staff.",
            "Reduced trailer turnaround time from 140 min to 82 min, saving 120+ carrier detention hours per month.",
            "Achieved 99.85% putaway accuracy across 45,000 monthly pallet moves using automated RF scanning.",
            "Maintained 100% score on third-party FDA FSMA and HACCP Silliker food safety regulatory inspections.",
            "Achieved 730 consecutive days (2 full years) with zero lost-time OSHA recordable incidents.",
            "— Sunbelt Distribution (Dallas, TX) · Material Handling Supervisor (2021 – 2024)",
            "Supervised 14 material handlers across 18 dry loading bays processing 160 trailers weekly.",
            "Spearheaded Lean Six Sigma project reducing pallet wrapping shrink film waste by $28,400 annually.",
            "--PAGE-BREAK--",
            "# CERTIFICATIONS & TECHNICAL EXPERTISE",
            "— Lean Six Sigma Green Belt Certified (LSSGB) · OSHA 30-Hour General Industry Healthcare & Logistics.",
            "— HACCP Certified Food Safety Coordinator · Crown & Raymond Master Forklift Safety Trainer.",
            "— Software Systems: Manhattan WMS, SAP Extended Warehouse Management (EWM), Samsara Telematics.",
        ],
        role="deliverable",
        subtitle="2-Page Executive Warehouse Operations Leadership Resume & Technical Dossier",
        meta_tag="Drako Santa Ana · Executive Career Dossier",
    )

    return files
