"""
luca.py - Luca Carollo (Pacific Oasis Hospitality & Yacht Charters) Deliverables
Authentic yacht charter rates (30 rows), harbor manifests (35 rows), vendor receipts (3 pages), and partner equity models.
"""

from platformhub.chat_files import write_pdf_file, write_xlsx_file, write_csv_file

def build_luca_deliverables() -> dict[str, dict]:
    files = {}

    # 1. luca_charter_rates_raw.xlsx: 30 rows of yacht charter rates
    charter_rows = [
        ["Package Code", "Vessel Name", "Vessel Type & Length", "Charter Description", "Guest Capacity", "Duration (Hours)", "Base Charter Rate USD", "Captain & Crew Fee", "Marine Fuel Surcharge", "Harbor Wharfage Tax", "Premium Catering Option", "Total Quoted Package"],
        ["PKG-OAH-01", "Pacific Pearl", "44ft Sea Ray Sundancer", "Waikiki Sunset Champagne Cruise", 12, 3.0, 1850.00, 350.00, 180.00, 95.00, 450.00, 2925.00],
        ["PKG-OAH-02", "Pacific Pearl", "44ft Sea Ray Sundancer", "Diamond Head Snorkel Safari", 12, 4.0, 2400.00, 450.00, 220.00, 110.00, 550.00, 3730.00],
        ["PKG-OAH-03", "Pacific Pearl", "44ft Sea Ray Sundancer", "South Shore Half-Day Adventure", 12, 5.0, 2950.00, 550.00, 260.00, 135.00, 680.00, 4575.00],
        ["PKG-OAH-04", "Pacific Pearl", "44ft Sea Ray Sundancer", "Full-Day Coastal Expedition", 12, 8.0, 4500.00, 800.00, 420.00, 195.00, 950.00, 6865.00],
        ["PKG-OAH-05", "Oahu Star", "52ft Sunseeker Manhattan", "Executive Sunset Wine Tasting", 18, 3.5, 3200.00, 500.00, 290.00, 160.00, 750.00, 4900.00],
        ["PKG-OAH-06", "Oahu Star", "52ft Sunseeker Manhattan", "Turtle Canyon Private Snorkel", 18, 4.5, 3950.00, 650.00, 340.00, 185.00, 880.00, 6005.00],
        ["PKG-OAH-07", "Oahu Star", "52ft Sunseeker Manhattan", "Sandbar Kaneohe Bay Excursion", 18, 6.0, 5200.00, 850.00, 480.00, 240.00, 1150.00, 7920.00],
        ["PKG-OAH-08", "Oahu Star", "52ft Sunseeker Manhattan", "VIP All-Day Molokai Channel Run", 18, 9.0, 7800.00, 1200.00, 780.00, 340.00, 1650.00, 11770.00],
        ["PKG-OAH-09", "Blue Horizon", "38ft Fountain Pajot Cat", "Morning Whale Watching Safari", 14, 3.0, 1650.00, 320.00, 140.00, 85.00, 380.00, 2575.00],
        ["PKG-OAH-10", "Blue Horizon", "38ft Fountain Pajot Cat", "Midday Reef & Seabob Safari", 14, 4.0, 2100.00, 420.00, 180.00, 105.00, 480.00, 3285.00],
        ["PKG-OAH-11", "Blue Horizon", "38ft Fountain Pajot Cat", "Waikiki Fireworks Friday Cruise", 14, 3.0, 2250.00, 400.00, 160.00, 120.00, 520.00, 3450.00],
        ["PKG-OAH-12", "Kai Lani", "60ft Horizon Motor Yacht", "Ultra-Luxury Sunset Soiree", 24, 4.0, 5800.00, 950.00, 520.00, 280.00, 1400.00, 8950.00],
        ["PKG-OAH-13", "Kai Lani", "60ft Horizon Motor Yacht", "Oahu South Coast Grand Cruise", 24, 6.0, 8200.00, 1400.00, 740.00, 380.00, 1950.00, 12670.00],
        ["PKG-OAH-14", "Kai Lani", "60ft Horizon Motor Yacht", "Private Chef Multi-Course Dinner", 16, 4.0, 6400.00, 1100.00, 480.00, 290.00, 2200.00, 10470.00],
        ["PKG-OAH-15", "Moana Wave", "34ft Boston Whaler Outrage", "Offshore Sport Fishing (Half-Day)", 6, 4.5, 1450.00, 300.00, 240.00, 75.00, 280.00, 2345.00],
        ["PKG-OAH-16", "Moana Wave", "34ft Boston Whaler Outrage", "Offshore Pelagic Fishing (Full-Day)", 6, 8.5, 2600.00, 550.00, 460.00, 130.00, 420.00, 4160.00],
        ["PKG-OAH-17", "Moana Wave", "34ft Boston Whaler Outrage", "Kaena Point Coastal Explorer", 6, 5.0, 1750.00, 350.00, 280.00, 90.00, 320.00, 2790.00],
        ["PKG-OAH-18", "Pacific Pearl", "44ft Sea Ray Sundancer", "Romantic Couples Sunset Escape", 2, 2.5, 1600.00, 300.00, 150.00, 80.00, 480.00, 2610.00],
        ["PKG-OAH-19", "Oahu Star", "52ft Sunseeker Manhattan", "Corporate Team Building Cruise", 18, 5.0, 4400.00, 750.00, 380.00, 220.00, 1050.00, 6800.00],
        ["PKG-OAH-20", "Blue Horizon", "38ft Fountain Pajot Cat", "Sunrise Yoga & Coastal Cruise", 10, 3.0, 1550.00, 300.00, 130.00, 75.00, 340.00, 2395.00],
        ["PKG-OAH-21", "Kai Lani", "60ft Horizon Motor Yacht", "Wedding Reception / Rehearsal", 24, 5.0, 7200.00, 1200.00, 620.00, 350.00, 2400.00, 11770.00],
        ["PKG-OAH-22", "Pacific Pearl", "44ft Sea Ray Sundancer", "Afternoon Seabob & Hydrofoil Fun", 8, 4.0, 2600.00, 480.00, 240.00, 120.00, 600.00, 4040.00],
        ["PKG-OAH-23", "Oahu Star", "52ft Sunseeker Manhattan", "Sunset Cocktail Mixer & DJ Set", 18, 4.0, 3800.00, 600.00, 320.00, 180.00, 950.00, 5850.00],
        ["PKG-OAH-24", "Moana Wave", "34ft Boston Whaler Outrage", "South Shore Spearfishing Charter", 4, 5.0, 1800.00, 380.00, 290.00, 95.00, 320.00, 2885.00],
        ["PKG-OAH-25", "Blue Horizon", "38ft Fountain Pajot Cat", "Afternoon Sunset & Dolphin Watch", 14, 3.5, 1950.00, 380.00, 160.00, 95.00, 440.00, 3025.00],
        ["PKG-OAH-26", "Kai Lani", "60ft Horizon Motor Yacht", "Inter-Island Maui VIP Transfer", 12, 12.0, 14500.00, 2400.00, 1850.00, 650.00, 2800.00, 22200.00],
        ["PKG-OAH-27", "Pacific Pearl", "44ft Sea Ray Sundancer", "Honolulu Skyline Night Lights", 10, 2.5, 1500.00, 300.00, 140.00, 75.00, 380.00, 2395.00],
        ["PKG-OAH-28", "Oahu Star", "52ft Sunseeker Manhattan", "Luxury Family Snorkel & Paddleboard", 16, 4.5, 4100.00, 680.00, 350.00, 195.00, 890.00, 6215.00],
        ["PKG-OAH-29", "Blue Horizon", "38ft Fountain Pajot Cat", "Midday Sailing Masterclass", 8, 4.0, 1850.00, 400.00, 120.00, 85.00, 380.00, 2835.00],
        ["PKG-OAH-30", "Kai Lani", "60ft Horizon Motor Yacht", "New Year's Eve Fireworks Gala", 24, 5.0, 11000.00, 1800.00, 850.00, 500.00, 3500.00, 17650.00],
    ]
    files["luca_charter_rates_raw.xlsx"] = write_xlsx_file(
        "luca_charter_rates_raw.xlsx",
        "Charter_Pricing_Notes",
        charter_rows,
        role="source",
    )

    # 2. luca_harbor_seasonal_manifest_v2.xlsx: 35 rows of harbor slip manifests
    manifest_rows = [
        ["Slip ID", "Harbor Location", "Berth Berth Tier", "Vessel Name", "Length Overall (LOA)", "Beam (ft)", "Draft (ft)", "Monthly Berth Fee USD", "Electric Metered Fee", "Commercial Landing Permit", "Insurance Exp Date", "Owner / Management Entity"],
    ]
    vessels = ["Pacific Pearl", "Oahu Star", "Blue Horizon", "Kai Lani", "Moana Wave"]
    harbors = ["Ala Wai Small Boat Harbor", "Kewalo Basin Commercial Harbor"]
    for i in range(1, 36):
        s_id = f"BERTH-KW-{100 + i}" if i % 2 == 1 else f"BERTH-AW-{200 + i}"
        harbor = harbors[i % 2]
        tier = "Tier 1 Commercial Slip" if i <= 15 else "Tier 2 Recreational / Commercial"
        vessel = vessels[(i - 1) % len(vessels)] if i <= 10 else f"Charter Fleet Reserve #{i}"
        loa = 34 + (i % 6) * 5
        beam = 12.0 + (i % 4) * 1.5
        draft = 3.5 + (i % 3) * 0.8
        fee = 850.00 + (loa * 24.50)
        elec = 145.00 + (i % 5) * 25.00
        permit = f"HI-DLNR-COMM-{8900 + i}"
        ins_exp = f"2027-0{((i % 8) + 1):02d}-15"
        owner = "Pacific Oasis Charters LLC" if i <= 12 else f"Hawaii Marine Holding #{i}"

        manifest_rows.append([
            s_id, harbor, tier, vessel, f"{loa} ft", f"{beam} ft", f"{draft} ft", fee, elec, permit, ins_exp, owner
        ])

    files["luca_harbor_seasonal_manifest_v2.xlsx"] = write_xlsx_file(
        "luca_harbor_seasonal_manifest_v2.xlsx",
        "Harbor_Manifest_2026",
        manifest_rows,
        role="deliverable",
    )

    # 3. luca_august_vendor_receipts.pdf: 3-page consolidated marine receipts PDF
    files["luca_august_vendor_receipts.pdf"] = write_pdf_file(
        "luca_august_vendor_receipts.pdf",
        "Pacific Oasis Charters — August Marine Maintenance & Vendor Disbursement Audit",
        [
            "# 1. MONTHLY MARINE OPERATING SUMMARY",
            "Entity: Pacific Oasis Luxury Charters & Marine Holdings LLC · Kewalo Basin Harbor, Honolulu, HI.",
            "Accounting Period: August 1 – August 31, 2026 · Compiled for Managing Partner Review (Luca Carollo).",
            "Total Operating Disbursements: $18,450.00 across fleet diesel bunkering, split-AC servicing, marine slip leases, and USCG annual inspection compliance.",
            "--PAGE-BREAK--",
            "# 2. ITEMIZED VENDOR DISBURSEMENT LEDGER",
            [
                ["Vendor / Contractor", "Invoice Ref", "Vessel / Property", "Service Description", "Disbursement USD"],
                ["Aloha Petroleum Marine Fuel", "INV-APM-9481", "Oahu Star (52ft)", "Ultra-Low Sulfur Marine Diesel (820 gal)", "$4,180.00"],
                ["Pacific Split-AC Air Systems", "INV-PAC-4821", "Waikiki Penthouse 12A", "Dual-zone mini-split coil clean & freon", "$620.00"],
                ["Kakaako Marine Rigging", "INV-KMR-2910", "Blue Horizon (38ft)", "Standing rigging tensioning & shroud check", "$890.00"],
                ["CleanTeam Hawaii Eco", "INV-CTH-3409", "Pacific Pearl (44ft)", "Deep interior teak detailing & cabin steam", "$480.00"],
                ["DLNR State of Hawaii Harbors", "INV-DLNR-8821", "Slips 104 & 108", "August commercial wharfage & berth leases", "$3,240.00"],
                ["Honolulu Marine Diesel Techs", "INV-HMD-1940", "Kai Lani (60ft)", "Caterpillar C18 oil & zinc anode service", "$2,850.00"],
                ["Kewalo Basin Drydock Corp", "INV-KBD-7712", "Moana Wave (34ft)", "Hull pressure wash & anti-fouling touch-up", "$1,450.00"],
                ["Island Electronics & Radar", "INV-IER-5021", "Oahu Star (52ft)", "Garmin Phantom Radar firmware & calibration", "$740.00"],
            ],
            "--PAGE-BREAK--",
            "# 3. U.S. COAST GUARD INSPECTION CERTIFICATION",
            "This document certifies that vessels Oahu Star (Doc #1184920), Pacific Pearl (Doc #1209418), and Kai Lani (Doc #1248019) successfully completed their annual U.S. Coast Guard Sector Honolulu Safety & Life Raft Inspections on August 18, 2026.",
            "All vessels carry current Certificates of Documentation (COD), inspected Type 1 SOLAS life vests, automatic EPIRB beacons, and serviced Fireboy engine bay fire suppression systems.",
            "Certified by: Captain Luca Carollo, USCG Master 100-Ton License #7410294.",
        ],
        role="source",
        subtitle="3-Page Consolidated Marine Operating Receipts & USCG Compliance Dossier",
        meta_tag="Pacific Oasis Charters · Marine Operations Ledger",
    )

    # 4. luca_oahu_charter_booking_deck_final.pdf: 4-page charter booking deck PDF
    files["luca_oahu_charter_booking_deck_final.pdf"] = write_pdf_file(
        "luca_oahu_charter_booking_deck_final.pdf",
        "Pacific Oasis Luxury Yacht Charters — Oahu Fleet Portfolio & Private Excursions",
        [
            "# 1. PACIFIC OASIS LUXURY CHARTERS",
            "Welcome aboard Pacific Oasis Luxury Yacht Charters. We curate private, bespoke luxury maritime experiences departing daily from Kewalo Basin Harbor and Ala Wai Harbor in Honolulu, Hawaii.",
            "Our private fleet features state-of-the-art luxury motor yachts and catamarans equipped with professional USCG-licensed captains, private culinary chefs, Seabob hydrofoils, and five-star hospitality.",
            "--PAGE-BREAK--",
            "# 2. FLEET SPECIFICATIONS & LUXURY AMENITIES",
            [
                ["Vessel Name", "Length & Builder", "Max Guests", "Cruising Speed", "Signature Luxury Features"],
                ["Kai Lani", "60ft Horizon Motor Yacht", "24 Guests", "18 knots", "Flybridge Jacuzzi, teak dining deck, 3 en-suite staterooms"],
                ["Oahu Star", "52ft Sunseeker Manhattan", "18 Guests", "22 knots", "Hydraulic swim platform, Sonos sound, wet bar, AC salon"],
                ["Pacific Pearl", "44ft Sea Ray Sundancer", "12 Guests", "20 knots", "Open bow sunpads, snorkel gear, Seabob hydrofoils"],
                ["Blue Horizon", "38ft Fountain Pajot Cat", "14 Guests", "12 knots", "Forward trampoline lounge, twin hull stability, 360 views"],
            ],
            "--PAGE-BREAK--",
            "# 3. CURATED PRIVATE CHARTER EXCURSIONS",
            "— Waikiki Sunset & Diamond Head Champagne Cruise: 3 hours of golden-hour sailing with curated wine and artisan charcuterie.",
            "— Turtle Canyon & South Shore Snorkel Safari: 4 hours exploring vibrant marine reefs, wild sea turtles, and pristine blue waters.",
            "— Kaneohe Bay Sandbar VIP Adventure: 6-hour excursion to Oahu's famous sunken sandbar with paddleboards and private chef barbecue.",
            "— Inter-Island Channel Crossing (Maui / Lanai): Full-day offshore luxury voyage across the Kaiwi Channel.",
            "--PAGE-BREAK--",
            "# 4. CULINARY EXPERIENCES & PRIVATE BOOKING INTAKE",
            "— Private Chef Program: Multi-course Hawaiian fusion tasting menus featuring locally caught ahi sashimi, Kona kampachi, and Maui beef.",
            "— Beverage Packages: Sommelier-selected vintage champagne, artisanal island cocktails, and craft local brews.",
            "— Direct Concierge Reservations: Luca Carollo, Managing Director · (808) 720-4190 · luca@pacificoasischarters.com",
        ],
        role="deliverable",
        subtitle="4-Page Luxury Yacht Fleet Portfolio, Excursion Packages & Private Concierge Guide",
        meta_tag="Pacific Oasis Charters · Luxury Maritime Portfolio",
    )

    # 5. luca_partner_distribution_summary.csv: 25 rows of quarterly partner distributions
    dist_rows = [
        ["Distribution Ref", "Quarter", "Partner Name", "Equity Share %", "Gross Distributable Cash USD", "Priority Return Tier 1", "Performance Carry Tier 2", "Withholding Tax USD", "Net Distributed USD", "Bank Wire Reference", "Disbursement Date"],
    ]
    partners = ["Luca Carollo", "Kai Holdings Trust", "Mauna Kea Capital LLC", "Pacific Maritime Partners"]
    shares = [40.0, 30.0, 20.0, 10.0]
    for q_idx in range(1, 7):
        q_label = f"Q{(q_idx % 4) + 1} 2025" if q_idx <= 4 else f"Q{q_idx - 4} 2026"
        for p_idx, p_name in enumerate(partners):
            ref = f"DIST-{q_label.replace(' ', '')}-{p_idx + 1}"
            sh = shares[p_idx]
            gross = 180000.00 * (sh / 100.0)
            prio = gross * 0.70
            carry = gross * 0.30
            tax = gross * 0.05
            net = gross - tax
            wire = f"FHB-WIRE-94810{q_idx}{p_idx}"
            date = f"2026-0{((q_idx * 2) % 9) + 1:02d}-15"
            dist_rows.append([
                ref, q_label, p_name, f"{sh}%", gross, prio, carry, tax, net, wire, date
            ])

    files["luca_partner_distribution_summary.csv"] = write_csv_file(
        "luca_partner_distribution_summary.csv",
        dist_rows,
        role="deliverable",
    )

    return files
