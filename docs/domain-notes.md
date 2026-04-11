# Domain Notes — python-1

## Purpose

`ingestion_utils` seeds and exercises the shared domain model described in
the PRD.  This document explains how each domain entity from the PRD maps to
the Python data structures used in this repository.

---

## Domain Entities

### DocumentSource

Defined in `seed_data.py` as dictionaries with the following fields:

| Field      | Type    | Example value            |
|------------|---------|--------------------------|
| `id`       | str     | `src-hr-shared-drive`    |
| `name`     | str     | `HR Shared Drive`        |
| `type`     | str     | `SHARED_DRIVE`           |
| `owner`    | str     | `hr-team`                |
| `location` | str     | `smb://fileserver/hr`    |
| `active`   | bool    | `True`                   |

Three baseline DocumentSources are pre-defined:
- `src-hr-shared-drive`
- `src-legal-archive`
- `src-finance-reports`

### Document

Defined in `seed_data.py` with the following fields:

| Field         | Type         | Example value                           |
|---------------|--------------|-----------------------------------------|
| `id`          | str          | `doc-1001`                              |
| `title`       | str          | `Quarterly Risk Summary`                |
| `sourceId`    | str          | `src-hr-shared-drive`                   |
| `tags`        | list[str]    | `["finance", "rag-test", "baseline"]`   |
| `version`     | str          | `1.0`                                   |
| `contentType` | str          | `application/pdf`                       |
| `metadata`    | dict         | `{"department": "Risk"}`                |

Five baseline Documents are pre-defined (doc-1001 through doc-1005).

### IngestionJob

Created dynamically by `submit_batch_jobs`.  The server-issued record includes:

| Field             | Type       | Notes                              |
|-------------------|------------|------------------------------------|
| `id`              | str        | Server-generated (e.g. `job-2001`) |
| `documentId`      | str        | ID of the associated Document      |
| `requestedBy`     | str        | Defaults to `python-seeder`        |
| `processingStatus`| str        | Starts as `PENDING`                |
| `submittedAt`     | str (ISO)  | Set by server                      |

### ProcessingStatus

Enum with values: `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`.

### ValidationResult

Submitted to java-2 with these fields:

| Field            | Example value        |
|------------------|----------------------|
| `documentId`     | `doc-1001`           |
| `jobId`          | server-generated     |
| `title`          | `Quarterly Risk...`  |
| `sourceId`       | `src-hr-shared-drive`|
| `version`        | `1.0`                |
| `tags`           | `["finance", ...]`   |
| `contentType`    | `application/pdf`    |

### Report

Fetched from java-2.  Key fields:

| Field           | Example value           |
|-----------------|-------------------------|
| `id`            | `rpt-3001`              |
| `type`          | `INGESTION_SUMMARY`     |
| `generatedAt`   | ISO timestamp           |
| `documentCount` | integer                 |
| `jobCount`      | integer                 |
| `summary`       | string description      |

---

## Shared IDs and Tags

The seed data intentionally reuses the canonical IDs from PRD §6.3:

- `doc-1001` — the primary test document (Quarterly Risk Summary)
- `src-hr-shared-drive` — the primary DocumentSource
- Tags: `finance`, `rag-test`, `baseline`

These IDs match the payloads and examples in `java-1`, `java-2`, `golang-1`,
and `react-web-1`.
