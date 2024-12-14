# app/server.py
class Server:
    def __init__(self, address_ipv4, address_ipv6, lip, port, game_name, game_mode, map_name, players, max_players, bots, has_password, description, version, version_nr, application_instance):
        self.address_ipv4 = address_ipv4
        self.address_ipv6 = address_ipv6
        self.lip = lip
        self.port = port
        self.game_name = game_name
        self.game_mode = game_mode
        self.map_name = map_name
        self.players = players
        self.max_players = max_players
        self.bots = bots
        self.has_password = has_password
        self.description = description
        self.version = version
        self.version_nr = version_nr
        self.application_instance = application_instance

    def __repr__(self):
        return f"Server({self.game_name}, {self.address_ipv4}, {self.port})"
        
    def get_game_mode(self):
        """Returns a human-readable string for the game mode."""
        game_modes = {
            1: "Versus",
            2: "Custom",
            3: "Campaign",
            4: "Survival"
        }
        return game_modes.get(self.game_mode, "Unknown")
