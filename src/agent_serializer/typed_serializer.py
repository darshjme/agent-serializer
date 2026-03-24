"""Schema-aware serializer that validates and coerces to a dataclass or TypedDict."""

from __future__ import annotations

import dataclasses
import json
from typing import Any, get_type_hints

from .serializer import Serializer


class TypedSerializer(Serializer):
    """Schema-aware serializer.

    Parameters
    ----------
    schema:
        A :func:`dataclasses.dataclass`-decorated class or a ``TypedDict`` subclass.
    """

    def __init__(self, schema: type) -> None:
        super().__init__()
        self._schema = schema
        self._is_dataclass = dataclasses.is_dataclass(schema)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def dumps(self, obj: Any) -> str:  # noqa: D102
        return super().dumps(obj)

    def loads(self, data: str) -> Any:
        """Deserialize *data* and coerce to the declared schema type."""
        raw = super().loads(data)
        return self._coerce(raw)

    def validate(self, data: dict) -> bool:
        """Return ``True`` if *data* satisfies the schema's required fields."""
        try:
            self._coerce(data)
            return True
        except (TypeError, KeyError, ValueError):
            return False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _coerce(self, raw: Any) -> Any:
        if not isinstance(raw, dict):
            return raw
        if self._is_dataclass:
            hints = get_type_hints(self._schema)
            fields = {f.name for f in dataclasses.fields(self._schema)}
            kwargs: dict[str, Any] = {}
            for field_name in fields:
                if field_name in raw:
                    kwargs[field_name] = raw[field_name]
            return self._schema(**kwargs)
        # TypedDict — just return the dict (TypedDict is not a runtime constructor)
        return raw
