# app/ui/screens/now_playing_screen.py

import logging
import subprocess
from typing import Optional

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Button
from textual.containers import Center, Horizontal

from app.core.player import play_video

class NowPlayingScreen(Screen):
    """Pantalla optimizada de reproducción."""
    
    CSS_PATH = "now_playing_screen.css"

    def __init__(
        self,
        media_path: str,
        title: str,
        save_progress: bool,
        start_pos: float = 0.0,
        mute_video: bool = False,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.media_path = media_path
        self.media_title = title
        self.save_progress_flag = save_progress
        self.start_pos = start_pos
        self.mute_video = mute_video
        self.mpv_process: Optional[subprocess.Popen] = None
        self._is_stopping = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, name="Reproduciendo")
        with Center():
            yield Static(
                f"Reproduciendo ahora:\n\n{self.media_title}",
                classes="title"
            )
        
        # Controles de radio (ocultos por defecto)
        with Horizontal(id="radio-controls", classes="radio-controls-hidden"):
            yield Button("⏯️ Pausar/Reanudar Radio", id="toggle_radio_pause")
            yield Button("⏹️ Detener Radio", id="stop_radio", variant="warning")

        yield Footer()
        yield Button("⏹️ Detener Reproducción", id="stop_button", variant="error")

    def on_mount(self) -> None:
        """Inicializa la reproducción."""
        # Mostrar controles de radio si está activa
        radio_controls = self.query_one("#radio-controls")
        if self.app.is_radio_playing():
            radio_controls.remove_class("radio-controls-hidden")
        
        # Iniciar reproducción en worker
        self.run_worker(self.run_playback, thread=True, exclusive=True)

    def run_playback(self):
        """Worker que gestiona la reproducción."""
        try:
            self.mpv_process = play_video(
                file_path=self.media_path,
                start_position=self.start_pos,
                save_progress_flag=self.save_progress_flag,
                mute_video=self.mute_video
            )

            if self.mpv_process:
                # Esperar a que termine el proceso
                self.mpv_process.wait()
            
            # Al terminar, detener radio si está activa
            if not self._is_stopping and self.app.is_radio_playing():
                self.app.call_from_thread(self.app.stop_radio)
        
        except Exception as e:
            logging.error(f"Error en reproducción: {e}")
        
        finally:
            # Volver a la pantalla anterior
            if not self._is_stopping:
                self.app.call_from_thread(self.app.pop_screen)

    def _stop_playback(self):
        """Detiene la reproducción de forma segura."""
        self._is_stopping = True
        
        if self.mpv_process and self.mpv_process.poll() is None:
            try:
                self.mpv_process.terminate()
                self.mpv_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.mpv_process.kill()
            except Exception as e:
                logging.error(f"Error al detener reproducción: {e}")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Maneja botones de la pantalla."""
        if event.button.id == "stop_button":
            if self.app.is_radio_playing():
                self.app.stop_radio()
            self._stop_playback()
            self.app.pop_screen()

        elif event.button.id == "toggle_radio_pause":
            self.app.toggle_radio_pause()
            
        elif event.button.id == "stop_radio":
            self.app.stop_radio()
            self.query_one("#radio-controls").add_class("radio-controls-hidden")