Markdown
# 🏎️ CAN Bus Edge Collector & Parser

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Platform](https://img.shields.io/badge/platform-linux-lightgrey.svg)
![Architecture](https://img.shields.io/badge/arch-Edge--to--Cloud-green.svg)

A high-throughput, resilient Edge data logging system designed to ingest, parse, and batch binary data from simulated vehicle and industrial sensors over a Linux CAN Bus interface.

---

## 📌 Architectural Overview

The system architecture decouples high-frequency hardware ingestion from slow disk I/O operations using an in-memory thread-safe pipeline.

[Raw CAN Bus Frame]
│
▼ (Ingestion - Non-blocking Read)
[SocketCAN / python-can]
│
▼ (Parsing - Memory Only)
[Dynamic Config-driven Bitwise Decoder]
│
▼ (Buffering)
[Thread-safe RAM Queue] ──(Accumulate Batch)──► [Local I/O Target (JSONL / DB)]


---

## 🚀 Architectural Steps

### 1. Environment & Hardware Simulation
* Configure a Linux virtual CAN interface (`vcan0`) using kernel modules.
* Implement a mock telemetry producer emitting realistic binary payloads simulating 4 distinct sensor nodes.

### 2. Static Binary Parsing
* Build a lightweight decoding utility utilizing Python's native `struct` module.
* Apply exact bit-masks and shift operations to extract raw metrics without high-level abstraction overhead.

### 3. Data-Driven Elasticity (Generic Parser)
* Abstract parsing logic by loading sensor specifications from an external configuration file (`config.toml` / `config.json`).
* **Performance Rule:** Configuration parameters are cached in memory **once at startup** to eliminate file I/O overhead inside the execution loop.

### 4. Concurrency & Memory Buffering (Batching)
* Deploy a thread-safe memory buffer (`queue.Queue`) to bridge the ingestion and storage layers.
* Accumulate streaming frames into block structures based on configurable thresholds (e.g., 100 messages or 2-second windows).

### 5. Storage Ingestion
* Evaluate and implement an append-only transaction sink (JSON Lines format or SQLite bulk inserts) optimized for localized, sequential write operations.

---

## 📊 Target Sensor Matrix

The binary payload structure layout decoded by the generic parser:

| Sensor Name | Device ID (HEX) | Data Length | Payload Layout (Bytes) | Target Unit |
| :--- | :---: | :---: | :--- | :---: |
| **Temperature** | `0x1A0` | 2 Bytes | Int16 (Big-Endian) | °C |
| **Humidity** | `0x1A1` | 2 Bytes | UInt16 (Big-Endian) | % |
| **Voltage** | `0x2B0` | 2 Bytes | UInt16 * 0.01 Scale | V |
| **RPM (Speed)** | `0x3C0` | 2 Bytes | UInt16 | RPM |

---

## 🔄 Data Processing Loop

1. **Ingest:** Intercept raw binary frames asynchronously from the `vcan0` socket interface.
2. **Decode:** Map raw byte slices into mathematical physical values via the runtime configuration schema. Gracefully quarantine corrupted frames to a dead-letter log without breaking execution flow.
3. **Buffer:** Safely enqueue state dictionaries into the thread-safe RAM queue.
4. **Flush:** Stream accumulated data matrices directly into the persistent storage backend via atomic batch transactions, minimizing system write bottlenecks.