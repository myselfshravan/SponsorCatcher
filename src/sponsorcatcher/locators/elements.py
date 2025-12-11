"""Centralized element locators for all pages."""

from selenium.webdriver.common.by import By


class LoginPageLocators:
    """Locators for the login page."""

    EMAIL_INPUT = (By.ID, "main_content_Login_txtLoginUserName")
    PASSWORD_INPUT = (By.ID, "main_content_Login_ctlLoginPassword_txtPassword")
    LOGIN_BUTTON = (By.ID, "LoginButton")
    VALIDATION_SUMMARY = (By.ID, "main_content_Login_LoginValidationSummary")


class SponsorPageLocators:
    """Locators for the sponsor booking page.

    These will be populated when the user provides element information
    for the sponsor selection and booking flow.
    """

    # Placeholder - to be added when user provides sponsor page elements
    pass
