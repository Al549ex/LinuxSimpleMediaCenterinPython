#!/usr/bin/env python3
# run.py - Archivo principal optimizado

import logging
import subprocess
import os
import socket
import json
import time
from textual.app import App, ComposeResult
from textual.widgets import Button, Header, Footer, Static
from textual.containers import Vertical

# Importaciones optimizadas
from app.core.config import config
from app.core.iptv_refresher import refresh_channels
from app.core.vpn import connect_vpn, disconnect_vpn, VPNStatus
from app.core.local_media import get_local_movie_list
from app.core.iptv import get_m3u_files

from app.ui.screens.movie_list_screen import MovieListScreen
from app.ui.screens.m3u_list_screen import M3uListScreen
from app.ui.screens.settings_screen import SettingsScreen
from app.ui.screens.radio_manager_screen import RadioManagerScreen

# Configuración del logging
logging.basicConfig(
    filename='app.log',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MediaCenterApp(App):
    """Media Center optimizado para Raspberry Pi 4."""

    TITLE = "RaspIPTV Media Center"
    
    CSS = """
    Screen {
        align: center middle;
    }
    #main-menu {
        width: 50%;
        height: auto;
        align: center middle;
    }
    Button {
        width: 100%;
        margin: 1;
    }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.radio_process: subprocess.Popen | None = None
        self.is_radio_paused: bool = False
        self.radio_socket_path = f"/tmp/raspiptv_mpv_{os.getpid()}.sock"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="main-menu"):
            yield Static("Bienvenido al Media Center", classes="title")
            yield Button("Ver Películas (Local)", id="btn_local_media", variant="primary")
            yield Button("IPTV", id="btn_iptv", variant="success")
            yield Button("Actualizar Canales IPTV", id="btn_refresh_iptv", variant="warning")
            yield Button("Gestionar Radios", id="btn_manage_radio")
            yield Button("Configuración", id="btn_settings")
        yield Footer()

    # --- Gestión de Radio ---
    
    def is_radio_playing(self) -> bool:
        """Comprueba si la radio está activa."""
        return self.radio_process is not None and self.radio_process.poll() is None

    def start_radio(self, url: str):
        """Inicia la reproducción de radio en segundo plano."""
        if self.is_radio_playing():
            self.run_worker(self._stop_radio_worker, thread=True, exclusive=True, group="radio_control")

        logging.info(f"Iniciando radio: {url}")
        try:
            command = [
                "mpv",
                "--no-video",
                "--force-window=no",
                f"--input-ipc-server={self.radio_socket_path}",
                url
            ]
            self.radio_process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.is_radio_paused = False
            time.sleep(0.5)
            self.notify("📻 Radio iniciada.")
        except Exception as e:
            logging.error(f"Error al iniciar radio: {e}")
            self.notify("❌ Error al iniciar radio.", severity="error")

    def _stop_radio_worker(self):
        """Worker que detiene la radio."""
        if self.radio_process and self.radio_process.poll() is None:
            process_to_stop = self.radio_process
            socket_to_clean = self.radio_socket_path

            self.call_from_thread(setattr, self, "radio_process", None)
            self.call_from_thread(setattr, self, "is_radio_paused", False)

            process_to_stop.terminate()
            process_to_stop.wait()

            if os.path.exists(socket_to_clean):
                try:
                    os.remove(socket_to_clean)
                except OSError as e:
                    logging.error(f"Error al eliminar socket: {e}")

            self.call_from_thread(self.notify, "📻 Radio detenida.")

    def stop_radio(self):
        """Detiene la radio."""
        self.run_worker(self._stop_radio_worker, thread=True, exclusive=True, group="radio_control")

    def _send_mpv_command(self, command: dict):
        """Envía un comando al socket de mpv."""
        if not self.radio_process or not os.path.exists(self.radio_socket_path):
            return
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.settimeout(1.0)
                s.connect(self.radio_socket_path)
                s.sendall(json.dumps(command).encode('utf-8') + b'\n')
        except Exception as e:
            logging.error(f"Error al enviar comando a mpv: {e}")

    def toggle_radio_pause(self):
        """Pausa/reanuda la radio."""
        if not self.radio_process:
            return

        self.is_radio_paused = not self.is_radio_paused
        command = {"command": ["set_property", "pause", self.is_radio_paused]}
        self._send_mpv_command(command)
        self.notify("⏸️ Radio pausada." if self.is_radio_paused else "▶️ Radio reanudada.")

    # --- Worker para actualizar canales ---
    
    def _run_channel_refresh(self):
        """Worker que actualiza los canales IPTV."""
        self.call_from_thread(self.notify, "🔌 Conectando a la VPN...")
        vpn_status = connect_vpn()

        if vpn_status == VPNStatus.FAILED:
            self.call_from_thread(self.notify, "❌ Error al conectar VPN. Abortando.", severity="error")
            return
        elif vpn_status == VPNStatus.SKIPPED:
            self.call_from_thread(self.notify, "⚠️ Conexión VPN omitida.", severity="warning")
        else:
            self.call_from_thread(self.notify, "✅ VPN conectada.")

        self.call_from_thread(self.notify, "🔄 Descargando canales...")
        
        source_url = config.get("IPTV", "source_url")
        output_dir = config.get("PATHS", "iptv_folder_path")

        try:
            num_groups, num_channels = refresh_channels(source_url, output_dir)
            self.call_from_thread(
                self.notify,
                f"✅ ¡Completado! {num_channels} canales en {num_groups} grupos.",
                timeout=10
            )
        except Exception as e:
            logging.error(f"Error en actualización: {e}")
            self.call_from_thread(
                self.notify,
                f"❌ Error: {e}",
                severity="error",
                timeout=15
            )
        finally:
            if vpn_status == VPNStatus.SUCCESS:
                self.call_from_thread(self.notify, "🔌 Desconectando VPN...")
                disconnect_vpn()
                self.call_from_thread(self.notify, "✅ VPN desconectada.")

    # --- Botones del menú ---
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Maneja los botones del menú principal."""
        if event.button.id == "btn_local_media":
            media_path = config.get('PATHS', 'local_media_path')
            if media_path and os.path.isdir(media_path):
                movies = get_local_movie_list(media_path)
                self.push_screen(MovieListScreen(movies=movies))
            else:
                self.notify("Ruta local no configurada o no válida.", severity="error")

        elif event.button.id == "btn_iptv":
            m3u_path = config.get('PATHS', 'iptv_folder_path')
            if m3u_path and os.path.isdir(m3u_path):
                m3u_files = get_m3u_files()
                self.push_screen(M3uListScreen(m3u_files=m3u_files))
            else:
                self.notify("Ruta M3U no configurada o no válida.", severity="error")

        elif event.button.id == "btn_refresh_iptv":
            source_url = config.get("IPTV", "source_url")
            output_dir = config.get("PATHS", "iptv_folder_path")
            
            if not source_url or not output_dir:
                self.notify(
                    "URL de origen o carpeta no configuradas.",
                    severity="error",
                    timeout=8
                )
                return
            
            self.run_worker(self._run_channel_refresh, thread=True, exclusive=True)

        elif event.button.id == "btn_settings":
            self.push_screen(SettingsScreen())
            
        elif event.button.id == "btn_manage_radio":
            self.push_screen(RadioManagerScreen())

if __name__ == "__main__":
    app = MediaCenterApp()
    app.run()