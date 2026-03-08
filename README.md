# COE892 Decentralized Cryptocurrency

A full-stack **decentralized network system for cryptocurrency** using a blockchain for transaction history. This repository implements the system described in the **COE892 Project Proposal** and uses the technologies from the Lab Manual: **FastAPI**, **gRPC**, **RabbitMQ**, and **Docker**.

**Course:** COE892 — Distributed and Cloud Computing · **Semester:** W2026 · **Instructor:** Dr. Muhammad Jaseemuddin  
**Team:** Jasdeep Singh, Arman Grewal, Hareesh Suresh, Gurpreet Singh Bhatti  

📄 **Full proposal:** [PROJECT_PROPOSAL.md](PROJECT_PROPOSAL.md)

---

## Problem Statement and Motivation (from Proposal)

Centralized financial systems act as a **single point of failure** (outages, errors, attacks can disrupt entire networks) and keep transaction books private, requiring full trust in institutions. This project establishes a **decentralized network with a distributed ledger** so that transaction history is **transparent, immutable, and resilient**, with data distributed over a **peer-to-peer architecture**. It addresses **data ownership** by putting users in charge of the ledger together—no single party can censor or manipulate the record. This **democratization of financial data** is the motivation for the blockchain-based solution.

---

## Proposed Technical Solution (from Proposal)

- **P2P distributed network:** Each node is connected to others; no central authority. Transactions are **broadcast** and **relayed** so the whole network is aware of them.
- **Majority rule / consensus:** If one node is compromised or lies, others **compare their copy of the history** and reject incorrect data; truth is determined by the group.
- **Blockchain:** Transactions are stored in **blocks** linked by a **mathematical fingerprint (hash)**. Tampering changes the fingerprint, breaks the chain, and is **rejected** by the network—making history effectively immutable.

**Mapping to this implementation:**  
P2P messaging is implemented via **RabbitMQ** (broadcast of transactions and new blocks) and **gRPC** (node-to-node chain sync). Blocks use **SHA256 hashes** and **proof-of-work** (leading zeros). Chain **validation** and optional **longest-chain** replacement implement consensus. The **REST API** and **web UI** provide the transaction viewer and monitoring (Integration & Testing role).

---

## Team Members and Responsibilities (from Proposal)

| Role | Member | Focus in this repo |
|------|--------|--------------------|
| **Ledger Logic** | Arman Grewal | Block structure, chaining, mining/validation rules → `blockchain/` (block, chain, transaction) |
| **Distributed Network** | Jasdeep Singh | P2P layer, message spread, node coordination, consistency → gRPC (`grpc_server.py`, `proto/`), RabbitMQ (publisher/consumer) |
| **Cryptography** | Gurpreet Singh Bhatti | Transaction signing/verification (e.g. public key), integrity → extensible in `blockchain/transaction.py`; hashing in `block.py` |
| **Integration and Testing** | Hareesh Suresh | Integration, docs, transaction viewer, monitoring → FastAPI app, frontend (`/app`), `/health`, README, Docker |

---

## Implementation Timeline (from Proposal)

- **Phase 1:** Planning and Proposal (Weeks 1–3) — Proposal by Feb 2, 2026  
- **Phase 2:** System Design and Early Implementation (Weeks 4–6) — Interim report by **Mar 9, 2026**  
- **Phase 3:** Full Implementation and Integration (Weeks 7–9)  
- **Phase 4:** Testing and Submission (Weeks 10–11) — Final code and report by **Mar 30, 2026**  
- **Phase 5:** Demonstration (Weeks 12–13) — **Mar 30 – Apr 10, 2026**

---

## Concepts Used (from Lab Manual)

| Lab | Technology | Use in this project |
|-----|------------|---------------------|
| Lab 1 | Concurrency, SHA256, proof-of-work (leading zeros) | Block hashing and mining (nonce with 4 leading zeros) |
| Lab 2 | gRPC, .proto | Node-to-node chain sync: `GetChain`, `SubmitBlock`, `StreamBlocks` |
| Lab 3 | RabbitMQ | Queues: `pending_transactions`, `new_blocks` for distributed messaging |
| Lab 4–5 | FastAPI, REST, Containers | REST API, frontend, Docker deployment |

## Architecture

- **Blockchain core**: Blocks with index, timestamp, transactions, previous_hash, nonce, SHA256 hash (proof-of-work: 4 leading zeros).
- **Backend**: Python; single process runs FastAPI (REST) + gRPC server (thread) + RabbitMQ consumer (thread).
- **Persistence**: JSON file (`backend/data/chain.json`) for chain and pending transactions.
- **Frontend**: Static HTML/CSS/JS (wallet, send, mine, chain explorer).

## Quick Start

### 1. Local run (no RabbitMQ required for basic use)

```bash
cd backend
pip install -r requirements.txt
python generate_grpc.py   # generate gRPC code from proto
python run.py
```

- **API**: http://localhost:8000  
- **Web UI**: http://localhost:8000/app  
- **API docs**: http://localhost:8000/docs  
- **gRPC**: localhost:50051  

### 2. With RabbitMQ (message queue)

Start RabbitMQ (e.g. Docker):

```bash
docker run -d -p 5672:5672 -p 15672:15672 --name rabbitmq rabbitmq:3-management
```

Then run the backend as above. Transactions and new blocks are published to RabbitMQ for other nodes.

### 3. Full stack with Docker Compose

From the **project root** (parent of `backend` and `frontend`):

```bash
docker-compose up --build
```

- **API + UI**: http://localhost:8000 and http://localhost:8000/app  
- **RabbitMQ**: port 5672; management UI: http://localhost:15672 (guest/guest)

## Project Layout

```
Project/
├── backend/
│   ├── api/
│   │   └── main.py          # FastAPI app (REST + static frontend)
│   ├── blockchain/
│   │   ├── block.py         # Block structure, SHA256, proof-of-work
│   │   ├── chain.py         # Chain, mine, validate, persist
│   │   └── transaction.py   # Transaction model
│   ├── proto/
│   │   ├── blockchain.proto # gRPC service definition
│   │   ├── blockchain_pb2.py
│   │   └── blockchain_pb2_grpc.py  # generated
│   ├── config.py
│   ├── state.py             # Shared blockchain instance
│   ├── nodes.py             # Node registry + sync from peers (P2P)
│   ├── wallet.py            # Ed25519 signing/verification (Cryptography)
│   ├── grpc_server.py       # gRPC node sync
│   ├── rabbitmq_publisher.py
│   ├── rabbitmq_consumer.py
│   ├── run.py               # Start API + gRPC
│   ├── generate_grpc.py
│   ├── requirements.txt
│   ├── tests/               # Pytest (Integration & Testing)
│   │   ├── test_blockchain.py
│   │   └── test_api.py
│   └── data/
│       ├── chain.json       # Persisted chain (created on first run)
│       ├── nodes.json       # Registered peer nodes
│       └── wallets.json    # Per-address key pairs (signing)
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## API Endpoints (FastAPI)

| Method | Path | Description |
|--------|------|-------------|
| GET | / | Redirect to /app |
| GET | /app | Web UI |
| GET | /chain | Full blockchain |
| GET | /blocks/{index} | Single block |
| GET | /transactions/pending | Pending transactions |
| POST | /transactions | Submit transaction (body: sender, receiver, amount) |
| GET | /balance/{address} | Balance for address |
| POST | /mine | Mine block (body: miner_address) |
| GET | /nodes | List registered peer nodes |
| POST | /nodes/register | Register peer (body: node_url, e.g. host:50051) |
| POST | /nodes/sync | Sync chain from all peers (longest valid wins) |
| GET | /health | Health and chain length |
| GET | /docs | Swagger UI |

## gRPC Service (BlockchainNode)

- **GetChain**: Return full chain for sync.
- **SubmitBlock**: Submit a mined block.
- **StreamBlocks**: Stream blocks after a given index.

## Environment Variables

- `API_HOST`, `API_PORT` (default 0.0.0.0, 8000)
- `GRPC_HOST`, `GRPC_PORT` (default 0.0.0.0, 50051)
- `RABBITMQ_HOST`, `RABBITMQ_PORT`, `RABBITMQ_USER`, `RABBITMQ_PASSWORD`

## Tests and performance

- **Run tests:** `cd backend && pytest tests/ -v`
- **Performance and monitoring:** [PERFORMANCE.md](PERFORMANCE.md) (what to measure, `/health`, test cases)

## References

- **Project proposal:** [PROJECT_PROPOSAL.md](PROJECT_PROPOSAL.md) (problem statement, technical solution, team roles, timeline)
- Lab Manual: `LabManual-COE892W26 (4).pdf`
- Lab 2 gRPC reference: `ref/lab2/`
- FastAPI: https://fastapi.tiangolo.com/
- gRPC: https://grpc.io/
- RabbitMQ: https://www.rabbitmq.com/
