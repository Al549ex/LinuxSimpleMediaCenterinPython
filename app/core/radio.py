# app/core/radio.py

import json
import logging
from pathlib import Path
from typing import List, Dict

from app.core.config import get_config_value

def _get_radio_file_path() -> Path | None:
    """Obtiene la ruta del archivo de radios desde la configuración."""
    radio_file = get_config_value("PATHS", "radio_file_path")
    if not radio_file:
        logging.error("La ruta del archivo de radios no está configurada en config.ini.")
        return None
    return Path(radio_file)

def load_radios() -> List[Dict[str, str]]:
    """
    Carga la lista de radios desde el archivo JSON.
    Si el archivo no existe, lo crea vacío.
    """
    radio_file_path = _get_radio_file_path()
    if not radio_file_path:
        return []

    if not radio_file_path.exists():
        logging.warning(f"El archivo de radios '{radio_file_path}' no existe. Se creará uno nuevo.")
        save_radios([]) # Crea un archivo vacío con una lista vacía
        return []

    try:
        with open(radio_file_path, 'r', encoding='utf-8') as f:
            radios = json.load(f)
            # Aseguramos que sea una lista de diccionarios con las claves correctas
            if isinstance(radios, list) and all(isinstance(r, dict) and 'name' in r and 'url' in r for r in radios):
                return radios
            else:
                logging.error(f"El formato del archivo de radios '{radio_file_path}' es incorrecto. Se creará uno nuevo.")
                save_radios([])
                return []
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Error al leer o decodificar el archivo de radios '{radio_file_path}': {e}")
        return []

def save_radios(radios: List[Dict[str, str]]) -> bool:
    """Guarda la lista completa de radios en el archivo JSON."""
    radio_file_path = _get_radio_file_path()
    if not radio_file_path:
        return False

    try:
        with open(radio_file_path, 'w', encoding='utf-8') as f:
            json.dump(radios, f, indent=4, ensure_ascii=False)
        logging.info(f"Lista de radios guardada correctamente en '{radio_file_path}'.")
        return True
    except IOError as e:
        logging.error(f"Error al guardar el archivo de radios '{radio_file_path}': {e}")
        return False

def add_radio(name: str, url: str) -> bool:
    """Añade una nueva radio a la lista."""
    if not name or not url:
        logging.warning("Se intentó añadir una radio con nombre o URL vacíos.")
        return False

    radios = load_radios()
    
    # Comprobamos si ya existe una radio con ese nombre
    if any(r['name'].lower() == name.lower() for r in radios):
        logging.warning(f"Ya existe una radio con el nombre '{name}'.")
        return False

    radios.append({"name": name, "url": url})
    return save_radios(radios)

def delete_radio(name_to_delete: str) -> bool:
    """Elimina una radio de la lista por su nombre."""
    radios = load_radios()
    
    initial_count = len(radios)
    # Creamos una nueva lista sin la radio que queremos borrar (insensible a mayúsculas)
    radios_updated = [r for r in radios if r['name'].lower() != name_to_delete.lower()]

    if len(radios_updated) < initial_count:
        logging.info(f"Radio '{name_to_delete}' eliminada.")
        return save_radios(radios_updated)
    else:
        logging.warning(f"No se encontró la radio '{name_to_delete}' para eliminar.")
        return False