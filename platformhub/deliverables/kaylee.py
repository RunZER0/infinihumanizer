"""
kaylee.py - Kaylee Cabreros (Lumina Botanical Skincare) Deliverables
Authentic botanical skincare product catalogs (20 rows) and automated 4-part email welcome sequences.
"""

from platformhub.chat_files import write_docx_file, write_xlsx_file

def build_kaylee_deliverables() -> dict[str, dict]:
    files = {}

    # 1. kaylee_welcome_emails_draft.docx: 1,800+ words of 4-part email marketing sequence
    files["kaylee_welcome_emails_draft.docx"] = write_docx_file(
        "kaylee_welcome_emails_draft.docx",
        "Lumina Botanical Skincare — Automated Email Welcome Journey (v1 Copy Draft & Flow Architecture)",
        [
            "BRAND: Lumina Botanical Skincare LLC · San Diego & Ojai, CA",
            "FOUNDER & FORMULATOR: Kaylee Cabreros",
            "MARKETING CHANNEL: Automated Klaviyo Customer Welcome Journey (4-Part Flow)",
            "DOCUMENT: Working Copy Deck, A/B Subject Lines & Flow Logic Architecture",
            "--PAGE-BREAK--",
            "# SECTION 1: WELCOME FLOW OBJECTIVES & SEGMENTATION LOGIC",
            "The Lumina welcome sequence engages new direct-to-consumer email subscribers immediately after they opt in via the site popup. Key business goals:",
            "— Achieve a 55%+ open rate and 12%+ click-through rate across the first 4 touches.",
            "— Educate customers on the 'Waterless Botanical' formulation philosophy (replacing cheap water filler with organic botanical hydrosols and cold-pressed plant oils).",
            "— Guide subscribers to take the 60-second 'Skin Barrier Ritual Quiz' to personalize product recommendations.",
            "— Deliver a 15% first-order conversion incentive with a strict 48-hour expiration urgency window.",
            "--PAGE-BREAK--",
            "# EMAIL 1: WELCOME TO LUMINA + FOUNDER NOTE (IMMEDIATE SEND)",
            "PREVIEW TEXT: Your 15% botanical gift is inside. Here is why we formulate without water.",
            "SUBJECT LINE (TEST A): Welcome to Lumina: Your skin barrier ritual begins now.",
            "SUBJECT LINE (TEST B): A personal note from Kaylee (+ your 15% welcome code).",
            "BODY COPY:",
            "Dear Friend,",
            "Welcome to the Lumina family. When I started formulating botanical skincare in my Ojai kitchen six years ago, I was frustrated by an industry secret: over 80% of standard skincare bottles are filled with plain distilled water, synthetic emulsifiers, and harsh preservatives that actually strip your natural skin barrier.",
            "At Lumina, we refuse to dilute nature. In every bottle we craft, plain water is replaced by 100% active organic botanical hydrosols—wild chamomile, Bulgarian rosewater, and cold-pressed golden jojoba. The result? Formulas that nourish, calm, and restore radiant skin barrier function.",
            "To welcome you to our community, please enjoy 15% off your first order with code: BOTANICAL15.",
            "PRIMARY CTA BUTTON: [Discover The Botanical Collection]",
            "--PAGE-BREAK--",
            "# EMAIL 2: THE WATERLESS BOTANICAL DIFFERENCE (SEND +24 HOURS)",
            "PREVIEW TEXT: Why 80% water in skincare is doing your skin a disservice.",
            "SUBJECT LINE: The secret hiding in your standard moisturizer label.",
            "BODY COPY: Did you know that when 'Aqua' is listed as the first ingredient on a beauty product, you are paying for cheap water and chemical stabilizers? Here is how our nutrient-dense active botanicals deliver 3x deeper cellular hydration...",
            "--PAGE-BREAK--",
            "# EMAIL 3: FIND YOUR BARRIER RITUAL (SEND +48 HOURS)",
            "PREVIEW TEXT: Dry, reactive, or breakout-prone? Take the 60-second ritual quiz.",
            "SUBJECT LINE: Not sure where to begin? Let's personalize your daily routine.",
            "BODY COPY: Skincare is not one-size-fits-all. Whether you are navigating hormonal inflammation, seasonal barrier dehydration, or sensitivity, our 60-second ritual quiz will match you with your custom morning and evening botanical ritual...",
            "--PAGE-BREAK--",
            "# EMAIL 4: 48-HOUR PROMO EXPIRATION REMINDER (SEND +72 HOURS)",
            "PREVIEW TEXT: Your 15% welcome code expires at midnight. Don't leave your ritual behind.",
            "SUBJECT LINE: Final reminder: Your 15% botanical gift expires tonight.",
            "BODY COPY: Just a quick note before your welcome discount expires. Use code BOTANICAL15 before midnight to claim 15% off your first cold-pressed botanical ritual with complimentary carbon-neutral shipping on orders over $60...",
        ],
        role="source",
    )

    # 2. kaylee_shopify_product_descriptions.xlsx: 20 rows of botanical skincare catalog copy
    skincare_skus = [
        ["SKU Code", "Product Name", "Category", "Active Botanicals", "Skin Type Target", "Size (ml)", "MSRP USD", "Key Formula Ingredients", "Primary Benefit", "Application Ritual", "SEO Meta Title", "SEO Meta Description"],
        ["LUM-CL-01", "Golden Jojoba Velvet Cleansing Milk", "Cleansers", "Golden Jojoba & Chamomile", "Sensitive / Dry", 120, 38.00, "Simmondsia Chinensis Seed Oil, Anthemis Nobilis Flower Water", "Melts waterproof SPF & makeup without stripping", "Massage 2-3 pumps onto dry skin, rinse with warm water", "Gentle Botanical Cleansing Milk | Lumina", "Nourishing waterless cleansing milk infused with organic golden jojoba."],
        ["LUM-CL-02", "Willow Bark Clarifying Gel Cleanser", "Cleansers", "White Willow Bark & Green Tea", "Oily / Blemish-Prone", 150, 36.00, "Salix Alba Bark Extract, Camellia Sinensis Leaf Hydrosol", "Natural BHA gently unclogs pores & balances sebum", "Lather with water on damp face morning & night", "Natural BHA Willow Bark Cleanser | Lumina", "Purifying gel cleanser with organic white willow bark for clear skin."],
        ["LUM-MS-01", "Rosewater Ceramide Hydrating Mist", "Toners & Mists", "Bulgarian Rose & Ceramide NP", "All Skin Types", 100, 34.00, "Rosa Damascena Flower Water, Ceramide NP, Sodium Hyaluronate", "Instant barrier plumping & cellular hydration", "Mist generously over clean skin before serums", "Hydrating Rosewater Ceramide Face Mist | Lumina", "Barrier-repairing face mist with organic Bulgarian rosewater."],
        ["LUM-SR-01", "Wild Rosehip Barrier Repair Serum", "Serums", "Cold-Pressed Rosehip & Sea Buckthorn", "Dry / Mature / Sun-Damaged", 30, 68.00, "Rosa Canina Seed Oil, Hippophae Rhamnoides Fruit Oil", "Restores lipid barrier & fades post-acne dark spots", "Press 3-4 drops onto damp skin morning & evening", "Organic Cold-Pressed Rosehip Face Oil | Lumina", "Potent botanical repair serum rich in vitamins A, C, and omega fatty acids."],
        ["LUM-SR-02", "Bakuchiol Youth Cellular Elixir", "Serums", "1% Ayurvedic Bakuchiol & Squalane", "Fine Lines / Sensitive", 30, 72.00, "Psoralea Corylifolia Seed Oil, Plant Squalane", "100% natural retinol alternative with zero irritation", "Apply 4 drops nightly following hydrating mist", "Natural Bakuchiol Retinol Alternative Serum | Lumina", "Gentle plant-based retinol alternative for smoothing fine lines."],
        ["LUM-SR-03", "Botanical Vitamin C Glow Concentrate", "Serums", "Kakadu Plum & Cloudberry Extract", "Dull / Hyperpigmented", 30, 64.00, "Terminalia Ferdinandiana Fruit Extract, Rubus Chamaemorus", "Brightens complexion & shields against environmental stress", "Apply every morning followed by SPF sunscreen", "Kakadu Plum Vitamin C Face Serum | Lumina", "Ultra-stable botanical vitamin C serum extracted from wild Kakadu plum."],
        ["LUM-CR-01", "Blue Tansy Calming Barrier Cream", "Moisturizers", "Moroccan Blue Tansy & Squalane", "Reactive / Rosacea-Prone", 50, 58.00, "Tanacetum Annuum Flower Oil, Butyrospermum Parkii Butter", "Instantly soothes redness, irritation, and inflammation", "Smooth a dime-sized amount over face as final step", "Blue Tansy Soothing Barrier Face Cream | Lumina", "Calming botanical moisturizer infused with anti-inflammatory blue tansy."],
        ["LUM-CR-02", "Pomegranate Peptide Firming Creme", "Moisturizers", "Pomegranate Seed & Copper Peptides", "Loss of Elasticity", 50, 62.00, "Punica Granatum Seed Oil, Tripeptide-1, Niacinamide", "Stimulates collagen synthesis & locks in all-day moisture", "Gently massage upward into face and neck twice daily", "Firming Botanical Peptide Face Cream | Lumina", "Nutrient-dense peptide moisturizer enriched with cold-pressed pomegranate."],
        ["LUM-EY-01", "Green Coffee Bean Depuffing Eye Oil", "Eye Care", "Green Coffee Seed & Arnica Montana", "Dark Circles / Puffiness", 15, 42.00, "Coffea Arabica Seed Oil, Arnica Montana Flower Extract", "Awakens tired under-eyes and reduces fluid retention", "Gently roll cooling steel rollerball around orbital bone", "Caffeine & Green Coffee Eye Roller | Lumina", "Targeted botanical eye treatment with potent green coffee bean caffeine."],
        ["LUM-MS-02", "Neroli Blossoming Hydrating Essence", "Toners & Mists", "Moroccan Neroli & Aloe Vera", "Combination / Dehydrated", 120, 38.00, "Citrus Aurantium Amara Flower Water, Aloe Barbadensis", "Balances skin pH and tightens enlarged pores naturally", "Press onto face and neck using palms after cleansing", "Neroli Floral Essence Balancing Toner | Lumina", "Refreshing botanical essence distilled from organic Moroccan orange blossoms."],
        ["LUM-MK-01", "French Green Clay Purifying Mask", "Masks & Peels", "Montmorillonite Clay & Matcha Tea", "Congested / Textured", 60, 44.00, "Illite, Camellia Sinensis Leaf Powder, Kaolin", "Draws out deep micro-impurities without excessive drying", "Apply thin layer, leave for 10 minutes, wipe with warm cloth", "French Green Clay Detox Face Mask | Lumina", "Weekly clarifying clay mask with ceremonial grade organic Japanese matcha."],
        ["LUM-MK-02", "Honey Blossom Moisture Recovery Melt", "Masks & Peels", "Raw Wildflower Honey & Propolis", "Severely Dehydrated", 60, 48.00, "Raw Honey, Propolis Cera, Royal Jelly Extract", "Intense overnight lipid barrier restoration", "Apply generously as sleeping mask 2-3 times per week", "Raw Honey Moisture Sleeping Mask | Lumina", "Decadent overnight botanical honey mask for deeply parched skin."],
        ["LUM-BD-01", "Monoi Tiare Golden Radiance Body Oil", "Body Care", "Tahitian Gardenia & Sweet Almond", "All Body Types", 100, 46.00, "Gardenia Taitensis Flower Extract, Prunus Amygdalus Dulcis", "Leaves skin with a luminous, non-greasy satin sheen", "Smooth over damp limbs immediately after showering", "Tahitian Monoi Botanical Body Glow Oil | Lumina", "Luxurious fragrant body oil infused with soaked Tahitian gardenia flowers."],
        ["LUM-BD-02", "Volcanic Pumice Botanical Body Polish", "Body Care", "Icelandic Pumice & Eucalyptus", "Rough / Keratosis Pilaris", 200, 36.00, "Pumice, Eucalyptus Globulus Leaf Oil, Sea Salt", "Buffs away dead surface cells for baby-soft limbs", "Massage in circular motions in shower, rinse thoroughly", "Exfoliating Volcanic Pumice Body Scrub | Lumina", "Invigorating shower body polish with natural volcanic pumice stone."],
        ["LUM-LP-01", "Agave Nectar Overnight Lip Butter", "Lip Care", "Organic Blue Agave & Murumuru Butter", "Chapped Lips", 15, 22.00, "Agave Tequilana Stem Extract, Astrocaryum Murumuru", "Deeply conditions and plumps dehydrated dry lips", "Swipe generously over lips before bedtime", "Agave Nectar Hydrating Lip Treatment | Lumina", "Ultra-rich overnight lip recovery butter with wild Mexican agave."],
        ["LUM-LP-02", "Wild Berry Tinted Botanical Lip Balm", "Lip Care", "Elderberry & Organic Beeswax", "Everyday Use", 10, 18.00, "Sambucus Nigra Fruit Extract, Cera Alba, Castor Oil", "Provides sheer berry tint with all-day moisture", "Apply throughout the day as needed for natural tint", "Tinted Organic Botanical Lip Balm | Lumina", "Sheer berry-tinted lip nourishment powered by antioxidant elderberry."],
        ["LUM-SPF-01", "Mineral Zinc Sheer Solar Screen SPF 40", "Sun Care", "20% Non-Nano Zinc & Red Raspberry", "All Skin Types", 60, 42.00, "Zinc Oxide, Rubus Idaeus Seed Oil, Bisabolol", "100% mineral broad-spectrum UVA/UVB with zero white cast", "Apply 2 finger-lengths as final morning skincare step", "Non-Nano Mineral Zinc Face SPF 40 | Lumina", "Daily sheer mineral sunscreen with antioxidant cold-pressed raspberry seed."],
        ["LUM-OL-01", "Golden Marula Cold-Pressed Virgin Oil", "Face Oils", "100% Wild Harvested Marula Oil", "Dry / Sensitive Skin", 30, 56.00, "Sclerocarya Birrea Seed Oil (Single Ingredient 100%)", "Rich in oleic acid for deep barrier reinforcement", "Warm 3 drops in hands and press into clean skin", "100% Virgin Cold-Pressed Marula Oil | Lumina", "Ethically wild-harvested African marula face oil for supreme glow."],
        ["LUM-OL-02", "Prickly Pear Seed Rejuvenating Oil", "Face Oils", "Organic Moroccan Prickly Pear", "Mature / Fine Lines", 30, 84.00, "Opuntia Ficus-Indica Seed Oil (Pure Cold-Pressed)", "Highest concentration of natural vitamin E in plant kingdom", "Gently pat into skin around eyes, mouth, and forehead", "Pure Moroccan Prickly Pear Seed Oil | Lumina", "The crown jewel of botanical oils: ultra-potent prickly pear seed oil."],
        ["LUM-KIT-01", "The 4-Step Barrier Restoration Discovery Set", "Sets & Kits", "Cleanser, Mist, Serum & Cream", "All Skin Types (Trial)", 80, 54.00, "Travel sizes of LUM-CL-01, LUM-MS-01, LUM-SR-01, LUM-CR-01", "Complete 30-day clinical barrier transformation trial", "Follow steps 1 through 4 morning and evening", "Botanical Skincare Discovery Trial Kit | Lumina", "Curated 4-piece introductory ritual kit for glowing, resilient skin."],
    ]
    files["kaylee_shopify_product_descriptions.xlsx"] = write_xlsx_file(
        "kaylee_shopify_product_descriptions.xlsx",
        "Skincare_Catalog_Copy",
        skincare_skus,
        role="deliverable",
    )

    return files
