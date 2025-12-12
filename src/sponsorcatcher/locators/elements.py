"""Centralized element locators for all pages.

IMPORTANT: All locators use ROBUST selectors that won't break:
- CSS classes (stable across page loads)
- Text content via XPath
- Attribute suffix selectors [id$='_suffix']
- NO auto-generated IDs like 'main_content_Pnl...'
"""

from selenium.webdriver.common.by import By


class LoginPageLocators:
    """Locators for the login page."""

    EMAIL_INPUT = (By.ID, "main_content_Login_txtLoginUserName")
    PASSWORD_INPUT = (By.ID, "main_content_Login_ctlLoginPassword_txtPassword")
    LOGIN_BUTTON = (By.ID, "LoginButton")
    VALIDATION_SUMMARY = (By.ID, "main_content_Login_LoginValidationSummary")


class SponsorPageLocators:
    """Locators for the sponsor booking page.

    Uses stable CSS classes and text-based XPath selectors.
    """

    # Search bar - stable classes
    SEARCH_INPUT = (By.CSS_SELECTOR, ".input-group input.form-control")
    SEARCH_BUTTON = (By.CSS_SELECTOR, ".input-group .btn.green")

    # Product cards container
    PRODUCTS_CONTAINER = (By.CSS_SELECTOR, ".products-list")

    # Product card - stable classes
    PRODUCT_CARDS = (By.CSS_SELECTOR, ".pricing")
    PRODUCT_CARD_SELECTED = (By.CSS_SELECTOR, ".pricing.selected")

    # Inside product card
    PRODUCT_TITLE = (By.CSS_SELECTOR, ".pricing-head h3")
    PRODUCT_PRICE = (By.CSS_SELECTOR, ".pricing-head h4")
    PRICING_FOOTER = (By.CSS_SELECTOR, ".pricing-footer")

    # Buttons inside product card footer
    ADD_TO_CART_BTN = (By.CSS_SELECTOR, ".pricing-footer .btn.green")
    REMOVE_FROM_CART_BTN = (By.CSS_SELECTOR, ".pricing-footer .btn.red")

    # Review & Checkout button (appears after adding to cart)
    REVIEW_CHECKOUT_BTN = (
        By.XPATH,
        "//a[contains(@class, 'btn') and contains(@class, 'green') and contains(text(), 'Checkout')]",
    )

    # Sold out indicator
    SOLD_OUT_LABEL = (By.CSS_SELECTOR, ".product-sold-out")


class CartPageLocators:
    """Locators for the shopping cart page."""

    # Sold out warning message
    SOLD_OUT_WARNING = (By.CSS_SELECTOR, ".alert.alert-warning")

    # Cart buttons
    CLEAR_CART_BTN = (By.CSS_SELECTOR, ".btn-cart-clear")
    UPDATE_CART_BTN = (By.CSS_SELECTOR, ".btn-cart-update")
    CHECKOUT_BTN = (By.CSS_SELECTOR, ".btn-cart-checkout")

    # Cart items
    CART_ITEMS = (By.CSS_SELECTOR, ".cart-item")


class CheckoutPageLocators:
    """Locators for the checkout/payment page.

    Uses attribute suffix selectors [id$='_suffix'] for stable matching
    since the prefix is auto-generated but the suffix is consistent.
    """

    # Order summary
    ORDER_TOTAL = (By.CSS_SELECTOR, "[id$='_lblTotal']")

    # Payment form fields - using suffix selectors
    NAME_ON_CARD = (By.CSS_SELECTOR, "input[id$='_txtName']")
    CARD_NUMBER = (By.CSS_SELECTOR, "input[id$='_txtCCNumber']")
    CVV = (By.CSS_SELECTOR, "input[id$='_txtCVV']")
    BILLING_ZIP = (By.CSS_SELECTOR, "input[id$='_txtCCZip']")
    CONFIRM_EMAIL = (By.CSS_SELECTOR, "input[id$='_txtCCEmail']")

    # Expiration date dropdowns
    EXP_MONTH = (By.CSS_SELECTOR, "select[id$='_ddlCCExpireMonth']")
    EXP_YEAR = (By.CSS_SELECTOR, "select[id$='_ddlCCExpireYear']")

    # Shipping address radio (first one is usually selected)
    SHIPPING_ADDRESS_RADIO = (By.CSS_SELECTOR, ".payment-address input[type='radio']")

    # Billing address radio
    BILLING_ADDRESS_RADIO = (
        By.CSS_SELECTOR,
        "[id$='_rdoBillingAddresses'] input[type='radio']",
    )

    # Credit card payment option
    CREDIT_CARD_RADIO = (By.ID, "rdoCredit")

    # Submit button - text-based for robustness
    SUBMIT_BTN = (
        By.XPATH,
        "//a[contains(@class, 'btn') and contains(@class, 'green') and contains(text(), 'Submit Your Order')]",
    )

    # Previous button
    PREVIOUS_BTN = (By.CSS_SELECTOR, "a[id$='_lnkPrevious']")

    # Validation error
    VALIDATION_ERROR = (By.CSS_SELECTOR, ".alert.alert-danger")
