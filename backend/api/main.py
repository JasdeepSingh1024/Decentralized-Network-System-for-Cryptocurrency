"""
FastAPI REST API for the cryptocurrency blockchain (Lab 4 style).
Endpoints: chain, blocks, transactions, balance, mine, nodes.
"""
import json
from contextlib import asynccontextmanager

import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from state import get_blockchain
from nodes import get_nodes, register_node as register_peer, sync_chain_from_peers

# Optional: start RabbitMQ consumer in background
def _start_background_consumers():
    try:
        from rabbitmq_consumer import start_consumer_background
        start_consumer_background()
    except Exception as e:
        print(f"RabbitMQ consumer not started: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _start_background_consumers()
    yield


app = FastAPI(title="COE892 Cryptocurrency API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# --- Pydantic models ---
class TransactionCreate(BaseModel):
    sender: str
    receiver: str
    amount: float


class MineRequest(BaseModel):
    miner_address: str


class NodeRegister(BaseModel):
    node_url: str


class DemoVerifyTransaction(BaseModel):
    """For security demo: transaction with signature and public_key to verify (no add to chain)."""
    transaction: dict  # id, sender, receiver, amount, timestamp, signature, public_key


# --- Routes ---
FRONTEND_PATH = Path(__file__).resolve().parent.parent.parent / "frontend"
INDEX_PATH = FRONTEND_PATH / "index.html"

@app.get("/")
async def root():
    if INDEX_PATH.exists():
        return RedirectResponse(url="/app")
    return {"service": "COE892 Decentralized Cryptocurrency", "docs": "/docs"}


@app.get("/chain")
async def get_chain():
    """Return full chain (blocks with transactions)."""
    chain = get_blockchain()
    return {
        "chain": [b.to_dict() for b in chain.chain],
        "length": len(chain.chain),
    }


@app.get("/blocks/{index}")
async def get_block(index: int):
    """Return a single block by index."""
    chain = get_blockchain()
    if index < 0 or index >= len(chain.chain):
        raise HTTPException(status_code=404, detail="Block not found")
    return chain.chain[index].to_dict()


@app.get("/transactions/pending")
async def get_pending_transactions():
    """Return pending transactions (not yet in a block)."""
    chain = get_blockchain()
    return {"pending": chain.pending_transactions}


@app.post("/transactions")
async def create_transaction(tx: TransactionCreate):
    """Submit a new transaction. Also published to RabbitMQ for other nodes."""
    if tx.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    chain = get_blockchain()
    balance = chain.get_balance(tx.sender, include_pending=True)  # reserve pending sends to prevent double-spend
    if balance < tx.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    try:
        created = chain.add_transaction(tx.sender, tx.receiver, tx.amount)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # Publish to RabbitMQ (Lab 3 style) so other nodes get the tx
    try:
        from rabbitmq_publisher import publish_transaction
        publish_transaction(created)
    except Exception:
        pass
    return {"message": "Transaction queued", "transaction": created}


@app.get("/balance/{address}")
async def get_balance(address: str):
    """Get balance for an address (confirmed/mined only; pending tx do not affect displayed balance)."""
    chain = get_blockchain()
    return {"address": address, "balance": chain.get_balance(address, include_pending=False)}


@app.post("/mine")
async def mine_block(req: MineRequest):
    """Mine a new block (proof-of-work). Reward goes to miner; optional pending tx included. Broadcasts via RabbitMQ."""
    chain = get_blockchain()
    block = chain.mine_block(req.miner_address)
    # Broadcast new block via RabbitMQ
    try:
        from rabbitmq_publisher import publish_block
        publish_block(block.to_dict())
    except Exception:
        pass
    return {"message": "Block mined", "block": block.to_dict()}


@app.get("/nodes")
async def list_nodes():
    """List registered peer nodes (for gRPC sync). Nodes find each other via register."""
    return {"nodes": get_nodes()}


@app.post("/nodes/register")
async def register_node(node: NodeRegister):
    """Register a peer node URL (host:port for gRPC) so this node can sync chain from peers."""
    added = register_peer(node.node_url)
    return {"message": "Node registered" if added else "Node already registered", "url": node.node_url, "nodes": get_nodes()}


@app.post("/nodes/sync")
async def sync_nodes():
    """Sync chain from all registered peers. Replaces local chain if a peer has a longer valid chain (consensus)."""
    result = sync_chain_from_peers()
    return result


@app.get("/health")
async def health():
    chain = get_blockchain()
    valid = chain.validate_chain()
    return {"status": "ok", "chain_valid": valid, "length": len(chain.chain)}


@app.post("/demo/verify-transaction")
async def demo_verify_transaction(body: DemoVerifyTransaction):
    """
    Security demo: verify a transaction's signature without adding to chain.
    Send a transaction with an invalid/forged signature to see it rejected (400).
    """
    try:
        from wallet import verify_transaction_signature
    except ImportError:
        raise HTTPException(status_code=501, detail="Cryptography not available")
    tx = body.transaction
    if not tx.get("signature") or not tx.get("public_key"):
        raise HTTPException(status_code=400, detail="Transaction must include signature and public_key for verification")
    if verify_transaction_signature(tx):
        return {"valid": True, "message": "Signature is valid"}
    raise HTTPException(status_code=400, detail="Invalid transaction signature")


@app.post("/demo/try-invalid-signature")
async def demo_try_invalid_signature():
    """
    Security demo: server builds a forged tx (valid key, signature for wrong payload)
    and runs verification. Always returns 400 so the UI can show "Rejected" reliably.
    """
    import time
    try:
        from wallet import sign_transaction, verify_transaction_signature, get_or_create_keypair
    except ImportError:
        raise HTTPException(status_code=501, detail="Cryptography not available")
    # Build tx_a (amount 1), sign it. Build tx_b (amount 100) with same signature.
    priv, pub = get_or_create_keypair("_demo_forge")
    tx_a = {"id": "demo-forge", "sender": "attacker", "receiver": "bob", "amount": 1, "timestamp": time.time()}
    sig = sign_transaction(tx_a, priv)
    tx_b = {"id": "demo-forge", "sender": "attacker", "receiver": "bob", "amount": 100, "timestamp": tx_a["timestamp"]}
    tx_b["signature"] = __import__("base64").b64encode(sig).decode()
    tx_b["public_key"] = __import__("base64").b64encode(pub).decode()
    if verify_transaction_signature(tx_b):
        raise HTTPException(status_code=500, detail="Demo failed: expected verification to fail")
    raise HTTPException(status_code=400, detail="Invalid transaction signature")


# Mount frontend at /static; serve app at /app
if FRONTEND_PATH.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_PATH)), name="static")
    @app.get("/app")
    async def serve_app():
        return FileResponse(INDEX_PATH)
