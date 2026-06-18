# 🏎️ CAN Bus Edge Collector & Parser

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Platform](https://img.shields.io/badge/platform-linux-lightgrey.svg)
![Architecture](https://img.shields.io/badge/arch-Edge--to--Cloud-green.svg)

A high-throughput, resilient Edge data logging system designed to ingest, parse, and batch binary data from simulated vehicle and industrial sensors over a Linux CAN Bus interface.

---

## 📌 Architectural Overview

The system architecture decouples high-frequency hardware ingestion from slow disk I/O operations using an in-memory thread-safe pipeline.



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

| Sensor Name | Device ID (HEX) | Min Value | Max Value |
| :--- | :---: | :---: | :---: |
| **Temp Sensor** | `0x10A` | 40.0 | 120.0 |
| **RPM Sensor** | `0x110` | 800.0 | 7200.0 |
| **Speed Sensor** | `0x120` | 0.0 | 180.0 |
| **Oil Pressure** | `0x130` | 0.5 | 5.0 |

---

## 🔄 Data Processing Loop

1. **Ingest:** Intercept raw binary frames asynchronously from the `vcan0` socket interface.
2. **Decode:** Map raw byte slices into mathematical physical values via the runtime configuration schema. Gracefully quarantine corrupted frames to a dead-letter log without breaking execution flow.
3. **Buffer:** Safely enqueue state dictionaries into the thread-safe RAM queue.
4. **Flush:** Stream accumulated data matrices directly into the persistent storage backend via atomic batch transactions, minimizing system write bottlenecks.

---

## 🛠️ Simulation & Development

The repository includes a dedicated `simulator/` module that provides a complete synthetic data environment. This allows for decoupled development of the ingest and parsing logic without requiring actual hardware connectivity.

* **Mock Engine:** A lightweight, asynchronous `canbus_simulator` (v1.0.0) that generates realistic sensor telemetry.
* **Protocol:** Employs UDP broadcasting (`127.0.0.1:5005`) to emulate the physical CAN bus behavior in a software-only environment, ensuring low-latency inter-process communication.
* **Resiliency:** The simulator is designed as a standalone "Sensor Node" – it streams data in a non-blocking `async` loop, adhering to real-world hardware behavior where the sender does not verify reception.

> **Development Note:** The simulator is version-controlled and provides a reliable baseline for testing the `Receiver/Collector` logic currently under development in the root directory.

---

## 📅 Recent Development Session (v0.2.0 Update)

### Decoupled Sensor Architecture & Core Interface Definition
In the latest session, we established the fundamental abstract architecture for the parsing engine to align with distributed microservice principles:

* **`BaseSensor` Interface Integration:** Defined a rigid, configuration-driven abstract base class (`ABC`) that isolates individual sensor logic from the main telemetry pipeline execution.
* **Pure Decoupling Rule:** Completely stripped hardcoded type constraints and thresholds from the initialization layer. Sensors now load limits, data types, and operational states dynamically via external runtime parameters.
* **Type-Agnostic Validation:** Extended the validation mechanism into an abstract method capable of handling generic payload mutations (e.g., dynamic type checking across float ranges, discrete integers, or boolean flag structures).
* **Pipeline vs Sensor Isolation:** Enforced a strict boundary where the sensor module remains stateless regarding downstream processing—it is solely responsible for parsing (`decode`) and safety-checking (`validate`) data fields, while the runtime orchestrator manages execution loops and external states.

