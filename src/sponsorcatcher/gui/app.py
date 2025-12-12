"""Main application window for SponsorCatcher GUI."""

import tkinter as tk
from tkinter import ttk

from .config_tab import ConfigTab
from .run_tab import RunTab
from ..paths import get_config_path, get_env_path, get_app_data_dir, is_packaged


class SponsorCatcherApp:
    """Main application window."""

    def __init__(self) -> None:
        """Initialize the application."""
        self.root = tk.Tk()
        self.root.title("SponsorCatcher")
        self.root.geometry("600x700")
        self.root.minsize(500, 500)

        # Set app icon if available (ignore if not found)
        try:
            self.root.iconbitmap("assets/icon.ico")
        except Exception:
            pass

        self._create_widgets()
        self._load_initial_config()

    def _create_widgets(self) -> None:
        """Create all application widgets."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create tabs
        self.config_tab = ConfigTab(self.notebook)
        self.run_tab = RunTab(
            self.notebook,
            get_config=self.config_tab.get_config,
            validate_config=self.config_tab.validate_config,
        )

        self.notebook.add(self.config_tab, text="Configuration")
        self.notebook.add(self.run_tab, text="Run Automation")

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief="sunken",
            anchor="w",
        )
        self.status_bar.pack(fill="x", side="bottom")

    def _load_initial_config(self) -> None:
        """Load initial configuration from files if available."""
        from pathlib import Path
        import yaml

        loaded_from = []

        # Try to load from config.yaml (check both app data dir and current dir)
        config_path = get_config_path()
        if not config_path.exists():
            config_path = Path("config.yaml")

        if config_path.exists():
            try:
                with open(config_path) as f:
                    config = yaml.safe_load(f)
                if config:
                    self.config_tab.set_config(config)
                    loaded_from.append(str(config_path))
            except Exception:
                pass

        # Try to load credentials from .env (check both app data dir and current dir)
        env_path = get_env_path()
        if not env_path.exists():
            env_path = Path(".env")

        if env_path.exists():
            try:
                env_vars = {}
                with open(env_path) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            env_vars[key.strip()] = value.strip().strip('"').strip("'")

                # Update only login fields from .env (support both old and new var names)
                current_config = self.config_tab.get_config()
                email = env_vars.get("SPONSOR_EMAIL") or env_vars.get("MHI_EMAIL")
                password = env_vars.get("SPONSOR_PASSWORD") or env_vars.get("MHI_PASSWORD")
                sponsor_url = env_vars.get("SPONSOR_URL") or env_vars.get("MHI_SPONSOR_URL")

                if email:
                    current_config["login"]["email"] = email
                if password:
                    current_config["login"]["password"] = password
                if sponsor_url:
                    current_config["login"]["sponsor_url"] = sponsor_url

                self.config_tab.set_config(current_config)
                loaded_from.append(str(env_path))
            except Exception:
                pass

        if loaded_from:
            self.status_var.set(f"Loaded: {', '.join(loaded_from)}")
        else:
            # Show app data dir in status for reference
            self.status_var.set(f"Config dir: {get_app_data_dir()}")

    def run(self) -> None:
        """Start the application main loop."""
        self.root.mainloop()


def main() -> None:
    """Main entry point for GUI."""
    app = SponsorCatcherApp()
    app.run()


if __name__ == "__main__":
    main()
