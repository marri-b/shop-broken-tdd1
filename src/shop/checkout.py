"""Order checkout.

The rules live in `src/shop/specs/checkout.md` - read it first.
Both functions below are stubs: their signature is final, the bodies are yours.
Do not change the constants: the tests rely on them.
"""

from shop.money import percent_of

PROMO_CODES = {"WELCOME10": 10, "SUMMER15": 15, "VIP35": 35}
SUPPORTED_CITIES = ("msk", "spb")
MAX_DISCOUNT_PERCENT = 30
VAT_PERCENT = 20
SHIPPING_KOPEKS = 49_000
FREE_DELIVERY_FROM_KOPEKS = 500_000
TIER_DISCOUNTS = ((10, 5), (25, 10), (50, 15))
REQUIRED_LINE_KEYS = ("sku", "qty", "unit_price_kopeks")

def validate_order(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> str | None:
    """Return a human readable reason why the order is invalid, or None if it is fine."""
    if not lines:
        return "order has no lines"

 (checkout and fix inventory)

    seen: set[str] = set()
    for i, line in enumerate(lines, start=1):
        for key in REQUIRED_LINE_KEYS:
            if key not in line:
                return f"line {i} is missing key {key}"
        if not line["sku"]:
            return f"line {i} has an empty sku"
        try:
            qty = int(line["qty"])
        except ValueError:
            return f"line {i} has a non-numeric qty"
        if qty <= 0:
            return f"line {i} has a non-positive qty"
        try:
            price = int(line["unit_price_kopeks"])
        except ValueError:
            return f"line {i} has a non-numeric price"
        if price < 0:
            return f"line {i} has a negative price"
        if line["sku"] in seen:
            return f"line {i} repeats sku {line['sku']}"
        seen.add(line["sku"])

    if promo_code and promo_code not in PROMO_CODES:
        return "unknown promo code"
    if shipping_city and shipping_city not in SUPPORTED_CITIES:
        return "unsupported city"
    return None

def calculate_order_total(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> int | None:
    """Return the order total in kopeck, or None if the order is invalid."""
    if validate_order(lines, promo_code, shipping_city) is not None:
        return None

    subtotal = sum(int(line["qty"]) * int(line["unit_price_kopeks"]) for line in lines)
    total_qty = sum(int(line["qty"]) for line in lines)

    tier_percent = 0
    for threshold, percent in TIER_DISCOUNTS:
        if total_qty >= threshold:
            tier_percent = percent

    promo_percent = PROMO_CODES.get(promo_code, 0)
    discount_percent = max(tier_percent, promo_percent)
    if discount_percent > MAX_DISCOUNT_PERCENT:
        discount_percent = MAX_DISCOUNT_PERCENT

    discount = percent_of(subtotal, discount_percent)
    discounted_subtotal = subtotal - discount

    delivery = 0
    if shipping_city and discounted_subtotal < FREE_DELIVERY_FROM_KOPEKS:
        delivery = SHIPPING_KOPEKS

    base = discounted_subtotal + delivery
    vat = percent_of(base, VAT_PERCENT)
    return base + vat