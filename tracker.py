"""
Tracker module - Core logic that fetches IP geolocation data from public APIs.
"""

import logging
from typing import Dict, Any, Optional

import requests

from utils import build_google_maps_url

logger = logging.getLogger(__name__)


class IPTrackerError(Exception):
    """Base exception for IP Tracker errors."""


class APIRateLimitError(IPTrackerError):
    """Raised when the API rate limit is exceeded."""


class APIFailureError(IPTrackerError):
    """Raised when the API returns a failure response."""


class NoInternetError(IPTrackerError):
    """Raised when there is no internet connectivity."""


class IPTracker:
    """
    Fetches geolocation and OSINT data for a given IP address.

    Uses ip-api.com (free tier, no API key required) as the primary source.
    Falls back to ipapi.co if the primary source fails.
    """

    PRIMARY_API = "http://ip-api.com/json/{ip}"
    PRIMARY_FIELDS = (
        "status,message,query,country,countryCode,region,regionName,city,zip,"
        "lat,lon,timezone,isp,org,as,asname,mobile,proxy,hosting,currency"
    )
    FALLBACK_API = "https://ipapi.co/{ip}/json/"

    def __init__(self, timeout: int = 10) -> None:
        """
        Initialize the tracker.

        Args:
            timeout (int): HTTP request timeout in seconds.
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "IP-Tracker/1.0 (Educational)"}
        )

    def fetch(self, ip: str) -> Dict[str, Any]:
        """
        Fetch information for the given IP.

        Args:
            ip (str): IP address.

        Returns:
            Dict[str, Any]: Normalized data dictionary.

        Raises:
            NoInternetError: On connection failure.
            APIRateLimitError: On 429 response.
            APIFailureError: On other API errors.
        """
        try:
            data = self._query_primary(ip)
        except (APIFailureError, APIRateLimitError) as exc:
            logger.warning(f"Primary API failed: {exc}. Falling back.")
            data = self._query_fallback(ip)

        return self._normalize(data, ip)

    def _query_primary(self, ip: str) -> Dict[str, Any]:
        """Query the primary API (ip-api.com)."""
        url = self.PRIMARY_API.format(ip=ip)
        try:
            response = self.session.get(
                url,
                params={"fields": self.PRIMARY_FIELDS},
                timeout=self.timeout,
            )
        except requests.exceptions.ConnectionError as exc:
            raise NoInternetError("No internet connection available.") from exc
        except requests.exceptions.Timeout as exc:
            raise APIFailureError("Primary API request timed out.") from exc

        if response.status_code == 429:
            raise APIRateLimitError("Primary API rate limit exceeded.")
        if response.status_code != 200:
            raise APIFailureError(
                f"Primary API returned HTTP {response.status_code}."
            )

        payload = response.json()
        if payload.get("status") != "success":
            raise APIFailureError(
                f"Primary API error: {payload.get('message', 'unknown')}"
            )
        payload["_source"] = "ip-api.com"
        return payload

    def _query_fallback(self, ip: str) -> Dict[str, Any]:
        """Query the fallback API (ipapi.co)."""
        url = self.FALLBACK_API.format(ip=ip)
        try:
            response = self.session.get(url, timeout=self.timeout)
        except requests.exceptions.ConnectionError as exc:
            raise NoInternetError("No internet connection available.") from exc
        except requests.exceptions.Timeout as exc:
            raise APIFailureError("Fallback API request timed out.") from exc

        if response.status_code == 429:
            raise APIRateLimitError("Fallback API rate limit exceeded.")
        if response.status_code != 200:
            raise APIFailureError(
                f"Fallback API returned HTTP {response.status_code}."
            )

        payload = response.json()
        if payload.get("error"):
            raise APIFailureError(
                f"Fallback API error: {payload.get('reason', 'unknown')}"
            )
        payload["_source"] = "ipapi.co"
        return payload

    def _normalize(self, raw: Dict[str, Any], ip: str) -> Dict[str, Any]:
        """
        Normalize responses from both APIs into a unified schema.

        Args:
            raw (Dict[str, Any]): Raw API response.
            ip (str): The queried IP.

        Returns:
            Dict[str, Any]: Unified data dictionary.
        """
        source = raw.get("_source", "unknown")

        if source == "ip-api.com":
            lat = raw.get("lat")
            lon = raw.get("lon")
            net_type = self._infer_network_type(raw)
            data = {
                "ip": raw.get("query", ip),
                "country": raw.get("country"),
                "country_code": raw.get("countryCode"),
                "region": raw.get("regionName"),
                "city": raw.get("city"),
                "zip": raw.get("zip"),
                "latitude": lat,
                "longitude": lon,
                "isp": raw.get("isp"),
                "organization": raw.get("org"),
                "asn": raw.get("as"),
                "timezone": raw.get("timezone"),
                "currency": raw.get("currency"),
                "calling_code": None,
                "languages": None,
                "network_type": net_type,
            }
        else:  # ipapi.co
            lat = raw.get("latitude")
            lon = raw.get("longitude")
            data = {
                "ip": raw.get("ip", ip),
                "country": raw.get("country_name"),
                "country_code": raw.get("country_code"),
                "region": raw.get("region"),
                "city": raw.get("city"),
                "zip": raw.get("postal"),
                "latitude": lat,
                "longitude": lon,
                "isp": raw.get("org"),
                "organization": raw.get("org"),
                "asn": raw.get("asn"),
                "timezone": raw.get("timezone"),
                "currency": raw.get("currency"),
                "calling_code": raw.get("country_calling_code"),
                "languages": raw.get("languages"),
                "network_type": None,
            }

        if lat is not None and lon is not None:
            data["google_maps"] = build_google_maps_url(lat, lon)
        else:
            data["google_maps"] = None

        data["flag"] = self._country_flag(data.get("country_code"))
        data["source"] = source
        return data

    @staticmethod
    def _infer_network_type(raw: Dict[str, Any]) -> Optional[str]:
        """Infer a rough network type label from API flags."""
        if raw.get("mobile"):
            return "Mobile"
        if raw.get("proxy"):
            return "Proxy/VPN"
        if raw.get("hosting"):
            return "Hosting/Datacenter"
        return "Residential/Business"

    @staticmethod
    def _country_flag(country_code: Optional[str]) -> Optional[str]:
        """
        Convert an ISO-3166 alpha-2 code into a flag emoji.

        Args:
            country_code (Optional[str]): Two-letter country code.

        Returns:
            Optional[str]: Flag emoji string.
        """
        if not country_code or len(country_code) != 2:
            return None
        return "".join(chr(0x1F1E6 + (ord(c.upper()) - ord("A"))) for c in country_code)
