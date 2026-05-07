"""
client.py — HTTP client wrappers for the Document Ingestion REST API (java-1)
and the Reporting / Validation API (java-2).

All functions raise requests.HTTPError on non-2xx responses.
"""

import requests

DEFAULT_JAVA1_URL = "http://localhost:8081"
DEFAULT_JAVA2_URL = "http://localhost:8082"


class IngestionClient:
    """
    Thin HTTP client for the java-1 Document Ingestion API.

    Domain entities created and managed by this client:
    - DocumentSource
    - Document
    - IngestionJob  (ProcessingStatus: PENDING / RUNNING / COMPLETED / FAILED)
    """

    
    def __init__(self, base_url: str = DEFAULT_JAVA1_URL):
        self.base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})

    # ------------------------------------------------------------------ #
    # DocumentSource endpoints                                             #
    # ------------------------------------------------------------------ #

    def create_document_source(self, payload: dict) -> dict:
        """POST /document-sources — create a new DocumentSource."""
        resp = self._session.post(f"{self.base_url}/document-sources", json=payload)
        resp.raise_for_status()
        return resp.json()

    
    
    def list_document_sources(self) -> list:
        """GET /document-sources — list all DocumentSources."""
        resp = self._session.get(f"{self.base_url}/document-sources")
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------ #
    # Document endpoints                                                   #
    # ------------------------------------------------------------------ #

    def create_document(self, payload: dict) -> dict:
        """POST /documents — create a new Document."""
        resp = self._session.post(f"{self.base_url}/documents", json=payload)
        resp.raise_for_status()
        return resp.json()

    def get_document(self, doc_id: str) -> dict:
        """GET /documents/{id} — retrieve Document metadata."""
        resp = self._session.get(f"{self.base_url}/documents/{doc_id}")
        resp.raise_for_status()
        return resp.json()

    def list_documents(self) -> list:
        """GET /documents — list all Documents."""
        resp = self._session.get(f"{self.base_url}/documents")
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------ #
    # IngestionJob endpoints                                               #
    # ------------------------------------------------------------------ #

    def submit_ingestion_job(self, doc_id: str, requested_by: str = "python-seeder") -> dict:
        """POST /documents/{id}/ingestion-jobs — submit an IngestionJob."""
        payload = {"requestedBy": requested_by}
        resp = self._session.post(
            f"{self.base_url}/documents/{doc_id}/ingestion-jobs", json=payload
        )
        resp.raise_for_status()
        return resp.json()

    def get_job_status(self, job_id: str) -> dict:
        """GET /ingestion-jobs/{id} — fetch IngestionJob and ProcessingStatus."""
        resp = self._session.get(f"{self.base_url}/ingestion-jobs/{job_id}")
        resp.raise_for_status()
        return resp.json()

    def list_document_jobs(self, doc_id: str) -> list:
        """GET /documents/{id}/ingestion-jobs — list all jobs for a Document."""
        resp = self._session.get(f"{self.base_url}/documents/{doc_id}/ingestion-jobs")
        resp.raise_for_status()
        return resp.json()

    def health(self) -> dict:
        """GET /health — readiness check."""
        resp = self._session.get(f"{self.base_url}/health")
        resp.raise_for_status()
        return resp.json()


class ReportingClient:
    """
    Thin HTTP client for the java-2 Reporting / Validation API.

    Domain entities created and managed by this client:
    - Report  (types: INGESTION_SUMMARY, VALIDATION_SUMMARY)
    - ValidationResult
    """

    def __init__(self, base_url: str = DEFAULT_JAVA2_URL):
        self.base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})

    def request_report(self, payload: dict) -> dict:
        """POST /report-requests — request a new Report."""
        resp = self._session.post(f"{self.base_url}/report-requests", json=payload)
        resp.raise_for_status()
        return resp.json()

    def get_report(self, report_id: str) -> dict:
        """GET /reports/{id} — retrieve a Report."""
        resp = self._session.get(f"{self.base_url}/reports/{report_id}")
        resp.raise_for_status()
        return resp.json()

    def submit_validation(self, payload: dict) -> dict:
        """POST /validation-results — validate a document payload."""
        resp = self._session.post(f"{self.base_url}/validation-results", json=payload)
        resp.raise_for_status()
        return resp.json()

    def get_validation_results(self, doc_id: str) -> list:
        """GET /validation-results/{documentId} — retrieve ValidationResults."""
        resp = self._session.get(f"{self.base_url}/validation-results/{doc_id}")
        resp.raise_for_status()
        return resp.json()

    def health(self) -> dict:
        """GET /health — readiness check."""
        resp = self._session.get(f"{self.base_url}/health")
        resp.raise_for_status()
        return resp.json()
