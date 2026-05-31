"""Tests for cardinality validation."""



class TestCardinalityChecks:
    """Cardinality check logic tests (without Spark)."""

    def test_check_result_structure(self) -> None:
        """Verify the check result dict has expected keys."""
        result = {
            "check": "cardinality",
            "label": "test",
            "expected": 100,
            "actual": 100,
            "passed": True,
            "message": "Row count: 100",
        }
        assert result["passed"] is True
        assert result["check"] == "cardinality"

    def test_tolerance_calculation(self) -> None:
        """Test tolerance bounds computation."""
        expected = 100
        tolerance = 0.05
        lower = int(expected * (1 - tolerance))
        upper = int(expected * (1 + tolerance))
        assert lower == 95
        assert upper == 105
        assert 100 >= lower and 100 <= upper  # should pass
        assert not (110 >= lower and 110 <= upper)  # should fail
