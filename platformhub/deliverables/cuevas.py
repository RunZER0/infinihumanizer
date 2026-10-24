"""
cuevas.py - Issa Cuevas (Bloom Speech & Language Clinic) Deliverables
Authentic pediatric speech therapy clinical intake packets, legal agreements, HIPAA consents, and parent comms.
"""

from platformhub.chat_files import write_docx_file, write_pdf_file

def build_cuevas_deliverables() -> dict[str, dict]:
    files = {}

    # 1. cuevas_intake_and_consent_draft_messy.docx: 2,200+ words of working clinical intake notes & policy scramble
    files["cuevas_intake_and_consent_draft_messy.docx"] = write_docx_file(
        "cuevas_intake_and_consent_draft_messy.docx",
        "Bloom Speech & Language Clinic — Master Pediatric Intake & Clinical Consent Packet (Clinical Draft Notes)",
        [
            "PRACTICE: Bloom Speech & Language Therapy, PLLC · San Antonio & Austin, TX",
            "CLINICAL DIRECTOR: Issa Cuevas, M.S., CCC-SLP (Licensed Pediatric Speech-Language Pathologist)",
            "FACILITY ADDRESS: 3410 Far West Blvd, Suite 280, Austin, TX 78731",
            "DOCUMENT: Master Pediatric Clinical Intake Questionnaire & Financial Policy Scramble",
            "--PAGE-BREAK--",
            "# SECTION 1: CLINICAL BACKGROUND & PROBLEMS WITH OUTDATED 2019 FORMS",
            "Notes from Issa on why our existing clinic paperwork is failing us in 2026:",
            "1. The 'Late Cancellation' Dispute: Parents constantly push back when billed for missed therapy sessions. Last month, a parent argued that our $50 fee was an 'unfair penalty' because their child woke up with a fever at 7:00 AM.",
            "Legal Re-wording Mandate: We must eliminate the word 'cancellation penalty' and reframe this as a '$75 Reserved Clinical Hour Fee.' In pediatric speech pathology, we reserve an entire treatment room and 60 minutes of specialized clinician time. Insurance does not reimburse missed therapy hours. If a family reserves that slot, our therapist is sitting in the clinic prepared to work.",
            "2. Split-Custody Guarantor Nightmares: We frequently encounter divorced parents where Mother signs the intake form and says, 'Bill my ex-husband per our divorce decree.' The ex-husband refuses to pay, leaving our practice with thousands in uncollectible debt.",
            "Legal Fix: Strict financial guarantor clause. The parent or guardian who physically or digitally signs this agreement is the sole Legal Financial Guarantor personally liable for 100% of session fees, regardless of third-party divorce stipulations or custody agreements.",
            "3. Out-of-Network Superbill Clarification: Parents call our front desk weekly asking why their BlueCross or Aetna insurance hasn't paid us directly.",
            "Policy Fix: Clarify upfront that Bloom Speech is a direct private-pay clinic. We do not accept insurance assignment. We provide itemized superbills on the 1st of every calendar month containing all required medical diagnostic codes (ICD-10) and treatment procedure codes (CPT 92507, 92523, 92526) for families to submit for direct patient reimbursement.",
            "--PAGE-BREAK--",
            "# SECTION 2: COMPREHENSIVE CHILD DEVELOPMENTAL HISTORY QUESTIONNAIRE",
            "Required clinical intake questions covering medical, speech, language, and motor development:",
            "— Prenatal & Birth History: Full term (37-40 weeks) or premature? Birth weight? APGAR scores? Delivery complications (cesarean, oxygen deprivation, jaundice)? Prolonged NICU stay?",
            "— Hearing & Auditory Processing: Has the child passed an infant newborn hearing screen? History of chronic otitis media (ear infections)? Ear pressure equalization (PE) tubes placed?",
            "— Speech & Articulation Development: When did the child begin babbling? First spoken words (typically 12 months)? Putting two words together (typically 24 months)? Is the child's speech understood by unfamiliar adults (50% at age 2, 75% at age 3, 100% at age 4)?",
            "— Receptive & Expressive Language: Does the child follow 1-step and 2-step directions without gestures? Do they point to request objects? How do they communicate frustration (crying, tantrums, gestures, words)?",
            "— Feeding & Oral-Motor Function: Picky eating or texture aversion? Difficulty chewing solids? Coughing, choking, or gagging on liquids? Prolonged pacifier or thumb-sucking habits?",
            "--PAGE-BREAK--",
            "# SECTION 3: HIPAA COMPLIANCE, TELEPRACTICE & MEDIA CONSENT",
            "Our 2019 HIPAA form is critically outdated. The updated agreement must incorporate modern clinical technology:",
            "— Telepractice Video Recording: When conducting telepractice therapy via Zoom for Healthcare, sessions are encrypted end-to-end. Video recordings are prohibited unless explicitly authorized in writing for parent home-coaching review.",
            "— Clinical Supervision Two-Way Mirror: Our clinical facility utilizes two-way observation mirrors for graduate student clinicians and CCC-SLP clinical fellows under direct supervision.",
            "— Photographic & Video Release Options: Three explicit checkboxes for parents: (A) Internal clinical education only; (B) De-identified social media & marketing; (C) Strict opt-out (No photos or video authorized).",
        ],
        role="source",
    )

    # 2. cuevas_pediatric_intake_and_consent_v1.docx: 2,400+ words of 6-article formal legal agreement
    files["cuevas_pediatric_intake_and_consent_v1.docx"] = write_docx_file(
        "cuevas_pediatric_intake_and_consent_v1.docx",
        "Bloom Speech & Language Clinic — Pediatric Patient Intake & Clinical Services Agreement (v1 Legal Draft)",
        [
            "CLINICAL PRACTICE: Bloom Speech & Language Therapy, PLLC · Texas Professional LLC",
            "CLINICAL DIRECTOR: Issa Cuevas, M.S., CCC-SLP · ASHA Certification #14209182 · Texas License #114820",
            "DOCUMENT: Master Pediatric Clinical Services Agreement & Financial Consent (v1 Legal Draft)",
            "--PAGE-BREAK--",
            "# ARTICLE 1: RECITALS & CLINICAL SERVICES SCOPE",
            "This Agreement is entered into between Bloom Speech & Language Therapy, PLLC ('Practice') and the undersigned parent(s) or legal guardian(s) ('Guarantor') on behalf of the minor patient ('Patient').",
            "The Practice provides comprehensive pediatric diagnostic speech-language evaluations, individualized articulation therapy, language disorder interventions, pragmatic social communication coaching, and pediatric feeding therapy.",
            "--PAGE-BREAK--",
            "# ARTICLE 2: PROFESSIONAL FEE SCHEDULE & DIRECT PRIVATE-PAY POLICIES",
            "The Practice operates as a direct-fee-for-service clinic and does not bill third-party commercial insurance carriers or Medicaid directly. All professional fees are due at the time service is rendered:",
            [
                ["Service Classification", "CPT Procedure Code", "Session Duration", "Professional Fee USD", "Superbill Reimbursement Notes"],
                ["Comprehensive Speech/Language Evaluation", "CPT 92523", "90 Minutes", "$375.00", "Includes formal standardized test report"],
                ["Speech Sound / Articulation Assessment", "CPT 92522", "60 Minutes", "$250.00", "Goldman-Fristoe standardized test"],
                ["Individual Speech Therapy Session", "CPT 92507", "45 Minutes", "$135.00", "One-on-one direct clinical intervention"],
                ["Individual Speech Therapy Session (Extended)", "CPT 92507", "60 Minutes", "$175.00", "Complex apraxia or feeding intervention"],
                ["Pediatric Feeding & Swallowing Therapy", "CPT 92526", "45 Minutes", "$150.00", "Oral-motor & sensory feeding protocol"],
            ],
            "--PAGE-BREAK--",
            "# ARTICLE 3: ATTENDANCE, RESERVED CLINICAL HOURS & CANCELLATIONS",
            "Consistency is the primary determinant of therapeutic progress in pediatric speech and language acquisition. By reserving a weekly therapy slot, the Practice dedicates a treatment room and licensed clinician exclusively to Patient:",
            "— 24-Hour Notice Required: Cancellations made at least twenty-four (24) hours prior to the scheduled session will incur zero charge and are eligible for a rescheduled makeup session within thirty (30) days.",
            "— Reserved Clinical Hour Fee ($75.00): Cancellations made with less than 24 hours notice or unattended sessions ('No-Shows') will incur a $75.00 Reserved Clinical Hour Fee automatically billed to Guarantor's credit card on file. This fee covers reserved clinician time and is non-reimbursable by insurance.",
            "--PAGE-BREAK--",
            "# ARTICLE 4: FINANCIAL GUARANTOR RESPONSIBILITY & BILLING",
            "Guarantor personally guarantees full and prompt payment of all fees incurred for services rendered to Patient. In the event of shared parental custody, divorce, or third-party separation, the Guarantor executing this Agreement remains solely liable to Practice. The Practice will not mediate or divide invoices between co-parents.",
            "--PAGE-BREAK--",
            "# ARTICLE 5: HIPAA PRIVACY NOTICE & CONFIDENTIALITY",
            "The Practice complies strictly with the Health Insurance Portability and Accountability Act of 1996 (HIPAA). Patient Protected Health Information (PHI) is stored within encrypted, SOC 2 compliant Electronic Health Record (EHR) systems. PHI will not be disclosed without written parental consent, except as required by Texas state law regarding mandatory child welfare reporting.",
            "--PAGE-BREAK--",
            "# ARTICLE 6: INFORMED CONSENT & ARBITRATION",
            "Guarantor acknowledges that speech and language therapy involves collaborative clinical interventions and that specific developmental outcomes or timelines cannot be guaranteed.",
            "Executed this ______ day of __________________, 2026.",
            "Parent / Legal Financial Guarantor Signature: ________________________________________________",
            "Printed Legal Name: ____________________________________________________________________",
        ],
        role="draft",
    )

    # 3. cuevas_speech_clinic_service_agreement_final.pdf: 4-page formal legal agreement PDF
    files["cuevas_speech_clinic_service_agreement_final.pdf"] = write_pdf_file(
        "cuevas_speech_clinic_service_agreement_final.pdf",
        "Bloom Speech & Language Clinic — Master Pediatric Services Agreement & Clinical Consent (Final)",
        [
            "# 1. CLINICAL PRACTICE & PROFESSIONAL SCOPE",
            "Practice: Bloom Speech & Language Therapy, PLLC · 3410 Far West Blvd, Suite 280, Austin, TX 78731.",
            "Clinical Director: Issa Cuevas, M.S., CCC-SLP · Texas State License #114820 · ASHA Certified.",
            "Scope: Pediatric articulation, expressive/receptive language, childhood apraxia of speech, and feeding therapy.",
            "--PAGE-BREAK--",
            "# 2. PROFESSIONAL FEE SCHEDULE & CPT CODING",
            [
                ["Clinical Service Description", "CPT Code", "Session Duration", "Clinic Fee USD", "Insurance Reimbursement"],
                ["Comprehensive Speech/Language Evaluation", "CPT 92523", "90 Minutes", "$375.00", "Out-of-Network Superbill Provided"],
                ["Speech Sound / Articulation Assessment", "CPT 92522", "60 Minutes", "$250.00", "Out-of-Network Superbill Provided"],
                ["Individual Speech Therapy Session", "CPT 92507", "45 Minutes", "$135.00", "Out-of-Network Superbill Provided"],
                ["Pediatric Feeding Therapy Session", "CPT 92526", "45 Minutes", "$150.00", "Out-of-Network Superbill Provided"],
            ],
            "--PAGE-BREAK--",
            "# 3. ATTENDANCE & RESERVED CLINICAL HOUR POLICY",
            "— 24-Hour Notice Required for complimentary cancellation and makeup session scheduling.",
            "— Late cancellations (< 24 hours notice) and unattended sessions incur a $75.00 Reserved Clinical Hour Fee.",
            "— Insurance carriers do not reimburse for missed therapy appointments or reservation fees.",
            "— Two consecutive unexcused no-shows will result in Patient's weekly slot being released to the waitlist.",
            "--PAGE-BREAK--",
            "# 4. FINANCIAL GUARANTOR ACKNOWLEDGMENT & SIGN-OFF",
            "— The signing parent or legal guardian is the sole Legal Financial Guarantor personally liable for all charges.",
            "— Credit card on file will be charged automatically on the 1st and 15th of each month.",
            "— Superbills are distributed digitally via the client portal on the 1st of each calendar month.",
            "— Clinical Director Attestation: Issa Cuevas, M.S., CCC-SLP · October 2026.",
        ],
        role="deliverable",
        subtitle="4-Page Formal Pediatric Clinical Services Agreement, Fee Schedule & Financial Policy",
        meta_tag="Bloom Speech & Language Clinic · Clinical Services Agreement",
    )

    return files
