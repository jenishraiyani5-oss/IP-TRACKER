#!/usr/bin/env python3
"""
IP Tracker - Main entry point.

Usage:
    python3 main.py 8.8.8.8
    python3 main.py --ip 1.1.1.1
    python3 main.py --file ips.txt --json out.json
"""

import argparse
import json
import os
import sys
from typing import Dict, Any, List, Optional

from rich.console import Console
from rich.table import Table
from rich import box

from banner import Banner
from validator import IPValidator
from tracker import (
    IPTracker,
    IPTrackerError,
    APIRateLimitError,
    APIFailureError,
    NoInternetError,
)
from network_tool import NetworkTools
from exporter import Exporter
from utils import setup_logger, spinner, timestamp, ensure_directory


HISTORY_FILE = os.path.expanduser("~/.ip_tracker_history.json")


class IPTrackerApp:
    """Main application controller."""

    def __init__(self) -> None:
        self.console = Console()
        self.logger = setup_logger()
        self.tracker = IPTracker()
        self.validator = IPValidator()
        self.nettools = NetworkTools()

    # ---------------------------- CLI setup ---------------------------- #

    parser.add_argument("--webcam", action="store_true", help="Capture a snap from local webcam")

    # Imports ke paas WebcamTools import kar lein:
from network_tools import NetworkTools, WebcamTools

# process_ip() ya run() method ke andar:
if args.webcam:
    with spinner(self.console, "Accessing Webcam..."):
        if WebcamTools.capture_photo("webcam_snap.jpg"):
            self.console.print("[green]✓ Webcam photo captured as 'webcam_snap.jpg'[/green]")
        else:
            self.console.print("[red]✗ Failed to access webcam.[/red]")

    def parse_args(self) -> argparse.Namespace:
        """Parse command-line arguments."""
        parser = argparse.ArgumentParser(
            prog="ip-tracker",
            description="Professional IP Geolocation and OSINT tool for Kali Linux.",
            epilog="Educational use only. Respect privacy and applicable laws.",
        )
        parser.add_argument("ip_positional", nargs="?", help="IP address to look up")
        parser.add_argument("--ip", dest="ip", help="IP address to look up")
        parser.add_argument("--file", help="Text file containing multiple IPs (one per line)")
        parser.add_argument("--json", help="Export result to JSON file")
        parser.add_argument("--csv", help="Export result to CSV file")
        parser.add_argument("--pdf", help="Export result to PDF file")
        parser.add_argument("--whois", action="store_true", help="Include Whois lookup")
        parser.add_argument("--ping", action="store_true", help="Include ping latency")
        parser.add_argument("--dns", action="store_true", help="Include DNS/reverse DNS info")
        parser.add_argument("--history", action="store_true", help="Show scan history and exit")
        parser.add_argument("--no-banner", action="store_true", help="Hide the ASCII banner")
        return parser.parse_args()

    # ---------------------------- History ---------------------------- #

    def _load_history(self) -> List[Dict[str, Any]]:
        if not os.path.exists(HISTORY_FILE):
            return []
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            return []

    def _save_history(self, entry: Dict[str, Any]) -> None:
        history = self._load_history()
        history.append({"time": timestamp(), **entry})
        history = history[-100:]  # keep last 100
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as fh:
                json.dump(history, fh, indent=2)
        except OSError as exc:
            self.logger.warning(f"Could not save history: {exc}")

    def show_history(self) -> None:
        history = self._load_history()
        if not history:
            self.console.print("[yellow]No scan history found.[/yellow]")
            return
        table = Table(title="Scan History", box=box.ROUNDED)
        table.add_column("Time", style="cyan")
        table.add_column("IP", style="magenta")
        table.add_column("Country", style="green")
        table.add_column("City", style="yellow")
        for e in history[-25:]:
            table.add_row(
                e.get("time", "-"),
                str(e.get("ip", "-")),
                str(e.get("country", "-")),
                str(e.get("city", "-")),
            )
        self.console.print(table)

    # ---------------------------- Rendering ---------------------------- #

    def render_result(self, data: Dict[str, Any]) -> None:
        """Render a single result to the terminal as a formatted table."""
        table = Table(
            title=f"IP Tracker Result — {data.get('ip', 'N/A')} {data.get('flag') or ''}",
            box=box.DOUBLE_EDGE,
            show_lines=False,
            title_style="bold cyan",
        )
        table.add_column("Field", style="bold yellow", no_wrap=True)
        table.add_column("Value", style="white")

        fields = [
            ("IP Address", data.get("ip")),
            ("Country", data.get("country")),
            ("Country Code", data.get("country_code")),
            ("Region/State", data.get("region")),
            ("City", data.get("city")),
            ("ZIP Code", data.get("zip")),
            ("Latitude", data.get("latitude")),
            ("Longitude", data.get("longitude")),
            ("Google Maps", data.get("google_maps")),
            ("ISP", data.get("isp")),
            ("Organization", data.get("organization")),
            ("ASN", data.get("asn")),
            ("Time Zone", data.get("timezone")),
            ("Currency", data.get("currency")),
            ("Calling Code", data.get("calling_code")),
            ("Languages", data.get("languages")),
            ("Network Type", data.get("network_type")),
            ("Reverse DNS", data.get("reverse_dns")),
            ("Ping (ms)", data.get("ping_ms")),
            ("Data Source", data.get("source")),
        ]
        for label, value in fields:
            if value is None or value == "":
                value = "[dim]N/A[/dim]"
            table.add_row(label, str(value))

        self.console.print(table)

        if data.get("whois"):
            self.console.rule("[bold]Whois[/bold]")
            self.console.print(data["whois"][:2000], style="dim")

    # ---------------------------- Enrichment ---------------------------- #

    def enrich(self, data: Dict[str, Any], args: argparse.Namespace) -> Dict[str, Any]:
        """Add optional lookups (dns, ping, whois) based on args."""
        ip = data.get("ip")
        if not ip:
            return data

        if args.dns:
            with spinner(self.console, "Performing DNS lookup..."):
                data["reverse_dns"] = self.nettools.reverse_dns(ip)
                data["dns_info"] = self.nettools.dns_info(ip)

        if args.ping:
            with spinner(self.console, "Pinging target..."):
                data["ping_ms"] = self.nettools.ping(ip)

        if args.whois:
            with spinner(self.console, "Running Whois lookup..."):
                data["whois"] = self.nettools.whois_lookup(ip)

        return data

    # ---------------------------- Core workflow ---------------------------- #

    def process_ip(self, ip: str, args: argparse.Namespace) -> Optional[Dict[str, Any]]:
        """
        Validate and fetch info for a single IP.

        Returns:
            Optional[Dict[str, Any]]: The result dict, or None on failure.
        """
        ip = ip.strip()
        if not ip:
            self.console.print("[red]✗ Empty IP address provided.[/red]")
            return None

        if not self.validator.is_valid_ip(ip):
            self.console.print(f"[red]✗ Invalid IP address:[/red] {ip}")
            return None

        if self.validator.is_private(ip):
            self.console.print(
                f"[yellow]⚠ Warning:[/yellow] {ip} is a private IP. "
                "Geolocation data will not be available."
            )

        try:
            with spinner(self.console, f"Fetching data for {ip}..."):
                data = self.tracker.fetch(ip)
        except NoInternetError:
            self.console.print("[red]✗ No internet connection.[/red]")
            return None
        except APIRateLimitError:
            self.console.print("[red]✗ API rate limit exceeded. Try again later.[/red]")
            return None
        except APIFailureError as exc:
            self.console.print(f"[red]✗ API failure:[/red] {exc}")
            return None
        except IPTrackerError as exc:
            self.console.print(f"[red]✗ Error:[/red] {exc}")
            return None
        except Exception as exc:  # noqa: BLE001
            self.logger.exception("Unexpected error")
            self.console.print(f"[red]✗ Unexpected error:[/red] {exc}")
            return None

        data = self.enrich(data, args)
        self.render_result(data)
        self._save_history(
            {"ip": data.get("ip"), "country": data.get("country"), "city": data.get("city")}
        )
        return data

    # ---------------------------- Export ---------------------------- #

    def export(self, data: Any, args: argparse.Namespace) -> None:
        """Handle export options."""
        try:
            if args.json:
                Exporter.to_json(data, args.json)
                self.console.print(f"[green]✓ JSON saved to {args.json}[/green]")
            if args.csv:
                if isinstance(data, list):
                    Exporter.batch_to_csv(data, args.csv)
                else:
                    Exporter.to_csv(data, args.csv)
                self.console.print(f"[green]✓ CSV saved to {args.csv}[/green]")
            if args.pdf:
                if isinstance(data, list):
                    self.console.print(
                        "[yellow]PDF export supports a single IP; using the first entry.[/yellow]"
                    )
                    Exporter.to_pdf(data[0], args.pdf)
                else:
                    Exporter.to_pdf(data, args.pdf)
                self.console.print(f"[green]✓ PDF saved to {args.pdf}[/green]")
        except Exception as exc:  # noqa: BLE001
            self.console.print(f"[red]✗ Export error:[/red] {exc}")

    # ---------------------------- Runner ---------------------------- #

    def run(self) -> int:
        """Main runner returning an exit code."""
        args = self.parse_args()

        if not args.no_banner:
            Banner.display(self.console)

        if args.history:
            self.show_history()
            return 0

        # Batch mode
        if args.file:
            if not os.path.exists(args.file):
                self.console.print(f"[red]✗ File not found:[/red] {args.file}")
                return 1
            with open(args.file, "r", encoding="utf-8") as fh:
                ips = [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]

            if not ips:
                self.console.print("[red]✗ No IPs found in file.[/red]")
                return 1

            results: List[Dict[str, Any]] = []
            for ip in ips:
                result = self.process_ip(ip, args)
                if result:
                    results.append(result)
            if results:
                self.export(results, args)
            return 0

        # Single IP mode
        ip = args.ip or args.ip_positional
        if not ip:
            try:
                ip = self.console.input("[bold cyan]Enter IP address:[/bold cyan] ").strip()
            except (KeyboardInterrupt, EOFError):
                self.console.print("\n[yellow]Aborted by user.[/yellow]")
                return 130

        result = self.process_ip(ip, args)
        if result:
            self.export(result, args)
            return 0
        return 1


def main() -> None:
    """Program entry point."""
    app = IPTrackerApp()
    try:
        sys.exit(app.run())
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(130)


if __name__ == "__main__":
    main()
