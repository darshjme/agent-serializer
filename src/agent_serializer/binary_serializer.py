"""Compact binary serializer using json + gzip (stdlib only)."""

from __future__ import annotations

import gzip
import json
from typing import Any

from .serializer import Serializer, _AgentEncoder, _decode_hook


class BinarySerializer(Serializer):
    """MessagePack-style binary serializer using ``json`` + ``gzip``.

    Zero external dependencies — pure stdlib.
    """

    def pack(self, obj: Any) -> bytes:
        """Serialize *obj* to compressed bytes."""
        json_bytes = json.dumps(obj, cls=_AgentEncoder, registry=self._registry).encode("utf-8")
        return gzip.compress(json_bytes)

    def unpack(self, data: bytes) -> Any:
        """Decompress and deserialize *data* back to Python objects."""
        registry = self._registry

        def hook(d: dict) -> Any:
            return _decode_hook(registry, d)

        json_str = gzip.decompress(data).decode("utf-8")
        return json.loads(json_str, object_hook=hook)

    def size_reduction(self, obj: Any) -> float:
        """Return the compression ratio as a fraction (0–1).

        A value of 0.4 means the packed form is 40% smaller than raw JSON.
        """
        raw_bytes = json.dumps(obj, cls=_AgentEncoder, registry=self._registry).encode("utf-8")
        packed = self.pack(obj)
        raw_size = len(raw_bytes)
        if raw_size == 0:
            return 0.0
        return (raw_size - len(packed)) / raw_size
