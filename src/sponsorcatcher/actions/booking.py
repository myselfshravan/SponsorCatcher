"""High-level booking workflow orchestration."""

from selenium.webdriver.remote.webdriver import WebDriver

from ..config import BookingConfig, Config
from ..pages.cart_page import CartPage
from ..pages.checkout_page import CheckoutPage
from ..pages.login_page import LoginPage
from ..pages.sponsor_page import SponsorPage


class BookingAction:
    """High-level booking workflow orchestrator.

    Executes the complete booking flow:
    1. Login
    2. Navigate to sponsor page
    3. Search for product
    4. Add to cart
    5. Review & Checkout
    6. Check for sold out
    7. Fill payment details
    8. (Optional) Submit order
    """

    def __init__(
        self,
        driver: WebDriver,
        config: Config,
        booking_config: BookingConfig,
    ) -> None:
        """Initialize booking action.

        Args:
            driver: Selenium WebDriver instance.
            config: Login configuration (from .env).
            booking_config: Booking configuration (from config.yaml).
        """
        self.driver = driver
        self.config = config
        self.booking_config = booking_config
        self._logged_in = False  # Track login state for monitoring

        # Initialize page objects
        self.login_page = LoginPage(driver, config)
        self.sponsor_page = SponsorPage(driver, config)
        self.cart_page = CartPage(driver)
        self.checkout_page = CheckoutPage(driver)

    def execute(self, submit_order: bool = False) -> bool:
        """Execute the complete booking workflow.

        Args:
            submit_order: If True, actually submit the order.
                         If False (default), stop before submitting.

        Returns:
            True if workflow completed successfully, False otherwise.
        """
        total_steps = 8 if submit_order else 7
        step = 0

        # Step 1: Login (skip if already logged in from monitoring)
        step += 1
        if not self._logged_in:
            print(f"[{step}/{total_steps}] Logging in...")
            self.login_page.navigate()
            self.login_page.login_and_wait()
            self._logged_in = True
            print(f"[{step}/{total_steps}] Login successful!")
        else:
            print(f"[{step}/{total_steps}] Already logged in, skipping...")

        # Step 2: Navigate to sponsor page
        step += 1
        print(f"[{step}/{total_steps}] Navigating to sponsor page...")
        self.sponsor_page.navigate()
        print(f"[{step}/{total_steps}] On sponsor page!")

        # Step 3: Search for product
        step += 1
        keyword = self.booking_config.search_keyword
        print(f"[{step}/{total_steps}] Searching for '{keyword}'...")
        self.sponsor_page.search(keyword)
        print(f"[{step}/{total_steps}] Search complete!")

        # Step 4: Find and add product to cart
        step += 1
        print(f"[{step}/{total_steps}] Finding product...")
        product_card = self.sponsor_page.find_product_by_name(keyword)

        if not product_card:
            print(f"ERROR: Product containing '{keyword}' not found!")
            return False

        title = self.sponsor_page.get_product_title(product_card)
        price = self.sponsor_page.get_product_price(product_card)
        print(f"[{step}/{total_steps}] Found: {title} - {price}")

        # Check availability
        if not self.sponsor_page.is_product_available(product_card):
            print("ERROR: Product is SOLD OUT!")
            return False

        # Add to cart
        print(f"[{step}/{total_steps}] Adding to cart...")
        if not self.sponsor_page.add_to_cart(product_card):
            print("ERROR: Failed to add to cart!")
            return False
        print(f"[{step}/{total_steps}] Added to cart!")

        # Step 5: Click Review & Checkout
        step += 1
        print(f"[{step}/{total_steps}] Clicking Review & Checkout...")

        # Re-find the product card (it may have been refreshed)
        product_card = self.sponsor_page.find_product_by_name(keyword)
        if not product_card:
            print("ERROR: Lost product card after adding to cart!")
            return False

        if not self.sponsor_page.click_review_checkout(product_card):
            print("ERROR: Failed to click Review & Checkout!")
            return False
        print(f"[{step}/{total_steps}] Navigated to cart!")

        # Step 6: Check for sold out and click Checkout
        step += 1
        print(f"[{step}/{total_steps}] Checking cart status...")

        if self.cart_page.is_sold_out():
            message = self.cart_page.get_sold_out_message()
            print(f"ERROR: Item is SOLD OUT! {message}")
            return False

        print(f"[{step}/{total_steps}] Cart looks good, clicking Checkout...")
        if not self.cart_page.click_checkout():
            print("ERROR: Failed to click Checkout!")
            return False
        print(f"[{step}/{total_steps}] Proceeded to payment page!")

        # Step 7: Fill payment details
        step += 1
        print(f"[{step}/{total_steps}] Filling payment details...")
        self.checkout_page.fill_payment_details(self.booking_config.payment)

        order_total = self.checkout_page.get_order_total()
        print(f"[{step}/{total_steps}] Order total: {order_total}")

        if not self.checkout_page.is_ready_to_submit():
            print("WARNING: Form may have validation errors!")

        # Step 8: Submit order (optional)
        if submit_order:
            step += 1
            print(f"[{step}/{total_steps}] SUBMITTING ORDER...")
            if not self.checkout_page.submit_order():
                print("ERROR: Failed to submit order!")
                return False
            print(f"[{step}/{total_steps}] ORDER SUBMITTED!")
        else:
            print()
            print("=" * 50)
            print("READY TO SUBMIT!")
            print("Payment details filled. Review and submit manually.")
            print("Or re-run with submit_order=True to auto-submit.")
            print("=" * 50)

        return True

    def check_availability(self) -> bool:
        """Quick check if product is available (for monitoring).

        This performs a lightweight check without adding to cart.

        Returns:
            True if product appears to be available.
        """
        # Login if not already logged in
        if not self._logged_in:
            print("  Logging in...")
            self.login_page.navigate()
            self.login_page.login_and_wait()
            self._logged_in = True
            print("  Login successful!")

        # Navigate to sponsor page (this refreshes the page)
        print("  Navigating to sponsor page...")
        self.sponsor_page.navigate()

        # Search for product
        keyword = self.booking_config.search_keyword
        print(f"  Searching for '{keyword}'...")
        self.sponsor_page.search(keyword)

        # Find product
        product_card = self.sponsor_page.find_product_by_name(keyword)
        if not product_card:
            print(f"  Product '{keyword}' not found!")
            return False

        # Check availability
        is_available = self.sponsor_page.is_product_available(product_card)
        if is_available:
            title = self.sponsor_page.get_product_title(product_card)
            print(f"  Found available: {title}")
        else:
            print("  Product is SOLD OUT")
        return is_available
