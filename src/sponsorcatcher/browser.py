"""Browser setup with speed optimizations."""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver

from .config import Config


def create_driver(config: Config) -> WebDriver:
    """Create a speed-optimized Chrome WebDriver.

    Args:
        config: Application configuration.

    Returns:
        Configured Chrome WebDriver instance.
    """
    options = Options()

    # === SPEED OPTIMIZATIONS ===

    # Disable images, notifications, and password manager popups
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.notifications": 2,
        # Disable password manager
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    }
    options.add_experimental_option("prefs", prefs)

    # Disable unnecessary features
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-browser-side-navigation")

    # Page load strategy: 'eager' waits for DOMContentLoaded, not all resources
    options.page_load_strategy = "eager"

    # Disable automation flags that might trigger bot detection
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Create driver
    driver = webdriver.Chrome(options=options)

    # Minimal implicit wait - we use explicit waits for specific elements
    driver.implicitly_wait(config.implicit_wait)

    # Maximize for visibility (user is watching)
    driver.maximize_window()

    return driver
