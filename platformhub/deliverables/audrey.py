"""
audrey.py - Audrey Brown (Studio Brown Photography) Deliverables
Authentic editorial photography website copy, wireframe notes, conversion audits, and booking architecture.
"""

from platformhub.chat_files import write_docx_file, write_pdf_file, write_screenshot_png_file

def build_audrey_deliverables() -> dict[str, dict]:
    files = {}

    # 1. audrey_wireframe_notes.docx: Studio Brown IA & client onboarding workflow notes
    files["audrey_wireframe_notes.docx"] = write_docx_file(
        "audrey_wireframe_notes.docx",
        "Studio Brown — Website Information Architecture & Client Experience Brief",
        [
            "CLIENT: Audrey Brown, Founder & Creative Director · Studio Brown",
            "LOCATION: 1812 E 6th Street, Unit 204, East Austin, TX 78702",
            "PROJECT: Digital Redesign, Client Onboarding Funnel & Conversion Architecture",
            "DOCUMENT VERSION: Working Architecture Brief & Strategy Notes",
            "--PAGE-BREAK--",
            "# SECTION 1: BRAND ARCHETYPE & CREATIVE POSITIONING",
            "Studio Brown operates at the intersection of high editorial fashion and intimate human portraiture. Our studio is an 1,800 square foot converted warehouse loft featuring 16-foot exposed timber ceilings, authentic whitewashed brick, polished concrete floors, and expansive north-facing factory windows that provide diffuse, shadowless daylight throughout the day.",
            "Brand Aesthetic & Visual Tenets:",
            "— Quiet Luxury: Restrained, sophisticated typography (editorial serif paired with geometric grotesk).",
            "— Organic Texture: Warm limestone, unbleached linen, espresso timber tones, and film grain.",
            "— Unhurried Intimacy: The antithesis of commercial high-volume photography studios. Sessions are structured around conversations, personal music playlists, and unhurried natural movement.",
            "--PAGE-BREAK--",
            "# SECTION 2: WEBSITE INFORMATION ARCHITECTURE & USER JOURNEY",
            "The redesigned website must eliminate client booking friction while preserving an exclusive, high-touch luxury feel:",
            "1. Homepage: Editorial Hero Video/Stills, Selected Commissions Gallery, Studio Aesthetic Philosophy, Client Accreditations (Architectural Digest, Kinfolk, Rangefinder), Direct Booking CTA.",
            "2. The Studio Experience: Visual tour of the East Austin daylight loft, French lime-wash backdrops, private client dressing room, curated wardrobe rack, and hair/makeup vanity stations.",
            "3. Portfolio Categories: Editorial Campaigns, Brand Lookbooks, Founder Profiles, Personal Legacy Portraits.",
            "4. Investment & Commissions: Transparent tier breakdown (The Editorial Lookbook $3,400, The Founder Narrative $2,200, The Personal Legacy Portrait $1,650, Commercial Add-Ons).",
            "5. Interactive Client Intake: Multi-step inquiry questionnaire capturing preferred session dates, shoot concept, styling requirements, and usage rights.",
            "6. Private Client Portal: Secure Pixieset/Pass gallery integration for proofing and high-res download delivery.",
            "--PAGE-BREAK--",
            "# SECTION 3: CLIENT DISCOVERY INTAKE QUESTIONNAIRE SPECIFICATION",
            "The booking intake form must screen for aligned clients and gather creative parameters before the initial consultation call:",
            "— Step 1: Session Intent (Brand Campaign / Executive Founder Profile / Personal Portrait / Apparel Lookbook).",
            "— Step 2: Target Timeline & Ideal Dates (Selection calendar with 3-week lead time minimum).",
            "— Step 3: Creative Mood & Visual Direction (Drop-down aesthetic descriptors: Minimalist Warmth, Moody Monochrome, Editorial High Fashion, Natural Daylight).",
            "— Step 4: Wardrobe & Styling Assistance (In-house wardrobe stylist request: Yes / No / Undecided).",
            "— Step 5: Commercial Licensing Scope (Personal print release / Digital editorial usage / Full commercial advertising buyout).",
            "--PAGE-BREAK--",
            "# SECTION 4: PRODUCTION TIMELINE & DELIVERABLE SLAS",
            [
                ["Milestone / Phase", "Turnaround Timeline", "Client Action Required", "Studio Deliverable"],
                ["Creative Consultation", "Within 48 hours of intake", "20-minute Zoom or studio coffee", "Curated mood board & shoot schedule"],
                ["Session Date", "Confirmed upon retainer", "Arrive 30 mins prior for HMUA", "Full production shoot (2 to 5 hours)"],
                ["Proofing Gallery", "5 business days post-shoot", "Select favorite images in portal", "Private proofing link (80 to 250 proofs)"],
                ["Final Master Retouching", "10 business days post-selection", "Review color grade & skin finish", "High-res print + web TIFF/JPEG files"],
                ["Fine Art Print Delivery", "15 business days post-approval", "Confirm shipping address", "Handmade archival cotton rag print box"],
            ],
            "# SECTION 5: STUDIO POLICIES & RETAINER TERMS",
            "— Retainer: 50% non-refundable deposit required to lock studio calendar date; balance due 7 days prior to shoot.",
            "— Rescheduling: 72-hour advance notice allows 1 complimentary reschedule within 90 days.",
            "— Weather Contingency: On-location natural light shoots rescheduled at zero penalty if heavy rain or severe cloud cover occurs.",
            "— Archival Guarantee: Studio Brown stores RAW digital negatives in dual off-site cloud archives for a minimum of 3 years.",
        ],
        role="source",
    )

    # 2. audrey_3page_website_copy_v1.docx: v1 working draft website copy with client redlines
    files["audrey_3page_website_copy_v1.docx"] = write_docx_file(
        "audrey_3page_website_copy_v1.docx",
        "Studio Brown — 3-Page Website Copy Deck (v1 Working Draft with Client Notes)",
        [
            "CLIENT: Studio Brown · Audrey Brown Photography",
            "PROJECT: 3-Page Website Copy Deck (v1 Draft)",
            "STATUS: Working Draft with Creative Director Redlines & Copy Polish",
            "--PAGE-BREAK--",
            "# PAGE 1: HOMEPAGE MASTER COPY",
            "CATEGORY BADGE: East Austin · Natural Light Warehouse Studio",
            "HERO HEADLINE: Editorial portraiture & brand lookbooks crafted with quiet elegance.",
            "HERO SUBHEAD: Natural light sessions in our East Austin warehouse studio, on-location campaigns across the Texas Hill Country, and curated visual narratives for visionary founders.",
            "PRIMARY CTA: [Reserve Studio Session] · SECONDARY CTA: [View Selected Commissions]",
            "EDITORIAL TRUST BAR: Featured in Kinfolk · Architectural Digest · Rangefinder Portrait Winner · Texas Monthly",
            "CREATIVE MANIFESTO: We believe the most compelling images happen in the quiet moments between poses. Under the soft, shifting daylight of our East Austin loft, we create images that feel like modern art yet belong entirely to you.",
            "--PAGE-BREAK--",
            "# PAGE 2: SERVICES & INVESTMENT TIERS",
            "1. THE EDITORIAL LOOKBOOK ($3,400): Full-day commercial commission (up to 6 hours) for apparel brands, makers, and lifestyle labels. Includes on-site wardrobe stylist, commercial usage rights, and 45 master retouched high-res deliverables.",
            "2. THE FOUNDER NARRATIVE ($2,200): Half-day studio session (3 hours) for entrepreneurs, creative directors, and industry executives. Includes 3 wardrobe looks, professional hair & makeup, and 20 master retouched portraits.",
            "3. THE PERSONAL LEGACY PORTRAIT ($1,650): 90-minute unhurried studio session. Includes private gallery proofing, 10 retouched images, and a signature 8x10 cotton rag archival print.",
            "--PAGE-BREAK--",
            "# PAGE 3: THE STUDIO EXPERIENCE & BOOKING INTAKE",
            "HOW WE WORK: Step 1: The Conversation · Step 2: The Mood Board & Wardrobe Prep · Step 3: The Shoot Day · Step 4: The Proofing Gallery · Step 5: Master Retouching.",
            "STUDIO LOCATION: 1812 E 6th Street, Unit 204, Austin, TX 78702. Complimentary private parking behind the warehouse.",
            "BOOKING CALENDAR NOTE: Studio sessions are booked 4 to 6 weeks in advance. Inquire below to reserve your date.",
        ],
        role="draft",
    )

    # 3. audrey_current_homepage_screenshot.png: Desktop Squarespace Homepage Capture
    files["audrey_current_homepage_screenshot.png"] = write_screenshot_png_file(
        "audrey_current_homepage_screenshot.png",
        url="https://studiobrownphotography.squarespace.com/",
        site_title="Studio Brown Photography · Austin, TX",
        hero_headline="Visual storytelling for modern life.",
        hero_subhead="[Current Live Subhead: None. No Austin location mention. No commercial vs portrait differentiation.]",
        items=[
            ("Card 01", "Sculptors Portrait · Northern Light", "No Category Tag / No Pricing"),
            ("Card 02", "Texas Hill Country Outerwear", "Commercial Lookbook Commission"),
            ("Card 03", "Architectural Warehouse Loft", "East Austin Interior Shoot"),
            ("Card 04", "Dripping Springs Wedding", "Personal Wedding Commission"),
            ("Card 05", "Ceramics Maker Editorial", "Austin Artisan Feature"),
            ("Card 06", "Executive Founder Profile", "Studio Portrait Session"),
        ],
        kind="browser",
        role="source",
    )

    # 4. audrey_current_booking_form_screenshot.png: Squarespace 14-Question Intake Form Capture
    files["audrey_current_booking_form_screenshot.png"] = write_screenshot_png_file(
        "audrey_current_booking_form_screenshot.png",
        url="https://studiobrownphotography.squarespace.com/book",
        site_title="Studio Brown Photography · Client Booking",
        hero_headline="FORM ABANDONMENT AUDIT REFERENCE: Squarespace Lightbox Modal (14 Mandatory Fields)",
        hero_subhead="Client Intake Questionnaire (14 Required Fields · 0 Starting Rates Shown)",
        items=[
            ("1. Full Legal Name *", "Required for contract verification"),
            ("2. Email Address *", "client@domain.com"),
            ("3. Mobile Phone Number *", "+1 (512) 000-0000"),
            ("4. How did you hear about Studio Brown? *", "Dropdown (Instagram, Referral, Google)"),
            ("5. Type of Session *", "Dropdown (Portrait, Brand, Event)"),
            ("6. Preferred Session Date + 2 Backup Dates *", "e.g. Oct 14th, Oct 21st, Nov 4th"),
            ("7. Desired Location / Venue *", "Studio, Outdoor, Specific Venue"),
            ("8. Wardrobe Vision & Outfit Changes Planned", "Describe fabric textures, color palettes..."),
            ("9. Do you require on-site Hair & Makeup coordination? *", "Yes / No / Need recommendations"),
            ("10. Pinterest Moodboard or Visual Inspiration URL *", "https://pinterest.com/... (REQUIRED FIELD)"),
            ("11. Total Project Budget Band for this shoot *", "Open blank text input (No starting rates shown)"),
            ("12. Intended Image Usage & Licensing Rights *", "Personal / Commercial / Editorial Advertising"),
        ],
        kind="form",
        role="source",
    )

    # 4. audrey_homepage_booking_audit.pdf: 4-page conversion architecture audit PDF
    files["audrey_homepage_booking_audit.pdf"] = write_pdf_file(
        "audrey_homepage_booking_audit.pdf",
        "Studio Brown — Homepage & Booking Conversion Audit (Comprehensive 4-Page Report)",
        [
            "# 1. COMPREHENSIVE CONVERSION ARCHITECTURE EVALUATION",
            "This report establishes the redesign specifications for Studio Brown (Audrey Brown Photography, East Austin, TX).",
            "By transitioning from an ambiguous portfolio showcase to a structured luxury booking engine, Studio Brown can increase monthly qualified commission inquiries by an estimated 240% without discounting rates.",
            "--PAGE-BREAK--",
            "# 2. 10-POINT LUXURY CONVERSION HEURISTIC AUDIT",
            [
                ["Heuristic Checkpoint", "Current Implementation", "Audit Status", "Redesign Solution"],
                ["1. Above-the-Fold Value Prop", "Single ambient photo with no text", "FAILED", "Add refined editorial headline & location badge"],
                ["2. Mobile Page Speed (LCP)", "5.4 seconds on 4G cellular", "FAILED", "Compress to WebP; Cloudflare CDN caching (< 1.2s)"],
                ["3. Transparent Investment Tiers", "None; 'Contact for custom quote'", "FAILED", "Publish Starter, Signature, and Full tiers"],
                ["4. Social Proof & Accreditations", "Hidden in About page footer", "FAILED", "Add prominent trust bar below hero section"],
                ["5. Studio Space Showcase", "Only exterior warehouse photo", "FAILED", "Photo carousel of interior daylight warehouse"],
                ["6. Guided Booking Flow", "Standard 4-field generic form", "FAILED", "5-step interactive intake widget with session tags"],
                ["7. Commercial Rights Clarity", "Unclear licensing terms", "FAILED", "Explicit licensing matrix for brand commissions"],
                ["8. Calendar Availability", "Manual email back-and-forth", "FAILED", "Integrate live booking intake with 3-week lead time"],
                ["9. Client Proofing Portal", "Separate disjointed sub-domain", "PASSED", "Embed sleek seamless client portal button in navbar"],
                ["10. Typography & White Space", "Default browser sans-serif", "FAILED", "Custom Cormorant Garamond + Inter typography"],
            ],
            "--PAGE-BREAK--",
            "# 3. REVENUE IMPACT PROJECTION (90-DAY FORECAST)",
            [
                ["Metric", "Current Baseline", "Projected Post-Redesign", "Variance %", "Annual Revenue Impact"],
                ["Monthly Unique Visitors", "2,400", "3,800", "+58.3%", "SEO & Speed Boost"],
                ["Intake Form Submissions", "45", "180", "+300.0%", "Structured Funnel"],
                ["Qualified Discovery Calls", "18", "65", "+261.1%", "Pre-Qualified Budget"],
                ["Monthly Booked Commissions", "5 sessions", "14 sessions", "+180.0%", "+$24,800 / month"],
                ["Average Order Value (AOV)", "$1,850", "$2,450", "+32.4%", "Upsell Package Tiers"],
            ],
            "--PAGE-BREAK--",
            "# 4. REDESIGN IMPLEMENTATION ROADMAP",
            "— Phase 1 (Week 1): Prototype & Information Architecture sign-off.",
            "— Phase 2 (Week 2): Master copy deck delivery & responsive styling implementation.",
            "— Phase 3 (Week 3): Interactive intake widget testing & CRM email automation hookup.",
            "— Phase 4 (Week 4): Production launch, Google Analytics 4 tracking verification, and DNS switch.",
        ],
        role="deliverable",
        subtitle="4-Page Comprehensive Conversion Architecture & Strategic Revenue Roadmap",
        meta_tag="Studio Brown · Conversion Architecture Master Audit",
    )

    return files
