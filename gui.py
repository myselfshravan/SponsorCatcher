#!/usr/bin/env python3
"""SponsorCatcher GUI - Main entry point for packaged application."""

from src.sponsorcatcher.gui import SponsorCatcherApp


def main() -> None:
    """Launch the SponsorCatcher GUI."""
    app = SponsorCatcherApp()
    app.run()


if __name__ == "__main__":
    main()
