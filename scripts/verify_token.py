"""Read-only NZT verification; no wallet, signing, custody or transactions.
Owner: Alexander Romaskevich — Founder · Owner · CEO, IMPERIAL Core.
An offline-testable observer, not a smart-contract security audit.
"""
import argparse
import hashlib
import ipaddress
import os
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CHAIN_ID = 137
EXPECTED_CONTRACT = '0xFbD410Eb877ABd33eB637f93346351a178100AC3'
MAX_RPC_RESPONSE_BYTES = 2_000_000

class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def validate_rpc_url(url):
    if not isinstance(url, str) or not 0 < len(url) <= 2048:
        raise ValueError("Invalid RPC endpoint")
    try:
        parsed = urlsplit(url)
        host = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise ValueError("Invalid RPC endpoint") from exc
    if (parsed.scheme != "https" or not host or parsed.username is not None
            or parsed.password is not None or parsed.fragment
            or any(ch.isspace() for ch in url)):
        raise ValueError("Trusted HTTPS RPC endpoint without credentials or fragments required")
    if port is not None and not 1 <= port <= 65535:
        raise ValueError("Invalid RPC port")
    if host in ("localhost", "localhost.localdomain") or host.endswith((".localhost", ".local", ".internal", ".test", ".invalid")):
        raise ValueError("Non-public RPC host is prohibited")
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        ip = None
    if ip is not None:
        if not ip.is_global:
            raise ValueError("Non-public RPC host is prohibited")
    elif "." not in host or not re.fullmatch(r"[A-Za-z0-9.-]{3,253}", host):
        raise ValueError("Public DNS name required")
    # Network/DNS egress enforcement belongs to the caller's own boundary.
    # Do not expose this verifier as an untrusted public URL fetch service.
    return url


def _unique_pairs(pairs):
    data = {}
    for key, value in pairs:
        if key in data:
            raise ValueError("Duplicate JSON-RPC key")
        data[key] = value
    return data


def _no_nan(value):
    raise ValueError("Nonfinite JSON-RPC constant")


def rpc(url, method, params):
    validate_rpc_url(url)
    if not isinstance(method, str) or not re.fullmatch(r"eth_[A-Za-z0-9]{1,45}", method):
        raise ValueError("Invalid RPC method")
    if not isinstance(params, list):
        raise ValueError("Invalid RPC parameters")
    request = Request(url, data=json.dumps({"jsonrpc": "2.0", "id": 1,
        "method": method, "params": params}).encode(), headers={
        "Content-Type": "application/json", "Accept": "application/json"})
    opener = build_opener(_NoRedirect())
    with opener.open(request, timeout=15) as response:
        raw = response.read(MAX_RPC_RESPONSE_BYTES + 1)
    if len(raw) > MAX_RPC_RESPONSE_BYTES:
        raise ValueError("Oversized JSON-RPC response")
    data = json.loads(raw, object_pairs_hook=_unique_pairs, parse_constant=_no_nan)
    if (type(data) is not dict or data.get("jsonrpc") != "2.0" or
            type(data.get("id")) is not int or data["id"] != 1 or
            "error" in data or "result" not in data or data["result"] is None):
        raise ValueError("Invalid or failed JSON-RPC response")
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

def validate_manifest(manifest):
    if type(manifest) is not dict or manifest.get("schema_version") != 1 or manifest.get("project") != "NZT" or manifest.get("symbol") != "NZT":
        raise ValueError("Unexpected NZT manifest identity")
    network = manifest.get("network")
    contract = manifest.get("contract")
    if type(network) is not dict or type(network.get("chain_id")) is not int or network["chain_id"] != EXPECTED_CHAIN_ID:
        raise ValueError("Unexpected manifest chain")
    if type(contract) is not dict or contract.get("address") != EXPECTED_CONTRACT:
        raise ValueError("Unexpected manifest contract")
    return contract["address"]


def _block(call, tag):
    result = call("eth_getBlockByNumber", [tag, False])
    if type(result) is not dict:
        raise ValueError("Missing block header")
    number = quantity(result.get("number"))
    block_hash = result.get("hash")
    if len(hexbytes(block_hash)) != 32:
        raise ValueError("Invalid block hash")
    if tag != "latest" and hex(number) != tag:
        raise ValueError("Block changed during observation")
    return number, block_hash


def verify(call, manifest):
    address = validate_manifest(manifest)
    chain = quantity(call("eth_chainId", []))
    if chain != EXPECTED_CHAIN_ID:
        raise ValueError("Unexpected chain")
    number, block_hash = _block(call, "latest")
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
    ending_number, ending_hash = _block(call, tag)
    if (ending_number, ending_hash) != (number, block_hash):
        raise ValueError("Block changed during observation")
    return {"chain_id": chain, "contract": address, "block_number": number,
            "block_hash": block_hash, "bytecode_bytes": len(code),
            "bytecode_sha256": hashlib.sha256(code).hexdigest(),
            "name": name, "symbol": symbol, "decimals": decimals,
            "total_supply_base_units": str(supply),
            "scope": "single RPC observation; not source verification or audit"}


def verify_two_providers(primary, secondary, manifest):
    """Require identical metadata and bytecode at the SAME observed block."""
    a = verify(primary, manifest)
    b = verify(secondary, manifest)
    fields = ("chain_id", "contract", "block_number", "block_hash", "bytecode_sha256",
              "bytecode_bytes", "name", "symbol", "decimals", "total_supply_base_units")
    if any(a[field] != b[field] for field in fields):
        raise ValueError("Independent RPC observations disagree or block heights differ")
    a["scope"] = "two matching RPC observations of one block; not source verification or audit"
    a["provider_observations"] = 2
    return a


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rpc", default=os.environ.get("NZT_RPC_URL"),
                        help="Trusted Polygon HTTPS RPC (or NZT_RPC_URL)")
    parser.add_argument("--rpc-secondary", default=os.environ.get("NZT_RPC_SECONDARY_URL"),
                        help="Optional independent RPC (or NZT_RPC_SECONDARY_URL)")
    args = parser.parse_args()
    try:
        if not args.rpc:
            raise ValueError("Primary trusted RPC endpoint required")
        manifest = json.loads((ROOT / "token.json").read_text())
        primary = lambda method, params: rpc(args.rpc, method, params)
        if args.rpc_secondary:
            secondary = lambda method, params: rpc(args.rpc_secondary, method, params)
            result = verify_two_providers(primary, secondary, manifest)
        else:
            result = verify(primary, manifest)
        print(json.dumps(result, indent=2))
    except Exception:
        print("Verification failed: check endpoint, chain, contract, block, ABI and provider agreement.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
