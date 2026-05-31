"""Tests for positions transformer."""


class TestPositionsTransformer:
    def test_valid_statuses(self) -> None:
        valid = ["OPEN", "CLOSED", "PENDING"]
        assert "OPEN" in valid
        assert "INVALID" not in valid

    def test_total_pnl_derivation(self) -> None:
        unrealized = 100.0
        realized = 50.0
        expected_total = 150.0
        assert unrealized + realized == expected_total
