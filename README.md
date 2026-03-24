# agent-serializer

> Production-grade serialization and deserialization for agent data — zero external dependencies.

Agents pass complex data between steps: tool results, structured outputs, intermediate states.
Without consistent serialization you get encoding errors, type loss (`datetime` → `str`), and
data corruption across boundaries. **agent-serializer** fixes that.

---

## Installation

```bash
pip install agent-serializer
```

Requires **Python ≥ 3.10**. Zero runtime dependencies (stdlib only: `json`, `gzip`, `dataclasses`).

---

## Quick Start — Agent Data Serialization

```python
import dataclasses
from datetime import datetime
from enum import Enum

from agent_serializer import Serializer, TypedSerializer, BinarySerializer, serialized

# ── 1. Base Serializer ────────────────────────────────────────────────────────

s = Serializer()

# Handles datetime, Enum, dataclass, set, bytes out of the box
payload = {
    "timestamp": datetime(2025, 6, 1, 12, 0),
    "tags": {"urgent", "llm"},
    "score": 0.97,
}

json_str = s.dumps(payload)
restored = s.loads(json_str)

assert isinstance(restored["timestamp"], datetime)  # ✓ type preserved
assert isinstance(restored["tags"], set)            # ✓ set preserved

# ── 2. Custom type registration ───────────────────────────────────────────────

class Vector:
    def __init__(self, values: list[float]):
        self.values = values

s.register(
    Vector,
    encoder=lambda v: v.values,
    decoder=lambda d: Vector(d),
)

vec = Vector([0.1, 0.2, 0.9])
result = s.loads(s.dumps(vec))
assert result.values == [0.1, 0.2, 0.9]

# ── 3. TypedSerializer — schema validation ────────────────────────────────────

@dataclasses.dataclass
class ToolResult:
    name: str
    output: str
    score: float = 0.0

ts = TypedSerializer(ToolResult)

data = ToolResult(name="web_search", output="The capital of France is Paris.", score=0.99)
raw = ts.dumps(data)
result = ts.loads(raw)  # returns a ToolResult instance, validated

assert isinstance(result, ToolResult)
assert ts.validate({"name": "x", "output": "y"})       # ✓
assert not ts.validate({"output": "missing name field"})  # ✗

# ── 4. BinarySerializer — compact binary format ───────────────────────────────

bs = BinarySerializer()

large_state = {"history": ["step"] * 1000, "ts": datetime.now()}
packed = bs.pack(large_state)          # bytes via json + gzip
unpacked = bs.unpack(packed)           # fully restored, types intact

ratio = bs.size_reduction(large_state)
print(f"Compressed {ratio:.0%} smaller than raw JSON")

# ── 5. @serialized decorator ──────────────────────────────────────────────────

class Status(Enum):
    DONE = "done"
    PENDING = "pending"

@serialized(s)
def agent_step(tool_result: dict) -> dict:
    """Agent step — args decoded, return value encoded automatically."""
    return {
        "status": Status.DONE,
        "processed_at": datetime.now(),
        "result": tool_result,
    }

output = agent_step({"score": 0.8})
# Return value is a clean Python dict with proper types
assert isinstance(output["processed_at"], datetime)
assert output["status"] == Status.DONE
```

---

## API Reference

### `Serializer`

| Method | Signature | Description |
|---|---|---|
| `dumps` | `(obj: any) → str` | Serialize to JSON string |
| `loads` | `(data: str) → any` | Deserialize from JSON string |
| `encode` | `(obj: any) → dict` | Encode to dict (embed in larger structures) |
| `register` | `(type_, encoder, decoder)` | Register custom type |

### `TypedSerializer(schema)`

Inherits `Serializer`. Adds:

| Method | Description |
|---|---|
| `loads(data)` | Deserialize + coerce to schema type |
| `validate(data)` | Validate dict against schema |

### `BinarySerializer`

Inherits `Serializer`. Adds:

| Method | Description |
|---|---|
| `pack(obj)` | Serialize to compressed bytes |
| `unpack(data)` | Decompress + deserialize |
| `size_reduction(obj)` | Compression ratio vs raw JSON (0–1) |

### `@serialized(serializer)`

Decorator. Wraps a function so that:
- Incoming `dict` arguments are decoded (type tokens resolved)
- Return value is round-tripped (type-safe output every time)

---

## Supported Types (Built-in)

| Type | Preserved |
|---|---|
| `datetime` / `date` / `time` | ✓ |
| `Enum` subclasses | ✓ |
| `@dataclass` instances | ✓ |
| `set` / `frozenset` | ✓ |
| `bytes` | ✓ |
| Any JSON-native type | ✓ |
| Custom types via `register()` | ✓ |

---

## License

MIT
