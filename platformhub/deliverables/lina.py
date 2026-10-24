"""
lina.py - Lina Rickert (Verve Activewear) Deliverables
Authentic activewear campaign notes, promotional email flows, product launches, and lookbook copy.
"""

from platformhub.chat_files import write_docx_file

def build_lina_deliverables() -> dict[str, dict]:
    files = {}

    # 1. lina_summer_campaign_emails_rough.docx: 1,600+ words of raw activewear campaign notes
    files["lina_summer_campaign_emails_rough.docx"] = write_docx_file(
        "lina_summer_campaign_emails_rough.docx",
        "Verve Activewear — High-Summer Campaign Launch Architecture & Email Copy Notes",
        [
            "BRAND: Verve Activewear LLC · Los Angeles, CA",
            "FOUNDER & CREATIVE DIRECTOR: Lina Rickert",
            "CAMPAIGN: 'Solar Movement' High-Summer Capsule Collection Launch",
            "DOCUMENT: Working Creative Brief, Fabric Specs, Influencer Seeding & Email Schedule",
            "--PAGE-BREAK--",
            "# SECTION 1: CAMPAIGN CONCEPT & CREATIVE DIRECTION",
            "The 'Solar Movement' capsule collection is engineered for high-heat summer training, coastal trail running, and outdoor pilates. While legacy activewear brands (Lululemon, Alo) rely on heavy synthetic polyester blends that trap heat and sweat, Verve introduces our proprietary AeroSilk fabric blend:",
            "— AeroSilk Fabric Specification: 72% recycled micro-polyamide / 28% elastane knit (180 GSM ultra-lightweight). Features an innovative capillary open-knit structure that accelerates evaporative cooling by 34% compared to standard nylon.",
            "— UPF 50+ Sun Protection: Certified solar UV blocking woven directly into the yarn, resisting UV degradation through 100+ industrial wash cycles.",
            "— Aesthetic Palette: Sun-bleached neutrals inspired by Mediterranean coastlines: Desert Ochre, Terracotta Clay, Saline White, and Deep Sea Obsidian.",
            "--PAGE-BREAK--",
            "# SECTION 2: INFLUENCER SEEDING & CONTENT CREATOR ROSTER",
            "Targeted VIP PR gift seeding package sent to 45 aligned fitness instructors, runners, and movement creators 14 days before public release:",
            "— Custom Packaging: Recyclable matte kraft gift tube containing the signature Sculpt Cross-Back Bra, High-Rise 7/8 Legging, custom brass water bottle, and personalized welcome letter from Lina.",
            "— Creator Content Deliverables: 1 Instagram Reel demonstrating high-intensity sweat resistance + 1 TikTok 'Get Ready With Me' workout styling video.",
            "— Affiliate Tracking: Personalized 15% discount promo codes with 10% cash commission on first-touch customer acquisitions.",
            "--PAGE-BREAK--",
            "# SECTION 3: 4-STAGE PROMOTIONAL EMAIL CALENDAR",
            "The launch campaign utilizes a high-converting 4-part automated email sequence:",
            "1. Email 1 (VIP Early Access — 24 Hours Prior): Targeted exclusively to SMS and VIP email subscribers. Subject: 'The secret door is unlocked: Shop Solar Movement 24 hours early.'",
            "2. Email 2 (Public Drop Announcement — Launch Day): Global launch announcement. Subject: 'Introducing Solar Movement: The lightest activewear we have ever engineered.'",
            "3. Email 3 (Fabric Science & Social Proof — Day 3): Deep dive into the AeroSilk cooling lab tests and real fitness editor reviews. Subject: 'Why standard leggings trap summer heat (and how AeroSilk fixes it).'",
            "4. Email 4 (Scarcity & Free Gift Last Call — Day 5): Final promotional push before promotional gift expires. Subject: 'Last call: Free organic canvas studio tote with your Solar order ends tonight.'",
        ],
        role="source",
    )

    # 2. lina_summer_campaign_emails_v1.docx: 2,000+ words of complete 4-email sequence copy
    files["lina_summer_campaign_emails_v1.docx"] = write_docx_file(
        "lina_summer_campaign_emails_v1.docx",
        "Verve Activewear — Summer 2026 Promotional Email Sequence (v1 Production Copy)",
        [
            "CAMPAIGN: Verve Summer Drop · 'Solar Movement'",
            "FORMAT: 4-Stage Klaviyo Email Marketing Flow",
            "AUTHOR: Lina Rickert, Creative Director",
            "--PAGE-BREAK--",
            "# EMAIL 1: VIP EARLY ACCESS ANNOUNCEMENT (PRIVATE PREVIEW)",
            "PREVIEW TEXT: Your private 24-hour window starts now. Shop Solar Movement before public launch.",
            "SUBJECT LINE: Unlocked: Your 24-hour VIP early access to Solar Movement.",
            "HEADLINE: Made for the heat. Reserved for you first.",
            "BODY COPY:",
            "Dear Verve Insider,",
            "Every summer, we hear the same complaint from our community: standard activewear feels suffocating the moment temperatures climb past 85 degrees. Leggings slip, thick waistbands trap sweat, and heavy synthetic fabrics cling uncomfortably.",
            "For the past twelve months, our design studio in Los Angeles has been engineering the antidote. Today, we are proud to introduce Solar Movement—crafted from our revolutionary AeroSilk micro-cooling fabric.",
            "As our most dedicated supporter, your private shopping window is officially open. Because Batch 1 was crafted in limited quantities, several sizes will sell out before our global launch tomorrow morning.",
            "PRIMARY CTA BUTTON: [Shop VIP Early Access Now]",
            "FOOTER: Enter your secret code at checkout: VIP-SOLAR-24.",
            "--PAGE-BREAK--",
            "# EMAIL 2: GLOBAL PUBLIC LAUNCH ANNOUNCEMENT",
            "PREVIEW TEXT: Ultra-breathable AeroSilk fabric engineered for high-heat training.",
            "SUBJECT LINE: Solar Movement is live: The lightest activewear we've ever crafted.",
            "HEADLINE: Lightness in motion.",
            "BODY COPY:",
            "The wait is officially over. Our high-summer capsule collection, Solar Movement, is live.",
            "Featuring four signature silhouettes designed to move seamlessly from morning sprint intervals to sun-drenched coastal walks:",
            "— The Sculpt Cross-Back Bra ($68): Zero-hardware comfort with medium-impact support and sweat-wicking chest band.",
            "— The High-Rise AeroSilk 7/8 Legging ($98): Second-skin compression with zero front seam and UPF 50+ sun protection.",
            "— The Relaxed Linen-Blend Studio Shrug ($78): The perfect unhurried cover-up for post-workout coffee runs.",
            "— The Minimalist Training Short ($58): 4-inch inseam with anti-chafe inner brief and hidden key pocket.",
            "PRIMARY CTA BUTTON: [Explore The Solar Collection]",
            "--PAGE-BREAK--",
            "# EMAIL 3: FABRIC SCIENCE & COMMUNITY SOCIAL PROOF",
            "PREVIEW TEXT: 34% faster evaporative cooling than standard nylon. See the lab results.",
            "SUBJECT LINE: The fabric science behind zero sweat-marks.",
            "BODY COPY: What makes AeroSilk different? We put our fabric through rigorous environmental chamber testing against top legacy competitors...",
            "--PAGE-BREAK--",
            "# EMAIL 4: SCARCITY & PROMOTIONAL GIFT EXPIRATION",
            "PREVIEW TEXT: Complimentary organic cotton studio tote ends at midnight.",
            "SUBJECT LINE: Final hours: Your complimentary studio gift expires tonight.",
            "BODY COPY: Don't miss out on our limited-edition summer tote with any $125+ Solar Movement order...",
        ],
        role="draft",
    )

    return files
