"""
Node registry: persist peer nodes and sync chain from them (P2P / Distributed Network role).
"""
import json
from pathlib import Path
from typing import Any

NODES_PATH = Path(__file__).resolve().parent / "data" / "nodes.json"
_nodes: list[str] | None = None


def _ensure_data_dir() -> None:
    NODES_PATH.parent.mkdir(parents=True, exist_ok=True)


def _load() -> list[str]:
    global _nodes
    if _nodes is not None:
        return _nodes
    _nodes = []
    if NODES_PATH.exists():
        try:
            with open(NODES_PATH) as f:
                data = json.load(f)
            _nodes = list(data.get("nodes", []))
        except Exception:
            pass
    return _nodes


def _save() -> None:
    _ensure_data_dir()
    with open(NODES_PATH, "w") as f:
        json.dump({"nodes": _load()}, f, indent=2)


def get_nodes() -> list[str]:
    """Return list of registered peer node URLs (host:port for gRPC)."""
    return list(_load())


def register_node(node_url: str) -> bool:
    """Register a peer node URL. Returns True if added, False if already present."""
    nodes = _load()
    node_url = (node_url or "").strip().rstrip("/")
    if not node_url:
        return False
    if node_url in nodes:
        return False
    nodes.append(node_url)
    global _nodes
    _nodes = nodes
    _save()
    return True


def sync_chain_from_peers() -> dict[str, Any]:
    """
    Contact each registered peer via gRPC GetChain; if any has a longer valid chain, replace ours.
    Returns {"replaced": bool, "from_node": str|None, "new_length": int, "errors": list}.
    """
    import grpc
    from proto import blockchain_pb2 as pb2
    from proto import blockchain_pb2_grpc as pb2_grpc
    from state import get_blockchain

    result: dict[str, Any] = {"replaced": False, "from_node": None, "new_length": 0, "errors": []}
    chain = get_blockchain()
    current_len = len(chain.chain)

    for node_url in get_nodes():
        host_port = node_url.strip()
        if "://" in host_port:
            result["errors"].append(f"Skip {host_port}: use host:port for gRPC")
            continue
        try:
            channel = grpc.insecure_channel(host_port)
            stub = pb2_grpc.BlockchainNodeStub(channel)
            resp = stub.GetChain(pb2.GetChainRequest(node_id="sync", from_index=0), timeout=5)
            channel.close()
            # Convert to list of block dicts
            blocks_data = []
            for b in resp.blocks:
                import json as _json
                blocks_data.append({
                    "index": b.index,
                    "timestamp": b.timestamp,
                    "previous_hash": b.previous_hash,
                    "nonce": b.nonce,
                    "hash": b.hash,
                    "transactions": _json.loads(b.transactions_json or "[]"),
                })
            if len(blocks_data) > current_len and chain.replace_chain(blocks_data):
                result["replaced"] = True
                result["from_node"] = host_port
                result["new_length"] = len(chain.chain)
                return result
        except Exception as e:
            result["errors"].append(f"{host_port}: {e}")
    result["new_length"] = len(chain.chain)
    return result
