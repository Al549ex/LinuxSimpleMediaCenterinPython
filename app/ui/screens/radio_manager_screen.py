# app/ui/screens/radio_manager_screen.py

import logging
from typing import Optional

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, ListView, ListItem, Label, Static
from textual.containers import Horizontal, ScrollableContainer

from app.core.radio import load_radios, add_radio, delete_radio
from app.ui.screens.add_radio_screen import AddRadioScreen
from app.ui.screens.confirm_screen import ConfirmScreen

class RadioManagerScreen(Screen):
    """Pantalla optimizada para gestionar radios."""

    CSS = """
    #radio-list-container {
        height: 1fr;
    }

    ListView {
        margin: 1;
    }
    
    #button-row {
        dock: bottom;
        height: 5;
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
        margin: 0 1;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_radio_name: Optional[str] = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, name="Gestionar Radios")
        
        with ScrollableContainer(id="radio-list-container"):
            yield ListView(id="radio_list")
        
        with Horizontal(id="button-row"):
            yield Button("Volver", id="exit_radio_manager", variant="error")
            yield Static() # Espaciador
            yield Button("Añadir", id="add_radio", variant="primary")
            yield Button(
                "Eliminar",
                id="delete_radio",
                variant="warning",
                disabled=True
            )
        
        yield Footer()

    def on_mount(self) -> None:
        """Carga las radios al montar."""
        self.refresh_radio_list()

    def refresh_radio_list(self):
        """Recarga la lista de radios."""
        radio_list = self.query_one(ListView)
        radio_list.clear()
        
        radios = load_radios()
        
        if not radios:
            item = ListItem(Label("No hay radios configuradas"))
            item.radio_name = None
            radio_list.append(item)
        else:
            for radio in radios:
                list_item = ListItem(Label(f"📻 {radio['name']}"))
                list_item.radio_name = radio['name']
                radio_list.append(list_item)
        
        self.query_one("#delete_radio", Button).disabled = True
        self.selected_radio_name = None

    def on_list_view_selected(self, event: ListView.Selected):
        """Activa al seleccionar un elemento."""
        if hasattr(event.item, 'radio_name') and event.item.radio_name:
            self.query_one("#delete_radio", Button).disabled = False
            self.selected_radio_name = event.item.radio_name
        else:
            self.query_one("#delete_radio", Button).disabled = True
            self.selected_radio_name = None

    def _handle_add_radio(self, data: Optional[dict]):
        """Callback tras añadir radio."""
        if data:
            name, url = data.get('name'), data.get('url')
            if name and url:
                if add_radio(name, url):
                    self.app.notify(f"✅ Radio '{name}' añadida.")
                    self.refresh_radio_list()
                else:
                    self.app.notify(
                        f"❌ Error: ¿La radio '{name}' ya existe?",
                        severity="error"
                    )

    def _handle_delete_confirmation(self, should_delete: bool):
        """Callback tras confirmar eliminación."""
        if should_delete and self.selected_radio_name:
            if delete_radio(self.selected_radio_name):
                self.app.notify(f"✅ Radio '{self.selected_radio_name}' eliminada.")
                self.refresh_radio_list()
            else:
                self.app.notify("❌ Error al eliminar.", severity="error")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Gestiona botones."""
        if event.button.id == "add_radio":
            self.app.push_screen(AddRadioScreen(), self._handle_add_radio)
        
        elif event.button.id == "delete_radio":
            if self.selected_radio_name:
                self.app.push_screen(
                    ConfirmScreen(
                        f"¿Eliminar '{self.selected_radio_name}'?\n\n"
                        "Esta acción no se puede deshacer."
                    ),
                    self._handle_delete_confirmation
                )

        elif event.button.id == "exit_radio_manager":
            self.app.pop_screen()