# Changelog

All notable changes to **agent-serializer** are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [1.0.0] — 2026-03-24

### Added
- `Serializer` — base serializer with type registry handling `datetime`, `date`, `time`, `Enum`, `dataclass`, `set`, `frozenset`, `bytes`
- `TypedSerializer` — schema-aware serializer with `validate()` and dataclass coercion
- `BinarySerializer` — compact binary format via `json` + `gzip` (stdlib only); `size_reduction()` metric
- `@serialized` decorator — automatic serialize/deserialize of function args and return values
- Custom type registration via `Serializer.register(type_, encoder, decoder)`
- Zero external dependencies (stdlib only)
- 27 pytest tests — 100% pass rate
