"""
keegan.py - Keegan Chin (Pacific Heritage Goods) Deliverables
Authentic 45-row Ningbo supplier SKU catalog, 3-page ocean freight rate sheet, and SKU margin models.
"""

from platformhub.chat_files import write_pdf_file, write_xlsx_file

def build_keegan_deliverables() -> dict[str, dict]:
    files = {}

    # 1. keegan_raw_sku_list.xlsx: 45 rows of authentic supplier SKUs from Ningbo factory
    supplier_skus = [
        ["SKU Code", "Product Category", "Item Name & Description", "Material Spec", "Carton Pack Qty", "Carton Dimensions (cm)", "Carton CBM", "Gross Weight (kg)", "FOB Ningbo USD", "HTS Tariff Code", "Duty Rate %", "MOQ Units"],
        ["PHG-WD-01", "Kitchen & Dining", "Handcrafted Acacia Cutting Board (Medium)", "Solid Acacia Hardwood", 12, "42 x 32 x 28", 0.0376, 14.5, 4.25, "4419.90.9000", 3.2, 500],
        ["PHG-WD-02", "Kitchen & Dining", "Handcrafted Acacia Cutting Board (Large)", "Solid Acacia Hardwood", 8, "52 x 38 x 26", 0.0514, 16.8, 6.80, "4419.90.9000", 3.2, 500],
        ["PHG-WD-03", "Kitchen & Dining", "End-Grain Teak Butcher Block Board", "Reclaimed Plantation Teak", 6, "45 x 35 x 30", 0.0473, 21.0, 14.50, "4419.90.9000", 3.2, 300],
        ["PHG-WD-04", "Tabletop", "Natural Edge Walnut Serving Platter", "Solid American Black Walnut", 10, "48 x 28 x 25", 0.0336, 13.2, 8.40, "4419.90.9000", 3.2, 400],
        ["PHG-WD-05", "Tabletop", "Teak Salad Bowl Set with Servers", "Organic Teak Root Turned", 8, "40 x 40 x 36", 0.0576, 15.0, 11.20, "4419.90.9000", 3.2, 300],
        ["PHG-CR-01", "Drinkware", "Speckled Ceramic Coffee Mug (12oz)", "Stoneware Matte Glaze", 24, "46 x 34 x 26", 0.0407, 12.8, 1.85, "6912.00.4100", 6.0, 1000],
        ["PHG-CR-02", "Drinkware", "Fluted Ceramic Tumbler (16oz)", "Stoneware Reactive Glaze", 24, "48 x 36 x 28", 0.0484, 14.2, 2.10, "6912.00.4100", 6.0, 1000],
        ["PHG-CR-03", "Dinnerware", "Organic Rim Ceramic Dinner Plate (10.5in)", "High-Fire Stoneware", 16, "45 x 45 x 28", 0.0567, 18.5, 3.40, "6912.00.4810", 6.0, 800],
        ["PHG-CR-04", "Dinnerware", "Organic Rim Ceramic Salad Plate (8.5in)", "High-Fire Stoneware", 20, "40 x 40 x 26", 0.0416, 16.0, 2.65, "6912.00.4810", 6.0, 800],
        ["PHG-CR-05", "Dinnerware", "Wide Rim Pasta & Grain Bowl (9in)", "High-Fire Stoneware", 16, "42 x 42 x 32", 0.0564, 17.2, 3.15, "6912.00.4810", 6.0, 800],
        ["PHG-GL-01", "Barware", "Hand-Blown Ribbed Rocks Glass (10oz)", "Lead-Free Soda-Lime Glass", 36, "50 x 38 x 24", 0.0456, 13.5, 1.45, "7013.37.2000", 5.0, 1200],
        ["PHG-GL-02", "Barware", "Hand-Blown Ribbed Highball Glass (14oz)", "Lead-Free Soda-Lime Glass", 36, "52 x 38 x 28", 0.0553, 15.2, 1.70, "7013.37.2000", 5.0, 1200],
        ["PHG-GL-03", "Barware", "Modernist Glass Cocktail Decanter (750ml)", "Borosilicate Glass with Cork", 12, "42 x 32 x 34", 0.0457, 11.0, 5.20, "7013.99.5000", 5.0, 500],
        ["PHG-TX-01", "Kitchen Linen", "Stone-Washed French Linen Dish Towel (2pk)", "100% Pure Flax Linen 220 GSM", 50, "40 x 30 x 25", 0.0300, 9.8, 3.80, "6302.99.1000", 8.8, 1000],
        ["PHG-TX-02", "Tabletop Linen", "Fringed Linen Table Runner (14x72in)", "100% Pure Flax Linen 240 GSM", 30, "45 x 35 x 22", 0.0347, 11.5, 6.40, "6302.59.1000", 8.8, 500],
        ["PHG-TX-03", "Tabletop Linen", "Stone-Washed Linen Napkin Set (4pk)", "100% Pure Flax Linen 220 GSM", 40, "42 x 32 x 28", 0.0376, 12.0, 5.10, "6302.59.1000", 8.8, 600],
        ["PHG-MT-01", "Kitchen Tools", "Matte Brass Measuring Cups & Spoons Set", "Solid Cast Brass Food-Safe", 20, "38 x 28 x 22", 0.0234, 14.0, 7.80, "8215.99.2000", 3.4, 500],
        ["PHG-MT-02", "Bar Tools", "Vintage Brass Cocktail Shaker (24oz)", "Stainless Steel Brass Plated", 24, "48 x 36 x 30", 0.0518, 13.8, 6.20, "7323.93.0080", 3.4, 600],
        ["PHG-MT-03", "Bar Tools", "Double-Sided Japanese Jigger (1oz / 2oz)", "Solid Cast Brass Mirror Polish", 50, "32 x 26 x 20", 0.0166, 8.5, 2.30, "8215.99.2000", 3.4, 1000],
        ["PHG-MT-04", "Cookware", "Pre-Seasoned Cast Iron Skillet (10in)", "Heavy Virgin Cast Iron", 6, "48 x 32 x 28", 0.0430, 19.5, 6.90, "7323.91.0000", 5.3, 500],
        ["PHG-MT-05", "Cookware", "Pre-Seasoned Cast Iron Skillet (12in)", "Heavy Virgin Cast Iron", 4, "54 x 36 x 26", 0.0505, 18.8, 9.40, "7323.91.0000", 5.3, 400],
        ["PHG-CD-01", "Home Fragrance", "Scented Soy Candle in Ceramic Vessel (8oz)", "100% Soy Wax & Cotton Wick", 24, "42 x 32 x 26", 0.0349, 14.2, 3.60, "3406.00.0000", 0.0, 800],
        ["PHG-CD-02", "Home Fragrance", "Scented Soy Candle in Brass Vessel (12oz)", "100% Soy Wax & Wood Wick", 18, "44 x 34 x 28", 0.0419, 15.6, 5.80, "3406.00.0000", 0.0, 600],
        ["PHG-CD-03", "Home Fragrance", "Aromatherapy Reed Diffuser (200ml)", "Glass Vessel with Rattan Reeds", 24, "46 x 34 x 30", 0.0469, 16.0, 4.40, "3307.49.0000", 4.9, 800],
        ["PHG-ST-01", "Organization", "Hand-Woven Water Hyacinth Storage Basket (M)", "Dried Natural Water Hyacinth", 10, "52 x 38 x 40", 0.0790, 11.2, 5.20, "4602.19.1800", 4.5, 400],
        ["PHG-ST-02", "Organization", "Hand-Woven Water Hyacinth Storage Basket (L)", "Dried Natural Water Hyacinth", 8, "58 x 44 x 46", 0.1174, 13.0, 7.80, "4602.19.1800", 4.5, 300],
        ["PHG-ST-03", "Organization", "Rattan Magazine & Record Holder", "Natural Cane Rattan", 6, "50 x 36 x 42", 0.0756, 9.5, 9.10, "4602.12.0500", 4.5, 300],
        ["PHG-BA-01", "Bath & Spa", "Waffle Weave Organic Cotton Bath Towel", "100% Organic Turkish Cotton 550GSM", 20, "50 x 38 x 36", 0.0684, 14.8, 7.20, "6302.60.0020", 9.1, 600],
        ["PHG-BA-02", "Bath & Spa", "Waffle Weave Organic Hand Towel (2pk)", "100% Organic Turkish Cotton 550GSM", 30, "44 x 34 x 30", 0.0449, 12.5, 4.80, "6302.60.0020", 9.1, 800],
        ["PHG-BA-03", "Bath & Spa", "Diatomaceous Earth Fast-Drying Bath Mat", "Natural Diatomite Stone 100%", 10, "64 x 42 x 22", 0.0591, 24.0, 6.90, "6809.90.0000", 4.0, 500],
        ["PHG-PL-01", "Garden & Decor", "Terracotta Planter with Drainage Saucer (6in)", "High-Fire Tuscan Terracotta", 18, "46 x 34 x 36", 0.0563, 16.5, 2.40, "6914.90.8000", 7.0, 800],
        ["PHG-PL-02", "Garden & Decor", "Terracotta Planter with Drainage Saucer (8in)", "High-Fire Tuscan Terracotta", 12, "48 x 38 x 40", 0.0730, 18.2, 3.90, "6914.90.8000", 7.0, 600],
        ["PHG-PL-03", "Garden & Decor", "Footed Ceramic Planter (10in)", "Speckled Stoneware Glazed", 6, "52 x 38 x 42", 0.0830, 17.0, 7.50, "6914.90.8000", 7.0, 400],
        ["PHG-WD-06", "Decor & Accents", "Minimalist Teak Wood Coaster Set (4pk)", "Solid Teak with Silicone Feet", 50, "36 x 26 x 22", 0.0206, 12.0, 2.10, "4419.90.9000", 3.2, 1000],
        ["PHG-WD-07", "Decor & Accents", "Sculptural Wooden Taper Candle Holder", "Turned Oak & Brass Inlay", 24, "40 x 30 x 28", 0.0336, 10.5, 4.60, "4420.90.8000", 3.2, 600],
        ["PHG-TX-04", "Bedding & Throw", "Washed Cotton Gauze Throw Blanket (50x60)", "4-Layer 100% Muslin Cotton", 12, "50 x 38 x 38", 0.0722, 13.4, 9.80, "6301.30.0010", 8.4, 400],
        ["PHG-TX-05", "Bedding & Throw", "Heavy Textured Wool Blend Throw (50x70)", "60% Wool 40% Recycled Cotton", 10, "52 x 40 x 42", 0.0874, 16.5, 14.80, "6301.20.0010", 7.5, 300],
        ["PHG-CR-06", "Kitchen Accents", "Ceramic Pour-Over Coffee Dripper Set", "Matte Stoneware & Glass Server", 12, "46 x 34 x 32", 0.0500, 13.0, 6.40, "6912.00.4100", 6.0, 600],
        ["PHG-CR-07", "Kitchen Accents", "Ceramic Butter Keeper French Bell", "Glazed Stoneware Water Seal", 24, "42 x 32 x 30", 0.0403, 14.5, 3.20, "6912.00.4810", 6.0, 800],
        ["PHG-GL-04", "Kitchen Accents", "Ribbed Glass Olive Oil Cruet (500ml)", "Borosilicate with Stainless Spout", 24, "44 x 32 x 34", 0.0479, 11.8, 3.10, "7013.99.5000", 5.0, 800],
        ["PHG-MT-06", "Tabletop Decor", "Solid Brass Trivet Hexagonal Design", "Heavy Cast Unlacquered Brass", 30, "40 x 30 x 24", 0.0288, 17.5, 5.40, "7418.10.1000", 3.0, 600],
        ["PHG-MT-07", "Tabletop Decor", "Taper Candle Snuffer & Wick Trimmer Set", "Solid Cast Brass Gift Boxed", 40, "38 x 28 x 22", 0.0234, 12.2, 4.10, "7418.10.1000", 3.0, 800],
        ["PHG-WD-08", "Office & Desk", "Solid Walnut Desktop Organizer Tray", "American Walnut CNC Milled", 20, "44 x 32 x 26", 0.0366, 14.0, 6.50, "4420.90.8000", 3.2, 500],
        ["PHG-WD-09", "Office & Desk", "Solid Walnut Magnetic Cable Block", "Walnut with Neodymium Magnets", 60, "32 x 24 x 20", 0.0154, 8.4, 2.80, "4420.90.8000", 3.2, 1000],
        ["PHG-ST-04", "Decor Accents", "Rattan Woven Wastebasket with Lid", "Natural Hand-Woven Rattan", 8, "48 x 48 x 52", 0.1198, 12.0, 8.20, "4602.12.0500", 4.5, 300],
    ]
    files["keegan_raw_sku_list.xlsx"] = write_xlsx_file(
        "keegan_raw_sku_list.xlsx",
        "Raw_SKU_Import",
        supplier_skus,
        role="source",
    )

    # 2. keegan_freight_duty_rates.pdf: 3-page ocean freight rate sheet & customs advisory
    files["keegan_freight_duty_rates.pdf"] = write_pdf_file(
        "keegan_freight_duty_rates.pdf",
        "Trans-Pacific LCL Ocean Freight & Customs Broker Rate Sheet — Pacific Heritage Goods",
        [
            "# 1. OCEAN FREIGHT SERVICE SPECIFICATIONS",
            "Freight Forwarding Partner: Apex Ocean Cargo Logistics · DB Schenker Network",
            "Trade Lane: Port of Ningbo / Shanghai, China to Port of Los Angeles (POLA) / Long Beach (POLB), California.",
            "Service Classification: Less-Than-Container-Load (LCL) Consolidation & Weekly Direct Vessel Dispatch.",
            "Average Ocean Transit Time: 14 to 18 calendar days port-to-port; 4 to 6 days deconsolidation and customs release.",
            "--PAGE-BREAK--",
            "# 2. COMPREHENSIVE LCL FREIGHT TARIFF SCHEDULE",
            [
                ["Service Line Item", "Tariff Basis", "Quoted Rate USD", "Fuel Surcharge Inclusion", "Billing Rules"],
                ["Ocean Freight (Ningbo -> LAX)", "Per CBM (Cubic Meter)", "$185.00 / CBM", "Includes BAF & Bunker Surcharge", "1 CBM = 1,000 kg minimum"],
                ["Terminal Handling Charge (THC)", "Per CBM", "$38.00 / CBM", "Included in ocean bill", "Charged at origin port"],
                ["ISF 10+2 Security Filing", "Per shipment bill of lading", "$45.00 flat fee", "Mandatory U.S. Customs", "Must file 24 hrs prior to vessel loading"],
                ["Customs Entry & Formal Clearance", "Per commercial entry", "$140.00 flat fee", "Covers up to 5 HTS tariff lines", "$12.00 per additional line"],
                ["Harbor Maintenance Fee (HMF)", "Ad valorem commercial value", "0.125% of entered cargo value", "U.S. Customs mandatory fee", "Collected on Form 7501"],
                ["Merchandise Processing Fee (MPF)", "Ad valorem commercial value", "0.3464% (Min $31.67 / Max $614.35)", "U.S. Customs mandatory fee", "Collected on Form 7501"],
                ["Port Drayage & Deconsolidation", "Per ocean bill of lading", "$185.00 flat entry + $18.50/pallet", "Includes CFS devanning", "Dock staging up to 4 days free"],
            ],
            "--PAGE-BREAK--",
            "# 3. CUSTOMS COMPLIANCE & SECTION 301 TARIFF ADVISORY",
            "Importers of home goods manufactured in China must evaluate Harmonized Tariff Schedule (HTS) Section 301 punitive tariff exclusions:",
            "— Wood Products (HTS 4419 / 4420): Standard column-1 duty rate is 3.2% + Section 301 List 3 tariff (25.0%). Combined effective duty is 28.2%.",
            "— Ceramic Stoneware (HTS 6912): Standard column-1 duty rate is 6.0% + Section 301 List 4A tariff (7.5%). Combined effective duty is 13.5%.",
            "— Glass Barware (HTS 7013): Standard column-1 duty rate is 5.0% + Section 301 List 3 tariff (25.0%). Combined effective duty is 30.0%.",
            "— Linen & Cotton Textiles (HTS 6302): Standard column-1 duty rate is 8.8% + Section 301 List 4A tariff (7.5%). Combined effective duty is 16.3%.",
            "— Landed Cost Recommendation: Pacific Heritage Goods must budget for a blended 24.5% import tariff on FOB goods when calculating wholesale and Amazon FBA unit margins.",
        ],
        role="source",
        subtitle="3-Page Trans-Pacific Logistics Tariff Schedule & U.S. Customs Section 301 Advisory",
        meta_tag="Pacific Heritage Goods · International Supply Chain Tariff Sheet",
    )

    # 3. keegan_sku_margin_calculator_v1.xlsx: 30 rows of SKU landed costs and margins
    margin_rows = [
        ["SKU Code", "Description", "FOB Ningbo USD", "Ocean Freight / Unit", "Customs Tariff (24.5%)", "Port Drayage / Unit", "Total Landed Cost", "Amazon FBA Fee", "FBA Referral (15%)", "Wholesale Price (50% Margin)", "Retail MSRP", "Gross Margin %"],
        ["PHG-WD-01", "Acacia Cutting Board (M)", 4.25, 0.58, 1.04, 0.22, 6.09, 4.85, 4.20, 12.50, 28.00, 51.3],
        ["PHG-WD-02", "Acacia Cutting Board (L)", 6.80, 0.95, 1.67, 0.28, 9.70, 6.20, 5.70, 19.50, 38.00, 50.8],
        ["PHG-WD-03", "Teak Butcher Block", 14.50, 1.45, 3.55, 0.35, 19.85, 9.50, 9.75, 39.00, 65.00, 49.1],
        ["PHG-WD-04", "Walnut Serving Platter", 8.40, 0.72, 2.06, 0.25, 11.43, 5.80, 6.30, 23.00, 42.00, 50.9],
        ["PHG-WD-05", "Teak Salad Bowl Set", 11.20, 1.35, 2.74, 0.30, 15.59, 7.80, 8.25, 32.00, 55.00, 51.3],
        ["PHG-CR-01", "Ceramic Coffee Mug (12oz)", 1.85, 0.32, 0.45, 0.15, 2.77, 4.20, 2.70, 6.50, 18.00, 57.4],
        ["PHG-CR-02", "Ceramic Tumbler (16oz)", 2.10, 0.38, 0.51, 0.16, 3.15, 4.40, 3.00, 7.50, 20.00, 58.0],
        ["PHG-CR-03", "Ceramic Dinner Plate (10.5in)", 3.40, 0.65, 0.83, 0.22, 5.10, 5.60, 4.20, 12.00, 28.00, 57.5],
        ["PHG-CR-04", "Ceramic Salad Plate (8.5in)", 2.65, 0.48, 0.65, 0.18, 3.96, 4.90, 3.60, 9.50, 24.00, 58.3],
        ["PHG-CR-05", "Ceramic Pasta Bowl (9in)", 3.15, 0.62, 0.77, 0.20, 4.74, 5.40, 3.90, 11.00, 26.00, 57.0],
        ["PHG-GL-01", "Ribbed Rocks Glass (10oz)", 1.45, 0.24, 0.36, 0.12, 2.17, 3.90, 2.40, 5.50, 16.00, 60.5],
        ["PHG-GL-02", "Ribbed Highball Glass (14oz)", 1.70, 0.28, 0.42, 0.14, 2.54, 4.20, 2.70, 6.50, 18.00, 60.8],
        ["PHG-GL-03", "Glass Cocktail Decanter", 5.20, 0.72, 1.27, 0.24, 7.43, 6.10, 6.30, 18.00, 42.00, 57.1],
        ["PHG-TX-01", "French Linen Towel (2pk)", 3.80, 0.12, 0.93, 0.08, 4.93, 3.60, 4.20, 12.00, 28.00, 59.0],
        ["PHG-TX-02", "Linen Table Runner", 6.40, 0.22, 1.57, 0.12, 8.31, 4.40, 6.60, 19.00, 44.00, 56.8],
        ["PHG-TX-03", "Linen Napkin Set (4pk)", 5.10, 0.18, 1.25, 0.10, 6.63, 4.10, 5.70, 16.00, 38.00, 58.6],
        ["PHG-MT-01", "Brass Measuring Cups Set", 7.80, 0.22, 1.91, 0.12, 10.05, 4.80, 7.20, 24.00, 48.00, 58.1],
        ["PHG-MT-02", "Vintage Brass Shaker", 6.20, 0.42, 1.52, 0.16, 8.30, 5.20, 6.75, 21.00, 45.00, 55.6],
        ["PHG-MT-03", "Japanese Brass Jigger", 2.30, 0.08, 0.56, 0.06, 3.00, 3.40, 3.30, 8.50, 22.00, 64.7],
        ["PHG-MT-04", "Cast Iron Skillet (10in)", 6.90, 1.35, 1.69, 0.35, 10.29, 8.80, 6.30, 22.00, 42.00, 53.2],
        ["PHG-MT-05", "Cast Iron Skillet (12in)", 9.40, 1.85, 2.30, 0.42, 13.97, 11.20, 8.70, 30.00, 58.00, 51.8],
        ["PHG-CD-01", "Soy Candle in Ceramic (8oz)", 3.60, 0.28, 0.88, 0.14, 4.90, 4.60, 4.80, 14.00, 32.00, 65.0],
        ["PHG-CD-02", "Soy Candle in Brass (12oz)", 5.80, 0.44, 1.42, 0.18, 7.84, 5.40, 6.30, 19.50, 42.00, 60.3],
        ["PHG-CD-03", "Reed Diffuser (200ml)", 4.40, 0.38, 1.08, 0.16, 6.02, 4.80, 5.70, 16.50, 38.00, 56.6],
        ["PHG-ST-01", "Hyacinth Storage Basket (M)", 5.20, 1.45, 1.27, 0.35, 8.27, 8.50, 6.30, 21.00, 42.00, 60.6],
        ["PHG-ST-02", "Hyacinth Storage Basket (L)", 7.80, 2.10, 1.91, 0.45, 12.26, 11.80, 8.70, 29.00, 58.00, 57.7],
        ["PHG-BA-01", "Waffle Bath Towel", 7.20, 0.65, 1.76, 0.22, 9.83, 5.80, 7.20, 24.00, 48.00, 59.0],
        ["PHG-BA-02", "Waffle Hand Towel (2pk)", 4.80, 0.28, 1.18, 0.14, 6.40, 4.40, 4.80, 14.50, 32.00, 55.9],
        ["PHG-BA-03", "Stone Bath Mat", 6.90, 1.15, 1.69, 0.32, 10.06, 9.20, 7.20, 24.00, 48.00, 58.1],
        ["PHG-WD-06", "Teak Coaster Set (4pk)", 2.10, 0.08, 0.51, 0.06, 2.75, 3.40, 3.00, 7.50, 20.00, 63.3],
    ]
    files["keegan_sku_margin_calculator_v1.xlsx"] = write_xlsx_file(
        "keegan_sku_margin_calculator_v1.xlsx",
        "Margin_Calculator_v1",
        margin_rows,
        role="source",
    )

    return files
