#!/usr/bin/env python3
"""Build script for SponsorCatcher using PyInstaller.

Usage:
    python build_exe.py           # Build with default options
    python build_exe.py --onefile # Build single-file executable

Outputs:
    - Windows: dist/SponsorCatcher.exe
    - macOS: dist/SponsorCatcher.app
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


def get_version() -> str:
    """Get version from git tag or default."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--always"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception:
        return "0.1.0"


def build_executable(onefile: bool = False) -> None:
    """Build the executable using PyInstaller.

    Args:
        onefile: If True, create a single-file executable.
    """
    version = get_version()
    system = platform.system()

    print(f"Building SponsorCatcher {version} for {system}...")
    print(f"Mode: {'single-file' if onefile else 'folder'}")

    # Base PyInstaller command
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=SponsorCatcher",
        "--windowed",  # No console window (GUI app)
        "--noconfirm",  # Replace output directory without asking
        "--clean",  # Clean PyInstaller cache
    ]

    # Add one-file option if requested
    if onefile:
        cmd.append("--onefile")

    # Add data files
    # Include config.yaml template if it exists
    if Path("config.yaml").exists():
        if system == "Windows":
            cmd.append("--add-data=config.yaml;.")
        else:
            cmd.append("--add-data=config.yaml:.")

    # Include firebase credentials if they exist (for gatekeeper)
    if Path("firebase-credentials.json").exists():
        if system == "Windows":
            cmd.append("--add-data=firebase-credentials.json;.")
        else:
            cmd.append("--add-data=firebase-credentials.json:.")

    # Platform-specific options
    if system == "Darwin":  # macOS
        cmd.extend([
            "--osx-bundle-identifier=com.sponsorcatcher.app",
        ])
        # Add icon if it exists
        if Path("assets/icon.icns").exists():
            cmd.append("--icon=assets/icon.icns")
    elif system == "Windows":
        # Add icon if it exists
        if Path("assets/icon.ico").exists():
            cmd.append("--icon=assets/icon.ico")

    # Hidden imports for selenium and tkinter
    cmd.extend([
        "--hidden-import=selenium",
        "--hidden-import=selenium.webdriver",
        "--hidden-import=selenium.webdriver.chrome",
        "--hidden-import=selenium.webdriver.chrome.service",
        "--hidden-import=selenium.webdriver.chrome.options",
        "--hidden-import=selenium.webdriver.common.by",
        "--hidden-import=selenium.webdriver.support.ui",
        "--hidden-import=selenium.webdriver.support.expected_conditions",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.filedialog",
    ])

    # Entry point - use gui.py for GUI mode
    cmd.append("gui.py")

    # Run PyInstaller
    print(f"\nRunning: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)

    if result.returncode != 0:
        print(f"\nBuild failed with exit code {result.returncode}")
        sys.exit(result.returncode)

    # Print output location
    print("\n" + "=" * 50)
    print("Build complete!")

    if system == "Darwin":
        print(f"Output: dist/SponsorCatcher.app")
    elif system == "Windows":
        if onefile:
            print(f"Output: dist/SponsorCatcher.exe")
        else:
            print(f"Output: dist/SponsorCatcher/SponsorCatcher.exe")
    else:
        print(f"Output: dist/SponsorCatcher")

    print("=" * 50)


def main() -> None:
    """Main entry point."""
    onefile = "--onefile" in sys.argv
    build_executable(onefile=onefile)


if __name__ == "__main__":
    main()
