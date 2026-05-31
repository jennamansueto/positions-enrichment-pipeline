"""End-to-end pipeline integration test (requires PySpark)."""

import pytest


@pytest.mark.integration
class TestPipelineE2E:
    """Full pipeline integration tests — skipped unless Spark is available."""

    def test_placeholder(self) -> None:
        """Placeholder for full e2e test requiring Spark + sample data."""
        pass
