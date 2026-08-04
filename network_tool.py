"""
Network tools module - Reverse DNS, Whois, Ping, and DNS lookups.
"""

import socket
import subprocess
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class NetworkTools:
    """Provides auxiliary network reconnaissance helpers."""

    @staticmethod
    def reverse_dns(ip: str) -> Optional[str]:
        """
        Perform reverse DNS lookup for a given IP.

        Args:
            ip (str): IP address.

        Returns:
            Optional[str]: Hostname or None.
        """
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except (socket.herror, socket.gaierror) as exc:
            logger.debug(f"Reverse DNS failed for {ip}: {exc}")
            return None

    @staticmethod
    def ping(ip: str, count: int = 3, timeout: int = 2) -> Optional[float]:
        """
        Ping the IP and return average latency in ms.

        Args:
            ip (str): IP address to ping.
            count (int): Number of ping requests.
            timeout (int): Timeout in seconds per ping.

        Returns:
            Optional[float]: Average latency in ms, None on failure.
        """
        try:
            result = subprocess.run(
                ["ping", "-c", str(count), "-W", str(timeout), ip],
                capture_output=True,
                text=True,
                timeout=count * timeout + 5,
            )
            if result.returncode != 0:
                return None

            # Parse "rtt min/avg/max/mdev = a/b/c/d ms"
            for line in result.stdout.splitlines():
                if "avg" in line and "=" in line:
                    stats = line.split("=")[1].strip().split(" ")[0]
                    avg = stats.split("/")[1]
                    return float(avg)
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError) as exc:
            logger.debug(f"Ping failed for {ip}: {exc}")
        return None

    @staticmethod
    def whois_lookup(ip: str) -> Optional[str]:
        """
        Run whois command on the IP.

        Args:
            ip (str): IP address.

        Returns:
            Optional[str]: Whois result text.
        """
        try:
            result = subprocess.run(
                ["whois", ip], capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
            logger.debug(f"Whois failed for {ip}: {exc}")
        return None

    @staticmethod
    def dns_info(ip: str) -> Dict[str, Any]:
        """
        Retrieve DNS information such as hostname and aliases.

        Args:
            ip (str): IP address.

        Returns:
            Dict[str, Any]: DNS details.
        """
        info: Dict[str, Any] = {"hostname": None, "aliases": [], "addresses": []}
        try:
            hostname, aliases, addresses = socket.gethostbyaddr(ip)
            info["hostname"] = hostname
            info["aliases"] = aliases
            info["addresses"] = addresses
        except (socket.herror, socket.gaierror):
            pass
        return info

import cv2

class WebcamTools:
    """Handles local webcam access and image capture."""

    @staticmethod
    def capture_photo(output_path: str = "webcam_snap.jpg", camera_index: int = 0) -> bool:
        """
        Webcam se ek photo capture karke save karta hai.
        
        Args:
            output_path (str): File saving location.
            camera_index (int): Camera ID (0 default camera hota hai).
        Returns:
            bool: True if successful, False otherwise.
        """
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            logger.error("Webcam open nahi ho saka.")
            return False

        ret, frame = cap.read()
        if ret:
            cv2.imwrite(output_path, frame)
            logger.info(f"Webcam photo saved at {output_path}")
            cap.release()
            return True
        
        cap.release()
        return False
