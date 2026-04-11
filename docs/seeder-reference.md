# Seeder Reference — python-1

## Baseline Seed Commands

This document is the evolved reference for the seeder and integration commands.
It was split from the original integration walkthrough to separate command
reference from workflow narrative.

For the full step-by-step workflow, see `docs/integration-walkthrough.md`.

---

## seed_documents

Seeds 3 DocumentSources and 5 Documents into java-1.

```bash
python -m ingestion_utils.cli seed_documents [--java1-url URL]
```

**DocumentSources seeded:**

| ID                       | Type            | Owner         |
|--------------------------|-----------------|---------------|
| `src-hr-shared-drive`    | SHARED_DRIVE    | hr-team       |
| `src-legal-archive`      | DOCUMENT_ARCHIVE| legal-team    |
| `src-finance-reports`    | REPORT_STORE    | finance-team  |

**Documents seeded:**

| ID         | Title                      | Source                  | Tags                            |
|------------|----------------------------|-------------------------|---------------------------------|
| `doc-1001` | Quarterly Risk Summary     | src-hr-shared-drive     | finance, rag-test, baseline     |
| `doc-1002` | Employment Policy Handbook | src-hr-shared-drive     | hr, policy, baseline            |
| `doc-1003` | Contract Template v3       | src-legal-archive       | legal, contract, rag-test       |
| `doc-1004` | Annual Finance Report 2023 | src-finance-reports     | finance, annual, rag-test       |
| `doc-1005` | Data Retention Policy      | src-legal-archive       | legal, policy, baseline         |

---

## submit_batch_jobs

Submits one `IngestionJob` per seeded Document.

```bash
python -m ingestion_utils.cli submit_batch_jobs \
  [--java1-url URL] \
  [--requested-by REQUESTER]
```

All jobs start with `processingStatus=PENDING`.

---

## export_jobs

Exports IngestionJobs for a single Document to JSON or CSV.

```bash
python -m ingestion_utils.cli export_jobs \
  --document-id doc-1001 \
  [--format json|csv] \
  [--output-dir exports/]
```

---

## export_reports

Exports a Report from java-2 to JSON or CSV.

```bash
python -m ingestion_utils.cli export_reports \
  --report-id rpt-3001 \
  [--format json|csv] \
  [--output-dir exports/]
```

---

## run_integration_scenario

Runs the full end-to-end ingestion timeline from seeding to report export.

```bash
python -m ingestion_utils.cli run_integration_scenario \
  [--java1-url URL] \
  [--java2-url URL] \
  [--output-dir exports/]
```

The **ingestion timeline** for a single Document:

1. DocumentSource created
2. Document created and linked to source
3. IngestionJob submitted → `processingStatus=PENDING`
4. Job tracked through `RUNNING` → `COMPLETED` / `FAILED`
5. ValidationResult submitted to java-2
6. Report requested from java-2
7. Job and report data exported to `exports/`

> **Terminology note:** Earlier documentation used the term "job history" to
> describe the sequence of job states for a document. The preferred label
> in current docs is **ingestion timeline** to align with the vocabulary
> used in java-1 v1.1.0 and golang-1 v1.1.0.
