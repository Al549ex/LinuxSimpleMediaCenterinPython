# app/ui/screens/m3u_list_screen.py

import os
from typing import List
from textual import log
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static
from textual.worker import Worker, WorkerState

# --- REFACTORIZACIÓN: Importamos el nuevo config ---
from app.core.config import config
from app.core.iptv import parse_m3u_file
from app.core.vpn import VPNStatus, connect_vpn
from app.ui.screens.iptv_list_screen import IptvListScreen

class M3uListScreen(Screen):
    """Una pantalla para mostrar la lista de archivos M3U disponibles."""

    def __init__(self, m3u_files: List[str], **kwargs):
        super().__init__(**kwargs)
        self.m3u_files = m3u_files
        self.file_map: dict[str, str] = {}

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, name="Seleccionar Lista M3U")
        with VerticalScroll(id="m3u-file-list"):
            if self.m3u_files:
                for i, file_name in enumerate(self.m3u_files):
                    display_name = os.path.splitext(file_name)[0]
                    button_id = f"m3u_button_{i}"
                    button = Button(display_name, id=button_id)
                    self.file_map[button_id] = file_name
                    yield button
            else:
                yield Static("No se encontraron archivos .m3u en la carpeta configurada.")
        
        yield Footer()
        yield Button("Volver", id="exit_m3u_list_button", variant="error")

    def _open_channel_list(self, file_name: str):
        """Parsea el archivo y abre la pantalla de la lista de canales."""
        iptv_folder = config.get("PATHS", "iptv_folder_path")
        if not iptv_folder:
            self.app.notify("Ruta de IPTV no configurada.", severity="error")
            return
            
        full_path = os.path.join(iptv_folder, file_name)
        channels = parse_m3u_file(full_path)
        
        if not channels:
            self.app.notify(f"El archivo '{file_name}' está vacío o no es válido.", severity="error")
            return
            
        self.app.push_screen(IptvListScreen(channels=channels))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Llamado cuando se presiona un botón."""
        
        if event.button.id == "exit_m3u_list_button":
            self.app.pop_screen()
            return

        button_id = event.button.id
        if button_id in self.file_map:
            file_name = self.file_map[button_id]
            
            use_vpn = config.get_boolean("VPN", "enabled_for_iptv", fallback=False)

            if not use_vpn:
                self._open_channel_list(file_name)
                return

            self.app.notify("🔌 Conectando a la VPN...")
            self.run_worker(
                lambda: (connect_vpn(), file_name),
                thread=True,
                name=f"vpn_connector_{button_id}" 
            )

    def on_worker_state_changed(self, event: WorkerState.Changed) -> None:
        """Escucha cuando un worker ha terminado."""
        if event.worker.name.startswith("vpn_connector_"):
            if event.state == WorkerState.SUCCESS:
                self.on_vpn_connection_finished(event.worker.result)
            else:
                log.error(f"El worker {event.worker.name} ha fallado.")
                self.app.notify("Error al conectar a la VPN.", severity="error")

    def on_vpn_connection_finished(self, result: tuple[VPNStatus, str]) -> None:
        """Se llama cuando la conexión VPN ha terminado."""
        vpn_status, file_name = result
        if vpn_status == VPNStatus.SUCCESS:
            self.app.notify("✅ VPN conectada. Abriendo canales...")
        else:
            self.app.notify("❌ Error al conectar a la VPN. Abriendo canales de todas formas...", severity="error")
        
        self._open_channel_list(file_name)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.app.dark = not self.app.dark