# app/ui/screens/movie_list_screen.py

import logging
import os
from pathlib import Path
from typing import List, Dict, Optional

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Static
from textual.containers import VerticalScroll

from app.core.progress import get_progress, clear_progress
from app.ui.screens.confirm_screen import ConfirmScreen
from app.ui.screens.now_playing_screen import NowPlayingScreen

class MovieListScreen(Screen):
    """Pantalla optimizada para mostrar películas locales."""

    CSS = """
    #movie-list {
        height: 1fr;
    }
    
    #movie-list Button {
        width: 100%;
        margin: 1;
    }
    
    .has-progress {
        background: $accent-darken-1;
    }
    """

    def __init__(self, movies: List[str], **kwargs):
        super().__init__(**kwargs)
        # Optimización: precalcular nombres y verificar existencia
        self.file_map: Dict[str, str] = {}
        self.file_progress: Dict[str, Optional[float]] = {}
        
        for i, path in enumerate(movies):
            if os.path.exists(path):
                file_id = f"movie_{i}"
                self.file_map[file_id] = path
                # Precalcular progreso para indicadores visuales
                self.file_progress[file_id] = get_progress(path)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, name="Películas Locales")
        
        with VerticalScroll(id="movie-list"):
            if self.file_map:
                for file_id, path in self.file_map.items():
                    file_name = Path(path).name
                    progress = self.file_progress.get(file_id)
                    
                    # Indicador visual si tiene progreso
                    label = file_name
                    if progress and progress > 10:
                        time_str = self._format_time(progress)
                        label = f"{file_name} [{time_str}]"
                    
                    button = Button(
                        label,
                        id=file_id,
                        classes="has-progress" if progress else ""
                    )
                    yield button
            else:
                yield Static("No se encontraron películas.")
        
        yield Footer()
        yield Button("Volver", id="exit_movie_button", variant="error")

    def _format_time(self, seconds: float) -> str:
        """Formatea segundos a HH:MM:SS."""
        secs = int(seconds)
        hours, rem = divmod(secs, 3600)
        mins, secs = divmod(rem, 60)
        
        if hours > 0:
            return f"{hours:02d}:{mins:02d}:{secs:02d}"
        return f"{mins:02d}:{secs:02d}"

    def _play_movie(self, file_path: str, start_position: float = 0.0):
        """Inicia la reproducción de una película."""
        title = Path(file_path).name
        self.app.push_screen(
            NowPlayingScreen(
                media_path=file_path,
                title=title,
                save_progress=True,
                start_pos=start_position
            )
        )

    def _handle_resume_choice(self, resume: bool, file_path: str, progress: float):
        """Callback tras decidir si reanudar."""
        if resume:
            self._play_movie(file_path, start_position=progress)
        else:
            clear_progress(file_path)
            self._play_movie(file_path)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Gestiona pulsación de botones."""
        if event.button.id == "exit_movie_button":
            self.app.pop_screen()
            return

        file_path = self.file_map.get(event.button.id)
        if not file_path:
            return

        progress = self.file_progress.get(event.button.id)
        
        if progress and progress > 10:
            time_str = self._format_time(progress)
            
            self.app.push_screen(
                ConfirmScreen(
                    f"¿Reanudar desde {time_str}?\n\n"
                    "Sí = Reanudar | No = Desde el inicio"
                ),
                lambda resume: self._handle_resume_choice(resume, file_path, progress)
            )
        else:
            self._play_movie(file_path)
