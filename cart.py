"""Shopping cart pricing helpers."""


def apply_discount(total: float, percent: float) -> float:
    """Apply a percentage discount. `percent` is between 0 and 100."""
    if not 0 <= percent <= 100:
        raise ValueError("discount percent must be between 0 and 100")
    return total * (1 - percent / 100)


def cart_total(items: list[dict], discount_percent: float = 0) -> float:
    subtotal = sum(i["price"] * i["qty"] for i in items)
    return round(apply_discount(subtotal, discount_percent), 2)
