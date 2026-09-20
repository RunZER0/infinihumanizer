LEGACY_LEDGER_SUMMARY = {
    "rows": 169,
    "success": 68,
    "abandoned": 77,
    "failed": 24,
    "successful_ranges": {
        "USD": "$1–$500",
        "KES": "KSh 20–KSh 2,000",
    },
    "principle": "Preserve the original transaction memo, add a normalized service classification only where evidence supports it, and keep ambiguous quick-pay records in manual review.",
}

LEGACY_RECONCILIATION_BANDS = [
    {
        "label": "Micro access / add-on",
        "usd": "$1–$20",
        "kes": "KSh 20–100",
        "meaning": "Low-value product access, top-ups or small assurance checks. Historical product references remain historical when they are not part of the current catalog.",
    },
    {
        "label": "Focused work",
        "usd": "$25–$75",
        "kes": "KSh 200–700",
        "meaning": "Focused review, content assurance, technical work or another narrow managed task when the memo supports that classification.",
    },
    {
        "label": "Professional work",
        "usd": "$85–$250",
        "kes": "KSh 1,500–2,000",
        "meaning": "A professional project, plan, research/production task or milestone. The original memo remains the primary evidence.",
    },
    {
        "label": "Project payment",
        "usd": "$250–$500+",
        "kes": "Custom",
        "meaning": "A deposit, milestone or larger one-off engagement when linked scope supports it. Amount alone never assigns the service.",
    },
]
