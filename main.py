#!/usr/bin/env python3
"""SponsorCatcher - Speed-optimized sponsor slot booking automation."""

import sys


def run_gui() -> None:
    """Launch the GUI application."""
    from src.sponsorcatcher.gui import SponsorCatcherApp
    app = SponsorCatcherApp()
    app.run()


def run_cli() -> None:
    """Run CLI mode."""
    from src.sponsorcatcher.actions.booking import BookingAction
    from src.sponsorcatcher.browser import create_driver
    from src.sponsorcatcher.config import BookingConfig, Config

    print("=" * 50)
    print("SponsorCatcher - Starting...")
    print("=" * 50)

    # Load login configuration from .env
    try:
        config = Config.load()
    except KeyError as e:
        print(f"Configuration error: {e}")
        return

    # Load booking configuration from config.yaml
    try:
        booking_config = BookingConfig.load()
    except FileNotFoundError as e:
        print(f"Configuration error: {e}")
        return

    print(f"Target: {config.sponsor_url}")
    print(f"Search: {booking_config.search_keyword}")
    print()

    # Check for --submit flag
    submit_order = "--submit" in sys.argv

    if submit_order:
        print("WARNING: --submit flag detected!")
        print("This will ACTUALLY SUBMIT the order!")
        confirm = input("Type 'YES' to confirm: ")
        if confirm != "YES":
            print("Aborted.")
            return

    # Create speed-optimized browser
    driver = create_driver(config)

    try:
        # Execute booking workflow
        action = BookingAction(driver, config, booking_config)
        success = action.execute(submit_order=submit_order)

        print()
        print("=" * 50)
        if success:
            print("Automation complete!")
            if not submit_order:
                print("Review the payment form and submit manually.")
        else:
            print("Automation encountered an error.")
            print("Check the browser for details.")
        print("=" * 50)

        # Keep browser open for manual review
        input("Press Enter to close browser...")

    finally:
        driver.quit()


def main() -> None:
    """Main entry point."""
    # Check for --gui flag
    if "--gui" in sys.argv:
        run_gui()
        return

    run_cli()


if __name__ == "__main__":
    main()
