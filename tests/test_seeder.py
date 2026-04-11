"""
tests/test_seeder.py — Baseline tests for ingestion_utils.

These tests use unittest.mock to patch HTTP calls, so no running services
are needed.  The test suite verifies:

  1. seed_document_sources calls the client the expected number of times.
  2. seed_documents calls the client the expected number of times.
  3. submit_batch_jobs calls the client once per document.
  4. export_jobs writes a JSON file into the exports directory.
"""

from __future__ import annotations

import json
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from ingestion_utils.seed_data import DOCUMENT_SOURCES, DOCUMENTS
from ingestion_utils.seeder import seed_document_sources, seed_documents, submit_batch_jobs
from ingestion_utils.exporter import export_jobs


class TestSeedDocumentSources:
    def test_seeds_all_baseline_sources(self):
        """seed_document_sources should call create_document_source once per seed entry."""
        mock_client = MagicMock()
        mock_client.create_document_source.side_effect = lambda src: src

        result = seed_document_sources(mock_client)

        assert mock_client.create_document_source.call_count == len(DOCUMENT_SOURCES)
        assert len(result) == len(DOCUMENT_SOURCES)

    def test_tolerates_partial_failures(self):
        """seed_document_sources should continue seeding even if some calls fail."""
        mock_client = MagicMock()
        mock_client.create_document_source.side_effect = [
            DOCUMENT_SOURCES[0],
            Exception("connection refused"),
            DOCUMENT_SOURCES[2],
        ]

        result = seed_document_sources(mock_client)
        # Only successfully created records are returned; failures are skipped
        assert len(result) == 2


class TestSeedDocuments:
    def test_seeds_all_baseline_documents(self):
        """seed_documents should call create_document once per seed entry."""
        mock_client = MagicMock()
        mock_client.create_document.side_effect = lambda doc: doc

        result = seed_documents(mock_client)

        assert mock_client.create_document.call_count == len(DOCUMENTS)
        assert len(result) == len(DOCUMENTS)


class TestSubmitBatchJobs:
    def test_submits_one_job_per_document(self):
        """submit_batch_jobs should call submit_ingestion_job once per document."""
        mock_client = MagicMock()
        job_template = {"id": "job-x", "processingStatus": "PENDING"}
        mock_client.submit_ingestion_job.side_effect = [
            {**job_template, "id": f"job-{i}"} for i in range(len(DOCUMENTS))
        ]

        result = submit_batch_jobs(mock_client)

        assert mock_client.submit_ingestion_job.call_count == len(DOCUMENTS)
        assert len(result) == len(DOCUMENTS)
        assert all(j.get("processingStatus") == "PENDING" for j in result)

    def test_submits_jobs_for_specified_ids_only(self):
        """submit_batch_jobs with explicit doc_ids submits for those IDs only."""
        mock_client = MagicMock()
        mock_client.submit_ingestion_job.side_effect = lambda doc_id, **kw: {
            "id": f"job-for-{doc_id}",
            "documentId": doc_id,
            "processingStatus": "PENDING",
        }

        result = submit_batch_jobs(mock_client, doc_ids=["doc-1001", "doc-1002"])

        assert mock_client.submit_ingestion_job.call_count == 2
        assert len(result) == 2


class TestExportJobs:
    def test_writes_json_file(self):
        """export_jobs should write a JSON file containing the job records."""
        mock_client = MagicMock()
        fake_jobs = [
            {"id": "job-2001", "documentId": "doc-1001", "processingStatus": "COMPLETED"},
        ]
        mock_client.list_document_jobs.return_value = fake_jobs

        with tempfile.TemporaryDirectory() as tmpdir:
            path = export_jobs(mock_client, "doc-1001", output_dir=tmpdir, fmt="json")
            assert os.path.exists(path)
            with open(path) as fh:
                data = json.load(fh)
            assert data == fake_jobs
