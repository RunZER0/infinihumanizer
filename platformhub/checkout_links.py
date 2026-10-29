"""
Central registry of dedicated, custom checkout links per client.
Different users have separate checkout links provided. These links are custom
and used by that user for the entire duration of their engagements.
"""

CLIENT_CUSTOM_CHECKOUT_LINKS = {
    "cruzjose6221@gmail.com": "https://paystack.shop/pay/4q5iounn6s",
    "audreymbrown2007@gmail.com": "https://paystack.shop/pay/ppiajw3f1-",
    "orozcoazael815@gmail.com": "https://paystack.shop/pay/ao-roofing1",
    "jackjohnson0533@gmail.com": "https://paystack.shop/pay/jj-crm92",
    "lucacaro@hawaii.edu": "https://paystack.shop/pay/892lxc01po",
    "kchin444@gmail.com": "https://paystack.shop/pay/kc-chin77",
    "vickyizad@gmail.com": "https://paystack.shop/pay/li-tampa44",
    "drako.santaana.glz@gmail.com": "https://paystack.shop/pay/ds-dock55",
    "estellawilliams06@gmail.com": "https://paystack.shop/pay/ew-williams8",
    "kayleecabreros@gmail.com": "https://paystack.shop/pay/kc-skin12",
    "dkiragu97@gmail.com": "https://paystack.shop/pay/dk-freight3",
    "uzbekquintero@gmail.com": "https://paystack.shop/pay/aq-cold61",
    "cami.kurtz@icloud.com": "https://paystack.shop/pay/ck-train88",
    "linarickert2514@gmail.com": "https://paystack.shop/pay/lr-summer22",
    "patrickhyland04@gmail.com": "https://paystack.shop/pay/ph-ferry34",
    "lemburgcarter@gmail.com": "https://paystack.shop/pay/cl-apex99",
    "issabelc207@gmail.com": "https://paystack.shop/pay/tx0ipp9eg4",
}

EMAIL_ALIASES = {
    "stellarae147@gmail.com": "estellawilliams06@gmail.com",
    "luca_carollo05@yahoo.com": "lucacaro@hawaii.edu",
}


def get_client_checkout_link(email_or_user) -> str:
    """Return the client's persistent custom checkout link, or empty string if not found."""
    if not email_or_user:
        return ""
    if hasattr(email_or_user, "email"):
        email = getattr(email_or_user, "email", "") or ""
    else:
        email = str(email_or_user)
    cleaned = email.strip().lower()
    cleaned = EMAIL_ALIASES.get(cleaned, cleaned)
    return CLIENT_CUSTOM_CHECKOUT_LINKS.get(cleaned, "")
