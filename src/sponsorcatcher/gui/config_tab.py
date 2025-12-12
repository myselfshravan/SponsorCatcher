"""Configuration tab for the GUI."""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from typing import Callable

import yaml

from ..paths import get_config_path, get_env_path, get_app_data_dir


class ConfigTab(ttk.Frame):
    """Configuration tab with login, search, and payment settings."""

    def __init__(self, parent: ttk.Notebook, on_config_change: Callable | None = None) -> None:
        """Initialize the configuration tab.

        Args:
            parent: Parent notebook widget.
            on_config_change: Callback when config changes.
        """
        super().__init__(parent)
        self.on_config_change = on_config_change

        # Create scrollable frame
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind mouse wheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Create form fields
        self._create_widgets()

    def _on_mousewheel(self, event: tk.Event) -> None:
        """Handle mouse wheel scrolling."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _create_widgets(self) -> None:
        """Create all form widgets."""
        padding = {"padx": 10, "pady": 5}

        # Login Credentials Section
        login_frame = ttk.LabelFrame(self.scrollable_frame, text="Login Credentials", padding=10)
        login_frame.pack(fill="x", **padding)

        ttk.Label(login_frame, text="Email:").grid(row=0, column=0, sticky="w", pady=2)
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(login_frame, textvariable=self.email_var, width=40)
        self.email_entry.grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, sticky="w", pady=2)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(login_frame, textvariable=self.password_var, width=40, show="*")
        self.password_entry.grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(login_frame, text="Sponsor URL:").grid(row=2, column=0, sticky="w", pady=2)
        self.sponsor_url_var = tk.StringVar(value="https://members.manufacturedhousing.org/sponsorships/become-a-sponsor")
        self.sponsor_url_entry = ttk.Entry(login_frame, textvariable=self.sponsor_url_var, width=40)
        self.sponsor_url_entry.grid(row=2, column=1, sticky="ew", pady=2)

        login_frame.columnconfigure(1, weight=1)

        # Search Section
        search_frame = ttk.LabelFrame(self.scrollable_frame, text="Search", padding=10)
        search_frame.pack(fill="x", **padding)

        ttk.Label(search_frame, text="Keyword:").grid(row=0, column=0, sticky="w", pady=2)
        self.keyword_var = tk.StringVar()
        self.keyword_entry = ttk.Entry(search_frame, textvariable=self.keyword_var, width=40)
        self.keyword_entry.grid(row=0, column=1, sticky="ew", pady=2)

        search_frame.columnconfigure(1, weight=1)

        # Payment Details Section
        payment_frame = ttk.LabelFrame(self.scrollable_frame, text="Payment Details", padding=10)
        payment_frame.pack(fill="x", **padding)

        ttk.Label(payment_frame, text="Name on Card:").grid(row=0, column=0, sticky="w", pady=2)
        self.name_on_card_var = tk.StringVar()
        self.name_on_card_entry = ttk.Entry(payment_frame, textvariable=self.name_on_card_var, width=40)
        self.name_on_card_entry.grid(row=0, column=1, columnspan=3, sticky="ew", pady=2)

        ttk.Label(payment_frame, text="Card Number:").grid(row=1, column=0, sticky="w", pady=2)
        self.card_number_var = tk.StringVar()
        self.card_number_entry = ttk.Entry(payment_frame, textvariable=self.card_number_var, width=40)
        self.card_number_entry.grid(row=1, column=1, columnspan=3, sticky="ew", pady=2)

        ttk.Label(payment_frame, text="CVV:").grid(row=2, column=0, sticky="w", pady=2)
        self.cvv_var = tk.StringVar()
        self.cvv_entry = ttk.Entry(payment_frame, textvariable=self.cvv_var, width=6, show="*")
        self.cvv_entry.grid(row=2, column=1, sticky="w", pady=2)

        ttk.Label(payment_frame, text="Billing Zip:").grid(row=2, column=2, sticky="w", pady=2, padx=(10, 0))
        self.billing_zip_var = tk.StringVar()
        self.billing_zip_entry = ttk.Entry(payment_frame, textvariable=self.billing_zip_var, width=10)
        self.billing_zip_entry.grid(row=2, column=3, sticky="w", pady=2)

        ttk.Label(payment_frame, text="Exp Month:").grid(row=3, column=0, sticky="w", pady=2)
        self.exp_month_var = tk.StringVar()
        months = [str(i).zfill(2) for i in range(1, 13)]
        self.exp_month_combo = ttk.Combobox(payment_frame, textvariable=self.exp_month_var, values=months, width=5, state="readonly")
        self.exp_month_combo.grid(row=3, column=1, sticky="w", pady=2)

        ttk.Label(payment_frame, text="Exp Year:").grid(row=3, column=2, sticky="w", pady=2, padx=(10, 0))
        self.exp_year_var = tk.StringVar()
        years = [str(i) for i in range(2024, 2036)]
        self.exp_year_combo = ttk.Combobox(payment_frame, textvariable=self.exp_year_var, values=years, width=6, state="readonly")
        self.exp_year_combo.grid(row=3, column=3, sticky="w", pady=2)

        ttk.Label(payment_frame, text="Confirm Email:").grid(row=4, column=0, sticky="w", pady=2)
        self.confirm_email_var = tk.StringVar()
        self.confirm_email_entry = ttk.Entry(payment_frame, textvariable=self.confirm_email_var, width=40)
        self.confirm_email_entry.grid(row=4, column=1, columnspan=3, sticky="ew", pady=2)

        payment_frame.columnconfigure(1, weight=1)

        # Buttons Section
        button_frame = ttk.Frame(self.scrollable_frame)
        button_frame.pack(fill="x", **padding)

        self.save_btn = ttk.Button(button_frame, text="Save", command=self._quick_save)
        self.save_btn.pack(side="left", padx=5)

        self.save_as_btn = ttk.Button(button_frame, text="Save As...", command=self._save_config)
        self.save_as_btn.pack(side="left", padx=5)

        self.load_btn = ttk.Button(button_frame, text="Load", command=self._load_config)
        self.load_btn.pack(side="left", padx=5)

        self.load_env_btn = ttk.Button(button_frame, text="Load .env", command=self._load_from_env)
        self.load_env_btn.pack(side="left", padx=5)

    def _quick_save(self) -> None:
        """Quick save to default config path without prompting."""
        if self.save_to_default_path():
            config_path = get_config_path()
            messagebox.showinfo("Saved", f"Configuration saved to:\n{config_path}")
        else:
            messagebox.showerror("Error", "Failed to save configuration")

    def _save_config(self) -> None:
        """Save current configuration to YAML file."""
        default_path = get_config_path()
        file_path = filedialog.asksaveasfilename(
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")],
            initialfile=default_path.name,
            initialdir=str(default_path.parent),
        )
        if not file_path:
            return

        config = self.get_config()
        try:
            with open(file_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False)
            messagebox.showinfo("Success", f"Configuration saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")

    def save_to_default_path(self) -> bool:
        """Save config to the default path without prompting.

        Returns:
            True if saved successfully.
        """
        config = self.get_config()
        try:
            config_path = get_config_path()
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False)
            return True
        except Exception:
            return False

    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        default_path = get_config_path()
        file_path = filedialog.askopenfilename(
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")],
            initialdir=str(default_path.parent),
        )
        if not file_path:
            return

        try:
            with open(file_path) as f:
                config = yaml.safe_load(f)
            self.set_config(config)
            messagebox.showinfo("Success", f"Configuration loaded from {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {e}")

    def _load_from_env(self) -> None:
        """Load credentials from .env file."""
        env_path = get_env_path()
        if not env_path.exists():
            # Also check current directory as fallback
            env_path = Path(".env")
            if not env_path.exists():
                messagebox.showwarning("Warning", f".env file not found.\nChecked: {get_env_path()} and ./.env")
                return

        try:
            env_vars = {}
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip().strip('"').strip("'")

            # Support both old (MHI_*) and new (SPONSOR_*) env var names
            email = env_vars.get("SPONSOR_EMAIL") or env_vars.get("MHI_EMAIL")
            password = env_vars.get("SPONSOR_PASSWORD") or env_vars.get("MHI_PASSWORD")
            sponsor_url = env_vars.get("SPONSOR_URL") or env_vars.get("MHI_SPONSOR_URL")

            if email:
                self.email_var.set(email)
            if password:
                self.password_var.set(password)
            if sponsor_url:
                self.sponsor_url_var.set(sponsor_url)

            messagebox.showinfo("Success", f"Credentials loaded from {env_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load .env: {e}")

    def get_config(self) -> dict:
        """Get current configuration as dictionary.

        Returns:
            Configuration dictionary.
        """
        # Allow comma-separated keywords for prioritization
        raw_keywords = self.keyword_var.get()
        keyword_list = [kw.strip() for kw in raw_keywords.split(",") if kw.strip()]
        if not keyword_list:
            keyword_list = [raw_keywords.strip()]

        return {
            "login": {
                "email": self.email_var.get(),
                "password": self.password_var.get(),
                "sponsor_url": self.sponsor_url_var.get(),
            },
            "search_keyword": self.keyword_var.get(),
            "search_keywords": keyword_list,
            "payment": {
                "name_on_card": self.name_on_card_var.get(),
                "card_number": self.card_number_var.get(),
                "cvv": self.cvv_var.get(),
                "exp_month": self.exp_month_var.get(),
                "exp_year": self.exp_year_var.get(),
                "billing_zip": self.billing_zip_var.get(),
                "confirmation_email": self.confirm_email_var.get(),
            },
        }

    def set_config(self, config: dict) -> None:
        """Set configuration from dictionary.

        Args:
            config: Configuration dictionary.
        """
        if "login" in config:
            login = config["login"]
            self.email_var.set(login.get("email", ""))
            self.password_var.set(login.get("password", ""))
            self.sponsor_url_var.set(login.get("sponsor_url", ""))

        if "search_keywords" in config and config["search_keywords"]:
            # Join back into a comma-separated string for the field
            self.keyword_var.set(", ".join(config["search_keywords"]))
        elif "search_keyword" in config:
            self.keyword_var.set(config["search_keyword"])

        if "payment" in config:
            payment = config["payment"]
            self.name_on_card_var.set(payment.get("name_on_card", ""))
            self.card_number_var.set(payment.get("card_number", ""))
            self.cvv_var.set(payment.get("cvv", ""))
            self.exp_month_var.set(payment.get("exp_month", ""))
            self.exp_year_var.set(payment.get("exp_year", ""))
            self.billing_zip_var.set(payment.get("billing_zip", ""))
            self.confirm_email_var.set(payment.get("confirmation_email", ""))

    def validate_config(self) -> tuple[bool, str]:
        """Validate current configuration.

        Returns:
            Tuple of (is_valid, error_message).
        """
        config = self.get_config()
        errors = []

        # Check required fields
        if not config["login"]["email"]:
            errors.append("Email is required")
        if not config["login"]["password"]:
            errors.append("Password is required")
        if not config["search_keyword"]:
            errors.append("Search keyword is required")
        if not config["payment"]["name_on_card"]:
            errors.append("Name on card is required")
        if not config["payment"]["card_number"]:
            errors.append("Card number is required")
        if not config["payment"]["cvv"]:
            errors.append("CVV is required")
        if not config["payment"]["exp_month"]:
            errors.append("Expiration month is required")
        if not config["payment"]["exp_year"]:
            errors.append("Expiration year is required")
        if not config["payment"]["billing_zip"]:
            errors.append("Billing zip is required")
        if not config["payment"]["confirmation_email"]:
            errors.append("Confirmation email is required")

        if errors:
            return False, "\n".join(errors)
        return True, ""
