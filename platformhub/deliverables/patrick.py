"""
patrick.py - Patrick Hyland (Atlantic Cross-Border Freight) Deliverables
Authentic 35-row Newfoundland ferry crossing logs, 30-row dispatch fuel trackers, and freight rate sheets.
"""

from platformhub.chat_files import write_xlsx_file

def build_patrick_deliverables() -> dict[str, dict]:
    files = {}

    # 1. patrick_newfoundland_dispatch_raw.xlsx: 35 rows of Marine Atlantic ferry crossings
    vessels = ["MV Blue Puttees", "MV Highlanders", "MV Atlantic Vision"]
    cargos = ["Refrigerated Fresh Produce", "Frozen Atlantic Seafood", "Packaged Groceries & Dry Goods", "Industrial Machinery Parts", "Building Materials & Timber"]

    ferry_rows = [
        ["Manifest Ref", "Crossing Date", "Departure Terminal", "Arrival Terminal", "Ferry Vessel", "Tractor Unit", "Trailer Unit", "Cargo Classification", "Gross Weight (lbs)", "Marine Ferry Fare (CAD)", "Fuel Surcharge (CAD)", "Weather Delay Status", "Total Crossing Cost (CAD)"],
    ]

    for i in range(1, 36):
        m_ref = f"FERRY-2026-{4000 + i}"
        day = (i % 28) + 1
        c_date = f"2026-09-{day:02d}"
        dep_port = "North Sydney, NS Terminal" if i % 2 == 1 else "Port aux Basques, NL Terminal"
        arr_port = "Port aux Basques, NL Terminal" if i % 2 == 1 else "North Sydney, NS Terminal"
        vessel = vessels[(i - 1) % len(vessels)]
        tractor = f"TR-NL-{100 + (i % 8)}"
        trailer = f"TRL-53R-{800 + i}"
        cargo = cargos[(i - 1) % len(cargos)]
        weight = 34000 + (i % 12) * 1200
        fare = 1420.00 if "Refrigerated" in cargo or "Frozen" in cargo else 1280.00
        fsc = round(fare * 0.185, 2)
        weather = "High Wind Advisory (Delayed 4 hrs)" if i % 7 == 0 else "Normal Sea Conditions [ON TIME]"
        total = fare + fsc

        ferry_rows.append([
            m_ref, c_date, dep_port, arr_port, vessel, tractor, trailer, cargo, weight, fare, fsc, weather, total
        ])

    files["patrick_newfoundland_dispatch_raw.xlsx"] = write_xlsx_file(
        "patrick_newfoundland_dispatch_raw.xlsx",
        "Raw_Dispatch_Logs",
        ferry_rows,
        role="source",
    )

    # 2. patrick_dispatch_and_fuel_tracker_v1.xlsx: 30 rows of Atlantic dispatch trips
    tracker_rows = [
        ["Trip ID", "Trip Date", "Origin City", "Destination City", "Total Miles", "Empty Miles", "Diesel Gallons", "Diesel Cost (CAD)", "Highway Tolls (CAD)", "Driver Pay (CAD)", "Freight Revenue (CAD)", "Net Operating Profit (CAD)"],
    ]
    routes = [
        ("Halifax, NS", "St. John's, NL", 880),
        ("Moncton, NB", "Corner Brook, NL", 640),
        ("Dartmouth, NS", "Gander, NL", 790),
        ("Truro, NS", "Mount Pearl, NL", 895),
        ("Saint John, NB", "Grand Falls, NL", 720),
    ]

    for i in range(1, 31):
        t_id = f"ATL-DISP-{3000 + i}"
        day = (i % 28) + 1
        t_date = f"2026-09-{day:02d}"
        origin, dest, miles = routes[(i - 1) % len(routes)]
        empty = 40 + (i % 5) * 15
        gals = round((miles + empty) / 6.8, 1)
        fuel_cost = round(gals * 7.45, 2)
        tolls = 125.00 if i % 2 == 0 else 65.00
        driver_pay = round(miles * 0.68, 2)
        rev = round(miles * 3.85, 2)
        profit = round(rev - (fuel_cost + tolls + driver_pay), 2)

        tracker_rows.append([
            t_id, t_date, origin, dest, miles, empty, gals, fuel_cost, tolls, driver_pay, rev, profit
        ])

    files["patrick_dispatch_and_fuel_tracker_v1.xlsx"] = write_xlsx_file(
        "patrick_dispatch_and_fuel_tracker_v1.xlsx",
        "Dispatch_Tracker_v1",
        tracker_rows,
        role="draft",
    )

    # 3. patrick_spring_freight_rates_final.xlsx: 30 rows of cross-border freight tariffs
    rate_rows = [
        ["Lane Code", "Origin Depot", "Destination Facility", "Equipment Class", "Transit Days", "Base Freight Rate CAD", "Fuel Surcharge %", "Marine Ferry Inclusion", "Customs Clearance Fee", "All-In Quoted Rate CAD"],
    ]
    origins = ["Halifax Logistics Park, NS", "Moncton Freight Hub, NB", "Saint John Industrial, NB", "Truro Distribution Depot, NS", "Sydney Freight Terminal, NS"]
    dests = ["St. John's Port, NL", "Corner Brook Depot, NL", "Grand Falls Terminal, NL", "Gander Warehouse, NL", "Mount Pearl Hub, NL", "Boston Distribution, MA (US)"]

    for i in range(1, 31):
        l_code = f"LANE-ATL-{200 + i}"
        orig = origins[(i - 1) % len(origins)]
        dst = dests[(i - 1) % len(dests)]
        equip = "53ft Tri-Axle Reefer (Temperature Controlled)" if i % 2 == 1 else "53ft Tandem Dry Van (Air Ride)"
        days = 2 if "NL" in dst else 3
        base = 2850.00 + (i % 5) * 250.00
        fsc_pct = 19.5
        ferry_inc = "Yes ($1,420 Marine Atlantic Included)" if "NL" in dst else "No (Highway Route)"
        cust_fee = 150.00 if "US" in dst else 0.00
        all_in = round(base * (1 + fsc_pct / 100.0) + cust_fee, 2)

        rate_rows.append([
            l_code, orig, dst, equip, days, base, fsc_pct, ferry_inc, cust_fee, all_in
        ])

    files["patrick_spring_freight_rates_final.xlsx"] = write_xlsx_file(
        "patrick_spring_freight_rates_final.xlsx",
        "Atlantic_Freight_Rates_2026",
        rate_rows,
        role="deliverable",
    )

    return files
