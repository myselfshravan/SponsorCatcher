"""Run automation tab for the GUI."""

import io
import sys
import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Callable


def timestamp() -> str:
    """Get current timestamp string."""
    return datetime.now().strftime("%H:%M:%S")


class LogRedirector(io.StringIO):
    """Redirect stdout/stderr to a tkinter Text widget with timestamps."""

    def __init__(self, text_widget: tk.Text, tag: str = "", add_timestamp: bool = True) -> None:
        """Initialize the log redirector.

        Args:
            text_widget: Text widget to write to.
            tag: Optional tag for text formatting.
            add_timestamp: If True, prepend timestamp to each line.
        """
        super().__init__()
        self.text_widget = text_widget
        self.tag = tag
        self.add_timestamp = add_timestamp
        self._line_buffer = ""

    def write(self, string: str) -> int:
        """Write string to text widget with timestamps.

        Args:
            string: String to write.

        Returns:
            Number of characters written.
        """
        if not string:
            return 0

        # Buffer partial lines and add timestamp to complete lines
        self._line_buffer += string

        # Process complete lines
        while "\n" in self._line_buffer:
            line, self._line_buffer = self._line_buffer.split("\n", 1)
            if line.strip():  # Only timestamp non-empty lines
                if self.add_timestamp:
                    line = f"[{timestamp()}] {line}"
            self.text_widget.after(0, self._append, line + "\n")

        return len(string)

    def _append(self, string: str) -> None:
        """Append string to text widget (thread-safe)."""
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", string, self.tag)
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")

    def flush(self) -> None:
        """Flush remaining buffer."""
        if self._line_buffer.strip():
            line = self._line_buffer
            if self.add_timestamp:
                line = f"[{timestamp()}] {line}"
            self.text_widget.after(0, self._append, line)
            self._line_buffer = ""


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
            height=15,
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

        # Monitoring frame
        monitor_frame = ttk.LabelFrame(self, text="Monitoring", padding=10)
        monitor_frame.pack(fill="x", **padding)

        # Monitoring enable checkbox
        self.monitor_var = tk.BooleanVar(value=False)
        self.monitor_check = ttk.Checkbutton(
            monitor_frame,
            text="Enable monitoring (refresh until available)",
            variable=self.monitor_var,
        )
        self.monitor_check.grid(row=0, column=0, columnspan=2, sticky="w", pady=2)

        # Interval setting
        ttk.Label(monitor_frame, text="Refresh interval (seconds):").grid(row=1, column=0, sticky="w", pady=2)
        self.interval_var = tk.StringVar(value="30")
        self.interval_entry = ttk.Entry(monitor_frame, textvariable=self.interval_var, width=8)
        self.interval_entry.grid(row=1, column=1, sticky="w", pady=2, padx=5)

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
            text="Start",
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

        # Get interval
        try:
            interval = int(self.interval_var.get())
            if interval < 5:
                interval = 5
                self.interval_var.set("5")
        except ValueError:
            interval = 30
            self.interval_var.set("30")

        # Disable controls
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self._stop_flag.clear()

        # Clear log
        self._clear_log()
        self._log("=" * 50)
        if self.monitor_var.get():
            self._log(f"SponsorCatcher - Starting monitoring (interval: {interval}s)...")
        else:
            self._log("SponsorCatcher - Starting automation...")
        self._log("=" * 50)

        # Start automation in background thread
        if self.monitor_var.get():
            self._automation_thread = threading.Thread(
                target=self._run_monitoring,
                args=(interval,),
                daemon=True
            )
        else:
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

    def _run_monitoring(self, interval: int) -> None:
        """Run monitoring loop that checks availability periodically.

        Args:
            interval: Seconds between checks.
        """
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

            keywords = config.get("search_keywords") or [config["search_keyword"]]

            payment_config = PaymentConfig(
                name_on_card=config["payment"]["name_on_card"],
                card_number=config["payment"]["card_number"],
                cvv=config["payment"]["cvv"],
                exp_month=config["payment"]["exp_month"],
                exp_year=config["payment"]["exp_year"],
                billing_zip=config["payment"]["billing_zip"],
                confirmation_email=config["payment"]["confirmation_email"],
            )

            monitoring_config = MonitoringConfig(
                enabled=True,
                interval_seconds=interval,
                email_on_available=False,
                smtp_host="",
                smtp_port=587,
                smtp_user="",
                smtp_password="",
                notify_email="",
            )

            booking_config = BookingConfig(
                search_keyword=config["search_keyword"],
                search_keywords=tuple(keywords),
                payment=payment_config,
                monitoring=monitoring_config,
            )

            print(f"Target: {login_config.sponsor_url}")
            print(f"Search: {list(booking_config.search_keywords)}")
            print(f"Interval: {interval} seconds")
            print()

            # Create browser
            self._driver = create_driver(login_config)
            action = BookingAction(self._driver, login_config, booking_config)

            check_count = 0
            while not self._stop_flag.is_set():
                check_count += 1
                print(f"\n[Check #{check_count}] Checking availability...")

                try:
                    # Check availability (login + navigate + search + check)
                    is_available = action.check_availability()

                    if is_available:
                        print(f"[Check #{check_count}] AVAILABLE! Starting booking...")
                        # Run full booking workflow
                        success = action.execute(submit_order=submit_order)

                        if success:
                            print("\n" + "=" * 50)
                            print("BOOKING SUCCESSFUL!")
                            if not submit_order:
                                print("Review and submit manually.")
                            print("=" * 50)
                            # Stop monitoring loop explicitly to avoid re-entry.
                            self._stop_flag.set()
                            break
                        else:
                            print(f"[Check #{check_count}] Booking failed, will retry...")
                    else:
                        print(f"[Check #{check_count}] Not available. Waiting {interval}s...")

                except Exception as e:
                    print(f"[Check #{check_count}] Error: {e}")
                    print(f"Will retry in {interval}s...")

                # Wait for interval (check stop flag periodically)
                for _ in range(interval):
                    if self._stop_flag.is_set():
                        break
                    time.sleep(1)

            if self._stop_flag.is_set():
                print("\n--- Monitoring stopped ---")
            else:
                print("\nBrowser will remain open for manual review.")
                print("Click Stop when done.")

        except Exception as e:
            print(f"\nERROR: {e}")
            import traceback
            traceback.print_exc()
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            self.after(0, self._enable_controls)

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

            keywords = config.get("search_keywords") or [config["search_keyword"]]

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
                search_keywords=tuple(keywords),
                payment=payment_config,
                monitoring=monitoring_config,
            )

            # Create browser
            print(f"Target: {login_config.sponsor_url}")
            print(f"Search: {list(booking_config.search_keywords)}")
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
                print("Automation complete!")
                if not submit_order:
                    print("Review the payment form and submit manually.")
            else:
                print("Automation encountered an error.")
                print("Check the browser for details.")
            print("=" * 50)

            # Keep browser open for manual review
            print("\nBrowser will remain open for manual review.")
            print("Click Stop or close the browser window when done.")

        except Exception as e:
            print(f"\nERROR: {e}")
            import traceback
            traceback.print_exc()
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            self.after(0, self._enable_controls)
