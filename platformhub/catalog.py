from decimal import Decimal

SERVICE_FAMILIES = {
    "text-intelligence": {
        "name": "Text Intelligence",
        "kicker": "Use a tool",
        "headline": "Make the writing sound like you.",
        "description": "Rewrite, refine and reshape text without flattening the voice.",
        "services": [
            {"code": "text-humanize", "name": "Humanize & refine", "summary": "Make the writing sound more natural while keeping the meaning.", "from_usd": 12, "billing": "subscription"},
            {"code": "text-rewrite", "name": "Rewrite & adapt", "summary": "Change the tone, structure or level of formality.", "from_usd": 15, "billing": "usage"},
            {"code": "text-compare", "name": "Version comparison", "summary": "See what changed between drafts and what still needs work.", "from_usd": 15, "billing": "usage"},
        ],
    },
    "assurance": {
        "name": "Content Assurance",
        "kicker": "Check the work",
        "headline": "Catch weak, copied or careless writing before it ships.",
        "description": "Check originality, sources, citations, structure and consistency before the work goes out.",
        "services": [
            {"code": "assurance-originality", "name": "Originality check", "summary": "A quick originality check with a short report.", "from_usd": 2, "billing": "per document"},
            {"code": "assurance-report", "name": "Originality report", "summary": "A fuller review of source overlap, readability and issues to fix.", "from_usd": 15, "billing": "per document"},
            {"code": "assurance-editorial", "name": "Editorial QA", "summary": "Review structure, citations, consistency, formatting and tone.", "from_usd": 35, "billing": "project"},
        ],
    },
    "studio": {
        "name": "Research & Production",
        "kicker": "Research and writing",
        "headline": "Research it properly. Write it clearly.",
        "description": "Research, analysis, reports, decks and technical writing with a clear point and a real voice.",
        "services": [
            {"code": "studio-review", "name": "Review & synthesis", "summary": "We read the material, pull out what matters and return a clear synthesis.", "from_usd": 35, "billing": "project"},
            {"code": "studio-research", "name": "Research brief", "summary": "Research built around the question or decision you need answered.", "from_usd": 75, "billing": "project"},
            {"code": "studio-deck", "name": "Deck & presentation", "summary": "Research, structure, writing and production for presentations.", "from_usd": 150, "billing": "project"},
            {"code": "studio-report", "name": "Report / white paper", "summary": "Long-form reports and white papers, including research, writing and editing.", "from_usd": 250, "billing": "project"},
            {"code": "studio-technical", "name": "Technical production", "summary": "Documentation, spreadsheets, specifications and other technical deliverables.", "from_usd": 75, "billing": "project"},
            {"code": "studio-retainer", "name": "Embedded research & production studio", "summary": "Ongoing research, reports, decks, review, documentation and website or product work.", "from_usd": 3000, "billing": "monthly"},
        ],
    },
    "communication": {
        "name": "Communication & Experience",
        "kicker": "Website and product language",
        "headline": "Make every screen say the right thing.",
        "description": "Website copy, product language and UX writing that sound like the product, not a template.",
        "services": [
            {"code": "communication-audit", "name": "Communication audit", "summary": "A page-by-page review of message, structure and friction.", "from_usd": 150, "billing": "project"},
            {"code": "communication-copy", "name": "Website / product copy", "summary": "Research, structure and final copy for websites, landing pages and product flows.", "from_usd": 350, "billing": "project"},
            {"code": "communication-system", "name": "Content system", "summary": "Voice, UX writing rules and reusable content patterns.", "from_usd": 1500, "billing": "project"},
        ],
    },
    "systems": {
        "name": "AI & Data Systems",
        "kicker": "AI and data systems",
        "headline": "Train the system to meet your standards.",
        "description": "Datasets, fine-tuning, evaluation and deployment for teams that care how the output reads.",
        "services": [
            {"code": "systems-discovery", "name": "AI systems discovery", "summary": "We review the problem, data and practical ways to build it.", "from_usd": 500, "billing": "project"},
            {"code": "systems-dataset", "name": "Dataset creation", "summary": "Data collection, cleaning, annotation, synthetic data and evaluation sets.", "from_usd": 1000, "billing": "project"},
            {"code": "systems-finetune", "name": "Fine-tuning & evaluation", "summary": "Model selection, fine-tuning, evaluation and iteration.", "from_usd": 2500, "billing": "project"},
            {"code": "systems-hosting", "name": "Hosted model operations", "summary": "Deployment, hosting, monitoring and maintenance.", "from_usd": 500, "billing": "monthly"},
            {"code": "systems-embedded", "name": "Embedded intelligence partner", "summary": "Ongoing research, content and AI work for teams with regular demand.", "from_usd": 10000, "billing": "monthly"},
        ],
    },
}

SERVICE_INDEX = {
    service["code"]: {**service, "family": family_slug, "family_name": family["name"]}
    for family_slug, family in SERVICE_FAMILIES.items()
    for service in family["services"]
}

PACKAGES = {
    "humanizer-individual": {
        "name": "Text Intelligence — Individual",
        "description": "Ongoing self-service humanization and rewriting.",
        "usd": Decimal("12.00"),
        "kes": Decimal("1500.00"),
        "cadence": "monthly",
        "service_code": "text-humanize",
        "word_credits": 100000,
        "account_type": "STANDARD",
        "max_devices": 1,
    },
    "humanizer-pro": {
        "name": "Text Intelligence — Pro",
        "description": "Higher-volume text work and priority processing.",
        "usd": Decimal("25.00"),
        "kes": Decimal("3200.00"),
        "cadence": "monthly",
        "service_code": "text-humanize",
        "word_credits": 250000,
        "account_type": "PRO",
        "max_devices": 2,
    },
    "humanizer-team": {
        "name": "Text Intelligence — Team",
        "description": "Shared access for small teams handling recurring content.",
        "usd": Decimal("50.00"),
        "kes": Decimal("6400.00"),
        "cadence": "monthly",
        "service_code": "text-humanize",
        "word_credits": 600000,
        "account_type": "ENTERPRISE",
        "max_devices": 5,
    },
    "originality-quick": {
        "name": "Originality Quick Check",
        "description": "Fast originality screening and result summary.",
        "usd": Decimal("2.00"),
        "kes": Decimal("200.00"),
        "cadence": "one-time",
        "service_code": "assurance-originality",
    },
}


RETAINERS = [
    {
        "name": "Studio",
        "usd": Decimal("3000.00"),
        "capacity": "Two active workstreams",
        "summary": "Regular research, writing and review for a small team.",
        "includes": ["Up to 3 major deliverables", "Weekly production review", "Research + writing + QA", "Priority revision queue"],
    },
    {
        "name": "Continuous Studio",
        "usd": Decimal("6000.00"),
        "capacity": "Three active workstreams",
        "summary": "Ongoing research and production across several workstreams.",
        "includes": ["Up to 5 major deliverables", "Research + decks + reports", "Website and product language support", "Assurance on delivered work", "Twice-weekly production review"],
    },
    {
        "name": "Embedded Partner",
        "usd": Decimal("10000.00"),
        "capacity": "Four active workstreams",
        "summary": "An embedded team for organizations with steady research, writing and communication work.",
        "includes": ["Up to 8 major deliverables", "Continuous research and review", "Reports, decks, documentation and product language", "Assurance on every deliverable", "Weekly strategy session", "Priority turnaround and revisions"],
    },
]

PRICE_BANDS = [
    {
        "label": "Quick professional task",
        "range": "$35–$75",
        "examples": "Focused review, spreadsheet work, concise research, document refinement.",
        "logic": "Small scope and limited research.",
    },
    {
        "label": "Scoped research / production",
        "range": "$75–$250",
        "examples": "Research brief, technical deliverable, deck, structured review, multi-source synthesis.",
        "logic": "Research plus one main deliverable.",
    },
    {
        "label": "Full deliverable / project milestone",
        "range": "$250–$750",
        "examples": "Report, white paper, complete presentation, website copy package, or a deposit/milestone on a larger engagement.",
        "logic": "More research, editing, formatting and revisions.",
    },
    {
        "label": "Strategic engagement",
        "range": "$750–$3,000+",
        "examples": "Multi-page communication work, content systems, larger research programs, dataset work.",
        "logic": "More workstreams, people and review.",
    },
    {
        "label": "Embedded partner",
        "range": "$5,000–$10,000+ / month",
        "examples": "Continuous research, production, content assurance, communication design and AI systems support.",
        "logic": "Reserved monthly capacity across several kinds of work.",
    },
]

RESEARCH_MULTIPLIERS = {
    "none": Decimal("1.00"),
    "light": Decimal("1.10"),
    "standard": Decimal("1.25"),
    "deep": Decimal("1.55"),
}
TURNAROUND_MULTIPLIERS = {
    "flexible": Decimal("0.95"),
    "standard": Decimal("1.00"),
    "priority": Decimal("1.35"),
}


def service_by_code(code):
    return SERVICE_INDEX.get(code)


def estimate_request(service_code, research_depth="standard", turnaround="standard"):
    service = SERVICE_INDEX.get(service_code)
    if not service:
        return None, None
    base = Decimal(str(service.get("from_usd", 50)))
    multiplier = RESEARCH_MULTIPLIERS.get(research_depth, Decimal("1.25"))
    multiplier *= TURNAROUND_MULTIPLIERS.get(turnaround, Decimal("1.00"))
    low = (base * multiplier).quantize(Decimal("1"))
    spread = Decimal("1.35") if base < 500 else Decimal("1.50")
    high = (low * spread).quantize(Decimal("1"))
    return low, high


def commercial_terms(total, service_code=""):
    """Return the payment structure for an accepted quote without redefining the service around payment."""
    amount = Decimal(str(total or 0))
    service = SERVICE_INDEX.get(service_code) or {}
    if service.get("billing") == "monthly":
        return {
            "label": "Monthly retainer",
            "percent": Decimal("100"),
            "due_now": amount,
            "description": "Billed at the start of each service month.",
        }
    if amount < Decimal("500"):
        return {
            "label": "Full payment",
            "percent": Decimal("100"),
            "due_now": amount,
            "description": "Paid in full once the scope is accepted.",
        }
    if amount < Decimal("5000"):
        return {
            "label": "50% project deposit",
            "percent": Decimal("50"),
            "due_now": (amount * Decimal("0.50")).quantize(Decimal("0.01")),
            "description": "50% starts the work. The balance is due at the agreed final milestone.",
        }
    return {
        "label": "30% mobilisation",
        "percent": Decimal("30"),
        "due_now": (amount * Decimal("0.30")).quantize(Decimal("0.01")),
        "description": "30% starts the work. The rest is billed against agreed milestones.",
    }
