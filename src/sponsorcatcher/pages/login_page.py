"""Login page object."""

from ..config import Config
from ..locators.elements import LoginPageLocators
from .base_page import BasePage


class LoginPage(BasePage):
    """Page object for the login page."""

    def __init__(self, driver, config: Config) -> None:
        """Initialize login page.

        Args:
            driver: Selenium WebDriver instance.
            config: Application configuration.
        """
        super().__init__(driver)
        self.config = config

    def navigate(self) -> None:
        """Navigate to login page."""
        self.navigate_to(self.config.login_url)

    def login(self) -> None:
        """Perform login with credentials from config.

        Uses instant typing for maximum speed.
        """
        self.type_instant(LoginPageLocators.EMAIL_INPUT, self.config.email)
        self.type_instant(LoginPageLocators.PASSWORD_INPUT, self.config.password)
        self.click_fast(LoginPageLocators.LOGIN_BUTTON)

    def login_and_wait(self) -> None:
        """Login and wait for navigation to complete.

        Waits for URL to change, indicating successful login.
        """
        current_url = self.driver.current_url
        self.login()
        self.wait_for_url_change(current_url)

    def is_login_error_displayed(self) -> bool:
        """Check if login validation error is shown.

        Returns:
            True if validation error is visible.
        """
        return self.is_element_present(LoginPageLocators.VALIDATION_SUMMARY)
