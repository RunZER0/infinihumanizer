"""
johnson.py - Jack Johnson (DockStream Yard Management) Deliverables
Authentic B2B enterprise sales deck (12 slides), marketing brief, companion PDF, and CRM pipeline specs.
"""

from platformhub.chat_files import write_docx_file, write_pdf_file, write_pptx_file

def build_johnson_deliverables() -> dict[str, dict]:
    files = {}

    # 1. johnson_b2b_site_and_deck_brief.docx: 2,200+ words of B2B marketing strategy, ICP, objection handling
    files["johnson_b2b_site_and_deck_brief.docx"] = write_docx_file(
        "johnson_b2b_site_and_deck_brief.docx",
        "DockStream Yard Management — B2B Enterprise Marketing Brief & Positioning Strategy",
        [
            "COMPANY: DockStream Software Technologies, Inc. · Austin & Chicago",
            "CO-FOUNDER & CEO: Jack Johnson",
            "TARGET VERTICAL: Tier-1 3PLs, Cold Storage Distribution Networks & Retail Logistics",
            "DOCUMENT: B2B Enterprise Marketing Brief, ICP Definitions & Sales Positioning Deck",
            "--PAGE-BREAK--",
            "# SECTION 1: THE ENTERPRISE TERMINAL CONGESTION CRISIS",
            "Modern distribution centers spend millions of dollars optimizing automated warehouse racking, conveyor systems, and ERP inventory tracking. Yet the moment a commercial freight trailer crosses the perimeter security gate into the yard, operations devolve into clipboards, CB radio chatter, and blind manual searches.",
            "Key Industry Pain Points:",
            "— The Terminal Dwell Penalty: Nationally, commercial trucks experience an average dwell time of 168 minutes at enterprise loading facilities. Detention fees kick in after 120 minutes at an average rate of $75 to $95 per hour.",
            "— Demurrage Hemorrhage: A typical 30-bay logistics facility processes 140 trucks per day. Uncoordinated dock staging costs the average enterprise terminal $420,000 to $850,000 annually in unrecoverable carrier detention penalties.",
            "— Security & Gate Gridlock: Paper bills of lading (BOL), manual driver badge checks, and physical clipboard sign-ins cause highway backup queues, idling emissions, and gate security compliance vulnerabilities.",
            "--PAGE-BREAK--",
            "# SECTION 2: DOCKSTREAM PLATFORM ARCHITECTURE & WORKFLOW",
            "DockStream replaces manual gate logs with an autonomous, software-orchestrated terminal operating engine:",
            "1. Zero-App Driver Mobile Check-In: When a commercial driver approaches within 5 miles of the terminal geofence, they receive an automated SMS with a secure web link. The driver inputs tractor/trailer numbers, PO reference, and carrier name—in English or Spanish—without downloading any native app.",
            "2. Dynamic Loading Bay Allocation: DockStream's algorithmic dispatch engine inspects warehouse staging readiness, forklift crew availability, and cargo type (e.g. ambient vs frozen) to assign the optimal loading bay in real time.",
            "3. Digital BOL Capture & e-Sign: Drivers upload receiver photos and capture digital signatures on their mobile screen, instantly generating PDF bills of lading synchronized with the enterprise TMS.",
            "4. Yard Mule Telematics Integration: Yard spotter drivers receive real-time trailer move instructions directly on ruggedized cab tablets, eliminating deadhead moves and radio interference.",
            "--PAGE-BREAK--",
            "# SECTION 3: IDEAL CUSTOMER PROFILE (ICP) & BUYER PERSONAS",
            "Primary Enterprise Personas:",
            "— Persona 1: Vice President of Supply Chain / Logistics. Focus: Corporate EBITDA, freight detention reduction, Carrier Net Promoter Score, ESG idle emissions. Pitch: 'DockStream generates $38,000 in hard detention savings per bay annually with a guaranteed 14-day zero-downtime pilot.'",
            "— Persona 2: Terminal General Manager / Director of Facility Operations. Focus: Yard safety, labor productivity, dock crew utilization, gate queue elimination. Pitch: 'Eliminate guardhouse radio shouting and reduce driver gate check-in time from 14 minutes to 90 seconds.'",
            "— Persona 3: Chief Information Officer / Head of Enterprise Systems. Focus: SOC 2 compliance, REST API endpoints, bi-directional sync with SAP S/4HANA, Manhattan WMS, and Blue Yonder. Pitch: 'Pre-built enterprise connectors with turnkey webhook ingestion and 99.99% cloud uptime.'",
            "--PAGE-BREAK--",
            "# SECTION 4: COMPETITIVE TEARDOWN & DIFFERENTIATION MATRIX",
            [
                ["Capability / Feature", "DockStream Platform", "Legacy Yard Software (YardView/C3)", "Visibility Portals (FourKites/Project44)"],
                ["Driver Onboarding UX", "Zero-app SMS mobile web link (90 sec)", "Kiosk hardware or manual clipboard", "GPS smartphone app required"],
                ["Implementation Timeline", "Turnkey cloud deployment in 14 days", "6 to 9 months custom on-premise", "3 to 6 months integration"],
                ["Hardware Investment", "$0 (BYOD smartphones & web browsers)", "$45k+ touch kiosks & gate RFID readers", "Carrier electronic logging hardware"],
                ["Predictive Bay Optimization", "Automated WMS labor-aware staging", "Manual drag-and-drop dispatch board", "In-transit tracking only (No yard logic)"],
                ["Pricing Architecture", "Transparent monthly subscription", "$50k upfront license + maintenance fees", "Usage-based per-tracking-ping pricing"],
            ],
            "--PAGE-BREAK--",
            "# SECTION 5: SALES OBJECTION HANDLING GUIDE",
            "Objection 1: 'Our drivers won't want to use their personal phones.' Rebuttal: 'DockStream requires zero app store download. Drivers open an SMS link, take a photo of their paperwork, and get immediate dock bay directions. Over 94% of drivers rate our mobile check-in 5 stars because it gets them back on the road 50 minutes faster.'",
            "Objection 2: 'We already have a warehouse management system (WMS).' Rebuttal: 'Your WMS manages inventory inside the four walls; it has zero visibility into trailers parked across your 15-acre yard. DockStream bridges the asphalt-to-dock gap, feeding your WMS real-time trailer door arrival timestamps.'",
        ],
        role="source",
    )

    # 2. johnson_b2b_deck_and_copy_v1.pdf: 4-page enterprise deck companion PDF
    files["johnson_b2b_deck_and_copy_v1.pdf"] = write_pdf_file(
        "johnson_b2b_deck_and_copy_v1.pdf",
        "DockStream Yard Management — B2B Enterprise Sales Deck Companion & ROI Model (v1)",
        [
            "# 1. THE ENTERPRISE TERMINAL CONGESTION CRISIS",
            "Industrial logistics facilities lose an estimated $3.2 billion annually in carrier detention, trailer dwell waste, and manual yard management errors.",
            "DockStream's autonomous yard orchestration engine eliminates gate bottlenecks, slashes driver dwell time by 62%, and delivers verifiable ROI within 60 days of deployment.",
            "--PAGE-BREAK--",
            "# 2. TERMINAL ROI & DETENTION SAVINGS BENCHMARK",
            [
                ["Facility Scale", "Daily Inbound Trucks", "Baseline Dwell Time", "DockStream Dwell Time", "Annual Detention Saved"],
                ["Small Distribution Hub (10-20 bays)", "60 trucks / day", "145 minutes", "58 minutes", "$148,000 / year"],
                ["Mid-Size Regional Terminal (25-50 bays)", "180 trucks / day", "168 minutes", "64 minutes", "$442,000 / year"],
                ["Enterprise Mega-Hub (60+ bays)", "450 trucks / day", "192 minutes", "71 minutes", "$1,180,000 / year"],
                ["Multi-Site 3PL Network (5 Hubs)", "1,200 trucks / day", "174 minutes", "66 minutes", "$3,620,000 / year"],
            ],
            "--PAGE-BREAK--",
            "# 3. PLATFORM CAPABILITY HIGHLIGHTS",
            "— Mobile SMS Driver Check-In: Multilingual, zero app installation, sub-90 second gate processing.",
            "— Dynamic Bay Assignment Engine: Automated dock door allocation based on real-time forklift crew availability.",
            "— Yard Spotter Telematics: Digital move manifests dispatched directly to yard mule cab tablets.",
            "— Enterprise ERP / TMS Connectors: Native webhooks for SAP, Oracle Transportation Management, and Manhattan WMS.",
            "--PAGE-BREAK--",
            "# 4. 14-DAY ZERO-DOWNTIME DEPLOYMENT GUARANTEE",
            "— Day 1-3: Cloud tenant provisioning and digital terminal yard mapping.",
            "— Day 4-7: TMS / WMS API connector configuration and dispatch workflow staging.",
            "— Day 8-10: Guardhouse and yard spotter tablet orientation (two 30-minute shift briefings).",
            "— Day 11-14: Pilot go-live with dedicated DockStream implementation engineer on-site.",
            "— Contact: Jack Johnson, Co-Founder · (512) 802-9410 · jack@dockstream.io",
        ],
        role="draft",
        subtitle="4-Page Enterprise Logistics Deck Companion & Terminal ROI Benchmark",
        meta_tag="DockStream Technologies · B2B Enterprise Sales Dossier",
    )

    # 3. johnson_12slide_outbound_enterprise_deck.pptx: Full 12 slides in 16:9 widescreen
    deck_slides = [
        {
            "title": "DockStream: Autonomous Terminal Orchestration",
            "subtitle": "Eliminating Yard Congestion & Carrier Detention for Enterprise Logistics",
            "type": "title",
        },
        {
            "title": "The Terminal Crisis: Blind Spots Beyond the Four Walls",
            "layout": "cards",
            "cards": [
                {"title": "168-Minute Dwell", "text": "Average carrier dwell time at enterprise logistics hubs nationally."},
                {"title": "$850k Annual Waste", "text": "Unrecoverable demurrage & detention fees paid per 30-bay facility."},
                {"title": "Manual Guardhouses", "text": "Paper clipboards, phone calls, and lost trailers stall dock operations."},
            ],
        },
        {
            "title": "The True Cost of Terminal Congestion",
            "layout": "text",
            "paragraphs": [
                "While enterprise distribution centers invest heavily in automated racking and warehouse WMS, the asphalt yard remains completely blind.",
                "Every minute a driver sits detained past 120 minutes incurs $75-$95/hour in detention penalties.",
                "Truck idling at terminal gates generates thousands of metric tons of avoidable carbon emissions.",
                "DockStream solves the terminal crisis through autonomous software orchestration.",
            ],
        },
        {
            "title": "Introducing DockStream: The Modern Yard Engine",
            "layout": "cards",
            "cards": [
                {"title": "Driver Mobile SMS", "text": "Zero-app multilingual check-in completed in under 90 seconds."},
                {"title": "Autonomous Bay Dispatch", "text": "AI bay allocation factoring staging crew, cold-chain, and priority."},
                {"title": "Yard Mule Telematics", "text": "Digital move manifests sent directly to yard spotter cab tablets."},
            ],
        },
        {
            "title": "The Driver Mobile Experience",
            "layout": "table",
            "table_data": [
                ["Step", "Driver Action", "System Automation", "Elapsed Time"],
                ["1. Geofence Approach", "Receives automated SMS link", "Samsara GPS triggers geofence event", "0 seconds"],
                ["2. Mobile Form", "Enters PO, tractor, trailer ID", "Validates against active TMS appointments", "45 seconds"],
                ["3. Bay Assignment", "Receives real-time dock bay assignment", "Assigns optimal door based on staging crew", "60 seconds"],
                ["4. Digital BOL & Gate In", "Snaps paperwork photo; drives in", "Digital BOL stored; security barrier raises", "90 seconds total"],
            ],
        },
        {
            "title": "Warehouse Operations Dispatch Console",
            "layout": "cards",
            "cards": [
                {"title": "Visual Yard Map", "text": "Real-time digital twin of all trailers, loading bays, and parking stalls."},
                {"title": "Dwell Alert Engine", "text": "Predictive warnings at 60 and 90 minutes before detention charges start."},
                {"title": "Cold-Chain Integrity", "text": "Temperature logger verification and reefer fuel status tracking."},
            ],
        },
        {
            "title": "Predictive Yard Optimization",
            "layout": "text",
            "paragraphs": [
                "DockStream analyzes historical turn times across carrier fleets, cargo types, and warehouse shift crews.",
                "Our machine learning model predicts trailer unload durations with 94.2% accuracy.",
                "Staging crews receive automated pre-alerts 15 minutes before high-priority inbound loads arrive.",
                "Result: 62% reduction in trailer dwell time and zero missed customer retail appointments.",
            ],
        },
        {
            "title": "Enterprise ERP & TMS Integrations",
            "layout": "cards",
            "cards": [
                {"title": "SAP S/4HANA", "text": "Native certified connector with real-time PO receipt sync."},
                {"title": "Manhattan Associates", "text": "Bi-directional WMS integration for dock door inventory staging."},
                {"title": "Oracle OTM & McLeod", "text": "Carrier appointment updates and automated detention billing export."},
            ],
        },
        {
            "title": "Enterprise Security & Compliance",
            "layout": "cards",
            "cards": [
                {"title": "SOC 2 Type II", "text": "Audited cloud infrastructure with end-to-end data encryption."},
                {"title": "FDA FSMA Compliant", "text": "Digital temperature logs and cold-chain custody tracking."},
                {"title": "C-TPAT Security", "text": "Automated trailer seal number verification and driver photo capture."},
            ],
        },
        {
            "title": "Customer Case Study: Apex Logistics Midwest",
            "layout": "table",
            "table_data": [
                ["Metric", "Pre-DockStream Baseline", "DockStream Implementation", "Measured Improvement"],
                ["Average Driver Dwell Time", "168 minutes per visit", "64 minutes per visit", "62% Dwell Reduction"],
                ["Annual Detention Penalties", "$482,000 billed", "$68,000 billed", "86% Demurrage Savings"],
                ["Gate Check-In Duration", "14.2 minutes (paper log)", "1.4 minutes (SMS flow)", "90% Gate Speedup"],
                ["Trailer Move Efficiency", "4.2 moves / spotter hour", "7.8 moves / spotter hour", "85% Yard Productivity"],
            ],
        },
        {
            "title": "Enterprise Subscription & ROI Tiers",
            "layout": "cards",
            "cards": [
                {"title": "Standard Hub ($1,200/mo)", "text": "Up to 20 active loading bays, unlimited driver check-ins, digital BOL."},
                {"title": "Enterprise Fleet ($2,800/mo)", "text": "Unlimited bays, bi-directional SAP/Oracle sync, predictive detention engine."},
                {"title": "Network SLA Guarantee", "text": "99.99% cloud uptime SLA with dedicated implementation engineer."},
            ],
        },
        {
            "title": "14-Day Pilot Deployment & Next Steps",
            "layout": "text",
            "paragraphs": [
                "Launch a zero-risk 14-day production pilot at your primary regional logistics terminal.",
                "Zero capital expenditure: DockStream runs entirely on existing smartphones and web browsers.",
                "Proven payback: Average enterprise client achieves 10x annualized ROI within 60 days.",
                "Contact: Jack Johnson, Co-Founder · jack@dockstream.io · (512) 802-9410",
            ],
        },
    ]
    files["johnson_12slide_outbound_enterprise_deck.pptx"] = write_pptx_file(
        "johnson_12slide_outbound_enterprise_deck.pptx",
        "DockStream: Autonomous Terminal Orchestration",
        deck_slides,
        role="deliverable",
    )

    return files
