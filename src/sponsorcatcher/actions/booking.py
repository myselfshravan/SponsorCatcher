"""High-level booking workflow orchestration."""

from selenium.webdriver.remote.webdriver import WebDriver

from ..config import Config
from ..pages.login_page import LoginPage
from ..pages.sponsor_page import SponsorPage


class BookingAction:
    """High-level booking workflow orchestrator."""

    def __init__(self, driver: WebDriver, config: Config) -> None:
        """Initialize booking action.

        Args:
            driver: Selenium WebDriver instance.
            config: Application configuration.
        """
        self.driver = driver
        self.config = config
        self.login_page = LoginPage(driver, config)
        self.sponsor_page = SponsorPage(driver, config)

    def execute(self) -> None:
        """Execute the complete booking workflow.

        Steps:
        1. Navigate to login page
        2. Login with credentials
        3. Navigate to sponsor page
        4. (Future) Perform booking actions
        """
        print("[1/2] Logging in...")
        self.login_page.navigate()
        self.login_page.login_and_wait()
        print("[1/2] Login successful!")

        print("[2/2] Navigating to sponsor page...")
        self.sponsor_page.navigate()
        print("[2/2] On sponsor page - ready for next steps!")

        # Future: Add more automated steps here
        # self.sponsor_page.select_sponsor_slot("platinum")
        # self.sponsor_page.click_book_button()
