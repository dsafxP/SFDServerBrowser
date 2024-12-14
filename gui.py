import tkinter as tk
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

        # Create the Listbox to display server names
        self.listbox = tk.Listbox(self.root, width=80, height=15)
        self.listbox.pack(fill=tk.BOTH, expand=True)  # Make it fill the entire window

        # Create a Text widget to display the server details
        self.details_text = tk.Text(self.root, height=8, wrap=tk.WORD)
        self.details_text.pack(fill=tk.X, padx=10, pady=10)  # Fill horizontally, with padding

        self.servers = None

        # Set a fetch interval (in milliseconds), e.g., 30,000 ms = 30 seconds
        self.fetch_interval = 30000  # 30 seconds

        # Start the periodic fetch operation
        self.start_auto_fetch()

        # Bind left-click on the listbox to display server details
        self.listbox.bind('<Button-1>', self.on_server_select)

    def fetch_servers(self):
        """Fetch servers in a new thread so the UI doesn't freeze."""
        threading.Thread(target=self.run_fetch_game_servers, daemon=True).start()

    def run_fetch_game_servers(self):
        """Run the fetch_game_servers function in an asyncio event loop."""
        asyncio.run(fetch_game_servers(callback=self.update_server_list))

    def update_server_list(self, servers):
        """Update the Listbox with the server list."""
        self.servers = servers  # Store the server list as an attribute for later use
        self.listbox.delete(0, tk.END)  # Clear the listbox before updating

        if not servers:
            self.listbox.insert(tk.END, "No servers found.")
        else:
            for server in servers:
                self.listbox.insert(tk.END, server.game_name)

    def on_server_select(self, event):
        """Handle left-click on a server in the listbox."""
        selected_index = self.listbox.curselection()  # Get the index of the selected item
        if selected_index:
            # Get the selected server object (using the index)
            selected_server = self.servers[selected_index[0]]

            # Show detailed information in the Text widget
            server_details = (
                f"Game Name: {selected_server.game_name}\n"
                f"Game Mode: {selected_server.get_game_mode()}\n"
                f"Address (IPv4): {selected_server.address_ipv4}\n"
                #f"Address (IPv6): {selected_server.address_ipv6}\n"
                #f"LIP: {selected_server.lip}\n"
                f"Port: {selected_server.port}\n"
                f"Map Name: {selected_server.map_name}\n"
                f"Players: {selected_server.players}/{selected_server.max_players}\n"
                f"Bots: {selected_server.bots}\n"
                f"Password Protected: {'Yes' if selected_server.has_password else 'No'}\n"
                f"Version: {selected_server.version}\n"
                #f"Version Number: {selected_server.version_nr}\n"
                #f"Application Instance: {selected_server.application_instance}\n"
            )

            # Clear and insert the server details in the Text widget
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, server_details)

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
