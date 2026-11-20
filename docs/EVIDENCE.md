# Verification evidence — 2026-11-19

## Offline test execution

Command: `python -m unittest discover -s tests -v`

Result: **8/8 PASS**, executed locally against files whose Git blob hashes matched the repository at commit `ddb7d0b2b4dc80f2ff1ebd4fcf7804084a07a500`.

| File | Git blob SHA-1 |
|---|---|
| scripts/verify_token.py | 284cc07235db203676f8e38785f571099de804bd |
| tests/test_verify_token.py | f5646fe8a9fda2023d2e11c732ee55b8c87bf3af |
| token.json | 47f7e54dc3e56a2d6e098f79b91bb13729d9f04b |

Tests cover matching mock metadata, wrong chain, absent bytecode, symbol mismatch, block changes, malformed ABI, exact contract identity and preservation of unknown supply.

## Outstanding checks

Live RPC: **NOT VERIFIED** — network unavailable in the execution environment. PolygonScan and Blockscout data retrieval also failed. Independent contract audit, deployed source review, circulating supply and market data remain unverified. Offline tests do not prove live token security.

## Brand asset

Original approved JPEG inspected locally: 1254 × 1254 pixels, 654095 bytes. SHA-256: `7526a35ec5a9016c710be754ea55120a1462c54d36fb159cf5554508d5569109`.

Repository asset verified against the original SHA-256. No replacement artwork was generated.


## Enterprise assurance update — 2026-11-20

**Evidence class:** developer-run, synthetic/offline, GitHub-committed sources. No third-party security audit or live RPC verification.

- Verification source: `scripts/verify_token.py` in commit `d6e914528043b6873ced6b8d1b069ba5394c8317`.
- Additional tests: `tests/test_enterprise_assurance.py` in commit `e558add9e6f33ca815f7ba9eb1181462efed9ce6`; historical `tests/test_verify_token.py` retained.
- Re-fetched actual branch files, including the original `assets/NZT-DUBAI.jpg`, and ran `python3 -m unittest discover -s tests -v` in isolated Python 3.11 compute.
- **Observed result: 20 tests in 0.011 seconds, OK, exit code 0.** 12 new synthetic security/integrity tests plus 8 existing ones.
- Added checks cover pinned NZT contract and chain, HTTP endpoint restrictions, strict JSON-RPC response parsing, no redirect-following transport, bytecode SHA-256, stable block fields, optional two-provider agreement, and original brand SHA-256.
- **Not tested here:** live Polygon chain, two real RPC providers, source/ownership/permission review, transaction controls, market data, and independent QA.
- Manual GitHub Actions workflow is **available for opt-in execution** after merge; this entry does **not** claim it has run.

See [Enterprise assurance profile](ENTERPRISE_ASSURANCE.md) and [verification guide](VERIFICATION.md). A test passing with mocked responses does not make the real contract secure or independently verified.
