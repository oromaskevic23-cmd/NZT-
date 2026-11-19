# Verification guide

Requirements: Python 3.10+; no third-party dependencies.

Run offline tests:
```sh
python -m unittest discover -s tests -v
```

Run a read-only chain observation with a trusted HTTPS Polygon RPC:
```sh
python scripts/verify_token.py --rpc https://YOUR_POLYGON_RPC
```

The verifier checks the chain ID, bytecode, ERC-20 metadata and exact total supply at one block number, then rechecks its block hash. A second independent provider and verified source review are required before publishing authoritative tokenomics. Mock tests use synthetic values and do not constitute live evidence. The script never signs or broadcasts transactions. It does not establish contract ownership, circulating supply, liquidity, upgradeability or security.
