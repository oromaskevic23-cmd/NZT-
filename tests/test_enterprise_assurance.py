"""Synthetic security and read-only assurance tests; no real RPC is called."""
import copy
import hashlib
import json
import unittest
from unittest.mock import patch
from pathlib import Path
from scripts.verify_token import (
    EXPECTED_CHAIN_ID, EXPECTED_CONTRACT, MAX_RPC_RESPONSE_BYTES,
    rpc, validate_rpc_url, validate_manifest, verify, verify_two_providers,
)
from test_verify_token import HASH, MANIFEST, mock, word


class StubHTTPResponse:
    def __init__(self, body):
        self.body = body
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        pass
    def read(self, count):
        return self.body[:count]


class StubOpener:
    def __init__(self, body):
        self.body = body
    def open(self, *args, **kwargs):
        return StubHTTPResponse(self.body)


class EnterpriseAssuranceTests(unittest.TestCase):
    def test_manifest_identity_is_pinned(self):
        self.assertEqual(validate_manifest(MANIFEST), EXPECTED_CONTRACT)
        for field, replacement in (
                ("project", "FAKE"), ("symbol", "FAKE"), ("schema_version", 2)):
            with self.subTest(field=field):
                altered = copy.deepcopy(MANIFEST)
                altered[field] = replacement
                with self.assertRaises(ValueError):
                    verify(lambda m, p: self.fail("RPC called before manifest check"), altered)

    def test_manifest_rejects_chain_and_contract_rebinding(self):
        for path, replacement in (("chain_id", 1), ("chain_id", True),
                                  ("address", "0x" + "01" * 20)):
            altered = copy.deepcopy(MANIFEST)
            altered["network" if path == "chain_id" else "contract"][path] = replacement
            with self.subTest(path=path), self.assertRaises(ValueError):
                verify(lambda m, p: self.fail("Unsafe RPC called"), altered)

    def test_rpc_url_validation_blocks_local_and_insecure_endpoints(self):
        for url in ("http://rpc.example.com", "https://127.0.0.1",
                    "https://10.1.0.1", "https://192.168.1.10",
                    "https://localhost", "https://rpc.local", "https://rpc.internal",
                    "https://user:password@rpc.example.com", "https://rpc.example.com/#fragment",
                    "file:///etc/passwd", "https://[::1]", "https://rpc.example.com:99999"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_rpc_url(url)
        self.assertEqual(validate_rpc_url("https://polygon-rpc.example.org/secret"),
                         "https://polygon-rpc.example.org/secret")

    def test_rpc_refuses_nonstandard_envelope_and_duplicate_keys(self):
        payloads = (
            b'{"jsonrpc":"2.0","id":true,"result":"0x89"}',
            b'{"jsonrpc":"2.0","id":1,"result":null}',
            b'{"jsonrpc":"2.0","id":1,"result":"0x89","result":"0x01"}',
            b'{"jsonrpc":"2.0","id":1,"result":NaN}',
            b'{"jsonrpc":"2.0","id":1,"error":{"code":-1},"result":"0x89"}',
            b'{"jsonrpc":"1.0","id":1,"result":"0x89"}',
            b'["not a JSON-RPC envelope"]',
            b'x' * (MAX_RPC_RESPONSE_BYTES + 1),
        )
        for body in payloads:
            with self.subTest(body=body[:100]):
                with patch("scripts.verify_token.build_opener",return_value=StubOpener(body)):
                    with self.assertRaises((ValueError, json.JSONDecodeError)):
                        rpc("https://rpc.example.org", "eth_chainId", [])

    def test_rpc_never_uses_redirect_following_opener(self):
        with patch("scripts.verify_token.build_opener", return_value=StubOpener(
                b'{"jsonrpc":"2.0","id":1,"result":"0x89"}')) as build:
            self.assertEqual(rpc("https://rpc.example.org","eth_chainId", []), "0x89")
            self.assertEqual(len(build.call_args.args), 1)
            self.assertEqual(build.call_args.args[0].__class__.__name__, "_NoRedirect")

    def test_bytecode_hash_is_recorded(self):
        observed = verify(mock, MANIFEST)
        self.assertEqual(observed["bytecode_sha256"], hashlib.sha256(b"\x60\x00").hexdigest())
        self.assertEqual(observed["chain_id"], EXPECTED_CHAIN_ID)

    def test_block_number_must_be_stable(self):
        def changed(method, params):
            if method == "eth_getBlockByNumber" and params[0] == "0x10":
                return {"number": "0x11", "hash": HASH}
            return mock(method, params)
        with self.assertRaises(ValueError):
            verify(changed, MANIFEST)

    def test_two_providers_same_block_pass(self):
        evidence = verify_two_providers(mock, mock, MANIFEST)
        self.assertEqual(evidence["provider_observations"], 2)
        self.assertEqual(evidence["block_number"], 16)

    def test_two_providers_different_code_or_supply_fail(self):
        def different_code(method, params):
            return "0x6001" if method == "eth_getCode" else mock(method, params)
        def different_supply(method, params):
            if method == "eth_call" and params[0]["data"] == "0x18160ddd":
                return "0x" + word(5).hex()
            return mock(method, params)
        for provider in (different_code, different_supply):
            with self.assertRaises(ValueError):
                verify_two_providers(mock, provider, MANIFEST)

    def test_cli_rejects_duplicate_rpc_endpoints_before_network(self):
        from io import StringIO
        from scripts.verify_token import main
        with patch("sys.argv", ["verify_token.py", "--rpc", "https://rpc.example.org",
                                "--rpc-secondary", "https://rpc.example.org"]):
            with patch("scripts.verify_token.rpc") as network:
                with patch("sys.stderr", new_callable=StringIO):
                    self.assertEqual(main(), 1)
                    network.assert_not_called()

    def test_completely_unknown_supply_remains_unverified(self):
        self.assertIsNone(MANIFEST["on_chain"]["total_supply_base_units"])
        self.assertEqual(MANIFEST["security"]["independent_audit"], "not_evidenced")
        self.assertIsNone(MANIFEST["market"]["price"])

    def test_brand_original_integrity(self):
        asset=Path(__file__).resolve().parents[1] / "assets/NZT-DUBAI.jpg"
        self.assertEqual(hashlib.sha256(asset.read_bytes()).hexdigest(),
                         "7526a35ec5a9016c710be754ea55120a1462c54d36fb159cf5554508d5569109")


if __name__ == "__main__":
    unittest.main()
