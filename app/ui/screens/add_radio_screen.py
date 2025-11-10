# app/ui/screens/add_radio_screen.py

from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.containers import Grid
from textual.widgets import Button, Input, Label
from typing import Dict, Optional

class AddRadioScreen(ModalScreen[Optional[Dict[str, str]]]):
    """Pantalla modal para añadir una nueva emisora de radio."""

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Nombre de la Radio:"),
            Input(placeholder="Ej: Rock FM", id="radio_name"),
            Label("URL de la Emisora:"),
            Input(placeholder="http://...", id="radio_url"),
            Button("Guardar", variant="primary", id="save"),
            Button("Cancelar", variant="default", id="cancel"),
            id="dialog",
        )

    def on_mount(self) -> None:
        """Enfoca el primer campo de texto al abrir la pantalla."""
        self.query_one("#radio_name", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            name = self.query_one("#radio_name", Input).value
            url = self.query_one("#radio_url", Input).value
            if name and url:
                self.dismiss({"name": name, "url": url})
            else:
                # Si falta algún campo, no hacemos nada y no cerramos la pantalla
                self.app.notify("Ambos campos son obligatorios.", severity="error")
        else: # Cancelar
            self.dismiss(None)