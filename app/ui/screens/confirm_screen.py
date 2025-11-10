# app/ui/screens/confirm_screen.py

from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.containers import Grid
from textual.widgets import Button, Label

class ConfirmScreen(ModalScreen[bool]):
    """Pantalla modal para una pregunta de confirmación Sí/No."""

    def __init__(self, question: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.question = question

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(self.question, id="question"),
            Button("Sí", variant="primary", id="yes"),
            Button("No", variant="error", id="no"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Cierra la pantalla modal y devuelve True para 'sí' o False para 'no'."""
        self.dismiss(event.button.id == "yes")