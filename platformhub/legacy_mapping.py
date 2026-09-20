import re
from decimal import Decimal, InvalidOperation

RULES = [
    (lambda row: str(row.get("Payment Type", "")).lower() == "turnitin_check", "assurance", "assurance-originality"),
    (lambda row: str(row.get("Reference", "")).startswith("ynai_subscription_"), "legacy-product", "legacy-software-subscription"),
    (lambda row: str(row.get("Reference", "")).startswith("ynai_upgrade_"), "legacy-product", "legacy-software-subscription"),
    (lambda row: "addon" in str(row.get("Reference", "")).lower(), "legacy-product", "legacy-research-access"),
]

# Historical labels are normalized for finance without pretending every old
# activity is a service InfiniAI sells today. Academic-course language stays
# explicitly legacy; professional research/technical/communication work maps
# into the current operating system where the memo supports it.
KEYWORDS = [
    (r"homework|assignment|exam|course|essays?\b", "legacy-production", "legacy-managed-production"),
    (r"excel|accounting|math|npv|spreadsheet", "studio", "studio-technical"),
    (r"scientific research|research paper|\bresearch\b|review|synthesis", "studio", "studio-research"),
    (r"website|checklist|copy", "communication", "communication-audit"),
    (r"coding|computer science|software|model", "systems", "systems-discovery"),
    (r"deck|presentation|slides", "studio", "studio-deck"),
]


def normalize_legacy_transaction(row):
    for predicate, family, code in RULES:
        try:
            if predicate(row):
                return family, code
        except Exception:
            continue

    description = str(row.get("Description") or "").strip().lower()
    for pattern, family, code in KEYWORDS:
        if re.search(pattern, description):
            return family, code

    # A generic quick-pay reference proves a payment happened, not what work it
    # bought. Keep it visible for manual reconciliation instead of inventing a
    # service category from the amount alone.
    return "unclassified", "legacy-unclassified"


def legacy_amount_band(row):
    try:
        amount = Decimal(str(row.get("Amount Paid") or "0"))
    except InvalidOperation:
        amount = Decimal("0")
    currency = str(row.get("Currency") or "").upper()

    if currency == "KES":
        if amount <= Decimal("100"):
            return "legacy_micro_access"
        if amount <= Decimal("700"):
            return "legacy_focused_work"
        if amount <= Decimal("2000"):
            return "legacy_plan_or_project_payment"
        return "legacy_large_payment"

    if currency == "USD":
        if amount <= Decimal("20"):
            return "legacy_micro_access"
        if amount <= Decimal("75"):
            return "legacy_focused_work"
        if amount <= Decimal("250"):
            return "legacy_professional_work"
        return "legacy_project_payment"

    return "legacy_unknown_currency"
