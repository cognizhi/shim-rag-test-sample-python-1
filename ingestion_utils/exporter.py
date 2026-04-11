"""
exporter.py — Export IngestionJob and Report data to JSON or CSV.

Used by the CLI commands:
  export_jobs     — export all job records for a document
  export_reports  — export a Report record
"""

from __future__ import annotations

import csv
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any

from .client import IngestionClient, ReportingClient


def _ensure_exports_dir(output_dir: str = "exports") -> str:
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def export_jobs(
    client: IngestionClient,
    doc_id: str,
    output_dir: str = "exports",
    fmt: str = "json",
) -> str:
    """
    Export all IngestionJobs for *doc_id* to a file in *output_dir*.

    Supported formats: "json", "csv".
    Returns the path of the written file.
    """
    jobs: list[dict[str, Any]] = client.list_document_jobs(doc_id)
    _ensure_exports_dir(output_dir)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if fmt == "csv":
        path = os.path.join(output_dir, f"jobs-{doc_id}-{ts}.csv")
        _write_csv(jobs, path)
    else:
        path = os.path.join(output_dir, f"jobs-{doc_id}-{ts}.json")
        _write_json(jobs, path)

    print(f"Exported {len(jobs)} IngestionJob(s) for document {doc_id} → {path}")
    return path


def export_reports(
    client: ReportingClient,
    report_id: str,
    output_dir: str = "exports",
    fmt: str = "json",
) -> str:
    """
    Export a single Report record to a file in *output_dir*.

    Supported formats: "json", "csv".
    Returns the path of the written file.
    """
    report: dict[str, Any] = client.get_report(report_id)
    _ensure_exports_dir(output_dir)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if fmt == "csv":
        path = os.path.join(output_dir, f"report-{report_id}-{ts}.csv")
        _write_csv([report], path)
    else:
        path = os.path.join(output_dir, f"report-{report_id}-{ts}.json")
        _write_json(report, path)

    print(f"Exported Report {report_id} → {path}")
    return path


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _write_json(data: Any, path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, default=str)


def _write_csv(records: list[dict[str, Any]], path: str) -> None:
    if not records:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("")
        return

    fieldnames = list(records[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
