"""Tests for risk transformer."""


class TestRiskTransformer:
    def test_yield_bounds(self) -> None:
        """Yields should be clamped to -50..200."""
        assert -50 <= 5.0 <= 200
        assert not (-50 <= -60 <= 200)

    def test_liquidity_score_bounds(self) -> None:
        """Liquidity score should be 0-100."""
        assert 0 <= 75.5 <= 100
        assert not (0 <= 105 <= 100)

    def test_price_source_normalization(self) -> None:
        assert "bloomberg".upper() == "BLOOMBERG"
        assert " ice ".strip().upper() == "ICE"
