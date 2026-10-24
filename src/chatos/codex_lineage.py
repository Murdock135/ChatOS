"""Validate declared Codex fork ancestry without accepting unrelated sessions."""

from typing import Any, Optional


class SessionLineage:
    """Track the owning session and the origin of inherited visible history."""

    def __init__(self, expected: Optional[str] = None):
        self.identity = expected
        self.current: Optional[str] = None
        self.metadata: dict[str, Any] = {}
        self.parents: dict[str, Optional[str]] = {}
        self.observed: list[str] = []

    def observe(self, payload: dict[str, Any]) -> None:
        """Accept only the owner or ancestors declared by an accepted header."""
        identity = payload.get("id")
        if not isinstance(identity, str) or not identity:
            raise ValueError("Source session ID is missing")
        if not self.observed:
            if self.identity and identity != self.identity:
                raise ValueError("Source conversation identity mismatch")
            self.identity = identity
            self.metadata = {
                key: payload.get(key)
                for key in [
                    "id",
                    "timestamp",
                    "cwd",
                    "originator",
                    "cli_version",
                    "source",
                    "model_provider",
                ]
            }
        allowed = {self.identity, *self.parents.values()}
        if identity not in allowed:
            raise ValueError(
                "Source conversation identity mismatch: undeclared ancestor"
            )
        parent = payload.get("forked_from_id")
        if parent is not None and (not isinstance(parent, str) or not parent):
            raise ValueError("Invalid fork parent identity")
        if (
            identity in self.parents
            and "forked_from_id" in payload
            and self.parents[identity] != parent
        ):
            raise ValueError("Conflicting fork parent identity")
        if identity not in self.parents or parent is not None:
            self.parents[identity] = parent
        seen = {identity}
        ancestor = self.parents[identity]
        while ancestor is not None:
            if ancestor in seen:
                raise ValueError("Cyclic fork ancestry")
            seen.add(ancestor)
            ancestor = self.parents.get(ancestor)
        if identity not in self.observed:
            self.observed.append(identity)
        self.current = identity

    def origin(self) -> dict[str, Any]:
        """Annotate fork context; ordinary single-session records stay unchanged."""
        if not self.parents.get(self.identity or ""):
            return {}
        return {
            "origin_conversation_id": self.current,
            "inherited": self.current != self.identity,
        }

    def evidence(self) -> dict[str, Any]:
        if not self.parents.get(self.identity or ""):
            return {}
        return {
            "forked_from_id": self.parents[self.identity or ""],
            "observed_session_ids": self.observed,
            "declared_ancestry": [
                {"id": identity, "forked_from_id": self.parents[identity]}
                for identity in self.observed
            ],
        }
