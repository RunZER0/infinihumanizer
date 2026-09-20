# InfiniAI Platform Operating Map

## Brand thesis

InfiniAI is a language-intelligence and professional knowledge-production company. A customer can use a self-serve text tool, ask for a review, hand over a complete research/production engagement, improve the communication layer of a website or product, or commission a custom AI/data system.

The platform is organized around the customer's intended outcome. Payments attach to engagements; they do not define services.

## Full user journey

1. **Discover** — Home explains the operating model and routes visitors to five capabilities.
2. **Orient** — Services pages explain when each capability is appropriate and what it produces.
3. **Scope** — The intake asks for outcome, deliverable, audience, existing material, research depth, complexity, timing and contact information.
4. **Estimate** — A proportional model produces a provisional band. Research depth, complexity and urgency change the estimate; the user is shown why.
5. **Commercial step** — Under $500 is normally paid in full. $500–$4,999 uses a 50% deposit. $5,000+ uses 30% mobilisation and milestones. Retainers bill monthly.
6. **Payment** — The project can request an invoice or start provider checkout when Paystack is configured. No project is marked paid until provider verification succeeds.
7. **Workspace** — The customer can see scope, current status, payment state and the delivery timeline.
8. **Production** — Persistent production states are Request → Scope → Quote → Production → Review → Delivery.
9. **Review / assurance** — Originality, source overlap, citation consistency, readability and final QA are part of the project rather than a disconnected add-on.
10. **Delivery / continuation** — A project may close after delivery, continue through revisions, or move into a monthly studio/AI retainer.

Until Stashi is connected, project records are intentionally session-backed. The external database connection can later replace session persistence without changing the public journey.

## Service taxonomy

- **Text Intelligence** — humanize, rewrite, tone, clarity, structure and repeatable text operations.
- **Content Assurance** — originality/source overlap, citation, consistency, readability and review reports.
- **Research & Production** — desk/market/technical/review research, source review, synthesis, analysis, writing, decks, reports, proposals, white papers, documentation, formatting, revisions and QA.
- **Communication & Experience** — website/landing-page language, positioning, UX writing, information hierarchy, pricing/onboarding communication and enterprise content systems.
- **AI & Data Systems** — dataset design/annotation, fine-tuning, NLP/document pipelines, evaluation, deployment, hosting and managed improvement.

## Pricing architecture

### Self-serve
Free, $19 Core, $49 Pro and $149 Team. These are product-access relationships.

### Projects
Focused review $75–$250; research brief $350–$900; produced deliverable $750–$2,500; strategic project $2,500–$12,000+.

### Communication
Message audit $250–$500; landing page $750–$1,500; website content system $2,000–$5,000+; product UX content $3,500–$10,000+; enterprise communication system $7,500–$30,000+.

### AI systems
Discovery $500–$1,500; dataset work from $2,000; fine-tuning pilot from $5,000; production AI system $10,000–$50,000+; managed operations $2,500–$10,000+/month.

### Retainers
$3,000 Studio, $6,000 Studio Plus and $10,000 Embedded Studio. The $10,000 plan reserves four concurrent workstreams, up to eight major deliverables monthly, continuous research/review, website/product language support, QA on every deliverable, weekly strategy and priority revisions. It is priced as an embedded operating function, not as a word allowance.

## Legacy transaction harmonization

The uploaded export contains 169 transaction rows: 68 successful, 77 abandoned and 24 failed. Only successful rows should be treated as realized transactions. Successful payments occur in KES and USD, with successful observed ranges of USD $1–$500 and KES KSh 20–KSh 2,000.

Legacy descriptions are not copied into the public service catalog. They are mapped by the kind of work performed:

- access/plan/top-up payments → Text Intelligence access or usage;
- low-value add-ons → Text Intelligence usage or Content Assurance focused work;
- research/paper/source-review work → Research & Production;
- spreadsheet, financial, quantitative or analytical work → Research & Production / analysis;
- website-related work → Communication & Experience;
- coding/technical system work → AI & Data Systems / technical build;
- legacy writing/review descriptions → Research & Production / legacy production-review;
- larger one-off payments → project deposit, milestone or custom project.

Amount bands provide a second reconciliation signal when descriptions are weak: USD $1–$20 or KES KSh 20–700 maps to usage/add-ons; USD $25–$65 or KES KSh 700–2,000 maps to focused work; USD $75–$160 maps to professional review/research; USD $250–$500+ maps to a project deposit or custom engagement.

The internal reconciliation screen is staff-only at /operations/reconciliation/.

## Frontend rationale

The frontend uses an editorial/technical system rather than a generic AI aesthetic. Warm paper surfaces communicate professional work; dark ink carries authority; blue is scarce and reserved for actions. Sharp lines, ledgers and process rails reflect scope, evidence, invoices and production stages. Cards are used only where plans are genuinely comparable. Page order follows the questions a buyer asks: what is this, is it relevant, how does it work, what does it cost, and what happens after I commit.
