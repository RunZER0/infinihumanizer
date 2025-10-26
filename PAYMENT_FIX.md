# Payment System Fix Documentation

## Problem Summary

The payment system had a critical bug where all amounts were being multiplied by 135 * 100, regardless of whether the amount was already in KES or USD. This caused:

1. **KES Prices (African Users)**: Were being multiplied unnecessarily, resulting in exorbitant charges
   - Example: 1500 KES → 20,250,000 kobo = 202,500 KES (135x too much!)
   
2. **USD Prices (International Users)**: Were being converted correctly but the system couldn't differentiate

## Solution

### Changes Made

#### 1. Dynamic Pricing Template (`humanizer/templates/pricing.html`)
- Updated to use dynamic pricing from Django context
- Now displays correct currency based on user's location (IP-based detection)
- Passes currency information to payment flow
- Added Django humanize filter for proper number formatting

#### 2. Payment Flow (`humanizer/views.py`)

**Updated `PLAN_WORD_QUOTAS` and `PLAN_TIERS`:**
```python
PLAN_WORD_QUOTAS = {
    # USD amounts
    30: 100_000,
    75: 250_000,
    150: 600_000,
    # KES amounts
    1500: 100_000,
    3200: 250_000,
    6400: 600_000,
}
```

**Fixed `start_payment` function:**
- Now checks the currency parameter
- If USD: Converts to KES (USD × 135 × 100 for kobo)
- If KES: Only converts to kobo (KES × 100)
- Passes currency information through the entire payment flow

**Updated `verify_payment` function:**
- Now accepts and handles the currency parameter
- Correctly maps amounts to word quotas regardless of currency

#### 3. Payment Template (`humanizer/templates/payment.html`)
- Now displays the correct currency symbol
- Passes currency as a hidden field in the form

## How It Works Now

### For African/Kenyan Users (KES Pricing)

1. User visits `/humanizer/pricing/`
2. IP detected as African → Shows KES prices (1500, 3200, 6400)
3. User selects a plan → Redirected to payment with `amount=1500&currency=KES`
4. Payment form shows: **KSh 1500**
5. On submit:
   - Amount: 1500 KES
   - Paystack receives: 150,000 kobo (1500 × 100)
   - **User pays exactly 1500 KES** ✓

### For International Users (USD Pricing)

1. User visits `/humanizer/pricing/`
2. IP detected as non-African → Shows USD prices (30, 75, 150)
3. User selects a plan → Redirected to payment with `amount=30&currency=USD`
4. Payment form shows: **$30**
5. On submit:
   - Amount: 30 USD
   - Converted to KES: 30 × 135 = 4050 KES
   - Paystack receives: 405,000 kobo (4050 × 100)
   - **User pays 4050 KES (equivalent to ~$30)** ✓

## Payment Comparison

| Plan | Old KES Behavior | New KES Behavior | Old USD Behavior | New USD Behavior |
|------|------------------|------------------|------------------|------------------|
| Standard | 202,500 KES ✗ | 1,500 KES ✓ | 4,050 KES ✓ | 4,050 KES ✓ |
| Pro | 432,000 KES ✗ | 3,200 KES ✓ | 10,125 KES ✓ | 10,125 KES ✓ |
| Enterprise | 864,000 KES ✗ | 6,400 KES ✓ | 20,250 KES ✓ | 20,250 KES ✓ |

## Testing

To test the payment logic locally:

```bash
cd /home/runner/work/infinihumanizer/infinihumanizer
python /tmp/test_payment_logic.py
```

This will verify the conversion logic for all plans and currencies.

## Key Files Modified

1. `humanizer/views.py` - Payment logic and currency handling
2. `humanizer/templates/pricing.html` - Dynamic pricing display
3. `humanizer/templates/payment.html` - Payment form with currency
4. `accounts/views.py` - Fixed allauth import issue

## Additional Notes

- Paystack only accepts KES, so all international payments are converted to KES
- Exchange rate is set to 1 USD = 135 KES (configurable in the code)
- The system uses IP geolocation to determine user's location
- Localhost/development IPs default to Kenyan pricing for testing
- The word quotas are the same regardless of currency (e.g., 100,000 words for both $30 and 1500 KES)
