import json
from dataclasses import dataclass
from typing import ClassVar, Dict, List

import requests


@dataclass
class Server:
    # Network
    address_ipv4: str
    port: int
    address_ipv6: str | None = None
    lip: str | None = None

    # Game info
    game_name: str = ""
    game_mode: int = 0
    map_name: str = ""

    # Player info
    players: int = 0
    max_players: int = 0
    bots: int = 0

    # Server details
    has_password: bool = False
    description: str = ""
    version: str = ""
    version_nr: int = 0
    application_instance: str | None = None

    GAME_MODES = {
        1: "Versus",
        2: "Custom",
        3: "Campaign",
        4: "Survival"
    }

    # Class-level cache for IP to country code mapping
    _country_cache: ClassVar[Dict[str, str]] = {}

    def __str__(self):
        return f"Server({self.game_name}, {self.address_ipv4}, {self.port})"

    @property
    def game_mode_name(self):
        """Returns human-readable game mode name."""
        return self.GAME_MODES.get(self.game_mode, "Unknown")

    @property
    def is_full(self):
        """Check if server is at capacity."""
        return self.players >= self.max_players

    @property
    def connection_string(self):
        """Get connection string for the server."""
        return f"{self.address_ipv4}:{self.port}"

    @property
    def country_code(self) -> str:
        """
        Get the country code for this server's IP address.

        If the IP is not in cache, this will make an API request and block
        until the result is available. Uses single IP endpoint for efficiency.

        Returns:
            Country code string (e.g., 'US', 'GB') or 'Unknown' if lookup fails
        """
        # Check if this IP is already cached
        if self.address_ipv4 in Server._country_cache:
            return Server._country_cache[self.address_ipv4]

        # IP not in cache, use single IP lookup for efficiency
        return Server._get_single_country_code(self.address_ipv4)

    @staticmethod
    def get_country_codes(servers: List['Server']) -> Dict[str, str]:
        """
        Retrieve country codes for a collection of Server instances using ip-api batch endpoint.

        Args:
            servers: List of Server instances

        Returns:
            Dictionary mapping IP addresses to country codes
        """
        if not servers:
            return {}

        # Get unique IP addresses that aren't already cached
        unique_ips = set(server.address_ipv4 for server in servers)
        uncached_ips = [ip for ip in unique_ips if ip not in Server._country_cache]

        # If all IPs are cached, return cached results
        if not uncached_ips:
            return {ip: Server._country_cache[ip] for ip in unique_ips}

        # Prepare batch request for uncached IPs
        # ip-api batch endpoint expects a JSON array of IP addresses or objects
        batch_data = uncached_ips

        try:
            response = requests.post(
                'http://ip-api.com/batch?fields=16386',
                json=batch_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()

            batch_results = response.json()

            # Process results and update cache
            for i, result in enumerate(batch_results):
                ip = uncached_ips[i]
                if result.get('status') == 'success':
                    country_code = result.get('countryCode', 'Unknown')
                    Server._country_cache[ip] = country_code
                else:
                    # Cache failed lookups as 'Unknown' to avoid repeated requests
                    Server._country_cache[ip] = 'Unknown'

        except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
            # On error, cache all uncached IPs as 'Unknown' to avoid repeated failed requests
            for ip in uncached_ips:
                Server._country_cache[ip] = 'Unknown'
            print(f"Error fetching country codes: {e}")

        # Return results for all requested IPs (both cached and newly fetched)
        return {ip: Server._country_cache[ip] for ip in unique_ips}

    @staticmethod
    def _get_single_country_code(ip: str) -> str:
        """
        Fetch country code for a single IP address using the single query endpoint.

        Args:
            ip: IP address to lookup

        Returns:
            Country code string or 'Unknown' if lookup fails
        """
        try:
            response = requests.get(
                f'http://ip-api.com/json/{ip}?fields=16386',
                timeout=10
            )
            response.raise_for_status()

            result = response.json()

            if result.get('status') == 'success':
                country_code = result.get('countryCode', 'Unknown')
                Server._country_cache[ip] = country_code
                return country_code
            else:
                # Cache failed lookups as 'Unknown' to avoid repeated requests
                Server._country_cache[ip] = 'Unknown'
                return 'Unknown'

        except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
            # On error, cache as 'Unknown' to avoid repeated failed requests
            Server._country_cache[ip] = 'Unknown'
            print(f"Error fetching country code for {ip}: {e}")
            return 'Unknown'

    @staticmethod
    def clear_country_cache():
        """Clear the country code cache."""
        Server._country_cache.clear()