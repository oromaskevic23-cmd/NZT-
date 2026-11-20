# NZT — Enterprise Assurance Profile (engineering baseline)

**As of:** 20 November 2026  
**Owner / final architectural authority:** Alexander Romaskevich · Founder · Owner · CEO, IMPERIAL Core  
**Scope:** public repository, read-only Polygon metadata observation, offline tests and release governance  
**Classification:** engineering control baseline. **NOT** an independently audited, production-certified or on-chain-verified token service.

## 1. Architecture and boundaries

NZT is a separate digital-asset initiative within the **CRYPTO IMPERIAL Ecosystem Boundary**. No token holder receives access to IMPERIAL Core, HANTER, VELION, federated orchestrators, Nano Core Agents, AI Passport, Guardian Core, Approval Gateway or Audit Ledger.

This repository does **not** contain or request wallet keys, seed phrases, signing, custody, transaction execution, payment processing, agent privileges or contract-admin access.

The *declared* Polygon PoS identity is chain ID **137**, contract **`0xFbD410Eb877ABd33eB637f93346351a178100AC3`**, symbol **NZT**. These are pinned to the read-only verifier to prevent accidental rebranding/rebinding during observations. They remain **owner-declared**, and a live independent on-chain match has not been established here.

## 2. Implemented defensive controls

| Area | Verified implementation | Evidence boundary |
| --- | --- | --- |
| Manifest admission | Schema version, project, symbol, chain ID and precise contract address must match pinned NZT values before any RPC call | Local offline tests only |
| RPC transport | HTTPS only, no URL-embedded usernames/passwords, redirects refused, obviously local/private endpoint literals rejected, 15-second HTTP timeout | This is a local CLI; DNS rebinding, outbound-firewall policy and hostname ownership require caller-side controls |
| RPC response | 2,000,000-byte maximum, strict JSON-RPC 2.0 envelope, integer ID, duplicate-key/nonfinite rejection and fail-closed errors | Mock transport tests; no live provider attestation |
| Block consistency | Record observed block number/hash; recheck numbered block after collecting code and token fields | Latest block may not be finalized |
| Code identity | Record SHA-256 of observed bytecode, plus length, ERC-20 name, symbol, decimals and totalSupply | Not an assessment of permissions, verified source or circulating supply |
| Two-provider agreement | Optional second trusted provider must return exactly matching block, code fingerprint and token metadata | Two independent provider connections are **not claimed to have been executed** |
| Original brand | SHA-256 check of approved `assets/NZT-DUBAI.jpg` | Artwork authenticity within repo only, not external endorsement |

Use `python -m unittest discover -s tests -v` from the root. An optional **manual-only** GitHub Actions workflow may repeat offline tests; it is not an automatic background monitor.

## 3. Evidence and truth constraints

**Observed developer-run checkpoint:** 19 tests passed on Python 3.11, exit code 0, in an isolated execution environment against GitHub-committed source from branch `feat/enterprise-assurance-20261120`, including the original unchanged JPEG. Tests are local with mocked RPC observations. A successful test does not prove the real contract's deployment, token name, decimals, supply, ownership, audit or operational readiness.

The original **8/8 PASS** reference is historical and retained in [EVIDENCE.md](EVIDENCE.md). Distinguish a source commit, a local developer test, a GitHub workflow result and independent third-party assessment.

The live verifier produces a single-provider observation or, when explicitly requested, a two-provider matching observation. **Neither is a verified-source comparison or a smart-contract audit.** Do not automatically amend `token.json` with observations; review and approve published claims.

## 4. Threat model

- **Wrong token or chain:** pinned chain/address/symbol and fail-closed checks.
- **Malformed RPC/ABI or untrusted response:** strict parsing, limits, typed fields and block-hash comparison.
- **Compromised RPC:** optional independent two-provider comparison, with explicit provider diversity required; it cannot protect against collusion or a shared compromised upstream.
- **Secret leakage:** read-only tooling, no wallets; prefer environment variables to putting RPC credentials in shell history; do not commit `.env` or production observations containing sensitive endpoint metadata.
- **Privileged contract attack or proxy upgrade:** **NOT ASSESSED**; requires verified source, admin/ownership, proxy implementation and role analysis at a pinned block.
- **Legal/commercial claims:** **NOT EVIDENCED**; no listing, liquidity, market price, partnership with Dubai authorities, exchange endorsement or guaranteed investment return is asserted.

## 5. Release gates (all required before claims of stronger assurance)

- [x] Public identity and explicit verification status documented.
- [x] Offline tests, rejection cases and original-brand integrity check implemented and run.
- [ ] Trusted live RPC observation recorded with block/hash and timestamp.
- [ ] Two independent trusted RPC observations at the same block reviewed; verify provider separation.
- [ ] Source verification, deployed bytecode comparison, compiler/settings, proxy detection and implementation review completed.
- [ ] Privileged roles, owner, mint/burn, pause, freeze, upgradeability and supply methodology independently reviewed.
- [ ] Secret and dependency supply-chain checks, reproducible CI and governance approvals completed.
- [ ] Independent security assessment and legal/compliance review documented.
- [ ] Owner approves any public release, marketing statements or integration with other IMPERIAL Core components.

**Decision: NOT RELEASE-CERTIFIED.** No permission is implied to operate a token treasury or execute transactions.

## 6. Incident and change control

1. Stop publication of unsupported claims and suspend any external integration under the applicable Approval Gateway.
2. Preserve reproducible read-only evidence (network/chain, full contract, pinned block/hash, code hash, source revision, UTC observation time, verifier version); redact endpoint secrets.
3. File a private security report via [SECURITY.md](../SECURITY.md), identify scope and affected artifacts.
4. An authorized owner reviews remediation, independent test results, release gates and any recovery action. No hidden automatic owner permission, token rebranding or wallet intervention.
5. Record the approval and release decision; keep prior evidence append-only whenever practical.

**Architecture → Implementation → Verification → Evidence → Release.**
