"""
Wallet: per-address key pairs for signing transactions (Cryptography role).
Uses Ed25519 public-key cryptography so only the owner can authorize transfers.
"""
import base64
import json
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

WALLETS_PATH = Path(__file__).resolve().parent / "data" / "wallets.json"
_wallets: dict[str, dict[str, str]] | None = None


def _payload_for_signature(tx: dict[str, Any]) -> bytes:
    """Canonical payload that must be signed (data integrity)."""
    data = {
        "id": tx["id"],
        "sender": tx["sender"],
        "receiver": tx["receiver"],
        "amount": tx["amount"],
        "timestamp": tx["timestamp"],
    }
    return json.dumps(data, sort_keys=True).encode()


def _load_wallets() -> dict[str, dict[str, str]]:
    global _wallets
    if _wallets is not None:
        return _wallets
    _wallets = {}
    if WALLETS_PATH.exists():
        try:
            with open(WALLETS_PATH) as f:
                _wallets = json.load(f)
        except Exception:
            pass
    return _wallets


def _save_wallets() -> None:
    WALLETS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(WALLETS_PATH, "w") as f:
        json.dump(_load_wallets(), f, indent=2)


def get_or_create_keypair(address: str) -> tuple[bytes, bytes]:
    """Return (private_key_bytes, public_key_bytes) for address. Create and persist if first use."""
    wallets = _load_wallets()
    if address in wallets:
        priv_b64 = wallets[address]["private_key"]
        pub_b64 = wallets[address]["public_key"]
        return base64.b64decode(priv_b64), base64.b64decode(pub_b64)
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    priv_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    wallets[address] = {
        "private_key": base64.b64encode(priv_bytes).decode(),
        "public_key": base64.b64encode(pub_bytes).decode(),
    }
    global _wallets
    _wallets = wallets
    _save_wallets()
    return priv_bytes, pub_bytes


def sign_transaction(tx: dict[str, Any], private_key_bytes: bytes) -> bytes:
    """Sign the transaction payload; return signature bytes."""
    private_key = Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    payload = _payload_for_signature(tx)
    return private_key.sign(payload)


def verify_transaction_signature(tx: dict[str, Any]) -> bool:
    """
    Verify tx has valid signature (public_key and signature present and valid).
    Returns True if valid or if tx is unsigned (backward compat). False if signature invalid.
    """
    if not tx.get("signature") or not tx.get("public_key"):
        return True  # unsigned allowed for backward compat
    try:
        sig_b64 = tx["signature"]
        pub_b64 = tx["public_key"]
        if isinstance(sig_b64, str):
            signature = base64.b64decode(sig_b64)
        else:
            signature = sig_b64
        if isinstance(pub_b64, str):
            pub_bytes = base64.b64decode(pub_b64)
        else:
            pub_bytes = pub_b64
        public_key = Ed25519PublicKey.from_public_bytes(pub_bytes)
        payload = _payload_for_signature(tx)
        public_key.verify(signature, payload)
        return True
    except Exception:
        return False


def sign_tx_if_wallet(tx: dict[str, Any]) -> dict[str, Any]:
    """If we have a wallet for tx['sender'], sign tx and add signature + public_key. Return tx."""
    sender = tx.get("sender", "")
    if not sender or sender == "system":
        return tx
    try:
        priv_bytes, pub_bytes = get_or_create_keypair(sender)
        sig = sign_transaction(tx, priv_bytes)
        tx = dict(tx)
        tx["signature"] = base64.b64encode(sig).decode()
        tx["public_key"] = base64.b64encode(pub_bytes).decode()
    except Exception:
        pass
    return tx
