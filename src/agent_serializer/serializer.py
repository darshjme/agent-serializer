"""Base serializer with type registry for agent data."""

from __future__ import annotations

import json
import dataclasses
from datetime import datetime, date, time
from enum import Enum
from typing import Any, Callable


_TYPE_TAG = "__type__"
_VALUE_TAG = "__value__"


class _AgentEncoder(json.JSONEncoder):
    """JSON encoder that handles agent-specific types."""

    def __init__(self, *args, registry: dict | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._registry = registry or {}

    def default(self, obj: Any) -> Any:  # noqa: ANN401
        # Check custom registry first
        for type_, (encoder, _) in self._registry.items():
            if isinstance(obj, type_):
                return {_TYPE_TAG: f"custom:{type_.__qualname__}", _VALUE_TAG: encoder(obj)}

        if isinstance(obj, datetime):
            return {_TYPE_TAG: "datetime", _VALUE_TAG: obj.isoformat()}
        if isinstance(obj, date):
            return {_TYPE_TAG: "date", _VALUE_TAG: obj.isoformat()}
        if isinstance(obj, time):
            return {_TYPE_TAG: "time", _VALUE_TAG: obj.isoformat()}
        if isinstance(obj, Enum):
            return {_TYPE_TAG: "enum", "cls": f"{obj.__class__.__module__}.{obj.__class__.__qualname__}", _VALUE_TAG: obj.value}
        if isinstance(obj, set):
            return {_TYPE_TAG: "set", _VALUE_TAG: list(obj)}
        if isinstance(obj, frozenset):
            return {_TYPE_TAG: "frozenset", _VALUE_TAG: list(obj)}
        if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
            return {
                _TYPE_TAG: "dataclass",
                "cls": f"{obj.__class__.__module__}.{obj.__class__.__qualname__}",
                _VALUE_TAG: dataclasses.asdict(obj),
            }
        if isinstance(obj, bytes):
            return {_TYPE_TAG: "bytes", _VALUE_TAG: obj.hex()}
        return super().default(obj)


def _decode_hook(registry: dict, obj: dict) -> Any:  # noqa: ANN401
    """Object hook for JSON decoder."""
    if _TYPE_TAG not in obj:
        return obj

    tag = obj[_TYPE_TAG]
    val = obj.get(_VALUE_TAG)

    if tag == "datetime":
        return datetime.fromisoformat(val)
    if tag == "date":
        return date.fromisoformat(val)
    if tag == "time":
        return time.fromisoformat(val)
    if tag == "set":
        return set(val)
    if tag == "frozenset":
        return frozenset(val)
    if tag == "bytes":
        return bytes.fromhex(val)
    if tag == "enum":
        # Try to import and reconstruct — best effort
        try:
            module_name, cls_name = obj["cls"].rsplit(".", 1)
            import importlib
            mod = importlib.import_module(module_name)
            cls = getattr(mod, cls_name)
            return cls(val)
        except Exception:
            return val
    if tag == "dataclass":
        try:
            parts = obj["cls"].rsplit(".", 1)
            if len(parts) == 2:
                module_name, cls_name = parts
                import importlib
                mod = importlib.import_module(module_name)
                cls = getattr(mod, cls_name)
                if dataclasses.is_dataclass(cls):
                    return cls(**val)
        except Exception:
            pass
        return val
    if tag.startswith("custom:"):
        custom_name = tag[len("custom:"):]
        for type_, (_, decoder) in registry.items():
            if type_.__qualname__ == custom_name:
                return decoder(val)
    return obj


class Serializer:
    """Base serializer with type registry.

    Handles datetime, Enum, dataclass, set, bytes out of the box.
    Supports custom type registration via :meth:`register`.
    """

    def __init__(self) -> None:
        self._registry: dict[type, tuple[Callable, Callable]] = {}

    def register(self, type_: type, encoder: Callable[[Any], Any], decoder: Callable[[Any], Any]) -> None:
        """Register a custom type with encoder/decoder callables."""
        self._registry[type_] = (encoder, decoder)

    def encode(self, obj: Any) -> Any:
        """Encode *obj* to a JSON-serialisable dict/primitive."""
        # Round-trip through JSON to apply all transformations
        raw = json.dumps(obj, cls=_AgentEncoder, registry=self._registry)
        return json.loads(raw)

    def dumps(self, obj: Any) -> str:
        """Serialize *obj* to a JSON string."""
        return json.dumps(obj, cls=_AgentEncoder, registry=self._registry)

    def loads(self, data: str) -> Any:
        """Deserialize a JSON string back to Python objects."""
        registry = self._registry

        def hook(d: dict) -> Any:
            return _decode_hook(registry, d)

        return json.loads(data, object_hook=hook)
