"""Configuration loading and validation."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple
import os

import yaml
from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    """Immutable configuration for login credentials (from .env)."""

    email: str
    password: str
    login_url: str
    sponsor_url: str
    implicit_wait: float

    @classmethod
    def load(cls, env_path: Optional[Path] = None) -> "Config":
        """Load configuration from .env file.

        Args:
            env_path: Optional path to .env file. Defaults to .env in current directory.

        Returns:
            Config instance with loaded values.

        Raises:
            KeyError: If required environment variables are missing.
        """
        if env_path:
            load_dotenv(env_path)
        else:
            load_dotenv()

        email = os.environ.get("SPONSOR_EMAIL")
        password = os.environ.get("SPONSOR_PASSWORD")

        if not email or not password:
            raise KeyError(
                "Missing required environment variables: SPONSOR_EMAIL and SPONSOR_PASSWORD. "
                "Please copy .env.example to .env and fill in your credentials."
            )

        return cls(
            email=email,
            password=password,
            login_url=os.getenv(
                "LOGIN_URL",
                "https://members.manufacturedhousing.org/account/login.aspx",
            ),
            sponsor_url=os.getenv(
                "SPONSOR_URL",
                "https://members.manufacturedhousing.org/sponsorships/become-a-sponsor",
            ),
            implicit_wait=float(os.getenv("IMPLICIT_WAIT", "0.5")),
        )


@dataclass(frozen=True)
class PaymentConfig:
    """Payment details configuration."""

    name_on_card: str
    card_number: str
    cvv: str
    exp_month: str
    exp_year: str
    billing_zip: str
    confirmation_email: str


@dataclass(frozen=True)
class MonitoringConfig:
    """Monitoring configuration (future feature)."""

    enabled: bool
    interval_seconds: int
    email_on_available: bool
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    notify_email: str


@dataclass(frozen=True)
class BookingConfig:
    """Full booking configuration from YAML."""

    search_keyword: str  # legacy single keyword (first in list)
    search_keywords: Tuple[str, ...]
    payment: PaymentConfig
    monitoring: MonitoringConfig

    @classmethod
    def load(cls, yaml_path: Optional[Path] = None) -> "BookingConfig":
        """Load booking configuration from YAML file.

        Args:
            yaml_path: Optional path to YAML file. Defaults to config.yaml in current directory.

        Returns:
            BookingConfig instance with loaded values.

        Raises:
            FileNotFoundError: If config.yaml doesn't exist.
            KeyError: If required fields are missing.
        """
        if yaml_path is None:
            yaml_path = Path("config.yaml")

        if not yaml_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {yaml_path}. "
                "Please copy config.yaml.example to config.yaml and fill in your details."
            )

        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)

        payment_data = data.get("payment", {})
        monitoring_data = data.get("monitoring", {})
        # Support prioritized list of keywords, falling back to single keyword.
        yaml_keywords = data.get("search_keywords") or []
        if isinstance(yaml_keywords, str):
            yaml_keywords = [yaml_keywords]

        legacy_keyword = data.get("search_keyword", "")
        keywords_list = yaml_keywords if yaml_keywords else [legacy_keyword]
        # Normalize and drop empties
        keywords_list = [kw for kw in (k.strip() for k in keywords_list) if kw]

        return cls(
            search_keyword=data.get("search_keyword", ""),
            search_keywords=tuple(keywords_list),
            payment=PaymentConfig(
                name_on_card=payment_data.get("name_on_card", ""),
                card_number=payment_data.get("card_number", ""),
                cvv=payment_data.get("cvv", ""),
                exp_month=str(payment_data.get("exp_month", "12")),
                exp_year=str(payment_data.get("exp_year", "2026")),
                billing_zip=payment_data.get("billing_zip", ""),
                confirmation_email=payment_data.get("confirmation_email", ""),
            ),
            monitoring=MonitoringConfig(
                enabled=monitoring_data.get("enabled", False),
                interval_seconds=monitoring_data.get("interval_seconds", 30),
                email_on_available=monitoring_data.get("email_on_available", True),
                smtp_host=monitoring_data.get("smtp_host", "smtp.gmail.com"),
                smtp_port=monitoring_data.get("smtp_port", 587),
                smtp_user=monitoring_data.get("smtp_user", ""),
                smtp_password=monitoring_data.get("smtp_password", ""),
                notify_email=monitoring_data.get("notify_email", ""),
            ),
        )
