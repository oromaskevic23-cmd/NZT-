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

Repository upload of this binary is pending. No replacement artwork was generated.
