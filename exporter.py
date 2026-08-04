"""
Exporter module - Save results to JSON, CSV, and PDF formats.
"""

import csv
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class Exporter:
    """Export IP tracking results to various file formats."""

    @staticmethod
    def to_json(data: Dict[str, Any], filepath: str) -> None:
        """Save data to a JSON file."""
        with open(filepath, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=4, ensure_ascii=False)
        logger.info(f"Saved JSON report: {filepath}")

    @staticmethod
    def to_csv(data: Dict[str, Any], filepath: str) -> None:
        """Save data to a CSV file (single row)."""
        with open(filepath, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(data.keys())
            writer.writerow(data.values())
        logger.info(f"Saved CSV report: {filepath}")

    @staticmethod
    def batch_to_csv(records: List[Dict[str, Any]], filepath: str) -> None:
        """Save multiple records to a single CSV file."""
        if not records:
            return
        keys = sorted({k for r in records for k in r.keys()})
        with open(filepath, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=keys)
            writer.writeheader()
            for r in records:
                writer.writerow(r)
        logger.info(f"Saved batch CSV report: {filepath}")

    @staticmethod
    def to_pdf(data: Dict[str, Any], filepath: str) -> None:
        """
        Export data to a PDF report using reportlab (optional dependency).

        Args:
            data (Dict[str, Any]): Data to export.
            filepath (str): Output PDF path.
        """
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
        except ImportError:
            logger.error("reportlab is not installed. Run: pip install reportlab")
            raise

        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4
        y = height - 60

        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, y, "IP Tracker Report")
        y -= 30

        c.setFont("Helvetica", 11)
        for key, value in data.items():
            if y < 60:
                c.showPage()
                y = height - 60
                c.setFont("Helvetica", 11)
            line = f"{key}: {value}"
            c.drawString(50, y, line[:110])
            y -= 18

        c.save()
        logger.info(f"Saved PDF report: {filepath}")
