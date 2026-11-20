# NZT verification guide

**Scope:** public read-only verification tooling. No signing, wallets, transfers, transactions or production token-security certification.

## Local requirements

- Python 3.10 or newer; no third-party Python packages.
- Only the pinned public NZT manifest from `token.json`.
- A trusted **HTTPS** Polygon PoS RPC endpoint for optional live observation; the project does not provide credentials.

Run deterministic offline regression:

```sh
python -m unittest discover -s tests -v
```

These tests use mocked RPC responses and the original approved NZT image. They make **no live blockchain calls**. The enterprise assurance test suite includes malformed JSON-RPC envelopes, redirect prevention, wrong chain/address, bytecode-hash disagreement, and fail-closed behavior.

## Optional single-provider read-only observation

Prefer an environment variable to passing a secret-bearing RPC URL on the command line:

```sh
export NZT_RPC_URL='https://YOUR_TRUSTED_POLYGON_RPC_ENDPOINT'
python scripts/verify_token.py
```

Do not check credentials, RPC API keys, .env files or internal endpoints into Git. A public endpoint with no token also works via `--rpc https://YOUR_TRUSTED_POLYGON_RPC_ENDPOINT`.

The verifier confirms the RPC-reported chain ID, requires code at the pinned address, reads standard ERC-20 metadata at a selected block, computes a bytecode SHA-256 and verifies the block hash again. The returned values represent **one RPC observation**, not contract source attestation.

## Stronger optional two-provider comparison

```sh
export NZT_RPC_URL='https://YOUR_FIRST_TRUSTED_POLYGON_RPC'
export NZT_RPC_SECONDARY_URL='https://YOUR_SECOND_INDEPENDENT_POLYGON_RPC'
python scripts/verify_token.py
```

This mode demands identical block number, block hash, code fingerprint, name, symbol, decimals and total supply. If providers are at different block heights or disagree, it **fails closed**. Use truly independent operators and capture the observation time separately. Both endpoints are supplied by the operator: this repository does not provision or pay for them.

A successful two-provider match is **not** a guarantee against compromised providers, reorganization, malicious contracts, admin roles or network attacks. The selected `latest` block may not be finalized.

## Publishing evidence: mandatory review

Record and verify the chain ID, full contract address, UTC time, block number/hash, SHA-256 of deployed code, source revision and which provider operators were used (without secrets). Independently check verified source, proxy implementation, admin controls, supply, decimals and legal claims before using the result in a public statement.

Do **not** write observed supply into `token.json` automatically. Total supply does not equal circulating supply. Do not publish prices, liquidity or exchange status without fresh independent market evidence.

Read [Enterprise Assurance Profile](ENTERPRISE_ASSURANCE.md), [Risk disclosure](RISK.md) and [Verification evidence](EVIDENCE.md).
