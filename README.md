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

---

## 📅 Recent Development Session (v0.3.0 Update)

### Protocol Layer Refinement & Data Integrity Workflow

In the latest session, we optimized the protocol ingestion layer to ensure robust, production-ready frame handling and structural clarity:

* **CRC-First Validation:** Integrated a strict integrity-check mechanism within the decoding pipeline. Frames failing the `calculate_can_crc` verification are now discarded immediately at the `decode` phase to prevent corrupted data propagation.
* **Separation of Concerns:** Explicitly decoupled raw frame identification (`parse_raw_frame`) from payload decoding (`decode_can_payload`). This ensures the protocol handler focuses solely on boundary definition and structural integrity.
* **Protocol-Agnostic Header Handling:** Standardized the header-to-payload slicing logic. The interface now dynamically adapts its offset based on the CAN frame type (Standard/Extended) without logic leakage into higher-level application components.
* **Resilient Logging & Diagnostics:** Standardized logging across the protocol module to follow production best practices, ensuring clear diagnostic trails for connection states and parity/CRC mismatches without cluttering the data stream.
* **Structural Cleanup:** Refactored the `Canbus` communication module for strict PEP 8 compliance, removing stale buffer definitions and implementing documentation-driven interface methods.

---

📅 Development Session (v0.3.1 Update)
Architectural Refinement & Interface Decoupling
In this session, we refactored the base sensor interface and the CAN protocol communication layer to support a passive data pipeline:

Signature Update: Updated the BaseSensor.read() signature to accept a raw_payload, shifting the sensor's responsibility from active acquisition to passive data transformation.

Interface Decoupling: Decoupled the sensor’s internal logic from the protocol’s communication method, ensuring sensors act as pure data decoders regardless of the acquisition source.

Resilience Implementation: Introduced defensive error handling within the read method, ensuring that decoding failures or validation errors return a controlled status instead of propagating exceptions.

Singleton State Management: Optimized the CAN protocol implementation to support shared instance usage, preventing resource contention and redundant connection initialization across sensor instances.

Validation Hook: Established the structural groundwork for a modular validator within the sensor’s processing pipeline, allowing for future integration of strict integrity checks.

---

