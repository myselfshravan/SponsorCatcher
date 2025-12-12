"""Run automation tab for the GUI."""

import io
import sys
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable


class LogRedirector(io.StringIO):
    """Redirect stdout/stderr to a tkinter Text widget."""

    def __init__(self, text_widget: tk.Text, tag: str = "") -> None:
        """Initialize the log redirector.

        Args:
            text_widget: Text widget to write to.
            tag: Optional tag for text formatting.
        """
        super().__init__()
        self.text_widget = text_widget
        self.tag = tag

    def write(self, string: str) -> int:
        """Write string to text widget.

        Args:
            string: String to write.

        Returns:
            Number of characters written.
        """
        if string:
            self.text_widget.after(0, self._append, string)
        return len(string)

    def _append(self, string: str) -> None:
        """Append string to text widget (thread-safe)."""
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", string, self.tag)
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")

    def flush(self) -> None:
        """Flush the stream (no-op)."""
        pass


class RunTab(ttk.Frame):
    """Run automation tab with log output and controls."""

    def __init__(
        self,
        parent: ttk.Notebook,
        get_config: Callable[[], dict],
        validate_config: Callable[[], tuple[bool, str]],
    ) -> None:
        """Initialize the run tab.

        Args:
            parent: Parent notebook widget.
            get_config: Callback to get current configuration.
            validate_config: Callback to validate configuration.
        """
        super().__init__(parent)
        self.get_config = get_config
        self.validate_config = validate_config

        self._automation_thread: threading.Thread | None = None
        self._stop_flag = threading.Event()
        self._driver = None

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create all widgets."""
        padding = {"padx": 10, "pady": 5}

        # Log output frame
        log_frame = ttk.LabelFrame(self, text="Automation Log", padding=10)
        log_frame.pack(fill="both", expand=True, **padding)

        # Create text widget with scrollbar
        self.log_text = tk.Text(
            log_frame,
            wrap="word",
            state="disabled",
            height=20,
            font=("Consolas", 10) if sys.platform == "win32" else ("Monaco", 10),
        )
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Configure text tags for formatting
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("warning", foreground="orange")

        # Controls frame
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill="x", **padding)

        # Submit checkbox with warning
        self.submit_var = tk.BooleanVar(value=False)
        self.submit_check = ttk.Checkbutton(
            controls_frame,
            text="Enable auto-submit (WARNING: will place order!)",
            variable=self.submit_var,
            command=self._on_submit_toggle,
        )
        self.submit_check.pack(side="left", padx=5)

        # Stop button
        self.stop_btn = ttk.Button(
            controls_frame,
            text="Stop",
            command=self._stop_automation,
            state="disabled",
        )
        self.stop_btn.pack(side="right", padx=5)

        # Start button
        self.start_btn = ttk.Button(
            controls_frame,
            text="Start Automation",
            command=self._start_automation,
        )
        self.start_btn.pack(side="right", padx=5)

        # Clear log button
        self.clear_btn = ttk.Button(
            controls_frame,
            text="Clear Log",
            command=self._clear_log,
        )
        self.clear_btn.pack(side="right", padx=5)

    def _on_submit_toggle(self) -> None:
        """Handle submit checkbox toggle."""
        if self.submit_var.get():
            result = messagebox.askyesno(
                "Warning",
                "Enabling auto-submit will ACTUALLY PLACE THE ORDER!\n\n"
                "Are you sure you want to enable this?",
                icon="warning",
            )
            if not result:
                self.submit_var.set(False)

    def _clear_log(self) -> None:
        """Clear the log output."""
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def _log(self, message: str, tag: str = "") -> None:
        """Add message to log.

        Args:
            message: Message to log.
            tag: Optional tag for formatting.
        """
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n", tag)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _start_automation(self) -> None:
        """Start the automation workflow."""
        # Validate configuration
        is_valid, error_msg = self.validate_config()
        if not is_valid:
            messagebox.showerror("Configuration Error", error_msg)
            return

        # Confirm if auto-submit is enabled
        if self.submit_var.get():
            result = messagebox.askyesno(
                "Confirm Order",
                "Auto-submit is ENABLED!\n\n"
                "This will ACTUALLY PLACE THE ORDER!\n\n"
                "Do you want to continue?",
                icon="warning",
            )
            if not result:
                return

        # Disable controls
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self._stop_flag.clear()

        # Clear log
        self._clear_log()
        self._log("=" * 50)
        self._log("SponsorCatcher - Starting automation...")
        self._log("=" * 50)

        # Start automation in background thread
        self._automation_thread = threading.Thread(target=self._run_automation, daemon=True)
        self._automation_thread.start()

    def _stop_automation(self) -> None:
        """Stop the automation workflow."""
        self._log("\n--- STOP REQUESTED ---", "warning")
        self._stop_flag.set()

        # Try to close the browser
        if self._driver:
            try:
                self._driver.quit()
            except Exception:
                pass
            self._driver = None

        self._enable_controls()

    def _enable_controls(self) -> None:
        """Re-enable controls after automation completes."""
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

    def _run_automation(self) -> None:
        """Run the automation workflow (in background thread)."""
        # Redirect stdout to log
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = LogRedirector(self.log_text)
        sys.stderr = LogRedirector(self.log_text, "error")

        try:
            config = self.get_config()
            submit_order = self.submit_var.get()

            # Import here to avoid circular imports
            from ..browser import create_driver
            from ..config import BookingConfig, Config, PaymentConfig, MonitoringConfig
            from ..actions.booking import BookingAction

            # Create config objects from GUI config
            login_config = Config(
                email=config["login"]["email"],
                password=config["login"]["password"],
                sponsor_url=config["login"]["sponsor_url"],
                login_url=config["login"].get("login_url", "https://members.manufacturedhousing.org/account/login.aspx"),
                implicit_wait=0.5,
            )

            payment_config = PaymentConfig(
                name_on_card=config["payment"]["name_on_card"],
                card_number=config["payment"]["card_number"],
                cvv=config["payment"]["cvv"],
                exp_month=config["payment"]["exp_month"],
                exp_year=config["payment"]["exp_year"],
                billing_zip=config["payment"]["billing_zip"],
                confirmation_email=config["payment"]["confirmation_email"],
            )

            # Create default monitoring config (disabled)
            monitoring_config = MonitoringConfig(
                enabled=False,
                interval_seconds=30,
                email_on_available=False,
                smtp_host="",
                smtp_port=587,
                smtp_user="",
                smtp_password="",
                notify_email="",
            )

            booking_config = BookingConfig(
                search_keyword=config["search_keyword"],
                payment=payment_config,
                monitoring=monitoring_config,
            )

            # Create browser
            print(f"Target: {login_config.sponsor_url}")
            print(f"Search: {booking_config.search_keyword}")
            print()

            self._driver = create_driver(login_config)

            # Execute booking workflow
            action = BookingAction(self._driver, login_config, booking_config)

            # Check stop flag periodically (could add more granular checks)
            if self._stop_flag.is_set():
                print("\n--- Automation stopped ---")
                return

            success = action.execute(submit_order=submit_order)

            print()
            print("=" * 50)
            if success:
                print("Automation complete!", "success")
                if not submit_order:
                    print("Review the payment form and submit manually.")
            else:
                print("Automation encountered an error.", "error")
                print("Check the browser for details.")
            print("=" * 50)

            # Keep browser open for manual review
            print("\nBrowser will remain open for manual review.")
            print("Click Stop or close the browser window when done.")

        except Exception as e:
            print(f"\nERROR: {e}", "error")
            import traceback
            traceback.print_exc()
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            self.after(0, self._enable_controls)
