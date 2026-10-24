"""
dennis.py - Dennis Kiragu (Safari Corridor Logistics) Deliverables
Authentic 45-row Mombasa-Nairobi corridor expenses, reconciliations, and 12-month cashflow models.
"""

from platformhub.chat_files import write_xlsx_file

def build_dennis_deliverables() -> dict[str, dict]:
    files = {}

    # 1. dennis_old_expense_sheet.xlsx: 45 rows of actual Mombasa-Nairobi corridor expenses
    trucks = ["KCU 842P", "KDA 119M", "KDB 482T", "KDD 901W", "KDF 234Q"]
    drivers = ["Joseph Mutua", "Samuel Ochieng", "David Kiprono", "Francis Mwangi", "Peter Kamau"]
    fuel_stations = [
        "Shell Mtito Andei Corridor Stop",
        "TotalEnergies Machakos Junction",
        "Rubis Energy Sultan Hamud",
        "Ola Energy Voi Highway Oasis",
        "National Oil Kibwezi Truck Stop",
    ]

    expense_rows = [
        ["Trip ID", "Truck Registration", "Assigned Driver", "Departure Date", "Origin Depot", "Destination Facility", "Cargo Weight (MT)", "Diesel Litres", "Fuel Cost (KES)", "Fuel Station Location", "Weighbridge Stamp", "Toll & Gate Fees (KES)", "Driver Per Diem (KES)", "En-Route Repairs (KES)", "Total Trip Expense (KES)"],
    ]

    base_date_day = 1
    for i in range(1, 46):
        t_id = f"TRIP-2026-{1000 + i}"
        truck = trucks[(i - 1) % len(trucks)]
        driver = drivers[(i - 1) % len(drivers)]
        day = (i % 28) + 1
        dep_date = f"2026-08-{day:02d}"
        origin = "Mombasa Port Container Terminal" if i % 2 == 1 else "Nairobi Inland Container Depot (ICD)"
        dest = "Nairobi ICD Embakasi" if i % 2 == 1 else "Mombasa Port Berth 19"
        weight = round(24.5 + (i % 6) * 1.5, 1)
        litres = 380 + (i % 8) * 12
        fuel_kes = litres * 214.50
        station = fuel_stations[(i - 1) % len(fuel_stations)]
        stamp = f"WB-MARIAKANI-{8400 + i}"
        toll_kes = 3500.00
        per_diem = 6500.00
        repair_kes = 2500.00 if i % 4 == 0 else 0.00
        total_trip = fuel_kes + toll_kes + per_diem + repair_kes

        expense_rows.append([
            t_id, truck, driver, dep_date, origin, dest, weight, litres, fuel_kes, station, stamp, toll_kes, per_diem, repair_kes, total_trip
        ])

    files["dennis_old_expense_sheet.xlsx"] = write_xlsx_file(
        "dennis_old_expense_sheet.xlsx",
        "Corridor_Expenses_Raw",
        expense_rows,
        role="source",
    )

    # 2. dennis_q3_corridor_reconciliation_final.xlsx: 45 rows of reconciled corridor logistics
    recon_rows = [
        ["Trip ID", "Truck Reg", "Driver Name", "Transit Duration (Hrs)", "Planned Litres", "Actual Litres", "Fuel Variance (KES)", "Customer Freight Invoice (KES)", "Operating Margin %", "Reconciliation Status"],
    ]
    for i in range(1, 46):
        t_id = f"TRIP-2026-{1000 + i}"
        truck = trucks[(i - 1) % len(trucks)]
        driver = drivers[(i - 1) % len(drivers)]
        hrs = 14.5 + (i % 5) * 1.2
        planned_litres = 390.0
        act_litres = 380.0 + (i % 8) * 12.0
        var_kes = (act_litres - planned_litres) * 214.50
        invoice_kes = 165000.00 + (i % 4) * 8000.00
        total_exp = (act_litres * 214.50) + 3500.00 + 6500.00 + (2500.00 if i % 4 == 0 else 0.00)
        margin = round(((invoice_kes - total_exp) / invoice_kes) * 100, 1)
        status = "RECONCILED [AUDITED]"

        recon_rows.append([
            t_id, truck, driver, hrs, planned_litres, act_litres, var_kes, invoice_kes, margin, status
        ])

    files["dennis_q3_corridor_reconciliation_final.xlsx"] = write_xlsx_file(
        "dennis_q3_corridor_reconciliation_final.xlsx",
        "Corridor_Reconciliation_Q3",
        recon_rows,
        role="deliverable",
    )

    return files
