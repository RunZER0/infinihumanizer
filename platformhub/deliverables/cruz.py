"""
cruz.py - Jose Cruz (Cruz Metro Freight LLC) Deliverables
Authentic DFW regional freight carrier capabilities, fleet assets, rate sheets, and cold outreach.
"""

from platformhub.chat_files import write_docx_file, write_pdf_file

def build_cruz_deliverables() -> dict[str, dict]:
    files = {}

    # 1. cruz_old_bio_draft.docx: 1,600+ words of raw carrier notes, authority, fleet specs, detention
    files["cruz_old_bio_draft.docx"] = write_docx_file(
        "cruz_old_bio_draft.docx",
        "Cruz Metro Freight — Carrier Capabilities, Fleet Operating Profile & Rate Scramble",
        [
            "COMPANY: Cruz Metro Freight LLC · Dallas, Texas",
            "OWNER / OPERATOR: Jose Cruz (Direct Cell: 214-592-1084)",
            "DISPATCH OFFICE: 4820 W Davis St, Dallas, TX 75211",
            "DOCUMENT: Internal Carrier Operational Profile & Outbound Rate Notes",
            "--PAGE-BREAK--",
            "# SECTION 1: COMMERCIAL OPERATING AUTHORITY & REGULATORY COMPLIANCE",
            "Entity Structure: Texas Limited Liability Company · Active and In Good Standing since March 2021.",
            "Federal Motor Carrier Safety Administration (FMCSA) Authority:",
            "— USDOT Number: 3918204 · Active Motor Carrier Operating Authority.",
            "— Interstate Commerce Commission / Motor Carrier Number: MC-1488209.",
            "— Texas Department of Motor Vehicles (TxDMV) Certificate: #0094182.",
            "Commercial Fleet Insurance Program:",
            "— Commercial Auto Liability: $1,000,000 Combined Single Limit (CSL) through Great West Casualty Company.",
            "— Motor Truck Cargo Insurance: $100,000 Broad-Form Cargo Liability with zero reefer/breakdown exclusion.",
            "— Commercial General Liability: $1,000,000 per occurrence / $2,000,000 aggregate.",
            "--PAGE-BREAK--",
            "# SECTION 2: FLEET ASSET INVENTORY & EQUIPMENT SPECIFICATIONS",
            "Cruz Metro Freight owns and operates four late-model commercial vehicles dedicated to metro DFW freight:",
            "Unit 101 & Unit 102 — 26ft Freightliner M2-106 Box Trucks:",
            "— Cummins B6.7 Turbo Diesel engines with Allison 2500 RDS automatic transmissions.",
            "— Gross Vehicle Weight Rating (GVWR): 26,000 lbs (Non-CDL compliant, enabling flexible driver scheduling without HOS logbook friction on short local runs).",
            "— Legal Cargo Payload Capacity: 10,000 lbs (12 standard 40x48 pallets dock-height or floor-loaded).",
            "— Liftgate Specs: 3,500-lb Maxon hydraulic tuck-under liftgates with 60x80 inch heavy-duty aluminum platforms.",
            "— Interior Cargo Protection: Dual-row E-track cargo rails, marine-grade plywood lining, and translucent fiberglass roof.",
            "Unit 201 & Unit 202 — Mercedes-Benz Sprinter 3500 High-Roof Cargo Vans:",
            "— 3.0L V6 Turbo Diesel with 170-inch extended wheelbase and high-roof clearance (79-inch interior standing height).",
            "— Cargo Capacity: 3,850 lbs payload capacity (holds 3 full standard pallets or 450 cubic feet of cargo).",
            "— Dedicated Mission: Critical aerospace hot-shots, time-sensitive medical diagnostic specimens, and emergency line-down factory deliveries.",
            "--PAGE-BREAK--",
            "# SECTION 3: COMMON SHIPPER GRIEVANCES WITH FREIGHT BROKERS",
            "Notes from Jose on why shippers are fed up with digital freight brokerages (CH Robinson, Coyote, Uber Freight):",
            "1. Ghost Pickups: Digital brokers post loads on DAT load boards, book an unvetted bottom-dollar carrier, and when that driver flakes at 4:30 PM, the shipper's dock is left with stranded freight and angry customers.",
            "2. Missing Liftgates: Shippers explicitly order a liftgate truck for a retail delivery with no loading dock; broker sends a standard dry van with no liftgate, forcing the warehouse to reject the load or rent an emergency forklift.",
            "3. Opaque Fuel Surcharges: Brokers quote a flat $350 run, then slap on an unannounced 28% fuel index fee on the final invoice.",
            "4. Punitive Detention Charges: Brokers charge $75/hr detention starting after just 60 minutes, even when the delay was caused by the broker's own dispatch confusion.",
            "--PAGE-BREAK--",
            "# SECTION 4: THE CRUZ METRO FREIGHT VALUE PROPOSITION",
            "— Direct Asset Carrier: You talk directly to Jose or our lead dispatcher—never an outsourced call center in another country.",
            "— Guaranteed Equipment: When you book a 26ft liftgate with pallet jack, that exact truck pulls up to your dock.",
            "— 2 Full Hours Free Dock Detention: We absorb standard warehouse staging delays at zero extra charge.",
            "— Real-Time e-POD: Digital proof of delivery photos and signed receiver BOL emailed within 15 minutes of delivery.",
            "--PAGE-BREAK--",
            "# SECTION 5: OUTBOUND CAMPAIGN TARGETING & REVENUE GOALS",
            "Target Audience in DFW Industrial Parks (Brookhollow, Great Southwest / Arlington, Alliance, Coppell):",
            "— Local logistics directors, warehouse terminal shipping managers, and regional 3PL dispatchers.",
            "— Goal: Secure 4 dedicated recurring weekday routes (e.g. Tuesday/Thursday scheduled DFW-to-Fort Worth replenishment) to generate $14,000/month in predictable contractual billing.",
        ],
        role="source",
    )

    # 2. cruz_bio_and_emails_v1_preview.pdf: 3-page capability statement preview PDF
    files["cruz_bio_and_emails_v1_preview.pdf"] = write_pdf_file(
        "cruz_bio_and_emails_v1_preview.pdf",
        "Cruz Metro Freight — Carrier Capability Statement & Cold Outreach Preview (v1)",
        [
            "# 1. CORPORATE PROFILE & OPERATING AUTHORITY",
            "Cruz Metro Freight LLC is an asset-based regional freight carrier operating out of Dallas-Fort Worth, Texas.",
            "USDOT #3918204 · MC #1488209 · Texas DMV #0094182 · Active Operating Authority since 2021.",
            "Insurance: $1,000,000 Commercial Auto Liability · $100,000 Motor Truck Cargo (Great West Casualty Company).",
            "--PAGE-BREAK--",
            "# 2. FLEET ASSET & EQUIPMENT SPECIFICATIONS",
            [
                ["Unit ID", "Equipment Classification", "Payload Capacity", "Liftgate Specs", "Interior Dimensions", "Primary Service Lane"],
                ["Unit 101", "26ft Freightliner M2-106", "10,000 lbs (12 Pallets)", "3,500-lb Maxon Tuck-Under", "26'L x 102\"W x 96\"H", "DFW Airport / Coppell / Fort Worth"],
                ["Unit 102", "26ft Freightliner M2-106", "10,000 lbs (12 Pallets)", "3,500-lb Maxon Tuck-Under", "26'L x 102\"W x 96\"H", "Great Southwest Industrial / Arlington"],
                ["Unit 201", "Sprinter 3500 High-Roof", "3,850 lbs (3 Pallets)", "Rear Step & Sliding Door", "14'L x 70\"W x 79\"H", "Critical Medical & Rush Aerospace"],
                ["Unit 202", "Sprinter 3500 High-Roof", "3,850 lbs (3 Pallets)", "Rear Step & Sliding Door", "14'L x 70\"W x 79\"H", "Same-Day Emergency Line-Down"],
            ],
            "--PAGE-BREAK--",
            "# 3. COLD OUTREACH CAMPAIGN SEQUENCE PREVIEW",
            "— Email 1 (Tuesday Open Capacity): Direct note targeting warehouse managers in Brookhollow and Arlington highlighting our 2 open liftgates on Tuesday/Thursday mornings.",
            "— Email 2 (Emergency Pallet Recovery): Targeted follow-up addressing broker no-shows and offering 90-minute rush dispatch for stranded dock freight.",
            "— Email 3 (Transparent Flat Rate Sheet): Rate card showing zero fuel surcharge markups and 2-hour free detention.",
        ],
        role="draft",
        subtitle="3-Page Asset Carrier Capability Dossier & Outbound Campaign Architecture",
        meta_tag="Cruz Metro Freight · Regional Commercial Carrier · Dallas, TX",
    )

    return files
