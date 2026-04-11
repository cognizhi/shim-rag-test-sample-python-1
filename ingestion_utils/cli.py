"""
cli.py — Command-line interface for ingestion_utils.

Commands:
  seed_documents          seed DocumentSources + Documents into java-1
  submit_batch_jobs       submit IngestionJobs for all seeded Documents
  export_jobs             export IngestionJobs for a Document to JSON or CSV
  export_reports          export a Report record from java-2 to JSON or CSV
  run_integration_scenario  run the full baseline integration workflow

Usage examples:
  python -m ingestion_utils.cli seed_documents
  python -m ingestion_utils.cli submit_batch_jobs
  python -m ingestion_utils.cli export_jobs --document-id doc-1001 --format csv
  python -m ingestion_utils.cli export_reports --report-id rpt-3001
  python -m ingestion_utils.cli run_integration_scenario
"""

from __future__ import annotations

import argparse
import sys

from .client import DEFAULT_JAVA1_URL, DEFAULT_JAVA2_URL, IngestionClient, ReportingClient
from .exporter import export_jobs as _export_jobs
from .exporter import export_reports as _export_reports
from .seeder import seed_document_sources, seed_documents, submit_batch_jobs
from .scenario import run_integration_scenario


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ingestion-utils",
        description=(
            "Seeder and integration utility for the Document Ingestion ecosystem.\n"
            "See README.md for context on the full multi-repository workflow."
        ),
    )

    # Global flags shared by all sub-commands
    parser.add_argument(
        "--java1-url",
        default=DEFAULT_JAVA1_URL,
        metavar="URL",
        help=f"Base URL for java-1 Document Ingestion API (default: {DEFAULT_JAVA1_URL})",
    )
    parser.add_argument(
        "--java2-url",
        default=DEFAULT_JAVA2_URL,
        metavar="URL",
        help=f"Base URL for java-2 Reporting API (default: {DEFAULT_JAVA2_URL})",
    )

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # ------------------------------------------------------------------ #
    # seed_documents                                                        #
    # ------------------------------------------------------------------ #
    sub.add_parser(
        "seed_documents",
        help="Seed baseline DocumentSources and Documents into java-1",
    )

    # ------------------------------------------------------------------ #
    # submit_batch_jobs                                                     #
    # ------------------------------------------------------------------ #
    batch_p = sub.add_parser(
        "submit_batch_jobs",
        help="Submit IngestionJobs for all baseline Documents",
    )
    batch_p.add_argument(
        "--requested-by",
        default="python-seeder",
        help="Value for requestedBy field (default: python-seeder)",
    )

    # ------------------------------------------------------------------ #
    # export_jobs                                                           #
    # ------------------------------------------------------------------ #
    export_jobs_p = sub.add_parser(
        "export_jobs",
        help="Export IngestionJobs for a Document to JSON or CSV",
    )
    export_jobs_p.add_argument("--document-id", required=True, metavar="ID")
    export_jobs_p.add_argument(
        "--format", dest="fmt", choices=["json", "csv"], default="json"
    )
    export_jobs_p.add_argument(
        "--output-dir", default="exports", metavar="DIR"
    )

    # ------------------------------------------------------------------ #
    # export_reports                                                        #
    # ------------------------------------------------------------------ #
    export_reports_p = sub.add_parser(
        "export_reports",
        help="Export a Report from java-2 to JSON or CSV",
    )
    export_reports_p.add_argument("--report-id", required=True, metavar="ID")
    export_reports_p.add_argument(
        "--format", dest="fmt", choices=["json", "csv"], default="json"
    )
    export_reports_p.add_argument(
        "--output-dir", default="exports", metavar="DIR"
    )

    # ------------------------------------------------------------------ #
    # run_integration_scenario                                              #
    # ------------------------------------------------------------------ #
    scenario_p = sub.add_parser(
        "run_integration_scenario",
        help="Run the full baseline integration workflow end-to-end",
    )
    scenario_p.add_argument(
        "--output-dir", default="exports", metavar="DIR",
        help="Directory for exported files (default: exports/)",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    ingestion_client = IngestionClient(args.java1_url)
    reporting_client = ReportingClient(args.java2_url)

    if args.command == "seed_documents":
        seed_document_sources(ingestion_client)
        seed_documents(ingestion_client)

    elif args.command == "submit_batch_jobs":
        submit_batch_jobs(ingestion_client, requested_by=args.requested_by)

    elif args.command == "export_jobs":
        _export_jobs(
            ingestion_client,
            doc_id=args.document_id,
            output_dir=args.output_dir,
            fmt=args.fmt,
        )

    elif args.command == "export_reports":
        _export_reports(
            reporting_client,
            report_id=args.report_id,
            output_dir=args.output_dir,
            fmt=args.fmt,
        )

    elif args.command == "run_integration_scenario":
        run_integration_scenario(
            java1_url=args.java1_url,
            java2_url=args.java2_url,
            output_dir=args.output_dir,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
