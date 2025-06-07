import flet as ft
import asyncio
import threading
from typing import List, Optional, Dict
from app.fetcher import fetch_game_servers
from app.server import Server


class GameServersApp:
    def __init__(self, page: ft.Page):
        self.loading_icon = ft.Icon  # Changed from ProgressRing to Icon
        self.details_card = ft.Card
        self.data_table = ft.DataTable
        self.server_list_container = ft.Container
        self.total_players_text = ft.Text
        self.auto_update_checkbox = ft.Checkbox
        self.update_button = ft.ElevatedButton
        self.search_field = ft.TextField
        self.page = page
        self.servers: List[Server] = []
        self.filtered_servers: List[Server] = []
        self.selected_server: Optional[Server] = None
        self.auto_update_enabled = True
        self.fetch_interval = 12  # seconds
        self.sort_reverse: Dict[str, bool] = {}  # Track sort direction for each column
        self.current_sort_column: Optional[str] = None  # Track current sort column

        # Add shutdown control
        self.shutdown_event = threading.Event()
        self.auto_update_timer: Optional[threading.Timer] = None

        # Register cleanup on page close
        self.page.on_window_event = self.on_window_event

        self.setup_page()
        self.build_ui()
        self.start_auto_fetch()

    def on_window_event(self, e):
        """Handle window events, including close."""
        if e.data == "close":
            self.cleanup()

    def cleanup(self):
        """Clean shutdown of all background threads."""
        self.shutdown_event.set()
        self.auto_update_enabled = False

        # Cancel any pending timer
        if self.auto_update_timer:
            self.auto_update_timer.cancel()
            self.auto_update_timer = None

    def setup_page(self):
        """Configure the main page settings."""
        self.page.title = "Superfighters Deluxe Game Servers"
        self.page.window_width = 1000
        self.page.window_height = 700
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 20

    def build_ui(self):
        """Build the user interface components."""
        # Search and controls section
        self.search_field = ft.TextField(
            hint_text="Search servers...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.on_search,
            expand=True
        )

        self.update_button = ft.ElevatedButton(
            text="Update",
            icon=ft.Icons.REFRESH,
            on_click=self.fetch_servers_click,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN,
                color=ft.Colors.WHITE
            )
        )

        self.auto_update_checkbox = ft.Checkbox(
            label="Auto Update",
            value=True,
            on_change=self.toggle_auto_update
        )

        # Loading icon - positioned next to auto update checkbox
        self.loading_icon = ft.Icon(
            ft.Icons.SYNC,
            size=20,
            color=ft.Colors.BLUE,
            visible=True,
            animate_rotation=ft.Animation(1000, ft.AnimationCurve.LINEAR)
        )

        # Total players display
        self.total_players_text = ft.Text(
            "Total Players: 0",
            size=16,
            weight=ft.FontWeight.BOLD
        )

        # Server list data table
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(
                    ft.Text("Game Name", weight=ft.FontWeight.BOLD),
                    on_sort=lambda e: self.sort_table("game_name")
                ),
                ft.DataColumn(
                    ft.Text("Game Mode", weight=ft.FontWeight.BOLD),
                    on_sort=lambda e: self.sort_table("game_mode")
                ),
                ft.DataColumn(
                    ft.Text("Players", weight=ft.FontWeight.BOLD),
                    on_sort=lambda e: self.sort_table("players")
                ),
                ft.DataColumn(
                    ft.Text("Password", weight=ft.FontWeight.BOLD),
                    on_sort=lambda e: self.sort_table("password")
                ),
                ft.DataColumn(
                    ft.Text("Version", weight=ft.FontWeight.BOLD),
                    on_sort=lambda e: self.sort_table("version")
                ),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=10,
            sort_column_index=2,  # Default sort by players
            sort_ascending=False
        )

        # Details section - compact when visible
        self.details_card = ft.Card(
            content=ft.Container(
                content=ft.Text("Select a server to view details"),
                padding=15
            ),
            visible=False
        )

        # Server list container
        self.server_list_container = ft.Container(
            content=ft.Column([
                self.data_table
            ], scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=10,
            padding=10,
            expand=True,
            width=float('inf')  # Expand to full width
        )

        # Layout the UI
        self.page.add(
            ft.Column([
                # Header section
                ft.Container(
                    content=ft.Row([
                        self.search_field,
                        self.update_button,
                        ft.Row([  # Group auto update checkbox and loading icon
                            self.auto_update_checkbox,
                            self.loading_icon
                        ], spacing=5)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.only(bottom=10)
                ),

                ft.Divider(height=1),

                # Stats section
                ft.Container(
                    content=self.total_players_text,
                    padding=ft.padding.only(bottom=10)
                ),

                # Server list section (expands to fill available space)
                self.server_list_container,

                # Details section
                self.details_card
            ],
                expand=True,
                spacing=5
            )
        )

    def fetch_servers_click(self, _):
        """Handle manual server fetch button click."""
        if not self.shutdown_event.is_set():
            self.fetch_servers()

    def fetch_servers(self):
        """Fetch servers in a separate thread."""
        if self.shutdown_event.is_set():
            return

        self.update_button.disabled = True
        self.loading_icon.visible = True
        # Start rotation animation
        self.loading_icon.rotate = ft.Rotate(0)

        # Check if page is still valid before updating
        try:
            self.page.update()
        except:
            return  # Page is closed, exit gracefully

        # Animate the rotation
        def animate_loading():
            for i in range(36):  # 360 degrees in 10-degree increments
                if self.shutdown_event.is_set():
                    break
                if self.loading_icon.visible:
                    self.loading_icon.rotate = ft.Rotate(i * 0.1745)  # Convert to radians
                    try:
                        self.page.update()
                    except:
                        break  # Page is closed, exit gracefully
                    threading.Event().wait(0.01)  # Small delay for smooth animation

        threading.Thread(target=animate_loading, daemon=True).start()
        threading.Thread(target=self.run_fetch_game_servers, daemon=True).start()

    def run_fetch_game_servers(self):
        """Run the async fetch operation."""
        if self.shutdown_event.is_set():
            return

        try:
            asyncio.run(fetch_game_servers(callback=self.update_server_list))
        except Exception as e:
            if not self.shutdown_event.is_set():
                # Schedule UI update on main thread
                def update_error():
                    if not self.shutdown_event.is_set():
                        self.handle_fetch_error(str(e))

                threading.Timer(0.1, update_error).start()

    def handle_fetch_error(self, error_msg: str):
        """Handle fetch errors on the main thread."""
        if self.shutdown_event.is_set():
            return

        self.loading_icon.visible = False
        self.update_button.disabled = False
        self.show_snackbar(f"Error: {error_msg}")

        try:
            self.page.update()
        except:
            pass  # Page is closed, ignore

    def update_server_list(self, servers: List[Server]):
        """Update the server list (called from background thread)."""
        if self.shutdown_event.is_set():
            return

        # Schedule UI update on main thread
        def update_ui():
            if not self.shutdown_event.is_set():
                self._update_server_list_ui(servers)

        threading.Timer(0.1, update_ui).start()

    def _update_server_list_ui(self, servers: List[Server]):
        """Update the UI with new server data."""
        if self.shutdown_event.is_set():
            return

        self.servers = servers
        self.filtered_servers = servers

        # Preserve current sort order if one exists
        if self.current_sort_column:
            self._apply_current_sort()

        self.display_servers(self.filtered_servers)

        # Update total players
        total_players = sum(server.players for server in servers)
        self.total_players_text.value = f"Total Players: {total_players}"

        # Hide loading indicator and reset rotation
        self.loading_icon.visible = False
        self.loading_icon.rotate = ft.Rotate(0)
        self.update_button.disabled = False

        try:
            self.page.update()
        except:
            pass  # Page is closed, ignore

    def display_servers(self, servers: List[Server]):
        """Display servers in the data table."""
        new_rows = []

        if not servers:
            new_rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("No servers found")),
                ])
            )
        else:
            for server in servers:
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(server.game_name or "Unknown")),
                        ft.DataCell(ft.Text(server.game_mode_name)),
                        ft.DataCell(ft.Text(f"{server.players}/{server.max_players}")),
                        ft.DataCell(ft.Text("Yes" if server.has_password else "No")),
                        ft.DataCell(ft.Text(server.version or "Unknown"))
                    ],
                    on_select_changed=lambda e, srv=server: self.on_server_select(srv)
                )
                new_rows.append(row)

        # Assign the new list to rows
        self.data_table.rows = new_rows

    def on_server_select(self, server: Server):
        """Handle server selection."""
        if self.shutdown_event.is_set():
            return

        self.selected_server = server

        # Build server details
        details_text = f"""Address: {server.address_ipv4 or 'Unknown'}
Port: {server.port}
Map Name: {server.map_name or 'Unknown'}"""

        if server.bots > 0:
            details_text += f"\nBots: {server.bots}"

        if server.description:
            details_text += f"\nDescription: {server.description}"

        # Update details card
        self.details_card.content = ft.Container(
            content=ft.Column([
                ft.Text("Server Details", size=18, weight=ft.FontWeight.BOLD),
                ft.Text(details_text),
                ft.Row([
                    ft.ElevatedButton(
                        "Copy IP",
                        icon=ft.Icons.COPY,
                        on_click=self.copy_ip_address
                    ),
                    ft.ElevatedButton(
                        "Copy Info",
                        icon=ft.Icons.INFO,
                        on_click=self.copy_game_info
                    ),
                    ft.ElevatedButton(
                        "Hide Details",
                        icon=ft.Icons.CLOSE,
                        on_click=self.hide_details
                    )
                ])
            ]),
            padding=15  # Reduced padding to be more compact
        )

        # Show details
        self.details_card.visible = True
        try:
            self.page.update()
        except:
            pass  # Page is closed, ignore

    def hide_details(self, _=None):
        """Hide the server details card."""
        if self.shutdown_event.is_set():
            return

        self.details_card.visible = False
        self.selected_server = None
        try:
            self.page.update()
        except:
            pass  # Page is closed, ignore

    def on_search(self, e):
        """Filter servers based on search input."""
        if self.shutdown_event.is_set():
            return

        search_term = e.control.value.lower()
        if search_term and self.servers:
            self.filtered_servers = [
                server for server in self.servers
                if search_term in (server.game_name or "").lower()
            ]
        else:
            self.filtered_servers = self.servers

        # Preserve current sort order after filtering
        if self.current_sort_column:
            self._apply_current_sort()

        self.display_servers(self.filtered_servers)
        try:
            self.page.update()
        except:
            pass  # Page is closed, ignore

    def sort_table(self, column: str):
        """Sort the server table by the specified column."""
        if not self.filtered_servers or self.shutdown_event.is_set():
            return

        # Track the current sort column
        self.current_sort_column = column

        reverse = self.sort_reverse.get(column, False)
        self.sort_reverse[column] = not reverse

        self._apply_current_sort()
        self.display_servers(self.filtered_servers)
        try:
            self.page.update()
        except:
            pass  # Page is closed, ignore

    def _apply_current_sort(self):
        """Apply the current sort to filtered_servers."""
        if not self.current_sort_column or not self.filtered_servers:
            return

        column = self.current_sort_column
        reverse = self.sort_reverse.get(column, False)

        if column == "game_name":
            self.filtered_servers.sort(key=lambda x: x.game_name or "", reverse=reverse)
        elif column == "game_mode":
            self.filtered_servers.sort(key=lambda x: x.game_mode_name, reverse=reverse)
        elif column == "players":
            self.filtered_servers.sort(key=lambda x: x.players, reverse=not reverse)  # Default desc for players
        elif column == "password":
            self.filtered_servers.sort(key=lambda x: x.has_password, reverse=reverse)
        elif column == "version":
            self.filtered_servers.sort(key=lambda x: x.version or "", reverse=reverse)

    def copy_ip_address(self, _=None):
        """Copy selected server's IP to clipboard."""
        if self.selected_server and not self.shutdown_event.is_set():
            try:
                self.page.set_clipboard(self.selected_server.connection_string)
                self.show_snackbar("IP address copied to clipboard!")
            except:
                pass  # Page is closed, ignore

    def copy_game_info(self, _=None):
        """Copy selected server's game info to clipboard."""
        if self.selected_server and not self.shutdown_event.is_set():
            server = self.selected_server
            game_info = f"""Game Name: {server.game_name or 'Unknown'}
Game Mode: {server.game_mode_name}
Players: {server.players}/{server.max_players}
Version: {server.version or 'Unknown'}
Address: {server.connection_string}"""

            try:
                self.page.set_clipboard(game_info)
                self.show_snackbar("Game info copied to clipboard!")
            except:
                pass  # Page is closed, ignore

    def show_snackbar(self, message: str):
        """Show a temporary message to the user."""
        if self.shutdown_event.is_set():
            return

        try:
            snack_bar = ft.SnackBar(
                content=ft.Text(message),
                duration=2000
            )
            self.page.overlay.clear()  # Clear existing overlays first
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.page.update()
        except:
            pass  # Page is closed, ignore

    def toggle_auto_update(self, e):
        """Toggle auto-update functionality."""
        self.auto_update_enabled = e.control.value
        if self.auto_update_enabled and not self.shutdown_event.is_set():
            self.start_auto_fetch()

    def start_auto_fetch(self):
        """Start automatic server fetching."""
        if self.shutdown_event.is_set():
            return

        if self.auto_update_enabled:
            self.fetch_servers()
            # Cancel previous timer if it exists
            if self.auto_update_timer:
                self.auto_update_timer.cancel()

            # Schedule next fetch
            self.auto_update_timer = threading.Timer(self.fetch_interval, self.start_auto_fetch)
            self.auto_update_timer.daemon = True
            self.auto_update_timer.start()


def run_gui():
    """Main entry point for the Flet application."""

    def main(page: ft.Page):
        GameServersApp(page)

    ft.app(
        target=main,
        name="Superfighters Deluxe Server Browser"
    )


if __name__ == '__main__':
    run_gui()