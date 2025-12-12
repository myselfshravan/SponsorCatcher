"""Shopping cart page object."""

from selenium.webdriver.remote.webdriver import WebDriver

from ..locators.elements import CartPageLocators
from .base_page import BasePage


class CartPage(BasePage):
    """Page object for the shopping cart page.

    Handles:
    - Checking for sold out warnings
    - Clicking checkout button
    """

    def __init__(self, driver: WebDriver) -> None:
        """Initialize cart page.

        Args:
            driver: Selenium WebDriver instance.
        """
        super().__init__(driver)

    def is_sold_out(self) -> bool:
        """Check if any items in cart are sold out.

        The sold out warning appears as an alert-warning div.
        We check if it's actually VISIBLE (not display:none).

        Returns:
            True if sold out warning is displayed and visible.
        """
        try:
            element = self.find_fast(CartPageLocators.SOLD_OUT_WARNING, timeout=1.0)
            # Check if element is actually displayed (not hidden with display:none)
            return element.is_displayed()
        except Exception:
            return False

    def get_sold_out_message(self) -> str:
        """Get the sold out warning message text.

        Returns:
            Warning message or empty string if not present.
        """
        return self.get_text_safe(CartPageLocators.SOLD_OUT_WARNING, timeout=1.0)

    def click_checkout(self) -> bool:
        """Click the Checkout button to proceed to payment.

        Returns:
            True if successfully clicked.
        """
        try:
            # Store current URL to detect navigation
            current_url = self.driver.current_url

            # Click checkout button using JS (handles __doPostBack)
            self.click_js_locator(CartPageLocators.CHECKOUT_BTN)

            # Wait for page to update
            self.wait_for_page_load()
            self.wait_short(1.0)

            return True
        except Exception as e:
            print(f"Failed to click Checkout: {e}")
            return False

    def click_clear_cart(self) -> bool:
        """Click Clear Cart button to empty the cart.

        Returns:
            True if successfully clicked.
        """
        try:
            self.click_js_locator(CartPageLocators.CLEAR_CART_BTN)
            self.wait_for_page_load()
            return True
        except Exception as e:
            print(f"Failed to clear cart: {e}")
            return False

    def is_checkout_button_present(self) -> bool:
        """Check if checkout button is present and visible.

        Returns:
            True if checkout button is present.
        """
        return self.is_element_present(CartPageLocators.CHECKOUT_BTN, timeout=2.0)
