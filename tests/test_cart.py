import pytest

from cart import apply_discount, cart_total


def test_ten_percent_coupon():
    assert apply_discount(100, 10) == pytest.approx(90)


def test_zero_discount_is_noop():
    assert apply_discount(59.99, 0) == pytest.approx(59.99)


def test_cart_total_with_coupon():
    items = [{"price": 20, "qty": 2}, {"price": 10, "qty": 6}]
    assert cart_total(items, 10) == 90.0


@pytest.mark.parametrize("bad", [-5, 150])
def test_invalid_percent_rejected(bad):
    with pytest.raises(ValueError):
        apply_discount(100, bad)
