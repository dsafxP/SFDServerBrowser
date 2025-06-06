from dataclasses import dataclass
from typing import Optional


@dataclass
class Server:
    # Network
    address_ipv4: str
    port: int
    address_ipv6: Optional[str] = None
    lip: Optional[str] = None

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
    application_instance: Optional[str] = None

    GAME_MODES = {
        1: "Versus",
        2: "Custom",
        3: "Campaign",
        4: "Survival"
    }

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