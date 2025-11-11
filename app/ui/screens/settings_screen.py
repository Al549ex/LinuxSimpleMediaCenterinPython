# app/ui/screens/settings_screen.py

import os
import logging
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Switch, Static

from app.core.config import config

class SettingsScreen(Screen):
    """Pantalla de configuración optimizada con validación."""

    CSS = """
    #settings-container {
        height: 1fr;
    }
    
    #settings-form {
        padding: 1;
        width: 80%;
        height: auto;
        align: center top;
    }
    
    Label {
        margin-top: 1;
        color: $accent;
    }
    
    Input {
        margin-bottom: 1;
    }
    
    #button-row {
        dock: bottom;
        height: auto;
        width: 100%;
        padding: 0 1;
        align: left middle;
        background: $panel;
    }

    #button-row > Static {
        width: 1fr;
    }
    
    #button-row > Button {
        width: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, name="Configuración")
        
        with ScrollableContainer(id="settings-container"):
            with Vertical(id="settings-form"):
                yield Label("Ruta multimedia local:")
                yield Input(
                    config.get("PATHS", "local_media_path", fallback="./Peliculas/"),
                    id="local_media_path",
                    placeholder="./Peliculas/"
                )

                yield Label("Ruta de archivos M3U:")
                yield Input(
                    config.get("PATHS", "iptv_folder_path", fallback="./Archivos M3U/"),
                    id="iptv_folder_path",
                    placeholder="./Archivos M3U/"
                )

                yield Label("URL de origen para IPTV:")
                yield Input(
                    config.get("IPTV", "source_url", fallback=""),
                    id="source_url",
                    placeholder="https://ejemplo.com/lista.m3u"
                )
                
                yield Label("País para la VPN:")
                yield Input(
                    config.get("VPN", "country", fallback="Spain"),
                    id="vpn_country",
                    placeholder="Spain"
                )

                yield Label("Usuario de la VPN:")
                yield Input(
                    config.get("VPN", "username", fallback=""),
                    id="vpn_username",
                    placeholder="Usuario"
                )

                yield Label("Contraseña de la VPN:")
                yield Input(
                    config.get("VPN", "password", fallback=""),
                    id="vpn_password",
                    placeholder="Contraseña",
                    password=True
                )

                yield Label("Usar VPN para IPTV:")
                yield Switch(
                    value=config.get_boolean("VPN", "enabled_for_iptv", fallback=False),
                    id="vpn_for_iptv"
                )

                yield Label("API Key de TMDB (opcional):")
                yield Input(
                    config.get("TMDB", "api_key", fallback=""),
                    id="tmdb_api_key",
                    placeholder="Obtén tu clave en themoviedb.org",
                    password=True
                )
        
        with Horizontal(id="button-row"):
            yield Button("Volver", variant="error", id="exit_settings")
            yield Static()  # Espaciador flexible
            yield Button("Guardar", variant="primary", id="save_settings")
        
        yield Footer()

    def _validate_path(self, path: str) -> bool:
        """Valida que una ruta sea accesible o pueda ser creada."""
        if not path:
            return False
        
        if os.path.exists(path):
            return os.path.isdir(path)
        
        parent = os.path.dirname(path) or '.'
        return os.path.isdir(parent)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_settings":
            # Obtener valores
            local_path = self.query_one("#local_media_path", Input).value.strip()
            iptv_path = self.query_one("#iptv_folder_path", Input).value.strip()
            source_url = self.query_one("#source_url", Input).value.strip()
            vpn_country = self.query_one("#vpn_country", Input).value.strip()
            vpn_username = self.query_one("#vpn_username", Input).value.strip()
            vpn_password = self.query_one("#vpn_password", Input).value
            vpn_enabled = self.query_one("#vpn_for_iptv", Switch).value
            tmdb_api_key = self.query_one("#tmdb_api_key", Input).value.strip()

            # Validar rutas
            if not self._validate_path(local_path):
                self.app.notify("⚠️ La ruta multimedia local no es válida.", severity="warning", timeout=5)
                return

            if not self._validate_path(iptv_path):
                self.app.notify("⚠️ La ruta de archivos M3U no es válida.", severity="warning", timeout=5)
                return

            # Guardar configuración
            config.set("PATHS", "local_media_path", local_path)
            config.set("PATHS", "iptv_folder_path", iptv_path)
            config.set("IPTV", "source_url", source_url)
            config.set("VPN", "country", vpn_country)
            config.set("VPN", "username", vpn_username)
            config.set("VPN", "password", vpn_password)
            config.set("VPN", "enabled_for_iptv", "yes" if vpn_enabled else "no")
            config.set("TMDB", "api_key", tmdb_api_key)

            if config.save():
                for path in [local_path, iptv_path]:
                    if path and not os.path.exists(path):
                        try:
                            os.makedirs(path, exist_ok=True)
                            logging.info(f"Directorio creado: {path}")
                        except OSError as e:
                            logging.error(f"Error al crear directorio {path}: {e}")
                
                self.app.notify("✅ Configuración guardada correctamente.")
                self.app.pop_screen()
            else:
                self.app.notify("❌ Error al guardar la configuración.", severity="error")

        elif event.button.id == "exit_settings":
            self.app.pop_screen()
