"""
scenario.py — Integration scenario runner.

Implements the canonical baseline integration scenario described in PRD §7.4:

  1. Create 3 DocumentSources.
  2. Create 5 Documents.
  3. Submit IngestionJobs for all documents.
  4. Query job statuses.
  5. Request a ValidationResult and a Report from java-2.
  6. Export results to exports/.

Run via:
  python -m ingestion_utils.cli run_integration_scenario
"""

from __future__ import annotations

import json
import sys
from typing import Any

from .client import IngestionClient, ReportingClient
from .exporter import export_jobs, export_reports
from .seeder import seed_document_sources, seed_documents, submit_batch_jobs


def run_integration_scenario(
    java1_url: str,
    java2_url: str,
    output_dir: str = "exports",
) -> dict[str, Any]:
    """
    Execute the full baseline integration scenario and return a summary dict.

    Steps:
    1. Seed DocumentSources into java-1.
    2. Seed Documents into java-1.
    3. Batch-submit IngestionJobs.
    4. Query job statuses for all submitted jobs.
    5. Submit a ValidationResult for the canonical document (doc-1001).
    6. Request an INGESTION_SUMMARY Report from java-2.
    7. Export job data and report data to *output_dir*.
    """
    ingestion = IngestionClient(java1_url)
    reporting = ReportingClient(java2_url)

    print("=" * 60)
    print("Integration Scenario: Baseline Document Ingestion Workflow")
    print("=" * 60)

    # Step 1 — Seed DocumentSources
    sources = seed_document_sources(ingestion)

    # Step 2 — Seed Documents
    docs = seed_documents(ingestion)
    doc_ids = [d.get("id") for d in docs if d.get("id")]

    # Step 3 — Batch-submit IngestionJobs
    jobs = submit_batch_jobs(ingestion, doc_ids=doc_ids)
    job_ids = [j.get("id") for j in jobs if j.get("id")]

    # Step 4 — Query job statuses
    print("\nQuerying IngestionJob statuses...")
    statuses: list[dict[str, Any]] = []
    for job_id in job_ids:
        try:
            status = ingestion.get_job_status(job_id)
            statuses.append(status)
            print(
                f"  Job {job_id}: processingStatus={status.get('processingStatus', '?')}"
            )
        except Exception as exc:
            print(f"  [WARN] Could not fetch status for job {job_id}: {exc}", file=sys.stderr)

    # Step 5 — Submit ValidationResult for doc-1001
    print("\nSubmitting ValidationResult for doc-1001...")
    validation_result: dict[str, Any] = {}
    try:
        validation_payload = {
            "documentId": "doc-1001",
            "jobId": job_ids[0] if job_ids else "job-2001",
            "title": "Quarterly Risk Summary",
            "sourceId": "src-hr-shared-drive",
            "version": "1.0",
            "tags": ["finance", "rag-test", "baseline"],
            "contentType": "application/pdf",
        }
        validation_result = reporting.submit_validation(validation_payload)
        print(
            f"  ValidationResult: valid={validation_result.get('valid', '?')} "
            f"validatorVersion={validation_result.get('validatorVersion', '?')}"
        )
    except Exception as exc:
        print(f"  [WARN] Could not submit validation: {exc}", file=sys.stderr)

    # Step 6 — Request an INGESTION_SUMMARY Report
    print("\nRequesting INGESTION_SUMMARY Report from java-2...")
    report: dict[str, Any] = {}
    report_id: str | None = None
    try:
        report_request = reporting.request_report(
            {
                "reportType": "INGESTION_SUMMARY",
                "includeValidation": True,
            }
        )
        report_id = report_request.get("id")
        if report_id:
            report = reporting.get_report(report_id)
            print(
                f"  Report: id={report.get('id', '?')} "
                f"type={report.get('type', '?')} "
                f"documentCount={report.get('documentCount', '?')}"
            )
    except Exception as exc:
        print(f"  [WARN] Could not generate report: {exc}", file=sys.stderr)

    # Step 7 — Export
    print("\nExporting results...")
    exported_paths: list[str] = []
    if doc_ids:
        try:
            path = export_jobs(ingestion, doc_ids[0], output_dir=output_dir)
            exported_paths.append(path)
        except Exception as exc:
            print(f"  [WARN] Could not export jobs: {exc}", file=sys.stderr)
    if report_id:
        try:
            path = export_reports(reporting, report_id, output_dir=output_dir)
            exported_paths.append(path)
        except Exception as exc:
            print(f"  [WARN] Could not export report: {exc}", file=sys.stderr)

    print("\n" + "=" * 60)
    print("Integration scenario complete.")
    print("=" * 60)

    return {
        "sources_seeded": len(sources),
        "documents_seeded": len(docs),
        "jobs_submitted": len(jobs),
        "job_statuses": statuses,
        "validation_result": validation_result,
        "report": report,
        "exported_files": exported_paths,
    }
