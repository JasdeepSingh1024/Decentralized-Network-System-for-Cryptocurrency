# Performance and Monitoring (Integration & Testing role)

This document describes how to run the system, what to measure, and how to use the monitoring endpoint for the COE892 project.

## Running the system

- **Docker Compose (recommended):** `docker-compose up --build` then open http://localhost:8000/app
- **Local:** From `backend/`, run `python run.py` (requires RabbitMQ on localhost for full messaging)

## Monitoring endpoint

- **GET /health** — Returns:
  - `status`: `"ok"` if the API is up
  - `chain_valid`: `true` if the blockchain passes validation (hashes and proof-of-work)
  - `length`: number of blocks in the chain

Use this for:
- Liveness checks (e.g. container health)
- Quick verification that the chain is consistent after sync or heavy load

Example:
```bash
curl http://localhost:8000/health
```

## What to measure

1. **Time to mine one block**  
   Proof-of-work (4 leading zeros) typically takes a few seconds to tens of seconds depending on hardware. Call **POST /mine** and measure elapsed time until 200 response.

2. **API latency**  
   - **GET /chain** — Response time grows with chain length (full chain in JSON).
   - **GET /balance/{address}** — O(chain length); fast for small chains.

3. **Node sync**  
   **POST /nodes/sync** — Time to contact all registered peers via gRPC and optionally replace the chain. Depends on number of nodes and network latency.

## Test cases

Automated test cases are in `backend/tests/`:

- **test_blockchain.py** — Block structure, chain operations, mining, balance, validation, replace_chain
- **test_api.py** — REST endpoints: /chain, /health, /balance, /mine, /transactions, /nodes (list, register, sync)

Run tests (from project root or backend):
```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

## Documentation of results

For the interim or final report, you can document:

- Screenshots or JSON of **GET /health** before/after sync
- A table of **POST /mine** response times (e.g. 5 runs, mean/std)
- Test run output: `pytest tests/ -v --tb=short`

This supports the Integration and Testing role (test cases, performance monitoring, documentation).
