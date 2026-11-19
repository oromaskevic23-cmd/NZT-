import json
import unittest
from pathlib import Path
from scripts.verify_token import verify, abi_string, uint, quantity

MANIFEST = json.loads((Path(__file__).resolve().parents[1] / "token.json").read_text())
HASH = "0x" + "ab" * 32

def word(n):
    return n.to_bytes(32, "big")

def text(s):
    data = s.encode()
    return "0x" + (word(32) + word(len(data)) + data + bytes((-len(data)) % 32)).hex()

def mock(method, params):
    if method == "eth_chainId": return "0x89"
    if method == "eth_getBlockByNumber": return {"number": "0x10", "hash": HASH}
    if method == "eth_getCode": return "0x6000"
    if method == "eth_call":
        assert params[1] == "0x10"
        return {"0x06fdde03": text("NZT"), "0x95d89b41": text("NZT"),
                "0x313ce567": "0x" + word(18).hex(),
                "0x18160ddd": "0x" + word(10**27).hex()}[params[0]["data"]]
    raise AssertionError(method)

class VerificationTests(unittest.TestCase):
    def test_observation(self):
        out = verify(mock, MANIFEST)
        self.assertEqual(out["total_supply_base_units"], str(10**27))
        self.assertEqual(out["block_hash"], HASH)
    def test_wrong_chain(self):
        with self.assertRaises(ValueError):
            verify(lambda m, p: "0x1" if m == "eth_chainId" else mock(m,p), MANIFEST)
    def test_no_bytecode(self):
        with self.assertRaises(ValueError):
            verify(lambda m, p: "0x" if m == "eth_getCode" else mock(m,p), MANIFEST)
    def test_symbol_mismatch(self):
        with self.assertRaises(ValueError):
            verify(lambda m,p: text("FAKE") if m == "eth_call" and p[0]["data"] == "0x95d89b41" else mock(m,p), MANIFEST)
    def test_reorg(self):
        with self.assertRaises(ValueError):
            verify(lambda m,p: {"number":"0x10","hash":"0x"+"cd"*32} if m == "eth_getBlockByNumber" and p[0] == "0x10" else mock(m,p), MANIFEST)
    def test_malformed_abi(self):
        for value in ["0x", "0x12", "0x" + (word(32)+word(100)).hex()]:
            with self.assertRaises(ValueError): abi_string(value)
        with self.assertRaises(ValueError): uint("0x01")
        with self.assertRaises(ValueError): quantity("0x01")
    def test_exact_address(self):
        self.assertEqual(MANIFEST["contract"]["address"], "0xFbD410Eb877ABd33eB637f93346351a178100AC3")
    def test_no_unverified_supply(self):
        self.assertIsNone(MANIFEST["on_chain"]["total_supply_base_units"])

if __name__ == "__main__":
    unittest.main()
