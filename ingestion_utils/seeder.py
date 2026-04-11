"""
seeder.py — Baseline seeders for DocumentSource and Document data.

Used by the CLI commands:
  seed_documents   — seed DocumentSources + Documents
  submit_batch_jobs — submit IngestionJobs for all seeded Documents
"""

from __future__ import annotations

import sys
from typing import Any

from .client import IngestionClient
from .seed_data import DOCUMENT_SOURCES, DOCUMENTS


def seed_document_sources(client: IngestionClient) -> list[dict[str, Any]]:
    """
    Seed all baseline DocumentSources into java-1.

    Returns a list of created source records.
    Prints a summary to stdout.
    """
    created = []
    print("Seeding DocumentSources...")
    for source in DOCUMENT_SOURCES:
        try:
            result = client.create_document_source(source)
            created.append(result)
            print(f"  [OK] DocumentSource: {result.get('id', source['id'])}")
        except Exception as exc:
            print(f"  [WARN] Could not seed source {source['id']}: {exc}", file=sys.stderr)
    print(f"  Seeded {len(created)} / {len(DOCUMENT_SOURCES)} DocumentSources.")
    return created


def seed_documents(client: IngestionClient) -> list[dict[str, Any]]:
    """
    Seed all baseline Documents into java-1.

    Returns a list of created document records.
    Prints a summary to stdout.
    """
    created = []
    print("Seeding Documents...")
    for doc in DOCUMENTS:
        try:
            result = client.create_document(doc)
            created.append(result)
            print(f"  [OK] Document: {result.get('id', doc['id'])} — {doc['title']}")
        except Exception as exc:
            print(f"  [WARN] Could not seed document {doc['id']}: {exc}", file=sys.stderr)
    print(f"  Seeded {len(created)} / {len(DOCUMENTS)} Documents.")
    return created


def submit_batch_jobs(
    client: IngestionClient,
    doc_ids: list[str] | None = None,
    requested_by: str = "python-seeder",
) -> list[dict[str, Any]]:
    """
    Submit IngestionJobs for the specified Document IDs (defaults to all
    baseline IDs in DOCUMENTS).

    Returns a list of submitted IngestionJob records.
    """
    if doc_ids is None:
        doc_ids = [d["id"] for d in DOCUMENTS]

    submitted = []
    print(f"Submitting batch IngestionJobs for {len(doc_ids)} document(s)...")
    for doc_id in doc_ids:
        try:
            job = client.submit_ingestion_job(doc_id, requested_by=requested_by)
            submitted.append(job)
            print(
                f"  [OK] IngestionJob: {job.get('id', '?')} "
                f"→ document {doc_id} "
                f"(processingStatus={job.get('processingStatus', '?')})"
            )
        except Exception as exc:
            print(f"  [WARN] Could not submit job for {doc_id}: {exc}", file=sys.stderr)
    print(f"  Submitted {len(submitted)} / {len(doc_ids)} IngestionJobs.")
    return submitted
