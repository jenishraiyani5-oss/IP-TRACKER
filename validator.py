"""
Validator module - Validates IPv4 and IPv6 addresses.
"""

import ipaddress
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class IPValidator:
    """Class responsible for validating IP addresses (IPv4/IPv6)."""

    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        """
        Check whether the given string is a valid IPv4 or IPv6 address.

        Args:
            ip (str): The IP address to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        if not ip or not isinstance(ip, str):
            return False
        try:
            ipaddress.ip_address(ip.strip())
            return True
        except ValueError:
            logger.debug(f"Invalid IP address: {ip}")
            return False

    @staticmethod
    def get_ip_version(ip: str) -> Optional[int]:
        """
        Return the IP version (4 or 6) of the given address.

        Args:
            ip (str): The IP address.

        Returns:
            Optional[int]: 4 or 6, or None if invalid.
        """
        try:
            return ipaddress.ip_address(ip.strip()).version
        except ValueError:
            return None

    @staticmethod
    def is_private(ip: str) -> bool:
        """
        Check whether the IP address is private (RFC1918 or link-local).

        Args:
            ip (str): IP to check.

        Returns:
            bool: True if private, False otherwise.
        """
        try:
            return ipaddress.ip_address(ip.strip()).is_private
        except ValueError:
            return False
