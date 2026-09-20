# InfiniAI platform map

## Thesis

InfiniAI is a professional knowledge-production and language-intelligence company. The humanizer is one self-service tool inside a wider system for research, production, content assurance, communication design, and AI/data systems.

The commercial rule is simple: the service exists first; the payment records the commercial event attached to it.

## Customer entry paths

### 1. Improve existing text

Route: Home -> Text Intelligence -> Humanizer -> checkout when an entitlement is required -> output.

The customer already has the substance. The task is voice, cadence, naturalness, clarity, or adaptation.

### 2. Check existing work

Route: Home -> Content Assurance -> quick check or managed report.

Quick check:
Sign in -> paste text -> USD 2 / KSh 200 checkout -> assurance queue -> report reference -> result in workspace.

Managed assurance:
Service page -> project brief -> scope -> quote -> accept -> invoice -> review -> report delivery.

### 3. Have work researched, reviewed, or produced

Route: Home -> Research & Production -> project brief -> directional range -> scope review -> quote -> accept -> invoice -> payment -> production -> QA -> client review -> delivery.

The studio is deliberately not limited to competitor research. Research can be market, technical, product, review, source, evidence, regulatory, vendor, industry, or other desk research. The customer may also enter after research already exists and ask for review, synthesis, writing, formatting, a deck, a report, documentation, a spreadsheet, or another technical deliverable.

### 4. Improve a website or product experience

Route: Home -> Communication & Experience -> audit/copy/content-system request -> scope -> quote -> invoice -> delivery.

The service is communication design: positioning, information architecture, website copy, UX writing, product language, onboarding, conversion language, and content systems.

### 5. Build an AI or data capability

Route: Home -> AI & Data Systems -> discovery -> scoped engagement -> quote -> invoice/milestone -> dataset/model/evaluation/deployment -> hosting or support.

This covers dataset creation, annotation, synthetic data, fine-tuning, NLP systems, evaluation, hosting, and retained AI operations.

### 6. Start with uncertainty

Route: any page -> Scoping consultation -> USD 50 checkout -> consultation -> project request/quote.

The consultation fee may be credited to a project commissioned within seven days.

## Commercial architecture

### Fixed self-service

- Text Intelligence Individual: USD 12 / KSh 1,500 monthly
- Text Intelligence Pro: USD 25 / KSh 3,200 monthly
- Text Intelligence Team: USD 50 / KSh 6,400 monthly
- Originality Quick Check: USD 2 / KSh 200
- Scoping consultation: USD 50 / KSh 6,500

### Managed work

- Quick professional task: USD 35-75
- Scoped research / production: USD 75-250
- Full deliverable: USD 250-750
- Strategic engagement: USD 750-3,000+
- Embedded Studio: USD 3,000 per month
- Continuous Studio: USD 6,000 per month
- Embedded Partner: USD 10,000 per month and above

Directional ranges are shown before scope. Quotes are authoritative after scope.

### AI systems anchors

- Discovery: from USD 500
- Dataset creation: from USD 1,000
- Fine-tuning and evaluation: from USD 2,500
- Hosting/operations: from USD 500 monthly
- Embedded intelligence partner: from USD 10,000 monthly

The USD 10,000 monthly engagement reserves up to four concurrent workstreams and multidisciplinary capacity across research, production, communication, assurance, and scoped AI systems support. It is not a token bundle.

Accepted project quotes create commercial events proportionally: focused work below USD 500 is normally paid in full; USD 500–4,999 starts with a 50% deposit; USD 5,000+ starts with 30% mobilisation and subsequent named milestones; monthly retainers are billed at the start of the service month.

## Payment model

Objects:
Customer -> Service Request -> Quote -> Quote Items -> Invoice -> Payment -> Deliverables.

Fixed self-service products skip quote/invoice only when the unit is already defined.

Every PaymentRecord stores:
- provider reference
- amount and currency
- status
- customer email
- linked request/invoice where applicable
- normalized service family/code
- original description for historical imports
- legacy flag and raw metadata

## Historical ledger normalization

The uploaded ledger contains 169 rows: 68 successful, 77 abandoned and 24 failed. Successful transactions span USD 1–500 and KSh 20–2,000. These historical amounts validate the need for usage payments, focused work, project payments and legacy product access, but they do not determine the current catalog.

Historical records are imported without rewriting the original description. A second normalized classification is added only where the reference or memo supports it. Ambiguous quick-pay transactions stay unclassified for manual review rather than being assigned a service from amount alone.

Examples:
- originality / Turnitin checks -> Content Assurance
- Excel, quantitative, spreadsheet, and structured technical work -> Research & Production / Technical Production
- research, paper, review, synthesis -> Research & Production
- website/copy/communication work -> Communication & Experience
- coding/software/model work -> AI & Data Systems
- generic quick-pay work with no usable memo -> legacy unclassified / manual review
- YNAI subscription and upgrade references -> legacy software product access, retained as historical product revenue rather than falsely relabeled as a new InfiniAI service

## Operational lifecycle

Request states:
new -> scoping -> quoted -> active -> review -> delivered -> closed

Quote states:
draft -> sent -> accepted / declined / expired

Invoice states:
draft -> open -> part paid -> paid / void

Deliverable states:
planned -> in progress -> review -> approved -> delivered

Client review actions:
comment / request revision / approve. A revision request reopens production with the note attached to the deliverable; approval is recorded against the client account.

Assurance states:
awaiting payment -> queued -> reviewing -> ready

## Design rationale

The visual system is editorial and technical because the product is about evidence, language, production, and scrutiny. Warm paper surfaces carry reading and working context; dark ink carries authority; red is scarce and used for action/proof marks. Sharp rules and rectangular geometry reference documents, reports, marked-up copy, and technical specifications rather than generic AI imagery.

The public site separates user jobs into distinct destinations instead of turning the home page into a catalogue. Copy, hierarchy, pricing, and interaction are sequenced around the buyer's actual questions: what this is, whether it fits the need, how the work happens, what it costs, and what happens after submitting.
