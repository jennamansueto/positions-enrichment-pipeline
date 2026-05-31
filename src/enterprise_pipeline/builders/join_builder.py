"""Builder for gold-layer joins."""

from __future__ import annotations

from enterprise_pipeline.config.models import JoinConfig


class JoinBuilder:
    """Fluent builder for constructing join configurations."""

    def __init__(self) -> None:
        self._joins: list[JoinConfig] = []

    def add_join(self, domain: str, join_key: str | list[str], join_type: str = "left") -> JoinBuilder:
        self._joins.append(JoinConfig(domain=domain, join_key=join_key, join_type=join_type))
        return self

    def build(self) -> list[JoinConfig]:
        return self._joins
