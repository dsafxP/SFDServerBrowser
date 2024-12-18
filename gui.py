import tkinter as tk
from tkinter import ttk
from tkinter import Menu
import asyncio
import threading
import sys
import os
from app.fetcher import fetch_game_servers

class GameServersApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Superfighters Deluxe Game Servers")
        self.root.geometry("600x400")

        # Set a custom icon
        self.root.iconbitmap(resource_path("img/SFDicon.ico"))  # Replace with your .ico file path

        # Apply a custom theme
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f5f5f5")
        self.style.configure("TLabel", font=("Helvetica", 12), background="#f5f5f5",
                             foreground="#333")
        self.style.configure("TButton", font=("Helvetica", 10, "bold"), padding=10,
                             relief="flat", background="#4CAF50", foreground="white")
        self.style.map("TButton", background=[('active', '#45a049')])

        # Create a frame for the search bar
        self.search_frame = ttk.Frame(self.root)
        self.search_frame.pack(fill=tk.X, padx=20, pady=10)

        # Add emoji icon to the search bar
        self.emoji_label = ttk.Label(self.search_frame, text="🔍", font=("Helvetica", 12))
        self.emoji_label.pack(side=tk.LEFT, padx=10)

        # Create a search bar to filter by game name
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=10)
        self.search_entry.insert(0, "Search...")  # Set default text
        self.search_entry.bind("<KeyRelease>", self.on_search)

        # Create the Treeview to display server data with sorting capabilities
        self.treeview = ttk.Treeview(self.root, columns=("Game Name", "Game Mode", "Players",
                                                         "Password", "Version"), show="headings",
                                                         style="Treeview")

        self.treeview.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Define column headings and configure column widths
        self.treeview.heading("Game Name", text="Game Name", command=lambda:
                              self.sort_treeview("Game Name"))
        self.treeview.heading("Game Mode", text="Game Mode", command=lambda:
                              self.sort_treeview("Game Mode"))
        self.treeview.heading("Players", text="Players", command=lambda:
                              self.sort_treeview("Players"))
        self.treeview.heading("Password", text="Password", command=lambda:
                              self.sort_treeview("Password"))
        self.treeview.heading("Version", text="Version", command=lambda:
                              self.sort_treeview("Version"))

        # Define column widths
        self.treeview.column("Game Name", width=150, anchor=tk.W)
        self.treeview.column("Game Mode", width=150, anchor=tk.W)
        self.treeview.column("Players", width=100, anchor=tk.W)
        self.treeview.column("Password", width=100, anchor=tk.W)
        self.treeview.column("Version", width=100, anchor=tk.W)

        # Create a frame for the detailed information below the list
        self.details_frame = ttk.Frame(self.root)
        self.details_frame.pack(fill=tk.X, padx=20, pady=10)

        self.servers = None
        self.filtered_servers = FileNotFoundError

        # Set a fetch interval (in milliseconds)
        self.fetch_interval = 10000  # 10 seconds
        self.start_auto_fetch()

        # Bind left-click on the Treeview to display server details
        self.treeview.bind('<ButtonRelease-1>', self.on_server_select)

        self.treeview.insert("", "end", values=("Loading...", "", "", ""))

        self.treeview.bind("<Button-3>", self.show_context_menu)

        # Create a context menu
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copy IP Address", command=self.copy_ip_address)
        self.context_menu.add_command(label="Copy Game Info", command=self.copy_game_info)

    def fetch_servers(self):
        """Fetch servers in a new thread so the UI doesn't freeze."""
        threading.Thread(target=self.run_fetch_game_servers, daemon=True).start()

    def run_fetch_game_servers(self):
        """Run the fetch_game_servers function in an asyncio event loop."""
        asyncio.run(fetch_game_servers(callback=self.update_server_list))

    def update_server_list(self, servers):
        """Update the Treeview with the server list."""
        self.servers = servers
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

    def on_server_select(self, _event):
        """Handle left-click on a server in the Treeview."""
        selected_item = self.treeview.selection()
        if selected_item:
            selected_server = None
            for item in selected_item:
                for server in self.servers:
                    if server.game_name == self.treeview.item(item)["values"][0]:
                        selected_server = server
                        break

            if selected_server:
                server_details = (
                    f"Address: {selected_server.address_ipv4}\n"
                    f"Port: {selected_server.port}\n"
                    f"Map Name: {selected_server.map_name}\n" +
                    (f"Bots: {selected_server.bots}\n" if selected_server.bots > 0 else "")
                )

                # Clear previous details in the frame
                for widget in self.details_frame.winfo_children():
                    widget.destroy()

                # Create a Label for the server details and pack it in the frame
                details_label = ttk.Label(self.details_frame, text=server_details, justify=tk.LEFT)
                details_label.pack(fill=tk.X, padx=10, pady=5)

    def on_search(self, _event):
        """Filter the server list by the search input."""
        search_term = self.search_var.get().lower()
        if search_term:
            self.filtered_servers = [server for server in self.servers if search_term in
                                     server.game_name.lower()]
        else:
            self.filtered_servers = self.servers  # No filter if search bar is empty

        self.display_servers(self.filtered_servers)

    def sort_treeview(self, col):
        """Sort the Treeview by the selected column."""
        column_index = self.treeview["columns"].index(col)

        items = [(self.treeview.item(item)["values"], item) for item in
                 self.treeview.get_children()]

        if col == "Players":
            items.sort(key=lambda x: int(x[0][2].split('/')[0]),
                       reverse=True)  # Sorting by current players
        elif col == "Password":
            items.sort(key=lambda x: x[0][3] == "Yes", reverse=False)  # False (No) comes first
        else:
            items.sort(key=lambda x: x[0][column_index])  # Alphabetical sorting for text columns

        for i, (_, item) in enumerate(items):
            self.treeview.move(item, '', i)

    def start_auto_fetch(self):
        """Start a periodic task to fetch game servers automatically."""
        self.fetch_servers()  # Fetch servers immediately
        self.root.after(self.fetch_interval,
                        self.start_auto_fetch) # Set the next fetch after the interval
        
    def show_context_menu(self, event):
        """Display the context menu on right-click."""
        # Identify the clicked item
        item = self.treeview.identify_row(event.y)
        if item:
            self.treeview.selection_set(item)  # Select the item
            self.context_menu.post(event.x_root, event.y_root)

    def copy_ip_address(self):
        """Copy the selected server's IP address to the clipboard."""
        selected_item = self.treeview.selection()
        if selected_item:
            for item in selected_item:
                for server in self.servers:
                    if server.game_name == self.treeview.item(item)["values"][0]:
                        self.root.clipboard_clear()
                        self.root.clipboard_append(server.address_ipv4)
                        self.root.update()  # Keep the clipboard updated
                        break

    def copy_game_info(self):
        """Copy the selected server's game information to the clipboard."""
        selected_item = self.treeview.selection()
        if selected_item:
            for item in selected_item:
                for server in self.servers:
                    if server.game_name == self.treeview.item(item)["values"][0]:
                        game_info = (
                            f"Game Name: {server.game_name}\n"
                            f"Game Mode: {server.get_game_mode()}\n"
                            f"Players: {server.players}/{server.max_players}\n"
                            f"Version: {server.version}"
                        )
                        self.root.clipboard_clear()
                        self.root.clipboard_append(game_info)
                        self.root.update()  # Keep the clipboard updated
                        break

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for development and for PyInstaller. """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def run_gui():
    """Set up the main Tkinter GUI window and start the application."""
    root = tk.Tk()
    GameServersApp(root)
    root.mainloop()

if __name__ == '__main__':
    run_gui()
