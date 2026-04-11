"""
seed_data.py — Baseline sample data for DocumentSource and Document seeding.

These payloads are intentionally aligned with the shared domain model used
across java-1, java-2, golang-1, and react-web-1.  Keep the IDs, tags, and
field names in sync with example payloads in other repositories.

Shared example IDs (documented in PRD §6.3):
  Document:  doc-1001  (Quarterly Risk Summary)
  Job:       job-2001  (submitted by system-seeder)
  Source:    src-hr-shared-drive, src-legal-archive, src-finance-reports
"""

# ---------------------------------------------------------------------------
# DocumentSource baseline seeds
# ---------------------------------------------------------------------------

DOCUMENT_SOURCES: list[dict] = [
    {
        "id": "src-hr-shared-drive",
        "name": "HR Shared Drive",
        "type": "SHARED_DRIVE",
        "owner": "hr-team",
        "location": "smb://fileserver/hr",
        "active": True,
    },
    {
        "id": "src-legal-archive",
        "name": "Legal Archive",
        "type": "DOCUMENT_ARCHIVE",
        "owner": "legal-team",
        "location": "https://legal.internal/archive",
        "active": True,
    },
    {
        "id": "src-finance-reports",
        "name": "Finance Reports Repository",
        "type": "REPORT_STORE",
        "owner": "finance-team",
        "location": "s3://finance-bucket/reports",
        "active": True,
    },
]

# ---------------------------------------------------------------------------
# Document baseline seeds
# ---------------------------------------------------------------------------

DOCUMENTS: list[dict] = [
    {
        "id": "doc-1001",
        "title": "Quarterly Risk Summary",
        "sourceId": "src-hr-shared-drive",
        "tags": ["finance", "rag-test", "baseline"],
        "version": "1.0",
        "contentType": "application/pdf",
        "metadata": {"department": "Risk", "owner": "ops-team"},
    },
    {
        "id": "doc-1002",
        "title": "Employment Policy Handbook",
        "sourceId": "src-hr-shared-drive",
        "tags": ["hr", "policy", "baseline"],
        "version": "2.1",
        "contentType": "application/pdf",
        "metadata": {"department": "HR", "owner": "hr-team"},
    },
    {
        "id": "doc-1003",
        "title": "Contract Template v3",
        "sourceId": "src-legal-archive",
        "tags": ["legal", "contract", "rag-test"],
        "version": "3.0",
        "contentType": "application/msword",
        "metadata": {"department": "Legal", "owner": "legal-team"},
    },
    {
        "id": "doc-1004",
        "title": "Annual Finance Report 2023",
        "sourceId": "src-finance-reports",
        "tags": ["finance", "annual", "rag-test"],
        "version": "1.0",
        "contentType": "application/pdf",
        "metadata": {"department": "Finance", "owner": "finance-team"},
    },
    {
        "id": "doc-1005",
        "title": "Data Retention Policy",
        "sourceId": "src-legal-archive",
        "tags": ["legal", "policy", "baseline"],
        "version": "1.2",
        "contentType": "text/plain",
        "metadata": {"department": "Legal", "owner": "compliance-team"},
    },
]
