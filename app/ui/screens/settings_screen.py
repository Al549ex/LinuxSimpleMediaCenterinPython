# app/ui/screens/settings_screen.py

import os
import logging
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Switch, Static

from app.core.config import config
from app.core.vpn import check_login_status, login_vpn

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
    
    #vpn_note {
        color: $text-muted;
        text-style: italic;
        margin: 1 0;
    }
    
    #vpn_status {
        color: $success;
        margin: 1 0;
    }
    
    #vpn_url_container {
        border: solid $accent;
        padding: 1;
        margin: 1 0;
        height: auto;
        display: none;
    }
    
    #vpn_url_container.visible {
        display: block;
    }
    
        #vpn_url_container #url_text {
        width: 100%;
        color: $text;
        text-style: bold;
    }
    
    #vpn_login_button {
        width: 100%;
        margin: 1 0;
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
                
                yield Label("País para la VPN (opcional):")
                yield Input(
                    config.get("VPN", "country", fallback="Spain"),
                    id="vpn_country",
                    placeholder="Spain, United_States, etc. (vacío = automático)"
                )

                # Botón de login y estado
                yield Button(
                    "🔐 Autenticar NordVPN",
                    id="vpn_login_button",
                    variant="primary"
                )
                
                yield Static("Verificando estado...", id="vpn_status")
                
                # Contenedor para mostrar la URL
                with Vertical(id="vpn_url_container"):
                    yield Label("🔗 URL de Autenticación:")
                    yield Static("", id="vpn_url_text")
                    yield Static(
                        "📋 Copia esta URL y ábrela en tu navegador",
                        id="vpn_url_hint"
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

    def on_mount(self) -> None:
        """Carga el estado de autenticación de VPN al montar."""
        self._update_vpn_status()
        # Ocultar el contenedor de URL al inicio
        self._hide_url_container()
    
    def _hide_url_container(self):
        """Oculta el contenedor de URL."""
        try:
            url_container = self.query_one("#vpn_url_container")
            url_container.remove_class("visible")
        except:
            pass
    
    def _show_url_container(self, url: str):
        """Muestra el contenedor de URL con la URL proporcionada."""
        try:
            url_container = self.query_one("#vpn_url_container")
            url_text = self.query_one("#vpn_url_text", Static)
            
            url_text.update(url)
            url_container.add_class("visible")
            
            # Hacer scroll hasta el contenedor
            url_container.scroll_visible()
        except Exception as e:
            import logging
            logging.error(f"Error mostrando URL: {e}")
    
    def _update_vpn_status(self):
        """Actualiza el texto del estado de VPN."""
        is_logged_in, message = check_login_status()
        
        status_widget = self.query_one("#vpn_status", Static)
        
        if is_logged_in:
            status_widget.update(f"✅ Estado: {message}")
            status_widget.styles.color = "green"
        else:
            status_widget.update(f"❌ Estado: {message}")
            status_widget.styles.color = "orange"
    
    def _handle_vpn_login(self):
        """Maneja el proceso de login de VPN en un worker."""
        self.app.notify("Iniciando autenticación de NordVPN...")
        
        # Ocultar URL anterior si existe
        self._hide_url_container()
        
        # Actualizar el estado
        status_widget = self.query_one("#vpn_status", Static)
        status_widget.update("🔄 Autenticando...")
        status_widget.styles.color = "yellow"
        
        # Ejecutar login en un worker
        self.run_worker(
            self._vpn_login_worker,
            thread=True,
            name="vpn_login_worker"
        )
    
    def _vpn_login_worker(self):
        """Worker que ejecuta el login de VPN."""
        return login_vpn()
    
    def on_worker_state_changed(self, event) -> None:
        """Maneja el resultado del worker de login."""
        from textual.worker import WorkerState
        
        if event.worker.name == "vpn_login_worker":
            if event.state == WorkerState.SUCCESS:
                success, message = event.worker.result
                
                if success:
                    if "https://" in message:
                        # Es una URL de autenticación - MOSTRAR EN PANTALLA
                        self._show_url_container(message)
                        
                        # También mostrar notificación breve
                        self.app.notify(
                            "✅ URL mostrada abajo. Ábrela en tu navegador",
                            timeout=10,
                            severity="information"
                        )
                        
                        # También en log para debugging
                        import logging
                        logging.info(f"URL DE AUTENTICACIÓN: {message}")
                        
                        # Copiar al portapapeles si es posible
                        try:
                            import subprocess
                            import platform
                            
                            if platform.system() == "Darwin":  # macOS
                                subprocess.run(
                                    ["pbcopy"],
                                    input=message.encode(),
                                    check=True
                                )
                                self.app.notify("📋 URL copiada al portapapeles (Cmd+V para pegar)", timeout=10)
                            elif platform.system() == "Linux":
                                # Intentar con xclip o xsel
                                try:
                                    subprocess.run(
                                        ["xclip", "-selection", "clipboard"],
                                        input=message.encode(),
                                        check=True
                                    )
                                    self.app.notify("📋 URL copiada al portapapeles", timeout=5)
                                except FileNotFoundError:
                                    try:
                                        subprocess.run(
                                            ["xsel", "--clipboard"],
                                            input=message.encode(),
                                            check=True
                                        )
                                        self.app.notify("📋 URL copiada al portapapeles", timeout=5)
                                    except FileNotFoundError:
                                        pass  # No hay xclip ni xsel disponibles
                        except Exception as e:
                            import logging
                            logging.warning(f"No se pudo copiar al portapapeles: {e}")
                        
                        # Actualizar estado
                        status_widget = self.query_one("#vpn_status", Static)
                        status_widget.update(f"🔗 Completa la autenticación en el navegador")
                        status_widget.styles.color = "yellow"
                    else:
                        # Mensaje informativo (ya autenticado, etc.)
                        self.app.notify(f"✅ {message}", timeout=10)
                        self._update_vpn_status()
                else:
                    # Error - mostrar mensaje completo
                    self.app.notify(f"❌ Error:\n{message}", severity="error", timeout=20)
                    
                    # También en log
                    import logging
                    logging.error(f"Error en login VPN: {message}")
                    
                    self._update_vpn_status()
            elif event.state == WorkerState.ERROR:
                self.app.notify("❌ Error durante la autenticación", severity="error")
                self._update_vpn_status()

    def _validate_path(self, path: str) -> bool:
        """Valida que una ruta sea accesible o pueda ser creada."""
        if not path:
            return False
        
        if os.path.exists(path):
            return os.path.isdir(path)
        
        parent = os.path.dirname(path) or '.'
        return os.path.isdir(parent)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "vpn_login_button":
            self._handle_vpn_login()
            return
        
        if event.button.id == "save_settings":
            # Obtener valores
            local_path = self.query_one("#local_media_path", Input).value.strip()
            iptv_path = self.query_one("#iptv_folder_path", Input).value.strip()
            source_url = self.query_one("#source_url", Input).value.strip()
            vpn_country = self.query_one("#vpn_country", Input).value.strip()
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
