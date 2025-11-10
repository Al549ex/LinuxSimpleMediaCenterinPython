#!/usr/bin/env python3
import subprocess  # Important for launching mpv, openvpn, etc.
from textual.app import App, ComposeResult
from textual.widgets import Button, Header, Footer, Static
from textual.containers import VerticalScroll

"""
This is a basic example of a Media Center using Textual.
"""

class MediaCenterApp(App):
    """The main media center application."""

    # CSS for styling. 
    # 'auto' in width/height centers it.
    CSS = """
    Screen {
        layout: vertical;
        align: center middle;
    }
    
    #menu {
        width: 60%;
        height: auto;
        border: solid $accent;
        padding: 2;
    }

    Button {
        width: 100%;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Defines the user interface (what you see)."""
        yield Header("My Media Center (Pi 4)")
        
        # A vertical container for the buttons
        with VerticalScroll(id="menu"):
            yield Static("What would you like to do?")
            yield Button("📺 Watch IPTV", id="btn_iptv", variant="primary")
            yield Button("🎬 Watch Movies (USB)", id="btn_local")
            yield Button("🎵 Listen to Radio (demo)", id="btn_radio")
            yield Button("🔌 Exit", id="btn_quit", variant="error")
            
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Called automatically when a button is pressed."""
        
        if event.button.id == "btn_iptv":
            # --- YOUR IPTV LOGIC HERE ---
            # 1. Connect to VPN
            # 2. List .m3u files
            # 3. Launch mpv
            # For now, we just simulate launching the main video
            # NOTE: We use subprocess.Popen to not block the app
            # subprocess.Popen(["mpv", "path/to/your/video.m3u8"])
            # (Remember that your C script already does this, you could call it)
            subprocess.Popen(["/path/to/your/c_program"])
            
            # (If you wanted to launch both mpv instances from Python)
            # subprocess.Popen(["mpv", "path/to/video.m3u8"])
            # subprocess.Popen(["mpv", "path/to/radio.m3u8"])


        elif event.button.id == "btn_local":
            # --- YOUR MOVIE LOGIC HERE ---
            # 1. Mount USB if not mounted
            # 2. Search for .mkv, .mp4 files
            # 3. (In the future) Show a list of files
            # 4. Launch mpv (with save progress option!)
            
            # Example path
            movie_path = "/Users/macdealex/Pictures/Router/" 
            
            # Launch mpv. mpv will save progress automatically
            # if you have 'save-position-on-quit=yes' in your mpv.conf
            subprocess.Popen(["mpv", movie_path])

        
        elif event.button.id == "btn_radio":
            # Ejemplo de cómo lanzar solo la radio
            subprocess.Popen(["mpv", "ruta/a/radio.m3u8"])


        elif event.button.id == "btn_quit":
            # Cierra la aplicación de Python
            self.exit()

# --- Esta es la parte que ejecuta la aplicación ---
if __name__ == "__main__":
    app = MediaCenterApp()
    app.run()