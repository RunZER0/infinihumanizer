import re

RULES = [
    (lambda row: str(row.get("Payment Type", "")).lower() == "turnitin_check", "assurance", "assurance-originality"),
    (lambda row: str(row.get("Reference", "")).startswith("ynai_subscription_"), "legacy-product", "legacy-software-subscription"),
    (lambda row: str(row.get("Reference", "")).startswith("ynai_upgrade_"), "legacy-product", "legacy-software-subscription"),
    (lambda row: "addon" in str(row.get("Reference", "")).lower(), "legacy-product", "legacy-research-access"),
]

KEYWORDS = [
    (r"excel|accounting|math|npv|spreadsheet", "studio", "studio-technical"),
    (r"research|essay|paper|anth|review", "studio", "studio-research"),
    (r"website|copy|checklist", "communication", "communication-copy"),
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

    if str(row.get("Payment Type", "")).lower() == "quick_pay":
        return "studio", "studio-review"

    return "unclassified", "legacy-unclassified"
