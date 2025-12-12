"""Sponsor page object for product search and cart operations."""

from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from ..config import Config
from ..locators.elements import SponsorPageLocators
from .base_page import BasePage


class SponsorPage(BasePage):
    """Page object for the sponsor booking page.

    Handles:
    - Product search
    - Finding product cards by name
    - Adding to cart
    - Clicking Review & Checkout
    """

    def __init__(self, driver: WebDriver, config: Config) -> None:
        """Initialize sponsor page.

        Args:
            driver: Selenium WebDriver instance.
            config: Application configuration.
        """
        super().__init__(driver)
        self.config = config

    def navigate(self) -> None:
        """Navigate to sponsor page."""
        self.navigate_to(self.config.sponsor_url)

    def search(self, keyword: str) -> None:
        """Search for products by keyword.

        Args:
            keyword: Search keyword to find products.
        """
        # Type the search keyword
        self.type_instant(SponsorPageLocators.SEARCH_INPUT, keyword)

        # Click search button using JS (handles __doPostBack)
        self.click_js_locator(SponsorPageLocators.SEARCH_BUTTON)

        # Wait for page to update after postback
        self.wait_for_page_load()
        self.wait_short(1.0)  # Extra wait for dynamic content

    def find_product_by_name(self, name: str) -> Optional[WebElement]:
        """Find product card containing the specified name in title.

        This uses text-based search which is robust against dynamic IDs.

        Args:
            name: Product name or partial name to search for.

        Returns:
            Product card WebElement or None if not found.
        """
        card = self._find_matching_card(name)
        if card:
            return card

        # Some products only render after scrolling the page/container.
        print(f"  Product '{name}' not visible yet, scrolling to load more results...")
        return self._scroll_and_find_product(name)

    def _find_matching_card(self, name: str) -> Optional[WebElement]:
        """Locate a product card whose title contains the given name."""
        cards = self.find_all(SponsorPageLocators.PRODUCT_CARDS)
        for card in cards:
            try:
                title_element = card.find_element(By.CSS_SELECTOR, ".pricing-head h3")
                title_text = title_element.text.strip()
                if name.lower() in title_text.lower():
                    return card
            except Exception:
                continue
        return None

    def _scroll_and_find_product(self, name: str, attempts: int = 8) -> Optional[WebElement]:
        """Scroll through the page to trigger lazy-loaded products."""
        last_height = -1
        stagnant_scrolls = 0

        try:
            container = self.find_fast(SponsorPageLocators.PRODUCTS_CONTAINER, timeout=1.0)
        except Exception:
            container = None

        for _ in range(attempts):
            if container:
                try:
                    self.driver.execute_script(
                        "arguments[0].scrollTop = arguments[0].scrollHeight;", container
                    )
                except Exception:
                    container = None

            try:
                current_height = self.driver.execute_script("return document.body.scrollHeight")
                self.driver.execute_script("window.scrollTo(0, arguments[0]);", current_height)
            except Exception:
                current_height = last_height

            self.wait_short(0.6)

            card = self._find_matching_card(name)
            if card:
                self.scroll_to_element(card)
                return card

            if current_height == last_height:
                stagnant_scrolls += 1
                try:
                    # Small nudge in case scroll height stops changing but items load on movement
                    self.driver.execute_script("window.scrollBy(0, 400);")
                except Exception:
                    pass
                if stagnant_scrolls >= 2:
                    break
            else:
                stagnant_scrolls = 0

            last_height = current_height

        try:
            self.driver.execute_script("window.scrollTo(0, 0);")
        except Exception:
            pass

        return self._find_matching_card(name)

    def is_product_in_cart(self, product_card: WebElement) -> bool:
        """Check if product is already in cart (has 'selected' class).

        Args:
            product_card: Product card WebElement.

        Returns:
            True if product is in cart.
        """
        classes = product_card.get_attribute("class") or ""
        return "selected" in classes

    def add_to_cart(self, product_card: WebElement) -> bool:
        """Click Add to Cart button on the product card.

        Args:
            product_card: Product card WebElement.

        Returns:
            True if successfully added, False if already in cart or failed.
        """
        if self.is_product_in_cart(product_card):
            print("Product already in cart")
            return True

        try:
            # Find the Add to Cart button within this card
            add_btn = product_card.find_element(
                By.CSS_SELECTOR, ".pricing-footer .btn.green"
            )

            # Scroll into view and click using JS
            self.scroll_to_element(add_btn)
            self.click_js(add_btn)

            # Wait for the card to update (gets 'selected' class)
            self.wait_for_page_load()
            self.wait_short(1.0)

            return True
        except Exception as e:
            print(f"Failed to add to cart: {e}")
            return False

    def click_review_checkout(self, product_card: WebElement) -> bool:
        """Click Review & Checkout button on the selected product card.

        This button appears after adding to cart.

        Args:
            product_card: Product card WebElement (must be in cart).

        Returns:
            True if successfully clicked.
        """
        try:
            # Find the Review & Checkout button within this card
            # It's a green button with "Checkout" text
            checkout_btn = product_card.find_element(
                By.XPATH,
                ".//a[contains(@class, 'btn') and contains(@class, 'green') and contains(text(), 'Checkout')]",
            )

            # Store current URL to detect navigation
            current_url = self.driver.current_url

            # Scroll and click using JS
            self.scroll_to_element(checkout_btn)
            self.click_js(checkout_btn)

            # Wait for navigation
            self.wait_for_url_change(current_url)
            self.wait_for_page_load()

            return True
        except Exception as e:
            print(f"Failed to click Review & Checkout: {e}")
            return False

    def is_product_available(self, product_card: WebElement) -> bool:
        """Check if product is available (not sold out).

        Args:
            product_card: Product card WebElement.

        Returns:
            True if product is available for purchase.
        """
        try:
            # Check for sold out indicator within the card
            sold_out = product_card.find_elements(
                By.CSS_SELECTOR, ".product-sold-out"
            )
            if sold_out:
                return False

            # Check if Add to Cart button exists and is enabled
            add_btn = product_card.find_elements(
                By.CSS_SELECTOR, ".pricing-footer .btn.green"
            )
            if not add_btn:
                return False

            return True
        except Exception:
            return False

    def get_product_price(self, product_card: WebElement) -> str:
        """Get the price of a product.

        Args:
            product_card: Product card WebElement.

        Returns:
            Price string or empty string if not found.
        """
        try:
            price_element = product_card.find_element(
                By.CSS_SELECTOR, ".pricing-head h4"
            )
            return price_element.text.strip()
        except Exception:
            return ""

    def get_product_title(self, product_card: WebElement) -> str:
        """Get the title of a product.

        Args:
            product_card: Product card WebElement.

        Returns:
            Title string or empty string if not found.
        """
        try:
            title_element = product_card.find_element(
                By.CSS_SELECTOR, ".pricing-head h3"
            )
            return title_element.text.strip()
        except Exception:
            return ""
