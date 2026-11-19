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
