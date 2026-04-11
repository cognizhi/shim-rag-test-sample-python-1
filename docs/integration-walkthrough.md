# Integration Walkthrough — python-1

## Overview

This document describes the end-to-end integration workflow driven by the
`ingestion_utils` Python utility.  It maps each command to the corresponding
REST API calls in `java-1` (Document Ingestion API) and `java-2`
(Reporting / Validation API).

---

## Prerequisites

- `java-1` running on `http://localhost:8081`
- `java-2` running on `http://localhost:8082`
- Python 3.11+ with dependencies installed (`pip install -e ".[dev]"`)

---

## Step-by-Step Workflow

### 1. Seed DocumentSources and Documents

```bash
python -m ingestion_utils.cli seed_documents
```

This command calls:

- `POST /document-sources` (3 times) to register:
  - `src-hr-shared-drive`
  - `src-legal-archive`
  - `src-finance-reports`
- `POST /documents` (5 times) to create documents including the canonical
  `doc-1001` (Quarterly Risk Summary).

All payloads use the shared domain vocabulary from PRD §6 and match the
example payloads in `java-1`, `golang-1`, and `react-web-1`.

### 2. Submit Ingestion Jobs

```bash
python -m ingestion_utils.cli submit_batch_jobs
```

This command calls `POST /documents/{id}/ingestion-jobs` for each seeded
Document.  The `requestedBy` field defaults to `python-seeder`.

Each created `IngestionJob` starts with `processingStatus=PENDING`.

### 3. Export Jobs for a Document

```bash
python -m ingestion_utils.cli export_jobs --document-id doc-1001
python -m ingestion_utils.cli export_jobs --document-id doc-1001 --format csv
```

Exports all IngestionJobs for `doc-1001` to `exports/jobs-doc-1001-<ts>.json`
or `.csv`.

### 4. Export a Report from java-2

```bash
python -m ingestion_utils.cli export_reports --report-id rpt-3001
python -m ingestion_utils.cli export_reports --report-id rpt-3001 --format csv
```

Calls `GET /reports/{id}` in java-2 and writes the result to
`exports/report-<id>-<ts>.json`.

### 5. Run the Full Integration Scenario

```bash
python -m ingestion_utils.cli run_integration_scenario
```

Runs all steps above in sequence plus:

- Submits a `ValidationResult` for `doc-1001` to `POST /validation-results`
  in java-2.
- Requests an `INGESTION_SUMMARY` Report via `POST /report-requests` in java-2.

---

## Cross-Repository Relationships

| Repository     | Interaction                                              |
|----------------|----------------------------------------------------------|
| `java-1`       | Creates DocumentSources, Documents, IngestionJobs        |
| `java-2`       | Receives ValidationResults and generates Reports         |
| `golang-1`     | Alternative CLI operator; shares same document IDs       |
| `react-web-1`  | Visualizes the full workflow driven by python-1          |

---

## Shared Domain Vocabulary

The payloads in `ingestion_utils/seed_data.py` use the same IDs and field names
as all other repositories:

- `doc-1001` — Quarterly Risk Summary
- `src-hr-shared-drive`, `src-legal-archive`, `src-finance-reports`
- `processingStatus` values: `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`
- Tags: `finance`, `rag-test`, `baseline`

---

## Baseline vs Branch Behaviour

On `main` (and `v1.0.0-baseline`), the seeder creates the five core documents
and submits one job per document.

The `feature/bulk-seeding` branch extends this with configurable bulk generation
for load testing and richer export field sets.
