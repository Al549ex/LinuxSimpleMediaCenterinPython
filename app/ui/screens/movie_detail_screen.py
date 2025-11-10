# app/ui/screens/movie_detail_screen.py

import logging
from typing import Dict, Optional
from pathlib import Path

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Static
from textual.containers import Vertical, Horizontal, ScrollableContainer

from app.core.progress import get_progress, clear_progress
from app.ui.screens.now_playing_screen import NowPlayingScreen

class MovieDetailScreen(Screen):
    """Pantalla con los detalles de una película."""

    CSS = """
    #movie-detail-container {
        width: 90%;
        height: auto;
        margin: 1 auto;
    }
    
    #movie-header {
        height: auto;
        margin-bottom: 1;
    }
    
    .movie-title {
        text-style: bold;
        color: $accent;
        content-align: center middle;
        margin: 1;
    }
    
    .movie-info {
        color: $text-muted;
        content-align: center middle;
    }
    
    .section-title {
        text-style: bold;
        color: $primary;
        margin-top: 1;
    }
    
    .movie-overview {
        margin: 1;
        color: $text;
    }
    
    #button-row {
        height: auto;
        margin-top: 2;
    }
    
    #button-row Button {
        margin: 0 1;
    }
    
    .progress-info {
        color: $warning;
        text-style: italic;
        margin: 1;
    }
    """

    def __init__(
        self,
        file_path: str,
        movie_info: Optional[Dict] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.file_path = file_path
        self.movie_info = movie_info or {}
        self.progress = get_progress(file_path)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, name="Detalles de la Película")
        
        with ScrollableContainer(id="movie-detail-container"):
            with Vertical(id="movie-header"):
                # Título
                title = self.movie_info.get('title', Path(self.file_path).stem)
                yield Static(title, classes="movie-title")
                
                # Información básica
                info_parts = []
                if self.movie_info.get('release_date'):
                    year = self.movie_info['release_date'][:4]
                    info_parts.append(year)
                
                if self.movie_info.get('runtime'):
                    runtime = self.movie_info['runtime']
                    hours = runtime // 60
                    mins = runtime % 60
                    info_parts.append(f"{hours}h {mins}min")
                
                if self.movie_info.get('vote_average'):
                    rating = self.movie_info['vote_average']
                    info_parts.append(f"⭐ {rating:.1f}/10")
                
                if info_parts:
                    yield Static(" • ".join(info_parts), classes="movie-info")
                
                # Géneros
                if self.movie_info.get('genres'):
                    genres = ", ".join(self.movie_info['genres'])
                    yield Static(f"🎬 {genres}", classes="movie-info")
                
                # Director
                if self.movie_info.get('director'):
                    yield Static(
                        f"🎥 Director: {self.movie_info['director']}",
                        classes="movie-info"
                    )
            
            # Sinopsis
            if self.movie_info.get('overview'):
                yield Static("Sinopsis:", classes="section-title")
                yield Static(self.movie_info['overview'], classes="movie-overview")
            
            # Reparto
            if self.movie_info.get('cast'):
                yield Static("Reparto:", classes="section-title")
                cast_text = ", ".join(self.movie_info['cast'])
                yield Static(cast_text, classes="movie-overview")
            
            # Información de progreso
            if self.progress and self.progress > 10:
                time_str = self._format_time(self.progress)
                yield Static(
                    f"⏱️ Tienes esta película vista hasta: {time_str}",
                    classes="progress-info"
                )
        
        yield Footer()
        
        # Botones
        with Horizontal(id="button-row"):
            if self.progress and self.progress > 10:
                yield Button("▶️ Reanudar", id="resume_movie", variant="primary")
                yield Button("🔄 Desde el inicio", id="restart_movie", variant="success")
            else:
                yield Button("▶️ Reproducir", id="play_movie", variant="primary")
            
            yield Button("⬅️ Volver", id="back_button", variant="error")

    def _format_time(self, seconds: float) -> str:
        """Formatea segundos a HH:MM:SS."""
        secs = int(seconds)
        hours, rem = divmod(secs, 3600)
        mins, secs = divmod(rem, 60)
        
        if hours > 0:
            return f"{hours:02d}:{mins:02d}:{secs:02d}"
        return f"{mins:02d}:{secs:02d}"

    def _play_movie(self, start_position: float = 0.0):
        """Inicia la reproducción."""
        title = self.movie_info.get('title', Path(self.file_path).stem)
        self.app.push_screen(
            NowPlayingScreen(
                media_path=self.file_path,
                title=title,
                save_progress=True,
                start_pos=start_position
            )
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Gestiona los botones."""
        if event.button.id == "play_movie":
            self._play_movie()
        
        elif event.button.id == "resume_movie":
            self._play_movie(start_position=self.progress)
        
        elif event.button.id == "restart_movie":
            clear_progress(self.file_path)
            self._play_movie()
        
        elif event.button.id == "back_button":
            self.app.pop_screen()
