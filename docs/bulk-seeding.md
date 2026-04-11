# Bulk Seeding Guide — python-1 (branch-only: feature/bulk-seeding)

## Overview

BRANCH-ONLY: This document exists only on `feature/bulk-seeding`.
The bulk seeding capability is not available on `main` or `v1.0.0-baseline`.

The `feature/bulk-seeding` branch extends the baseline seeder with configurable
volume generation for higher-load testing and richer export field sets.

---

## New Module: `ingestion_utils/bulk_seeder.py`

This branch introduces `bulk_seeder.py` with two functions:

- `generate_bulk_documents(count, source_ids)` — generates synthetic Document payloads
- `seed_bulk_documents(client, count, source_ids, requested_by)` — seeds Documents + Jobs

### Generated Document Properties

- Unique IDs: `doc-bulk-<random>` format
- Tags drawn from: `finance`, `legal`, `hr`, `policy`, `rag-test`, `annual`,
  `quarterly`, `priority`, `contract`, `baseline`
- Sources: cycles through the 3 baseline DocumentSources
- Content types: `application/pdf`, `application/msword`, `text/plain`, `application/vnd.ms-excel`
- Includes `metadata.bulkSeed=True` to distinguish from seeded baseline documents

---

## Usage (branch-only)

```python
from ingestion_utils.client import IngestionClient
from ingestion_utils.bulk_seeder import seed_bulk_documents

client = IngestionClient("http://localhost:8081")
summary = seed_bulk_documents(client, count=50)
print(summary)
# {
#   "documents_requested": 50,
#   "documents_seeded": 50,
#   "documents_failed": 0,
#   "jobs_submitted": 50
# }
```

---

## Comparison with Baseline Seeder

| Feature                          | `main` baseline       | `feature/bulk-seeding` |
|----------------------------------|:---------------------:|:----------------------:|
| Seed fixed 5 Documents           | ✓                     | ✓                      |
| Seed configurable N Documents    | —                     | ✓                      |
| Random tag assignment per doc    | —                     | ✓                      |
| `metadata.bulkSeed` flag         | —                     | ✓                      |
| Random content type assignment   | —                     | ✓                      |

---

## Why Not on Main

Bulk seeding introduces non-deterministic document IDs which complicates
cross-repository ID alignment.  The baseline uses fixed canonical IDs
(`doc-1001`, `src-hr-shared-drive`, etc.) to ensure reproducible RAG
retrieval test scenarios.  The bulk seeder is left as a branch-only
enhancement.
