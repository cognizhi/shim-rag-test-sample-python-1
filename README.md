# shim-rag-test-sample-python-1 — Seeder and Integration Utility

## Overview

This repository contains `ingestion_utils`, a Python CLI utility that seeds
sample data, drives integration workflows, and exports records across the
Document Ingestion ecosystem.

It operates as the **data seeder and integration test driver** for the
multi-repository RAG test environment, working alongside:

- [`shim-rag-test-sample-java-1`](../shim-rag-test-sample-java-1) — primary backend API (Document Ingestion)
- [`shim-rag-test-sample-java-2`](../shim-rag-test-sample-java-2) — Reporting and Validation API
- [`shim-rag-test-sample-golang-1`](../shim-rag-test-sample-golang-1) — operator CLI
- [`shim-rag-test-sample-react-web-1`](../shim-rag-test-sample-react-web-1) — web dashboard

---

## Repository Role in the Ecosystem

`python-1` is the seeder and integration utility responsible for:

1. Creating canonical `DocumentSource` records in java-1.
2. Seeding baseline `Document` records that other repositories reference.
3. Submitting batch `IngestionJob` requests to java-1.
4. Exporting job and report data to JSON or CSV files.
5. Running a full end-to-end integration scenario from seeding to reporting.

Its payloads are intentionally aligned with the examples in java-1, java-2,
and golang-1 so that cross-repository retrieval queries resolve consistently.

---

## Relationship to Other Repositories

| Repository     | Relationship                                                  |
|----------------|---------------------------------------------------------------|
| `java-1`       | Primary target — creates DocumentSources, Documents, Jobs     |
| `java-2`       | Secondary target — submits validations and fetches Reports     |
| `golang-1`     | Peer CLI — shares document IDs and vocabulary                 |
| `react-web-1`  | Consumer — displays workflow driven by python-1               |

---

## Domain Concepts Used in This Repository

This repository uses the shared domain vocabulary from the PRD:

- **Document** — enterprise document with title, sourceId, tags, version, contentType
- **DocumentSource** — origin system for documents (type, owner, location)
- **IngestionJob** — processing request; tracked via ProcessingStatus
- **ProcessingStatus** — `PENDING` → `RUNNING` → `COMPLETED` / `FAILED`
- **ValidationResult** — outcome of validating a document payload
- **Report** — generated summary (types: `INGESTION_SUMMARY`, `VALIDATION_SUMMARY`)

Shared example IDs used across all repositories:

- Document: `doc-1001` (Quarterly Risk Summary)
- Sources: `src-hr-shared-drive`, `src-legal-archive`, `src-finance-reports`
- Tags: `finance`, `rag-test`, `baseline`

---

## Local Setup

### Prerequisites

- Python 3.11+
- `java-1` and `java-2` running locally (optional — tests work without services)

### Install

```bash
python3 -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

---

## How to Run

### Quick help

```bash
python -m ingestion_utils.cli --help
```

### Seed DocumentSources and Documents

```bash
python -m ingestion_utils.cli seed_documents
```

### Submit Batch IngestionJobs

```bash
python -m ingestion_utils.cli submit_batch_jobs
```

### Export Jobs for a Document

```bash
# JSON (default)
python -m ingestion_utils.cli export_jobs --document-id doc-1001

# CSV
python -m ingestion_utils.cli export_jobs --document-id doc-1001 --format csv
```

### Export a Report

```bash
python -m ingestion_utils.cli export_reports --report-id rpt-3001
```

### Run the Full Integration Scenario

```bash
python -m ingestion_utils.cli run_integration_scenario
```

---

## Key Folders and Files

```
ingestion_utils/
  __init__.py        — package entry point
  client.py          — HTTP clients for java-1 (IngestionClient) and java-2 (ReportingClient)
  seed_data.py       — baseline DocumentSource and Document payloads
  seeder.py          — seed_document_sources, seed_documents, submit_batch_jobs
  exporter.py        — export_jobs, export_reports to JSON/CSV
  scenario.py        — full integration scenario runner
  cli.py             — argparse CLI entry point
tests/
  test_seeder.py     — unit tests using mocked HTTP clients
docs/
  integration-walkthrough.md  — step-by-step workflow documentation
  domain-notes.md             — domain entity reference
examples/
  sample-document.json        — example Document payload (doc-1001)
  sample-ingestion-job.json   — example IngestionJob payload (job-2001)
exports/                       — output directory for export commands (git-ignored)
```

---

## Main Workflows

1. **Seeding**: `seed_documents` → calls java-1 to create DocumentSources and Documents
2. **Ingestion**: `submit_batch_jobs` → submits IngestionJobs to java-1
3. **Export**: `export_jobs` / `export_reports` → writes JSON or CSV artifacts
4. **Integration scenario**: `run_integration_scenario` → full workflow end-to-end

---

## Example Commands

```bash
# Seed all baseline data into local java-1 instance
python -m ingestion_utils.cli seed_documents --java1-url http://localhost:8081

# Submit jobs for all seeded documents
python -m ingestion_utils.cli submit_batch_jobs --java1-url http://localhost:8081

# Export job history for doc-1001 as CSV
python -m ingestion_utils.cli export_jobs --document-id doc-1001 --format csv

# Run the full integration scenario
python -m ingestion_utils.cli run_integration_scenario \
  --java1-url http://localhost:8081 \
  --java2-url http://localhost:8082
```

---

## Running Tests

```bash
.venv/bin/pytest tests/ -v
```

Tests use `unittest.mock` to patch HTTP calls; no running services required.

---

## Baseline vs Branch-Only Features

| Feature                            | `main` / `v1.0.0-baseline` | `feature/bulk-seeding` |
|------------------------------------|:---------------------------:|:----------------------:|
| Seed 3 DocumentSources             | ✓                           | ✓                      |
| Seed 5 Documents                   | ✓                           | ✓                      |
| Batch job submission               | ✓                           | ✓                      |
| Export to JSON/CSV                 | ✓                           | ✓                      |
| Configurable bulk document volume  | —                           | ✓ (branch-only)        |
| Richer export field set            | —                           | ✓ (branch-only)        |

The `feature/bulk-seeding` branch introduces richer seed generation for
higher-volume testing scenarios.  It does not merge to `main` in this baseline.
