"""Platform-specific paths for configuration and data storage."""

import os
import sys
from pathlib import Path

APP_NAME = "SponsorCatcher"


def get_app_data_dir() -> Path:
    """Get the application data directory for storing config files.

    Returns platform-specific directory:
    - Windows: %APPDATA%/SponsorCatcher
    - macOS: ~/Library/Application Support/SponsorCatcher
    - Linux: ~/.config/SponsorCatcher

    Returns:
        Path to application data directory (created if doesn't exist).
    """
    if sys.platform == "win32":
        # Windows: %APPDATA%/SponsorCatcher
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        # macOS: ~/Library/Application Support/SponsorCatcher
        base = Path.home() / "Library" / "Application Support"
    else:
        # Linux/other: ~/.config/SponsorCatcher
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))

    app_dir = base / APP_NAME
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_config_path() -> Path:
    """Get the path to the config.yaml file.

    For development (running from source), uses current directory.
    For packaged apps, uses the app data directory.

    Returns:
        Path to config.yaml file.
    """
    # Check if running as packaged app (PyInstaller)
    if getattr(sys, "frozen", False):
        # Running as packaged app - use app data directory
        return get_app_data_dir() / "config.yaml"
    else:
        # Running from source - use current directory
        return Path("config.yaml")


def get_env_path() -> Path:
    """Get the path to the .env file.

    For development (running from source), uses current directory.
    For packaged apps, uses the app data directory.

    Returns:
        Path to .env file.
    """
    # Check if running as packaged app (PyInstaller)
    if getattr(sys, "frozen", False):
        # Running as packaged app - use app data directory
        return get_app_data_dir() / ".env"
    else:
        # Running from source - use current directory
        return Path(".env")


def is_packaged() -> bool:
    """Check if running as a packaged application.

    Returns:
        True if running as PyInstaller executable.
    """
    return getattr(sys, "frozen", False)
