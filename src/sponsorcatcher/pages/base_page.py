"""Base page object with speed-optimized utilities."""

import time
from typing import List, Optional, Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
)

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

    def find_all(
        self, locator: Locator, timeout: float = DEFAULT_TIMEOUT
    ) -> List[WebElement]:
        """Find all matching elements.

        Args:
            locator: Tuple of (By, selector).
            timeout: Maximum wait time in seconds.

        Returns:
            List of found WebElements.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return self.driver.find_elements(*locator)
        except TimeoutException:
            return []

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

    def click_js(self, element: WebElement) -> None:
        """Click element using JavaScript.

        Use this for buttons that use __doPostBack or have click handlers
        that don't work with regular Selenium click.

        Args:
            element: WebElement to click.
        """
        self.driver.execute_script("arguments[0].click();", element)

    def click_js_locator(
        self, locator: Locator, timeout: float = DEFAULT_TIMEOUT
    ) -> None:
        """Find element and click using JavaScript.

        Args:
            locator: Tuple of (By, selector).
            timeout: Maximum wait time in seconds.
        """
        element = self.find_fast(locator, timeout)
        self.click_js(element)

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

    def select_dropdown(
        self, locator: Locator, value: str, timeout: float = DEFAULT_TIMEOUT
    ) -> None:
        """Select dropdown option by visible text or value.

        Args:
            locator: Tuple of (By, selector).
            value: Value or visible text to select.
            timeout: Maximum wait time in seconds.
        """
        element = self.find_fast(locator, timeout)
        select = Select(element)
        try:
            select.select_by_value(value)
        except Exception:
            select.select_by_visible_text(value)

    def select_dropdown_js(
        self, locator: Locator, value: str, timeout: float = DEFAULT_TIMEOUT
    ) -> None:
        """Select dropdown option using JavaScript for speed.

        Args:
            locator: Tuple of (By, selector).
            value: Value to select.
            timeout: Maximum wait time in seconds.
        """
        element = self.find_fast(locator, timeout)
        self.driver.execute_script(
            """
            var select = arguments[0];
            var value = arguments[1];
            for (var i = 0; i < select.options.length; i++) {
                if (select.options[i].value == value || select.options[i].text == value) {
                    select.selectedIndex = i;
                    select.dispatchEvent(new Event('change', {bubbles: true}));
                    break;
                }
            }
            """,
            element,
            value,
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
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.current_url != current_url
        )

    def wait_for_element_staleness(
        self, element: WebElement, timeout: float = 10.0
    ) -> None:
        """Wait for element to become stale (page refresh/navigation).

        Args:
            element: WebElement to wait for staleness.
            timeout: Maximum wait time in seconds.
        """
        WebDriverWait(self.driver, timeout).until(EC.staleness_of(element))

    def wait_for_page_load(self, timeout: float = 10.0) -> None:
        """Wait for page to fully load using document.readyState.

        Args:
            timeout: Maximum wait time in seconds.
        """
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def wait_for_ajax(self, timeout: float = 10.0) -> None:
        """Wait for AJAX requests to complete (if jQuery is present).

        Args:
            timeout: Maximum wait time in seconds.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script(
                    "return (typeof jQuery === 'undefined' || jQuery.active === 0)"
                )
            )
        except Exception:
            pass  # jQuery not present or other error

    def find_element_by_text(
        self, tag: str, text: str, timeout: float = DEFAULT_TIMEOUT
    ) -> Optional[WebElement]:
        """Find element by its text content.

        Args:
            tag: HTML tag to search (e.g., 'h3', 'a', 'div').
            text: Text content to search for (partial match).
            timeout: Maximum wait time in seconds.

        Returns:
            Found WebElement or None.
        """
        locator = (By.XPATH, f"//{tag}[contains(text(), '{text}')]")
        try:
            return self.find_fast(locator, timeout)
        except Exception:
            return None

    def find_parent(self, element: WebElement, levels: int = 1) -> WebElement:
        """Find parent element N levels up.

        Args:
            element: Child WebElement.
            levels: Number of levels to go up.

        Returns:
            Parent WebElement.
        """
        xpath = "/".join([".."] * levels)
        return element.find_element(By.XPATH, xpath)

    def scroll_to_element(self, element: WebElement) -> None:
        """Scroll element into view.

        Args:
            element: WebElement to scroll to.
        """
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});",
            element,
        )

    def get_text_safe(self, locator: Locator, timeout: float = DEFAULT_TIMEOUT) -> str:
        """Get element text, returning empty string if not found.

        Args:
            locator: Tuple of (By, selector).
            timeout: Maximum wait time in seconds.

        Returns:
            Element text or empty string.
        """
        try:
            element = self.find_fast(locator, timeout)
            return element.text.strip()
        except Exception:
            return ""

    def wait_short(self, seconds: float = 0.5) -> None:
        """Short explicit wait for timing-sensitive operations.

        Args:
            seconds: Time to wait.
        """
        time.sleep(seconds)
