# InfiniAI & PlatformHub: Master System Handover & Operational Context

> **CRITICAL DIRECTIVE**: Moving forward, the AI Assistant's role on this project is **STRICTLY AUDIT**. 
> Do not generate repetitive deliverable pipelines, boilerplate file attachments, or force interactions into a generic delivery loop. Your responsibility is rigorous verification, regression auditing, architectural sanity, security validation, and ensuring authentic human execution.

---

## 1. Executive Summary & Core Thesis

InfiniAI is not a "file attachment machine" or an automated deliverable script. It is an end-to-end **professional language intelligence, research, communication design, and operational platform**.

### The Fundamental Rule
> **"The service exists first; the payment records the commercial event attached to it."**

The platform exists to solve high-stakes human and business problems:
- **Language Intelligence & Humanization**: High-speed, natural text rewriting that removes AI cadence and optimizes burstiness and perplexity.
- **Content Assurance**: Verifying originality, tone, and factual claims.
- **Operational Studio & Agency**: Hands-on technical writing, B2B positioning, financial modeling, RFP bidding, and systems discovery.
- **Client Workspace & Operations Desk**: Real-time communication, invoice generation, payment processing (Paystack & Apple Pay), and document delivery.
- **Live Hosted Showcases**: Bespoke web prototypes built directly into the platform to demo real-world client applications.

---

## 2. Root Cause Analysis: The "Deliverable Fixation"

During recent development cycles, the assistant fell into an echo-chamber trap:
1. **The Deliverable Tunnel Vision**: When asked to ensure client files were substantial and not empty stubs, the assistant incorrectly flattened the entire system into a single repetitive pattern: *Issue brief → generate file → issue invoice → mark paid → deliver file*.
2. **Loss of Human Nuance**: Every conversation began to sound like an automated robotic script where clients instantly agreed in one line and immediately received an invoice and payment link before agreeing on scope.
3. **The Correction**: Real agency engagements involve discovery, hesitation, skepticism, scope adjustments, budget checks, payment hiccups (e.g., bank fraud filters), and human personalities. Deliverables are merely incidental artifacts of strategic advisory and engineering—never the sole focus.

---

## 3. Technology Stack & Architectural Map

```
                     ┌─────────────────────────────────────────┐
                     │          Browser / Public Web           │
                     └────────────────────┬────────────────────┘
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
     ┌────────────────────────┐                     ┌────────────────────────┐
     │  PlatformHub (Studio)  │                     │   Humanizer Engine     │
     │  - Operations Desk     │                     │   - Concurrent Runtime │
     │  - Client Chat & Feeds │                     │   - Sentence Batching  │
     │  - Invoicing & QR Code │                     │   - OpenRouter API     │
     │  - Paystack/Apple Pay  │                     │   - Word Gating        │
     │  - Hosted Showcases    │                     └────────────────────────┘
     └────────────┬───────────┘
                  │
                  ▼
     ┌────────────────────────────────────────────────────────┐
     │      PostgreSQL / SQLite Database Layer                │
     │      - ClientConversation / ClientMessage              │
     │      - ServiceRequest / Deliverable                    │
     │      - Invoice / PaymentRecord                         │
     │      - Custom User / Profile                           │
     └────────────────────────────────────────────────────────┘
```

### Application Breakdown

1. **`core/`**:
   - `core.settings`: Configuration supporting local development and Render production (`byinfini.online`).
   - Handles `ALLOWED_HOSTS`, database configuration via `DATABASE_URL`, and Allauth OAuth.
2. **`humanizer/`**:
   - The high-speed text humanization engine.
   - Routes through `POST /humanizer/humanize/` -> `humanizer.service.rewrite_text`.
   - Uses sentence-local concurrent processing with OpenRouter (`mistralai/ministral-3b-2512`).
   - Zero client-side engine pickers or gimmicks; pure, high-throughput text rewriting.
3. **`platformhub/`**:
   - **Operations Desk** (`/operations/desk/`): The internal cockpit used by team members to manage incoming conversations, inspect payment logs, and dispatch deliverables.
   - **Client Workspace** (`/workspace/`, `/workspace/chat/`): Dedicated client-facing portal with real-time chat, upload capabilities, and invoice status.
   - **Financial Engine** (`/quickpay/`, `/billing/checkout/`, `/billing/webhook/`): Paystack gateway integration, automated transaction reconciliation, and Apple Pay merchant domain association.
   - **Invoice Verification** (`/invoices/<id>/pdf/`, `/invoices/verify/<id>/`): Dynamic ReportLab invoice generation with cryptographic QR codes linking to public verification endpoints.
   - **Hosted Showcases** (`/showcase/...`): Live, fully styled, interactive website deliverables hosted directly on the platform.
4. **`accounts/`**:
   - Manages user profiles, plan subscriptions, and authentication.

---

## 4. The 4 Live Hosted Web Showcases

The platform hosts 4 distinct website deliverables representing live client projects. **They do NOT follow the same pattern, palette, typography, or layout.**

```
+----------------------------------------------------------------------------------------------------+
| 1. STUDIO BROWN (Audrey Brown)                                                                     |
| URL: /showcase/studio-brown/  |  Direct: /studio-brown/                                            |
| Palette: Warm Charcoal (#100F0D), Champagne Gold (#C89D66), Bone (#F7F4EC)                         |
| Typography: Cormorant Garamond (Serif) + DM Sans                                                   |
| Theme: Austin natural light editorial portraiture & commercial brand campaigns                     |
| Interactive Components:                                                                            |
|   - Portfolio category filtering tabs (Editorial, Portrait, Studio, Lookbook)                      |
|   - 5-field interactive booking intake drawer                                                      |
|   - Transparent tier cards ($450 Essential, $950 Studio, $2,200 Campaign)                          |
+----------------------------------------------------------------------------------------------------+
| 2. DOCKSTREAM (Jack Johnson)                                                                       |
| URL: /showcase/dockstream/  |  Direct: /dockstream/                                                |
| Palette: Cyber Navy (#07090E), Electric Cyan (#00E5FF), Freight Orange (#FF5722)                   |
| Typography: Space Grotesk + JetBrains Mono                                                         |
| Theme: Chicago enterprise B2B yard logistics & cross-dock terminal management                      |
| Interactive Components:                                                                            |
|   - 12-bay live cross-dock terminal inspector with dynamic status toggles                          |
|   - Interactive trailer detention ROI savings calculator                                           |
|   - Enterprise ERP/TMS integration matrix (SAP, Oracle, Blue Yonder, Manhattan)                   |
+----------------------------------------------------------------------------------------------------+
| 3. OROZCO COMMERCIAL ROOFING (Azael Orozco)                                                        |
| URL: /showcase/orozco-roofing/  |  Direct: /orozco-roofing/                                        |
| Palette: Rugged Graphite (#121417), Safety Amber (#F59E0B), Cold Steel (#94A3B8)                  |
| Typography: Barlow Semi Condensed + Inter                                                          |
| Theme: South Texas commercial flat roofing systems & industrial storm restoration                  |
| Interactive Components:                                                                            |
|   - Commercial Square-Foot Bid Estimator (60-mil TPO, Standing Seam Metal, Modified Bitumen)       |
|   - 20-Year NDL (No Dollar Limit) manufacturer warranty selector                                   |
|   - 24/7 McAllen & Brownsville emergency dispatch banner                                           |
+----------------------------------------------------------------------------------------------------+
| 4. APEXDESK HARDWARE (Carter Lemburg)                                                              |
| URL: /showcase/apexdesk/  |  Direct: /apexdesk/                                                    |
| Palette: Stealth Obsidian (#0B0C0E), Bead-Blasted Silver (#E2E8F0), Safety Orange (#FF5400)        |
| Typography: Syne + Plus Jakarta Sans                                                               |
| Theme: Boulder CNC-machined aerospace 6063 aluminum modular desk hardware                          |
| Interactive Components:                                                                            |
|   - 3D unibody colorway toggle (Space Black Anodized, Raw Silver, Matte Desert Tan)                |
|   - Magnetic Qi2 modular rail builder with live running subtotal calculation                       |
|   - 1-tap Apple Pay pre-order modal with simulated tactile feedback                                |
+----------------------------------------------------------------------------------------------------+
```

---

## 5. The 18 Client Profiles & Conversational Narratives

The database is pre-seeded with 18 realistic client accounts across diverse industries. Each client has a distinct personality, communication cadence, payment method, and operational challenge:

1. **Audrey Brown** (`audreymbrown2007@gmail.com`):
   - *Industry*: Austin editorial photography.
   - *Narrative*: Stressed about site drop-offs; agency diagnoses her 14-question intake form and lack of upfront pricing; clears $90 diagnostic via Apple Pay; later returns for 3-page copy ($270); experiences Texas debit card fraud filter before clearing on Paystack.
2. **Jose Cruz** (`cruzjose6221@gmail.com`):
   - *Industry*: DFW independent trucking (Cruz Metro Freight).
   - *Narrative*: Texts from the cab of his Peterbilt; Chase mobile fraud alert resolved with a $1 test deposit; clears $24 balance on Apple Pay; requests 3,500-lb tuck-under liftgate specs for local shippers.
3. **Azael Orozco** (`orozcoazael815@gmail.com`):
   - *Industry*: Rio Grande Valley commercial roofing contractor.
   - *Narrative*: Up on a hot roof in McAllen; adjusts quote down to $334.95 (QP2609-1BD487BA) to remove residential work; reviews 60-mil TPO specs over tacos in Pharr; opens takeoff formulas on truck laptop.
4. **Jack Johnson** (`jackjohnson0533@gmail.com`):
   - *Industry*: Chicago B2B logistics director (DockStream).
   - *Narrative*: Multi-month progression: April HubSpot routing spec ($160) turned around for a Monday executive review; returns in September for a 5-page site overhaul and 12-slide enterprise deck ($500); swaps slide 4 metrics for actual Q3 Midwest pilot numbers.
5. **Luca Caro** (`lucacaro@hawaii.edu`):
   - *Industry*: Waikiki catamaran charters & Ala Moana rentals.
   - *Narrative*: Stressed about Q3 accountant audit; ensures Hawaii GET (4.712%) and TAT (10.25%) taxes are segregated; pays $220 via Apple Pay while untying bow lines before taking a charter past Diamond Head.
6. **Keegan Chin** (`kchin444@gmail.com`):
   - *Industry*: Los Angeles specialty coffee equipment importer.
   - *Narrative*: Hit by Section 301 tariffs on stainless pour-over kettles; verifies separate HTS tariff lookups per SKU; locks Excel formula cells to prevent warehouse staff overwrites.
7. **Liza / Vicky Izad** (`vickyizad@gmail.com`):
   - *Industry*: Tampa commercial medical cleaning contractor.
   - *Narrative*: Bidding on a 4-building medical plaza; ensures outpatient surgical suite terminal disinfection protocols are highlighted in the proposal.
8. **Drako Santa Ana** (`drako.santaana.glz@gmail.com`):
   - *Industry*: El Paso warehouse shift supervisor.
   - *Narrative*: 540 shifts zero-incident record; hates corporate buzzwords; ensures his bilingual English/Spanish crew management is highlighted on his resume.
9. **Estella Williams** (`estellawilliams06@gmail.com`):
   - *Industry*: Tech consultancy managing partner.
   - *Narrative*: High-velocity executive; Q4 board presentation, executive briefing memo, and 4-role onboarding SOPs across multi-milestone payments.
10. **Alexa / Uzbek Quintero** (`uzbekquintero@gmail.com`):
    - *Industry*: First-time B2B trade logistics founder.
    - *Narrative*: Imposter syndrome before 10-slide angel demo day; coaches on CAC payback and gross margins.
11. **Cami Kurtz** (`cami.kurtz@icloud.com`):
    - *Industry*: Corporate leadership coach.
    - *Narrative*: Types notes on Amtrak train between Philly and NYC; synthesizes raw discovery interviews into an executive action sheet.
12. **Kaylee Cabreros** (`kayleecabreros@gmail.com`):
    - *Industry*: Botanical skincare founder.
    - *Narrative*: Replaces dry clinical dermatological jargon with sensory verbs (blue tansy, squalane absorption, nighttime rituals).
13. **Dennis Kiragu** (`dkiragu97@gmail.com`):
    - *Industry*: East Africa fleet manager (Mombasa-Nairobi corridor).
    - *Narrative*: Multi-currency reconciliation of KES fuel receipts and USD weighbridge tolls.
14. **Lina Rickert** (`linarickert2514@gmail.com`):
    - *Industry*: Independent apparel designer.
    - *Narrative*: Overcomes email drop-offs by unburying product benefits and rewriting passive CTA buttons.
15. **Patrick Hyland** (`patrickhyland04@gmail.com`):
    - *Industry*: Newfoundland maritime freight dispatcher.
    - *Narrative*: Severe Port aux Basques ferry delays and volatile diesel surcharges modeled in dynamic spreadsheets.
16. **Issa Cuevas / Beltran** (`issabelc207@gmail.com`):
    - *Industry*: Pediatric therapy clinic director.
    - *Narrative*: Methodical compliance review; parent consent and speech service disclosure packets.
17. **Carter Lemburg** (`lemburgcarter@gmail.com`):
    - *Industry*: Boulder hardware founder (ApexDesk).
    - *Narrative*: Shifts from machine-shop invoice speak to tactile zero-cable luxury; verifies mobile Kickstarter layout; adds Lifetime Unibody Guarantee.
18. **Victor / Valdace AI** (`valdaceai@gmail.com`):
    - *Industry*: AI systems engineer.
    - *Narrative*: Production tone calibration blueprint and anti-cliché heuristic parameters.

---

## 6. Technical Guidelines & Gotchas

1. **File Sizes & Deliverable Authenticity**:
   - All files in `public/chat_files/` must remain $\ge 10,240$ bytes (10 KB) and contain rich, multi-page data.
   - Do NOT use synthetic padding or artificial filler strings. Use real tables, schemas, and templates.
2. **Windows File Locking (`WinError 32`)**:
   - In Django unit tests on Windows, `FileResponse` locks the file handle until the response is explicitly closed.
   - When writing tests that inspect downloadable files, always call `response.close()` before file cleanup.
3. **Data Masking & Security**:
   - Client PII is masked in public views (`mask_name`, `mask_email`) to prevent data leakage.
   - Paystack webhooks verify HMAC-SHA512 signatures using `PAYSTACK_SECRET_KEY`.
4. **Offline Resilience**:
   - If `OFFLINE_MODE=True`, network calls to Paystack, OpenRouter, and Brevo fail gracefully without crashing.

---

## 7. The Mandatory Operating Loop for Audit

Moving forward, your mandate is **STRICTLY AUDIT**:

```
+-------------------------------------------------------------------------+
|                        MANDATORY AUDIT LOOP                             |
|                                                                         |
|  1. INSPECT      -> Read the code, state, and test assertions.          |
|  2. RUN AUDIT    -> Execute scripts/audit_platform.py & test suites.    |
|  3. OBSERVE      -> Review the actual stdout, exit codes, and logs.     |
|  4. DIAGNOSE     -> Pinpoint discrepancies against the core thesis.     |
|  5. VERIFY       -> Confirm with fresh, direct, reproducible evidence.  |
|  6. CONCLUDE     -> Report facts, not assumptions or repetitive files.  |
+-------------------------------------------------------------------------+
```

To run a complete audit at any time:
```powershell
python scripts/audit_platform.py
python manage.py test platformhub.tests
```
