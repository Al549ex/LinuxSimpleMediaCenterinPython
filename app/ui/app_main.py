#!/usr/bin/env python3
import subprocess  # Importante para lanzar mpv, openvpn, etc.
from textual.app import App, ComposeResult
from textual.widgets import Button, Header, Footer, Static
from textual.containers import VerticalScroll

"""
Este es un ejemplo básico de un Centro Multimedia usando Textual.
"""

class MediaCenterApp(App):
    """La aplicación principal de tu centro multimedia."""

    # CSS para dar un poco de estilo. 
    # 'auto' en width/height hace que se centre.
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
        """Define la interfaz de usuario (lo que se ve)."""
        yield Header("Mi Centro Multimedia (Pi 4)")
        
        # Un contenedor vertical para los botones
        with VerticalScroll(id="menu"):
            yield Static("¿Qué quieres hacer?")
            yield Button("📺 Ver IPTV", id="btn_iptv", variant="primary")
            yield Button("🎬 Ver Películas (USB)", id="btn_local")
            yield Button("🎵 Escuchar Radio (demo)", id="btn_radio")
            yield Button("🔌 Salir", id="btn_quit", variant="error")
            
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Se llama automáticamente cuando se pulsa un botón."""
        
        if event.button.id == "btn_iptv":
            # --- TU LÓGICA DE IPTV AQUÍ ---
            # 1. Conectar a VPN
            # 2. Listar .m3u
            # 3. Lanzar mpv
            # Por ahora, solo simulamos lanzando el vídeo principal
            # NOTA: Usamos subprocess.Popen para no bloquear la app
            # subprocess.Popen(["mpv", "ruta/a/tu/video.m3u8"])
            # (Recuerda que tu script en C ya hace esto, podrías llamarlo)
            subprocess.Popen(["/ruta/a/tu/programa_en_c"])
            
            # (Si quisieras lanzar los dos mpv desde Python)
            # subprocess.Popen(["mpv", "ruta/a/video.m3u8"])
            # subprocess.Popen(["mpv", "ruta/a/radio.m3u8"])


        elif event.button.id == "btn_local":
            # --- TU LÓGICA DE PELÍCULAS AQUÍ ---
            # 1. Montar USB si no lo está
            # 2. Buscar archivos .mkv, .mp4
            # 3. (En un futuro) Mostrar una lista de archivos
            # 4. Lanzar mpv (¡con la opción de guardar progreso!)
            
            # Ruta de ejemplo
            ruta_pelicula = "/Users/macdealex/Pictures/Router/" 
            
            # Lanzamos mpv. mpv guardará el progreso automáticamente
            # si tienes 'save-position-on-quit=yes' en tu mpv.conf
            subprocess.Popen(["mpv", ruta_pelicula])

        
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