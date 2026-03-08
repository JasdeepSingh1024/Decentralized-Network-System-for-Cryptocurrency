"""
Transaction model for the cryptocurrency: sender, receiver, amount, tx_id.
"""
import hashlib
import json
import time
import uuid
from typing import Any


def create_transaction(sender: str, receiver: str, amount: float, tx_id: str | None = None) -> dict[str, Any]:
    """Create a transaction dict with optional id; otherwise generate one."""
    tx_id = tx_id or str(uuid.uuid4())
    tx = {
        "id": tx_id,
        "sender": sender,
        "receiver": receiver,
        "amount": amount,
        "timestamp": time.time(),
    }
    return tx


def transaction_hash(tx: dict[str, Any]) -> str:
    """SHA256 hash of transaction for integrity."""
    data = json.dumps(
        {"id": tx["id"], "sender": tx["sender"], "receiver": tx["receiver"], "amount": tx["amount"], "timestamp": tx["timestamp"]},
        sort_keys=True,
    )
    return hashlib.sha256(data.encode()).hexdigest()


