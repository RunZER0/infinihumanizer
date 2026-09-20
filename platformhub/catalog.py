from decimal import Decimal

SERVICE_FAMILIES = {
    "text-intelligence": {
        "name": "Text Intelligence",
        "kicker": "Use a tool",
        "headline": "Work directly on the words.",
        "description": "Self-service text transformation for people who already have material and need it clearer, more natural, more controlled, or better matched to an audience.",
        "services": [
            {"code": "text-humanize", "name": "Humanize & refine", "summary": "Improve cadence, voice, clarity and naturalness without changing the underlying meaning.", "from_usd": 12, "billing": "subscription"},
            {"code": "text-rewrite", "name": "Rewrite & adapt", "summary": "Change tone, audience, density, structure or level of formality.", "from_usd": 15, "billing": "usage"},
            {"code": "text-compare", "name": "Version comparison", "summary": "Compare drafts, identify material changes and isolate what still needs work.", "from_usd": 15, "billing": "usage"},
        ],
    },
    "assurance": {
        "name": "Content Assurance",
        "kicker": "Check the work",
        "headline": "Know what needs attention before it leaves your hands.",
        "description": "Originality, source, structure, consistency and quality review for finished or nearly finished work.",
        "services": [
            {"code": "assurance-originality", "name": "Originality check", "summary": "A lightweight originality scan with a concise result summary.", "from_usd": 2, "billing": "per document"},
            {"code": "assurance-report", "name": "Originality report", "summary": "A documented review with source-overlap notes, readability observations and recommended fixes.", "from_usd": 15, "billing": "per document"},
            {"code": "assurance-editorial", "name": "Editorial QA", "summary": "Structure, citations, internal consistency, formatting, tone and release-readiness review.", "from_usd": 35, "billing": "project"},
        ],
    },
    "studio": {
        "name": "Research & Production",
        "kicker": "Hand us the work",
        "headline": "Start with a question. Leave with something usable.",
        "description": "A managed production track for research, review, analysis, synthesis, writing, decks, reports, technical documents and other knowledge work.",
        "services": [
            {"code": "studio-review", "name": "Review & synthesis", "summary": "We read the material, find what matters, reconcile it and return a usable view.", "from_usd": 35, "billing": "project"},
            {"code": "studio-research", "name": "Research brief", "summary": "Desk, market, competitor, product, technical or evidence research built around a specific decision.", "from_usd": 75, "billing": "project"},
            {"code": "studio-deck", "name": "Deck & presentation", "summary": "Research, storyline, slide architecture, writing and production for decision-ready decks.", "from_usd": 150, "billing": "project"},
            {"code": "studio-report", "name": "Report / white paper", "summary": "Research-backed long-form work with source synthesis, structure, editing, formatting and QA.", "from_usd": 250, "billing": "project"},
            {"code": "studio-technical", "name": "Technical production", "summary": "Documentation, quantitative work, spreadsheets, specifications and structured technical deliverables.", "from_usd": 75, "billing": "project"},
        ],
    },
    "communication": {
        "name": "Communication & Experience",
        "kicker": "Make the product communicate",
        "headline": "The words should do a job in the interface.",
        "description": "Website and product communication shaped around what the user needs to understand, trust and do next.",
        "services": [
            {"code": "communication-audit", "name": "Communication audit", "summary": "A page-by-page review of positioning, information order, conversion friction and language.", "from_usd": 150, "billing": "project"},
            {"code": "communication-copy", "name": "Website / product copy", "summary": "Research, positioning, architecture and final copy for landing pages, websites and product flows.", "from_usd": 350, "billing": "project"},
            {"code": "communication-system", "name": "Content system", "summary": "Voice, UX writing rules, reusable patterns and cross-product communication standards.", "from_usd": 1500, "billing": "project"},
        ],
    },
    "systems": {
        "name": "AI & Data Systems",
        "kicker": "Build the capability",
        "headline": "When the work needs its own intelligence layer.",
        "description": "Dataset engineering, model evaluation, fine-tuning, NLP systems, deployment, hosting and ongoing improvement.",
        "services": [
            {"code": "systems-discovery", "name": "AI systems discovery", "summary": "Problem framing, data audit, architecture options, risk review and implementation plan.", "from_usd": 500, "billing": "project"},
            {"code": "systems-dataset", "name": "Dataset creation", "summary": "Collection, cleaning, annotation, synthetic generation and evaluation-set design.", "from_usd": 1000, "billing": "project"},
            {"code": "systems-finetune", "name": "Fine-tuning & evaluation", "summary": "Model selection, supervised fine-tuning, evals, iteration and release criteria.", "from_usd": 2500, "billing": "project"},
            {"code": "systems-hosting", "name": "Hosted model operations", "summary": "Deployment, inference hosting, monitoring, versioning and maintenance.", "from_usd": 500, "billing": "monthly"},
            {"code": "systems-embedded", "name": "Embedded intelligence partner", "summary": "A retained research, production, communication and AI systems team for organizations with continuous demand.", "from_usd": 10000, "billing": "monthly"},
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
    },
    "humanizer-pro": {
        "name": "Text Intelligence — Pro",
        "description": "Higher-volume text work and priority processing.",
        "usd": Decimal("25.00"),
        "kes": Decimal("3200.00"),
        "cadence": "monthly",
        "service_code": "text-humanize",
    },
    "humanizer-team": {
        "name": "Text Intelligence — Team",
        "description": "Shared access for small teams handling recurring content.",
        "usd": Decimal("50.00"),
        "kes": Decimal("6400.00"),
        "cadence": "monthly",
        "service_code": "text-humanize",
    },
    "originality-quick": {
        "name": "Originality Quick Check",
        "description": "Fast originality screening and result summary.",
        "usd": Decimal("2.00"),
        "kes": Decimal("200.00"),
        "cadence": "one-time",
        "service_code": "assurance-originality",
    },
    "consultation": {
        "name": "Scoping Consultation",
        "description": "A focused scoping session. The fee can be credited to a project commissioned within seven days.",
        "usd": Decimal("50.00"),
        "kes": Decimal("6500.00"),
        "cadence": "one-time",
        "service_code": "studio-review",
    },
}

PRICE_BANDS = [
    {
        "label": "Quick professional task",
        "range": "$35–$75",
        "examples": "Focused review, spreadsheet work, concise research, document refinement.",
        "logic": "Narrow scope, one deliverable, limited external research.",
    },
    {
        "label": "Scoped research / production",
        "range": "$75–$250",
        "examples": "Research brief, technical deliverable, deck, structured review, multi-source synthesis.",
        "logic": "Research and production are both required, with one main output.",
    },
    {
        "label": "Full deliverable",
        "range": "$250–$750",
        "examples": "Report, white paper, complete presentation, website copy package.",
        "logic": "Deeper research, editorial QA, formatting and revision cycles.",
    },
    {
        "label": "Strategic engagement",
        "range": "$750–$3,000+",
        "examples": "Multi-page communication work, content systems, larger research programs, dataset work.",
        "logic": "Several workstreams, more stakeholders, more review and more production depth.",
    },
    {
        "label": "Embedded partner",
        "range": "$5,000–$10,000+ / month",
        "examples": "Continuous research, production, content assurance, communication design and AI systems support.",
        "logic": "Reserved monthly capacity across several capabilities rather than isolated one-off tasks.",
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
