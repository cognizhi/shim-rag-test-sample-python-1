"""
bulk_seeder.py — Branch-only bulk seeding for feature/bulk-seeding.

BRANCH-ONLY: This module exists only on feature/bulk-seeding.
It is NOT available on main or v1.0.0-baseline.

Provides configurable volume seeding for higher-load testing scenarios.
"""

from __future__ import annotations

import random
import string
import uuid
from typing import Any

from .client import IngestionClient
from .seed_data import DOCUMENT_SOURCES

# Document types available for random generation
_CONTENT_TYPES = [
    "application/pdf",
    "application/msword",
    "text/plain",
    "application/vnd.ms-excel",
]

_TAG_POOL = [
    "finance",
    "legal",
    "hr",
    "policy",
    "rag-test",
    "baseline",
    "annual",
    "quarterly",
    "priority",
    "contract",
]

_DEPARTMENTS = ["Risk", "Finance", "HR", "Legal", "Compliance", "Operations"]


def _random_suffix(n: int = 6) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def generate_bulk_documents(count: int, source_ids: list[str] | None = None) -> list[dict[str, Any]]:
    """
    Generate *count* synthetic Document payloads for bulk seeding.

    BRANCH-ONLY: feature/bulk-seeding

    Args:
        count: Number of Document payloads to generate.
        source_ids: DocumentSource IDs to assign; cycles through available sources.

    Returns:
        List of Document dict payloads ready to POST to java-1.
    """
    if source_ids is None:
        source_ids = [s["id"] for s in DOCUMENT_SOURCES]

    documents = []
    for i in range(count):
        dep = random.choice(_DEPARTMENTS)
        doc_id = f"doc-bulk-{_random_suffix()}"
        tags = random.sample(_TAG_POOL, k=random.randint(1, 4))
        documents.append(
            {
                "id": doc_id,
                "title": f"{dep} Document {i + 1}",
                "sourceId": source_ids[i % len(source_ids)],
                "tags": tags,
                "version": f"1.{i}",
                "contentType": _CONTENT_TYPES[i % len(_CONTENT_TYPES)],
                "metadata": {
                    "department": dep,
                    "owner": f"{dep.lower()}-team",
                    "bulkSeed": True,
                },
            }
        )
    return documents


def seed_bulk_documents(
    client: IngestionClient,
    count: int = 20,
    source_ids: list[str] | None = None,
    requested_by: str = "python-bulk-seeder",
) -> dict[str, Any]:
    """
    Generate and seed *count* Documents, then submit IngestionJobs for each.

    BRANCH-ONLY: feature/bulk-seeding

    Returns a summary dict with counts and any failures.
    """
    documents = generate_bulk_documents(count, source_ids)

    print(f"Bulk seeding {count} Document(s)...")
    seeded_docs: list[dict] = []
    failed_docs: list[str] = []
    for doc in documents:
        try:
            result = client.create_document(doc)
            seeded_docs.append(result)
        except Exception as exc:
            print(f"  [WARN] Failed to seed {doc['id']}: {exc}")
            failed_docs.append(doc["id"])

    print(f"  Seeded {len(seeded_docs)} / {count} documents.")

    doc_ids = [d.get("id") for d in seeded_docs if d.get("id")]
    submitted_jobs: list[dict] = []
    print(f"Submitting {len(doc_ids)} IngestionJob(s)...")
    for doc_id in doc_ids:
        try:
            job = client.submit_ingestion_job(doc_id, requested_by=requested_by)
            submitted_jobs.append(job)
        except Exception as exc:
            print(f"  [WARN] Failed to submit job for {doc_id}: {exc}")

    print(f"  Submitted {len(submitted_jobs)} / {len(doc_ids)} jobs.")

    return {
        "documents_requested": count,
        "documents_seeded": len(seeded_docs),
        "documents_failed": len(failed_docs),
        "jobs_submitted": len(submitted_jobs),
    }
