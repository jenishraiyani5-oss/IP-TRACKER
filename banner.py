"""
Banner module - Displays the ASCII art banner for IP Tracker.
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class Banner:
    """Handles displaying the application banner."""

    ASCII_ART = r"""
     ___ ____    _____                _
    |_ _|  _ \  |_   _|_ __ __ _  ___| | _____ _ __
     | || |_) |   | | | '__/ _` |/ __| |/ / _ \ '__|
     | ||  __/    | | | | | (_| | (__|   <  __/ |
    |___|_|       |_| |_|  \__,_|\___|_|\_\___|_|
    """

    @staticmethod
    def display(console: Console) -> None:
        """
        Display a colorful ASCII banner to the terminal.

        Args:
            console (Console): Rich console instance.
        """
        text = Text(Banner.ASCII_ART, style="bold cyan")
        subtitle = Text(
            "Professional IP Geolocation & OSINT Tool  |  For Kali Linux",
            style="bold yellow",
            justify="center",
        )
        author = Text(
            "Educational Use Only — Respect Privacy & Laws",
            style="italic red",
            justify="center",
        )

        console.print(text)
        console.print(subtitle)
        console.print(author)
        console.print("=" * 70, style="bold magenta")
