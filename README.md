<div align="center">
<img src="assets/hero.svg" width="100%"/>
</div>

# agent-serializer

**Production-grade serialization and deserialization for agent data**

[![PyPI version](https://img.shields.io/pypi/v/agent-serializer?color=yellow&style=flat-square)](https://pypi.org/project/agent-serializer/) [![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square)](https://python.org) [![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE) [![Tests](https://img.shields.io/badge/tests-passing-brightgreen?style=flat-square)](#)

---

## The Problem

Without a shared serializer, agent messages use ad-hoc JSON that breaks on floats, datetimes, and nested objects. Version mismatches between sender and receiver produce silent data corruption that only surfaces in production.

## Installation

```bash
pip install agent-serializer
```

## Quick Start

```python
from agent_serializer import BinarySerializer, _AgentEncoder

# Initialise
instance = BinarySerializer(name="my_agent")

# Use
# see API reference below
print(result)
```

## API Reference

### `BinarySerializer`

```python
class BinarySerializer(Serializer):
    """MessagePack-style binary serializer using ``json`` + ``gzip``.
    def pack(self, obj: Any) -> bytes:
        """Serialize *obj* to compressed bytes."""
    def unpack(self, data: bytes) -> Any:
        """Decompress and deserialize *data* back to Python objects."""
    def size_reduction(self, obj: Any) -> float:
        """Return the compression ratio as a fraction (0–1).
```

### `_AgentEncoder`

```python
class _AgentEncoder(json.JSONEncoder):
    """JSON encoder that handles agent-specific types."""
    def __init__(self, *args, registry: dict | None = None, **kwargs):
    def default(self, obj: Any) -> Any:  # noqa: ANN401
def _decode_hook(registry: dict, obj: dict) -> Any:  # noqa: ANN401
        """Object hook for J
```


## How It Works

### Flow

```mermaid
flowchart LR
    A[User Code] -->|create| B[BinarySerializer]
    B -->|configure| C[_AgentEncoder]
    C -->|execute| D{Success?}
    D -->|yes| E[Return Result]
    D -->|no| F[Error Handler]
    F --> G[Fallback / Retry]
    G --> C
```

### Sequence

```mermaid
sequenceDiagram
    participant App
    participant BinarySerializer
    participant _AgentEncoder

    App->>+BinarySerializer: initialise()
    BinarySerializer->>+_AgentEncoder: configure()
    _AgentEncoder-->>-BinarySerializer: ready
    App->>+BinarySerializer: run(context)
    BinarySerializer->>+_AgentEncoder: execute(context)
    _AgentEncoder-->>-BinarySerializer: result
    BinarySerializer-->>-App: WorkflowResult
```

## Philosophy

> Brahman is ineffable, yet the Vedas serialized the cosmos into *rk, saman, yajus* — structure enables transmission.

---

*Part of the [arsenal](https://github.com/darshjme/arsenal) — production stack for LLM agents.*

*Built by [Darshankumar Joshi](https://github.com/darshjme), Gujarat, India.*
