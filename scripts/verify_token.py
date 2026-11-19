"""Read-only NZT verification. No wallets, signing or transactions."""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]

def rpc(url, method, params):
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("HTTPS RPC endpoint required")
    req = Request(url, data=json.dumps({"jsonrpc": "2.0", "id": 1,
        "method": method, "params": params}).encode(), headers={
        "Content-Type": "application/json", "Accept": "application/json"})
    with urlopen(req, timeout=20) as response:
        data = json.loads(response.read(2_000_001))
    if data.get("id") != 1 or "error" in data or "result" not in data:
        raise ValueError("Invalid or failed RPC response")
    return data["result"]

def hexbytes(value):
    if not isinstance(value, str) or not re.fullmatch(r"0x(?:[0-9a-fA-F]{2})*", value):
        raise ValueError("Invalid hex bytes")
    return bytes.fromhex(value[2:])

def uint(value):
    raw = hexbytes(value)
    if len(raw) != 32:
        raise ValueError("Invalid ABI uint256")
    return int.from_bytes(raw, "big")

def abi_string(value):
    raw = hexbytes(value)
    if len(raw) < 64 or len(raw) % 32 or int.from_bytes(raw[:32], "big") != 32:
        raise ValueError("Invalid ABI string offset")
    size = int.from_bytes(raw[32:64], "big")
    if size > 4096 or len(raw) != 64 + ((size + 31) // 32) * 32:
        raise ValueError("Invalid ABI string length")
    if any(raw[64 + size:]):
        raise ValueError("Invalid ABI string padding")
    return raw[64:64 + size].decode("utf-8")

def quantity(value):
    if not isinstance(value, str) or not re.fullmatch(r"0x(?:0|[1-9a-fA-F][0-9a-fA-F]*)", value):
        raise ValueError("Invalid RPC quantity")
    return int(value, 16)

def verify(call, manifest):
    address = manifest["contract"]["address"]
    if not re.fullmatch(r"0x[0-9a-fA-F]{40}", address):
        raise ValueError("Invalid contract address")
    chain = quantity(call("eth_chainId", []))
    if chain != manifest["network"]["chain_id"]:
        raise ValueError("Unexpected chain")
    block = call("eth_getBlockByNumber", ["latest", False])
    number = quantity(block["number"])
    block_hash = block["hash"]
    if len(hexbytes(block_hash)) != 32:
        raise ValueError("Invalid block hash")
    tag = hex(number)
    code = hexbytes(call("eth_getCode", [address, tag]))
    if not code:
        raise ValueError("No deployed bytecode at address")
    def read(selector):
        return call("eth_call", [{"to": address, "data": selector}, tag])
    name = abi_string(read("0x06fdde03"))
    symbol = abi_string(read("0x95d89b41"))
    decimals = uint(read("0x313ce567"))
    supply = uint(read("0x18160ddd"))
    if symbol != manifest["symbol"] or decimals > 255:
        raise ValueError("Unexpected token symbol or decimals")
    if call("eth_getBlockByNumber", [tag, False])["hash"] != block_hash:
        raise ValueError("Block changed during observation")
    return {"chain_id": chain, "contract": address, "block_number": number,
            "block_hash": block_hash, "bytecode_bytes": len(code), "name": name,
            "symbol": symbol, "decimals": decimals,
            "total_supply_base_units": str(supply),
            "scope": "single RPC observation; not source verification or audit"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rpc", required=True, help="Trusted Polygon HTTPS RPC")
    args = parser.parse_args()
    try:
        manifest = json.loads((ROOT / "token.json").read_text())
        result = verify(lambda method, params: rpc(args.rpc, method, params), manifest)
        print(json.dumps(result, indent=2))
    except Exception:
        print("Verification failed: check endpoint, chain, contract and ABI.", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
