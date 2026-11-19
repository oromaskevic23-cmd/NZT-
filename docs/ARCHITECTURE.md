# NZT architecture and trust boundaries

## Public surface
The public repository exposes token metadata, documentation and read-only verification. It must never contain seed phrases, private keys, API credentials, wallet access or internal infrastructure details.

## Proposed integration architecture
1. Public token identity manifest: chain ID + contract address.
2. Read-only blockchain evidence: bytecode, metadata and observed supply at a recorded block.
3. External application adapters: untrusted inputs, least privilege and explicit transaction intent.
4. Governance: any future privileged integration requires separate approval, audit and revocation mechanisms.

## CRYPTO IMPERIAL Ecosystem Boundary
NZT is separate from IMPERIAL Core's private execution plane. Holding NZT must not confer agent identity, execution authority or access to protected systems. AI Passport, Guardian Core, Approval Gateway and Audit Ledger remain separate architectural controls. These integrations are design requirements, not claims of deployment.

## Release gates
Contract identity and chain verified; source and privilege review; reproducible evidence; independent security assessment; approved disclosures. Do not represent a gate as passed without evidence.
