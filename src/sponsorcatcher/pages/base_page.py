"""Base page object with speed-optimized utilities."""

from typing import Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Type alias for locators
Locator = Tuple[By, str]


class BasePage:
    """Base page with speed-optimized common utilities."""

    # Short default timeout for speed-critical operations
    DEFAULT_TIMEOUT: float = 3.0

    def __init__(self, driver: WebDriver) -> None:
        """Initialize base page.

        Args:
            driver: Selenium WebDriver instance.
        """
        self.driver = driver

    def find_fast(
        self, locator: Locator, timeout: float = DEFAULT_TIMEOUT
    ) -> WebElement:
        """Find element with minimal wait - optimized for speed.

        Args:
            locator: Tuple of (By, selector).
            timeout: Maximum wait time in seconds.

        Returns:
            Found WebElement.
        """
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )

    def click_fast(self, locator: Locator, timeout: float = DEFAULT_TIMEOUT) -> None:
        """Click element as soon as it's clickable.

        Args:
            locator: Tuple of (By, selector).
            timeout: Maximum wait time in seconds.
        """
        element = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
        element.click()

    def type_fast(
        self, locator: Locator, text: str, timeout: float = DEFAULT_TIMEOUT
    ) -> None:
        """Type into element using send_keys.

        Args:
            locator: Tuple of (By, selector).
            text: Text to type.
            timeout: Maximum wait time in seconds.
        """
        element = self.find_fast(locator, timeout)
        element.clear()
        element.send_keys(text)

    def type_instant(
        self, locator: Locator, text: str, timeout: float = DEFAULT_TIMEOUT
    ) -> None:
        """Type via JavaScript for maximum speed.

        This bypasses the simulated keystroke approach and directly sets
        the value, which is significantly faster.

        Args:
            locator: Tuple of (By, selector).
            text: Text to set.
            timeout: Maximum wait time in seconds.
        """
        element = self.find_fast(locator, timeout)
        self.driver.execute_script(
            """
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
            arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
            """,
            element,
            text,
        )

    def navigate_to(self, url: str) -> None:
        """Navigate to URL.

        Args:
            url: Target URL.
        """
        self.driver.get(url)

    def is_element_present(self, locator: Locator, timeout: float = 0.5) -> bool:
        """Quick check if element exists.

        Args:
            locator: Tuple of (By, selector).
            timeout: Maximum wait time in seconds.

        Returns:
            True if element is present, False otherwise.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except Exception:
            return False

    def wait_for_url_change(self, current_url: str, timeout: float = 10.0) -> None:
        """Wait for URL to change from current.

        Args:
            current_url: URL to wait to change from.
            timeout: Maximum wait time in seconds.
        """
        WebDriverWait(self.driver, timeout).until(lambda d: d.current_url != current_url)
