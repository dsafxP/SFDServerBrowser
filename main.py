import asyncio
import os

from app.fetcher import fetch_game_servers


def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def display_server_details(servers):
    """Display raw server details in a readable format."""
    if not servers:
        print("No servers found.")
    else:
        for i, server in enumerate(servers, start=1):
            print(f"Server {i}:")
            print(f"  IP Address (IPv4): {server.address_ipv4}")
            #print(f"  IP Address (IPv6): {server.address_ipv6}")
            #print(f"  LIP: {server.lip}")
            print(f"  Port: {server.port}")
            print(f"  Country: {server.country_code}")
            print(f"  Game Name: {server.game_name}")
            print(f"  Game Mode: {server.game_mode_name}")
            print(f"  Map Name: {server.map_name}")
            print(f"  Players: {server.players}/{server.max_players}")

            if server.bots > 0:
                print(f"  Bots: {server.bots}")

            print(f"  Has Password: {server.has_password}")

            if server.description:
                print(f"  Description: {server.description}")

            print(f"  Version: {server.version}")
            print(f"  Version Number: {server.version_nr}")
            print(f"  Application Instance: {server.application_instance}")
            print("-" * 50)

def main():
    """Main function to fetch and display servers."""
    print("Fetching game servers...")

    # Fetch servers asynchronously
    servers = asyncio.run(fetch_game_servers())

    cls()

    print("\n--- Game Servers Details ---")
    print(f"Total Players: {sum(server.players for server in servers)}")
    print("-" * 50)
    
    display_server_details(servers)

    # Wait for the user to press Enter to continue
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
