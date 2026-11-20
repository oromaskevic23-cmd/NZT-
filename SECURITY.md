# Security policy

## Scope
This repository contains public metadata, documentation and read-only tools. The deployed contract and third-party services require separate assessments.

Report suspected vulnerabilities privately through the repository owner's GitHub profile: https://github.com/oromaskevic23-cmd. Do not post exploit details, private keys or sensitive evidence in public issues.

## Controls
- Never request or store seed phrases or private keys.
- Validate chain ID and contract identity; do not trust token symbols alone.
- Fail closed on RPC errors, missing bytecode or malformed metadata.
- Require explicit owner approval and independent review before any future privileged transaction or contract change.
- Keep public and private IMPERIAL Core surfaces separate.

No completed independent smart-contract audit is claimed. Do not send funds based on this repository alone.


## Engineering release controls

- Proposed changes to `token.json`, verifier policy, RPC source, security documentation or original artwork require owner review. `.github/CODEOWNERS` routes review requests but **does not itself enforce branch protection**.
- No unreviewed change may substitute a different chain, contract, token symbol or image while continuing to claim the existing NZT identity.
- The optional GitHub Actions workflow is manual and offline-only. It does not receive wallet credentials or trusted RPC secrets. Do not trigger paid network services without explicit owner authorization.
- Reject redirects, malformed RPC envelopes, wrong chain IDs, absent contract bytecode and mismatched block fingerprints. Live RPC output must be treated as untrusted observation rather than proof of token legitimacy.
- For suspected contract/admin compromise: preserve read-only observations and source hashes, cease unsupported public claims, and seek an independent contract and authority review before publication or integration. This repository has no delegated power to freeze funds or alter the contract.
- Independent source-code audits, on-chain ownership controls, proxy/admin analysis and legal review remain **pending**, as documented in [ENTERPRISE_ASSURANCE.md](docs/ENTERPRISE_ASSURANCE.md).
