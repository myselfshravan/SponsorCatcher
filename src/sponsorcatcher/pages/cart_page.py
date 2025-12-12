"""Shopping cart page object."""

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

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

    def get_sold_out_items(self) -> list[str]:
        """Extract sold-out item names from the warning message if present."""
        names: list[str] = []
        try:
            items = self.find_all(CartPageLocators.CART_WARNING_ITEMS, timeout=1.0)
            for item in items:
                text = item.text.strip()
                if text:
                    names.append(text)
        except Exception:
            pass

        if names:
            return names

        # Fallback to parsing the alert text lines.
        message = self.get_sold_out_message()
        if message:
            lines = [line.strip() for line in message.splitlines() if line.strip()]
            if len(lines) > 1:
                names = lines[1:]
        return names

    def list_cart_items(self) -> list[tuple[str, WebElement]]:
        """Return a list of (name, delete_button_element) for cart rows."""
        items: list[tuple[str, object]] = []
        rows = self.find_all(CartPageLocators.CART_ITEM_ROWS, timeout=2.0)
        for row in rows:
            try:
                name_el = row.find_element(*CartPageLocators.CART_ITEM_NAME)
                delete_el = row.find_element(*CartPageLocators.CART_ITEM_REMOVE_BTN)
                name = name_el.text.strip()
                items.append((name, delete_el))
            except Exception:
                continue
        return items

    def remove_items_by_names(self, names: list[str]) -> list[str]:
        """Remove cart items whose names match provided list (case-insensitive).

        Returns:
            List of names successfully removed.
        """
        removed: list[str] = []
        if not names:
            return removed

        names_lower = [n.lower() for n in names]
        items = self.list_cart_items()

        # Auto-confirm any JS confirmation dialogs before clicking remove.
        try:
            self.driver.execute_script(
                "window.confirm = function(){return true;};"
                "if (window.dialog && dialog.confirm) { dialog.confirm = function(){return true;}; }"
            )
        except Exception:
            pass

        for item_name, delete_el in items:
            try:
                if any(n in item_name.lower() for n in names_lower):
                    self.click_js(delete_el)
                    removed.append(item_name)
                    self.wait_for_page_load()
            except Exception:
                continue

        return removed
