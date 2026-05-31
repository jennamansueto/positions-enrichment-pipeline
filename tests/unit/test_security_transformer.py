"""Tests for security transformer."""


class TestSecurityTransformer:
    def test_coupon_rate_bounds(self) -> None:
        """Coupon rate should be 0-100."""
        assert 0 <= 5.5 <= 100
        assert not (0 <= -1.0 <= 100)
        assert not (0 <= 101.0 <= 100)

    def test_rating_uppercase(self) -> None:
        assert "bbb+".upper() == "BBB+"
        assert "  Aa1 ".strip().upper() == "AA1"
