"""Sponsor page object."""

from ..config import Config
from .base_page import BasePage


class SponsorPage(BasePage):
    """Page object for the sponsor booking page.

    This page will be extended when the user provides
    element information for the booking flow.
    """

    def __init__(self, driver, config: Config) -> None:
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

    # Future methods to be added when user provides element info:
    # def select_sponsor_slot(self, slot_identifier: str) -> None:
    # def click_book_button(self) -> None:
    # def fill_booking_form(self, data: dict) -> None:
