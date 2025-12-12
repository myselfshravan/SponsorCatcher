"""Checkout/payment page object."""

from selenium.webdriver.remote.webdriver import WebDriver

from ..config import PaymentConfig
from ..locators.elements import CheckoutPageLocators
from .base_page import BasePage


class CheckoutPage(BasePage):
    """Page object for the checkout/payment page.

    Handles:
    - Filling payment form (name, card, CVV, expiry, zip, email)
    - Submitting order (disabled by default for safety)
    """

    def __init__(self, driver: WebDriver) -> None:
        """Initialize checkout page.

        Args:
            driver: Selenium WebDriver instance.
        """
        super().__init__(driver)

    def fill_name_on_card(self, name: str) -> None:
        """Fill the name on card field.

        Args:
            name: Name as it appears on the card.
        """
        self.type_instant(CheckoutPageLocators.NAME_ON_CARD, name)

    def fill_card_number(self, card_number: str) -> None:
        """Fill the card number field.

        Args:
            card_number: Credit card number.
        """
        self.type_instant(CheckoutPageLocators.CARD_NUMBER, card_number)

    def fill_cvv(self, cvv: str) -> None:
        """Fill the CVV field.

        Args:
            cvv: Card CVV/security code.
        """
        self.type_instant(CheckoutPageLocators.CVV, cvv)

    def fill_billing_zip(self, zip_code: str) -> None:
        """Fill the billing zip code field.

        Args:
            zip_code: Billing address zip/postal code.
        """
        self.type_instant(CheckoutPageLocators.BILLING_ZIP, zip_code)

    def fill_confirmation_email(self, email: str) -> None:
        """Fill the confirmation email field.

        Args:
            email: Email address for order confirmation.
        """
        self.type_instant(CheckoutPageLocators.CONFIRM_EMAIL, email)

    def select_expiry_month(self, month: str) -> None:
        """Select expiration month from dropdown.

        Args:
            month: Month value (1-12 or "01"-"12").
        """
        self.select_dropdown_js(CheckoutPageLocators.EXP_MONTH, month)

    def select_expiry_year(self, year: str) -> None:
        """Select expiration year from dropdown.

        Args:
            year: Year value (e.g., "2026").
        """
        self.select_dropdown_js(CheckoutPageLocators.EXP_YEAR, year)

    def fill_payment_details(self, payment: PaymentConfig) -> None:
        """Fill all payment form fields.

        Args:
            payment: PaymentConfig with all payment details.
        """
        print("Filling payment details...")

        # Fill each field
        self.fill_name_on_card(payment.name_on_card)
        self.fill_card_number(payment.card_number)
        self.fill_cvv(payment.cvv)
        self.select_expiry_month(payment.exp_month)
        self.select_expiry_year(payment.exp_year)
        self.fill_billing_zip(payment.billing_zip)
        self.fill_confirmation_email(payment.confirmation_email)

        print("Payment details filled successfully!")

        # Scroll to submit button so user can see it
        self.scroll_to_submit_button()

        if self.is_submit_button_visible():
            print("Submit button detected.")
        else:
            print("Submit button not visible yet (may be hidden by validation).")

    def scroll_to_submit_button(self) -> None:
        """Scroll the submit button into view.

        This ensures the user can see the submit button after
        payment details are filled.
        """
        try:
            submit_btn = self.find_fast(CheckoutPageLocators.SUBMIT_BTN, timeout=2.0)
            self.scroll_to_element(submit_btn)
        except Exception:
            # Not critical if scroll fails
            pass

    def is_submit_button_present(self) -> bool:
        """Check if submit button is present.

        Returns:
            True if submit button is present.
        """
        return self.is_element_present(CheckoutPageLocators.SUBMIT_BTN, timeout=2.0)

    def is_submit_button_visible(self) -> bool:
        """Check if submit button is present and displayed."""
        try:
            element = self.find_fast(CheckoutPageLocators.SUBMIT_BTN, timeout=2.0)
            return element.is_displayed()
        except Exception:
            return False

    def submit_order(self) -> bool:
        """Click Submit Your Order button.

        WARNING: This will actually submit the order!
        Only call this when you're ready to purchase.

        Returns:
            True if successfully clicked.
        """
        try:
            # Store current URL to detect navigation
            current_url = self.driver.current_url

            # Click submit button using JS
            self.click_js_locator(CheckoutPageLocators.SUBMIT_BTN)

            # Wait for navigation to confirmation page
            self.wait_for_url_change(current_url)
            self.wait_for_page_load()

            return True
        except Exception as e:
            print(f"Failed to submit order: {e}")
            return False

    def click_previous(self) -> bool:
        """Click Previous button to go back.

        Returns:
            True if successfully clicked.
        """
        try:
            self.click_js_locator(CheckoutPageLocators.PREVIOUS_BTN)
            self.wait_for_page_load()
            return True
        except Exception as e:
            print(f"Failed to click Previous: {e}")
            return False

    def has_validation_error(self) -> bool:
        """Check if there's a validation error displayed.

        Returns:
            True if validation error is present.
        """
        try:
            element = self.find_fast(CheckoutPageLocators.VALIDATION_ERROR, timeout=1.0)
            return element.is_displayed()
        except Exception:
            return False

    def get_order_total(self) -> str:
        """Get the order total amount.

        Returns:
            Order total string or empty string if not found.
        """
        return self.get_text_safe(CheckoutPageLocators.ORDER_TOTAL, timeout=2.0)

    def is_ready_to_submit(self) -> bool:
        """Check if form is filled and ready to submit.

        Verifies that submit button is present and no validation errors.

        Returns:
            True if ready to submit.
        """
        return self.is_submit_button_visible() and not self.has_validation_error()
