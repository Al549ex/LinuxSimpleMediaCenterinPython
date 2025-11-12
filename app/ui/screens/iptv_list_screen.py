# app/ui/screens/iptv_list_screen.py

import logging
from typing import List, Dict, Optional

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Static
from textual.containers import VerticalScroll

from app.core.vpn import disconnect_vpn, VPNStatus
from app.ui.screens.now_playing_screen import NowPlayingScreen
from app.ui.screens.confirm_screen import ConfirmScreen
from app.ui.screens.radio_selector_screen import RadioSelectorScreen


class IptvListScreen(Screen):
    """Pantalla optimizada para mostrar canales IPTV."""

    CSS = """
    #iptv-channel-list {
        height: 1fr;
    }
    
    #iptv-channel-list Button {
        width: 100%;
        margin: 1;
    }
    """

    def __init__(self, channels: List, **kwargs):
        super().__init__(**kwargs)
        # Optimización: usar diccionario en lugar de list comprehension
        self.channel_map: Dict[str, str] = {}
        self.channel_names: Dict[str, str] = {}
        
        for i, channel in enumerate(channels):
            button_id = f"channel_{i}"
            self.channel_map[button_id] = channel.url
            self.channel_names[button_id] = channel.name
        
        self.selected_channel_url: Optional[str] = None
        self.selected_channel_name: Optional[str] = None
        self.channels = channels

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, name="Canales IPTV")
        
        with VerticalScroll(id="iptv-channel-list"):
            if self.channel_map:
                for button_id, name in self.channel_names.items():
                    yield Button(name, id=button_id)
            else:
                yield Static("No se encontraron canales en el archivo.")
        
        yield Footer()
        yield Button("Volver al Menú", id="exit_iptv_button", variant="error")

    def play_iptv_channel(self, radio_url: Optional[str] = None) -> None:
        """Inicia la reproducción del canal IPTV."""
        if not self.selected_channel_url or not self.selected_channel_name:
            logging.error("play_iptv_channel llamado sin canal seleccionado.")
            return

        # Iniciar radio si se proporcionó
        if radio_url:
            logging.info(f"Iniciando radio: {radio_url}")
            self.app.start_radio(radio_url)

        # Reproducir canal
        logging.info(f"Reproduciendo canal: {self.selected_channel_name}")
        self.app.push_screen(
            NowPlayingScreen(
                media_path=self.selected_channel_url,
                title=self.selected_channel_name,
                save_progress=False,
                mute_video=(radio_url is not None)
            )
        )

    def handle_radio_selection(self, radio_url: Optional[str]) -> None:
        """Callback tras seleccionar radio."""
        self.play_iptv_channel(radio_url=radio_url)

    def handle_radio_confirmation(self, confirmed: bool) -> None:
        """Callback tras confirmar si quiere radio."""
        if confirmed:
            self.app.push_screen(RadioSelectorScreen(), self.handle_radio_selection)
        else:
            self.play_iptv_channel()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Maneja la pulsación de botones."""
        if event.button.id == "exit_iptv_button":
            self.app.notify("🔌 Desconectando VPN...")
            self.run_worker(self.do_disconnect, thread=True)
            return

        # Verificar si es un botón de canal
        if event.button.id in self.channel_map:
            self.selected_channel_url = self.channel_map[event.button.id]
            self.selected_channel_name = self.channel_names[event.button.id]

            # Si la radio ya está activa, reproducir directamente
            if self.app.is_radio_playing():
                self.play_iptv_channel()
            else:
                self.app.push_screen(
                    ConfirmScreen("¿Reproducir radio en segundo plano?"),
                    self.handle_radio_confirmation
                )

    def do_disconnect(self):
        """Worker de desconexión VPN."""
        vpn_result = disconnect_vpn()
        self.app.call_from_thread(self.on_disconnect_finished, vpn_result)

    def on_disconnect_finished(self, vpn_result: VPNStatus) -> None:
        """Finaliza la desconexión y vuelve al menú."""
        if vpn_result == VPNStatus.SKIPPED:
            self.app.notify("⚠️ Desconexión VPN omitida.", timeout=3)
        elif vpn_result == VPNStatus.SUCCESS:
            self.app.notify("✅ VPN desconectada.")
        else:
            self.app.notify("⚠️ VPN no estaba conectada.", severity="warning")
        
        # Volver al menú principal de forma segura
        try:
            num_screens = len(self.app.screen_stack) - 1
            for _ in range(num_screens):
                self.app.pop_screen()
        except Exception as e:
            logging.error(f"Error al volver al menú: {e}")
