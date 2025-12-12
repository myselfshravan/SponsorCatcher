"""Page objects for web automation."""

from .base_page import BasePage
from .cart_page import CartPage
from .checkout_page import CheckoutPage
from .login_page import LoginPage
from .sponsor_page import SponsorPage

__all__ = [
    "BasePage",
    "CartPage",
    "CheckoutPage",
    "LoginPage",
    "SponsorPage",
]
