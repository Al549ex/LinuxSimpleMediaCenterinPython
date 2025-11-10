from textual.app import ComposeResult
from textual.widgets import Header, Footer, DataTable
from textual.screen import ModalScreen
from textual.binding import Binding

from app.core import radio

class RadioSelectorScreen(ModalScreen):
    """A modal screen to select a radio station to play."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Volver", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, name="Seleccionar Radio")
        yield DataTable(id="radio_selector_table")
        yield Footer()

    def on_mount(self) -> None:
        """Load radios into the DataTable when the screen is mounted."""
        table = self.query_one(DataTable)
        table.add_column("Nombre", key="name")
        table.add_column("URL", key="url")
        table.cursor_type = "row"
        
        radios = radio.load_radios()
        for radio_item in radios:
            radio_name = radio_item.get("name")
            radio_url = radio_item.get("url")
            if radio_name and radio_url:
                table.add_row(radio_name, radio_url, key=radio_name)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle radio selection."""
        row_key = event.row_key.value
        if row_key:
            radios = radio.load_radios()
            selected_url = None
            for radio_item in radios:
                if radio_item.get("name") == row_key:
                    selected_url = radio_item.get("url")
                    break
            
            if selected_url:
                self.dismiss(selected_url)