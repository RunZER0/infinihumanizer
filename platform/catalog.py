SERVICE_FAMILIES = [
    {
        "slug": "text-intelligence",
        "index": "01",
        "name": "Text Intelligence",
        "verb": "Improve what already exists.",
        "summary": "Humanization, rewriting, tone, structure, readability and document-level language work.",
        "best_for": "Individuals and teams who already have text and need it to read, sound or perform better.",
        "starting_price": 19,
        "price_label": "from $19/mo",
        "cta": "Use the tools",
        "features": [
            "Humanize and rewrite existing text",
            "Control tone, clarity and density",
            "Preserve meaning while changing expression",
            "Compare versions and improve readability",
            "Run quality and originality preflights",
        ],
        "outcomes": ["Natural language", "Consistent voice", "Faster revision"],
    },
    {
        "slug": "content-assurance",
        "index": "02",
        "name": "Content Assurance",
        "verb": "Know what will hold up.",
        "summary": "Originality, source overlap, citation, structural and publication-readiness review.",
        "best_for": "Teams that need evidence about the quality, provenance and consistency of a document before it ships.",
        "starting_price": 25,
        "price_label": "from $25",
        "cta": "Check a document",
        "features": [
            "Originality and source-overlap review",
            "Citation and internal consistency checks",
            "Readability and structural assessment",
            "Revision verification and comparison",
            "Downloadable review reports",
        ],
        "outcomes": ["Clear risk picture", "Review trail", "Actionable fixes"],
    },
    {
        "slug": "research-production",
        "index": "03",
        "name": "Research & Production",
        "verb": "Give us the question. Get the finished work.",
        "summary": "Research, review, synthesis, writing and production for any serious professional deliverable.",
        "best_for": "People and companies that need a complete piece of knowledge work, not just a writing tool.",
        "starting_price": 75,
        "price_label": "from $75",
        "cta": "Start a project",
        "features": [
            "Desk, market, technical and review research",
            "Source and evidence review",
            "Synthesis and structured analysis",
            "Reports, decks, proposals and white papers",
            "Technical writing, documentation and formatting",
            "Editorial review, revisions and QA",
        ],
        "outcomes": ["Decision-ready research", "Finished deliverables", "One accountable workflow"],
    },
    {
        "slug": "communication-experience",
        "index": "04",
        "name": "Communication & Experience",
        "verb": "Make the product easier to understand and act on.",
        "summary": "Website copy, UX writing, positioning and communication design tied to a real conversion or product outcome.",
        "best_for": "Companies whose product or service is stronger than the way it is currently explained.",
        "starting_price": 250,
        "price_label": "from $250",
        "cta": "Improve the experience",
        "features": [
            "Website and landing-page messaging",
            "Information hierarchy and page strategy",
            "UX writing and product microcopy",
            "Brand voice and value proposition",
            "Pricing and onboarding communication",
            "Enterprise content systems",
        ],
        "outcomes": ["Sharper positioning", "Clearer journeys", "Higher-conviction actions"],
    },
    {
        "slug": "ai-data-systems",
        "index": "05",
        "name": "AI & Data Systems",
        "verb": "Build the capability into your own system.",
        "summary": "Datasets, fine-tuning, NLP systems, evaluation, deployment and managed model operations.",
        "best_for": "Teams that need a custom language or machine-learning capability rather than an off-the-shelf tool.",
        "starting_price": 500,
        "price_label": "discovery from $500",
        "cta": "Scope a system",
        "features": [
            "Dataset design, creation and annotation",
            "Model selection and fine-tuning",
            "Evaluation sets and benchmarking",
            "NLP and document-processing pipelines",
            "Deployment, hosting and integrations",
            "Ongoing monitoring and improvement",
        ],
        "outcomes": ["Owned capability", "Production deployment", "Managed improvement"],
    },
]

SERVICE_BY_SLUG = {item["slug"]: item for item in SERVICE_FAMILIES}

SELF_SERVE_PLANS = [
    {
        "name": "Free",
        "price": 0,
        "period": "month",
        "description": "For trying the text workspace.",
        "features": ["2,000 words", "Basic rewrite modes", "Readability signals", "Project discovery access"],
    },
    {
        "name": "Core",
        "price": 19,
        "period": "month",
        "description": "For regular individual writing work.",
        "features": ["50,000 words", "Humanization and rewriting", "Tone controls", "Originality preflight"],
    },
    {
        "name": "Pro",
        "price": 49,
        "period": "month",
        "description": "For high-volume professional use.",
        "features": ["200,000 words", "Advanced text controls", "Full reports", "Priority processing"],
        "recommended": True,
    },
    {
        "name": "Team",
        "price": 149,
        "period": "month",
        "description": "For shared language workflows.",
        "features": ["600,000 words", "5 seats", "Shared standards", "Central billing"],
    },
]

STUDIO_OFFERS = [
    {"name": "Focused review", "price": "$75–$250", "use": "A document, source set or existing draft needs a professional review."},
    {"name": "Research brief", "price": "$350–$900", "use": "A question needs investigation, synthesis and a concise decision-ready output."},
    {"name": "Produced deliverable", "price": "$750–$2,500", "use": "A report, deck, proposal, white paper or documentation set needs to be produced end to end."},
    {"name": "Strategic project", "price": "$2,500–$12,000+", "use": "Multiple workstreams, deeper research, stakeholders or a substantial communication system."},
]

RETAINER_PLANS = [
    {
        "name": "Studio",
        "price": 3000,
        "description": "A standing production partner for a small team.",
        "features": ["2 active workstreams", "Research + writing + review", "Up to 3 major deliverables monthly", "Weekly production review", "Priority revisions"],
    },
    {
        "name": "Studio Plus",
        "price": 6000,
        "description": "Continuous research and communication production.",
        "features": ["3 active workstreams", "Up to 5 major deliverables monthly", "Website/product language support", "Quality and originality review", "Twice-weekly production review"],
    },
    {
        "name": "Embedded Studio",
        "price": 10000,
        "description": "An embedded language and research function without building the team internally.",
        "features": ["4 concurrent workstreams", "Up to 8 major deliverables monthly", "Continuous research and review", "Decks, reports, product and website language", "QA on every deliverable", "Weekly strategy session", "Priority turnaround and revisions"],
        "recommended": True,
    },
]

COMMUNICATION_OFFERS = [
    {"name": "Message audit", "price": "$250–$500"},
    {"name": "Landing page", "price": "$750–$1,500"},
    {"name": "Website content system", "price": "$2,000–$5,000+"},
    {"name": "Product UX content", "price": "$3,500–$10,000+"},
    {"name": "Enterprise communication system", "price": "$7,500–$30,000+"},
]

AI_OFFERS = [
    {"name": "Discovery & architecture", "price": "$500–$1,500"},
    {"name": "Dataset project", "price": "$2,000+"},
    {"name": "Fine-tuning pilot", "price": "$5,000+"},
    {"name": "Production AI system", "price": "$10,000–$50,000+"},
    {"name": "Managed AI operations", "price": "$2,500–$10,000+/mo"},
]

PROJECT_BASES = {
    "text-intelligence": 25,
    "content-assurance": 75,
    "research-production": 350,
    "communication-experience": 750,
    "ai-data-systems": 2500,
}

RESEARCH_MULTIPLIERS = {
    "none": 0.75,
    "light": 1.0,
    "standard": 1.35,
    "deep": 1.9,
}

COMPLEXITY_MULTIPLIERS = {
    "focused": 0.75,
    "standard": 1.0,
    "complex": 1.8,
    "enterprise": 3.2,
}

URGENCY_MULTIPLIERS = {
    "flexible": 0.9,
    "standard": 1.0,
    "priority": 1.35,
    "urgent": 1.75,
}

def estimate_project(service_slug, research_depth="standard", complexity="standard", urgency="standard"):
    base = PROJECT_BASES.get(service_slug, 350)
    research = RESEARCH_MULTIPLIERS.get(research_depth, 1.0)
    comp = COMPLEXITY_MULTIPLIERS.get(complexity, 1.0)
    speed = URGENCY_MULTIPLIERS.get(urgency, 1.0)
    estimate = round(base * research * comp * speed / 25) * 25
    low = max(25, round(estimate * 0.8 / 25) * 25)
    high = max(low, round(estimate * 1.25 / 25) * 25)
    return low, high

def payment_structure(estimate_high, engagement_type="project"):
    if engagement_type == "retainer":
        return {"label": "Monthly retainer", "percent": 100, "explanation": "Billed at the start of each service month."}
    if estimate_high < 500:
        return {"label": "Full payment", "percent": 100, "explanation": "Focused engagements are paid in full when scope is approved."}
    if estimate_high < 5000:
        return {"label": "50% deposit", "percent": 50, "explanation": "Half starts the work; the balance is due before final delivery."}
    return {"label": "30% mobilisation", "percent": 30, "explanation": "Larger projects begin with mobilisation, then bill against agreed milestones."}

LEGACY_PAYMENT_BANDS = [
    {"band": "Usage / top-up", "usd": "$1–$20", "kes": "KSh 20–KSh 700", "maps_to": "Text Intelligence usage, credits or small add-ons"},
    {"band": "Focused work", "usd": "$25–$65", "kes": "KSh 700–KSh 2,000", "maps_to": "Content Assurance, focused review or research add-ons"},
    {"band": "Professional review", "usd": "$75–$160", "kes": "custom", "maps_to": "Review, analysis, research brief or production milestone"},
    {"band": "Custom project", "usd": "$250–$500+", "kes": "custom", "maps_to": "Project deposit, milestone or scoped production work"},
]
