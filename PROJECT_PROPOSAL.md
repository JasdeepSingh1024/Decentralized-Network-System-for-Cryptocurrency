# COE892 Project Proposal — Decentralized Network System for Cryptocurrency

**Course:** COE892 — Distributed and Cloud Computing  
**Semester/Year:** W2026  
**Instructor:** Muhammad Jaseemuddin  

**Team:**

| Last Name | First Name | Student Number | Section | Signature |
|-----------|------------|----------------|---------|-----------|
| Singh     | Jasdeep    | 501089933      | 13      | JS        |
| Grewal    | Arman      | 501100160      | 13      | AG        |
| Suresh    | Hareesh    | 500830145      | 08      | HS        |
| Bhatti    | Gurpreet   | 501103368      | 13      | GB        |

---

## Problem Statement and Motivation

The modern financial system is largely built around centralized systems, where large entities have total control over the transactions and registries. The issue with these centralized systems is that they can act as a **single point of failure**, and that is their biggest weakness. Whether a system outage, internal error, or cyberattack occurs, entire networks can be disrupted. Also, since transaction books are kept privately, one must have complete trust in institutions to be honest and correct in their operations. Such lack of transparency may lead to inefficiencies, slow settlements, reduced accountability, and increased operation costs. This project aims at addressing these shortcomings by establishing a **decentralized network using a distributed ledger**. The system makes the history of transactions **transparent, immutable, and resilient** to local failure or malicious interference by distributing the data over a **peer-to-peer architecture**.

The proposed system also solves the issue of **data ownership** by eliminating the intermediary. In the modern banking model, the bank possesses the information and the ledger. With a decentralized cryptocurrency network, the **users are in charge of the ledger together** so that no one individual can censor transactions and manipulate the historical record to their advantage. This **democratization of financial data** is the primary motivation for pursuing a blockchain-based solution.

---

## Proposed Technical Solution

This project is based on a **Peer-to-Peer (P2P) distributed network**. In a P2P network, each computer is a **node** and is connected to other computers. **No central entity** informs all what to do. When a user sends money, this movement is **broadcast on the P2P network**. The news is heard by each computer and is **relayed to neighbors** until all computers in the distributed network are aware of the transaction.

This project addresses the issues of centralized systems by **distributing responsibility** across the whole network. Under a centralized system, one hack could alter the balance of all accounts. In our distributed solution, when one node is hacked or attempts to lie about a transaction, the **other nodes compare their copy of the history** and will know that the data is incorrect. This brings about a **majority-rule system** where the truth is determined by the group as a whole and not by a single authority. Since the information is saved in **numerous locations simultaneously**, the system is never offline and can be verified by any person who becomes a member.

The system is referred to as a **blockchain** due to the way information is stored. Transactions are not kept in a single long list but in **blocks**. After a block is filled, it is **linked to the previous block via a special mathematical fingerprint** (hash). This produces a **digital timeline that is permanent**. Should someone attempt to modify a transaction within an old block, the fingerprint will be altered, the chain will be broken, and the rest of the P2P network will **reject the forged data** immediately. It is this **chaining of blocks** that makes the history impossible to alter and is the reason the technology is so secure.

---

## Team Members and Responsibilities

The project is completed by a team of four with responsibilities distributed to cover the full scope of a decentralized system. Roles overlap slightly to ensure seamless integration across the development cycle.

| Role | Member | Responsibilities |
|------|--------|------------------|
| **Ledger Logic** | Arman Grewal | Structure of blocks; how transactions are chained and recorded; rules for mining and validating new blocks; rules for checks within the network. |
| **Distributed Network** | Jasdeep Singh | P2P communication layer; nodes finding each other and coordinating ledger information; message spread; node join/leave; maintaining consistency of the distributed ledger under latency and partial failure. |
| **Cryptography** | Gurpreet Singh Bhatti | Cryptographic validation of transactions and identity; signing and verifying transactions (e.g. public key cryptography); attack vectors; data integrity when nodes exchange data. |
| **Integration and Testing** | Hareesh Suresh | Component integration; documentation; support tools (e.g. transaction viewer, monitoring); test cases; performance monitoring; cohesion of components; making the system visible and demonstrable. |

---

## Implementation Timeline

| Phase | Weeks | Description | Deliverable / Date |
|-------|--------|-------------|--------------------|
| **1. Planning and Proposal** | 1–3 | Finalize scope, system goals, decentralized blockchain solution; assign roles. | Project proposal by **Feb 2, 2026** |
| **2. System Design and Early Implementation** | 4–6 | Architecture design: blockchain data structure, transaction format, P2P communication; start core implementation. | Interim report (5–7 pages) by **Mar 9, 2026** |
| **3. Full Implementation and Integration** | 7–9 | Complete main functionality: consensus, cryptographic validation, node sync; integrate modules into one decentralized network. | — |
| **4. Testing, Finalization, Submission** | 10–11 | Testing and optimization; stability and correctness. | Final code + 10-page report by **Mar 30, 2026** |
| **5. Demonstration** | 12–13 | Demonstrate system to TA: functionality, usability, design decisions. | **Mar 30 – Apr 10, 2026** |

---

*This document reflects the project proposal submitted for COE892 W2026. The repository implementation aligns with this proposal and the course lab manual (FastAPI, gRPC, RabbitMQ, Docker).*
