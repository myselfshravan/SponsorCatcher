#!/usr/bin/env python3
"""SponsorCatcher - Speed-optimized sponsor slot booking automation."""

from src.sponsorcatcher.actions.booking import BookingAction
from src.sponsorcatcher.browser import create_driver
from src.sponsorcatcher.config import Config


def main() -> None:
    """Main entry point."""
    print("=" * 50)
    print("SponsorCatcher - Starting...")
    print("=" * 50)

    # Load configuration
    try:
        config = Config.load()
    except KeyError as e:
        print(f"Configuration error: {e}")
        return

    print(f"Target: {config.sponsor_url}")
    print()

    # Create speed-optimized browser
    driver = create_driver(config)

    try:
        # Execute booking workflow
        action = BookingAction(driver, config)
        action.execute()

        print()
        print("=" * 50)
        print("Automation complete!")
        print("Browser left open for manual steps.")
        print("Close browser manually when done.")
        print("=" * 50)

        # Keep browser open - user handles rest manually
        input("Press Enter to close browser...")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
