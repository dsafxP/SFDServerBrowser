import tkinter as tk
from tkinter import ttk
import asyncio
import threading
from app.fetcher import fetch_game_servers

class GameServersApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Superfighters Deluxe Game Servers")
        self.root.geometry("600x400")

        # Set a custom icon
        self.root.iconbitmap("img/SFDicon.ico")  # Replace with your .ico file path

        # Create a frame for the search bar
        self.search_frame = tk.Frame(self.root)
        self.search_frame.pack(fill=tk.X, padx=10, pady=5)

        # Create a search bar to filter by game name
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.search_frame, textvariable=self.search_var, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=10)
        self.search_entry.bind("<KeyRelease>", self.on_search)  # Bind search function to key release event

        # Create the Treeview to display server data with sorting capabilities
        self.treeview = ttk.Treeview(self.root, columns=("Game Name", "Game Mode", "Players", "Password", "Version"), show="headings")
        self.treeview.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Define column headings and configure column widths
        self.treeview.heading("Game Name", text="Game Name", command=lambda: self.sort_treeview("Game Name"))
        self.treeview.heading("Game Mode", text="Game Mode", command=lambda: self.sort_treeview("Game Mode"))
        self.treeview.heading("Players", text="Players", command=lambda: self.sort_treeview("Players"))
        self.treeview.heading("Password", text="Password", command=lambda: self.sort_treeview("Password"))
        self.treeview.heading("Version", text="Version", command=lambda: self.sort_treeview("Version"))

        self.treeview.column("Game Name", width=100, anchor=tk.W)
        self.treeview.column("Game Mode", width=100, anchor=tk.W)
        self.treeview.column("Players", width=100, anchor=tk.W)
        self.treeview.column("Password", width=100, anchor=tk.W)
        self.treeview.column("Version", width=100, anchor=tk.W)

        # Create a frame for the detailed information below the list
        self.details_frame = tk.Frame(self.root)
        self.details_frame.pack(fill=tk.X, padx=10, pady=10)

        self.servers = None

        # Set a fetch interval (in milliseconds), e.g., 30,000 ms = 30 seconds
        self.fetch_interval = 30000  # 30 seconds

        # Start the periodic fetch operation
        self.start_auto_fetch()

        # Bind left-click on the Treeview to display server details
        self.treeview.bind('<ButtonRelease-1>', self.on_server_select)

    def fetch_servers(self):
        """Fetch servers in a new thread so the UI doesn't freeze."""
        threading.Thread(target=self.run_fetch_game_servers, daemon=True).start()

    def run_fetch_game_servers(self):
        """Run the fetch_game_servers function in an asyncio event loop."""
        asyncio.run(fetch_game_servers(callback=self.update_server_list))

    def update_server_list(self, servers):
        """Update the Treeview with the server list."""
        self.servers = servers  # Store the server list as an attribute for later use
        self.filtered_servers = servers  # Initially, no filter is applied
        self.display_servers(self.filtered_servers)

    def display_servers(self, servers):
        """Display servers in the Treeview."""
        for item in self.treeview.get_children():
            self.treeview.delete(item)  # Clear the existing entries in the Treeview

        if not servers:
            self.treeview.insert("", "end", values=("No servers found", "", "", ""))
        else:
            for server in servers:
                self.treeview.insert("", "end", values=(
                    server.game_name,
                    server.get_game_mode(),
                    f"{server.players}/{server.max_players}",
                    "Yes" if server.has_password else "No",
                    server.version
                ))

    def on_server_select(self, event):
        """Handle left-click on a server in the Treeview."""
        selected_item = self.treeview.selection()  # Get the selected item
        if selected_item:
            # Get the corresponding server object for the selected item
            selected_server = None
            for item in selected_item:
                # Find the server object based on the item value (server game name or other unique info)
                for server in self.servers:
                    if server.game_name == self.treeview.item(item)["values"][0]:  # Match by game name (or any unique identifier)
                        selected_server = server
                        break

            if selected_server:
                # Create detailed information for the selected server
                server_details = (
                    f"Game Name: {selected_server.game_name}\n"
                    f"Game Mode: {selected_server.get_game_mode()}\n"
                    f"Address (IPv4): {selected_server.address_ipv4}\n"
                    f"Port: {selected_server.port}\n"
                    f"Map Name: {selected_server.map_name}\n"
                    f"Players: {selected_server.players}/{selected_server.max_players}\n"
                    f"Bots: {selected_server.bots}\n"
                    f"Password Protected: {'Yes' if selected_server.has_password else 'No'}\n"
                    f"Version: {selected_server.version}\n"
                )

                # Clear previous details in the frame
                for widget in self.details_frame.winfo_children():
                    widget.destroy()

                # Create a Label for the server details and pack it in the frame
                details_label = tk.Label(self.details_frame, text=server_details, justify=tk.LEFT)
                details_label.pack(fill=tk.X, padx=10, pady=5)

    def on_search(self, event):
        """Filter the server list by the search input."""
        search_term = self.search_var.get().lower()
        if search_term:
            self.filtered_servers = [server for server in self.servers if search_term in server.game_name.lower()]
        else:
            self.filtered_servers = self.servers  # No filter if search bar is empty

        self.display_servers(self.filtered_servers)

    def sort_treeview(self, col):
        """Sort the Treeview by the selected column."""
        column_index = self.treeview["columns"].index(col)
        items = [(self.treeview.item(item)["values"], item) for item in self.treeview.get_children()]
    
        if col == "Players":
            # Sort by the current players (extracted from the format current_players/max_players)
            items.sort(key=lambda x: int(x[0][2].split('/')[0]), reverse=True)  # Sorting by current players
        elif col == "Password":
            # Sort by password status (No should come before yes)
            items.sort(key=lambda x: x[0][3] == "Yes", reverse=False)  # False (No) comes first
        else:
            # Default sorting for other columns (Game Name, Game Mode, Version)
            items.sort(key=lambda x: x[0][column_index])  # Alphabetical sorting for text columns

        # Re-insert sorted items into the Treeview
        for i, (_, item) in enumerate(items):
            self.treeview.move(item, '', i)

    def start_auto_fetch(self):
        """Start a periodic task to fetch game servers automatically."""
        self.fetch_servers()  # Fetch servers immediately
        self.root.after(self.fetch_interval,
                        self.start_auto_fetch)  # Set the next fetch after the interval

def run_gui():
    """Set up the main Tkinter GUI window and start the application."""
    root = tk.Tk()
    GameServersApp(root)
    root.mainloop()

if __name__ == '__main__':
    run_gui()
