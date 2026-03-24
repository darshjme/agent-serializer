# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅ Active  |

## Reporting a Vulnerability

**Do not open a public GitHub Issue for security vulnerabilities.**

Please report security issues privately via email to the maintainer or by using GitHub's
[private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability).

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

You will receive a response within **48 hours**.

## Security Considerations

- `agent-serializer` uses Python's built-in `json` module. It does **not** use `pickle` or
  `eval`, so deserialization of untrusted data carries no code-execution risk beyond standard
  JSON parsing.
- The `BinarySerializer` uses `gzip` — decompression of untrusted data should be size-limited
  by the caller to prevent zip-bomb attacks.
- Custom `decoder` callables registered via `Serializer.register()` run with the privileges of
  the calling process — validate custom decoder inputs.
