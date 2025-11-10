# app/core/config.py

import configparser
import logging
import os
from typing import Optional

class Config:
    """
    Clase Singleton para gestionar la configuración de la aplicación.
    Centraliza la carga, acceso y guardado del archivo config.ini.
    Optimizado para Raspberry Pi 4.
    """
    _instance: Optional['Config'] = None
    _config_path = 'config.ini'
    _default_config = {
        'PATHS': {
            'local_media_path': './Peliculas/',
            'iptv_folder_path': './Archivos M3U/',
            'radio_file_path': 'radios.json'
        },
        'VPN': {
            'enabled_for_iptv': 'no',
            'country': 'Spain',
            'username': '',
            'password': ''
        },
        'IPTV': {
            'source_url': ''
        },
        'TMDB': {
            'api_key': ''
        }
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._parser = configparser.ConfigParser()
            cls._instance._loaded = False
        return cls._instance

    def load(self) -> bool:
        """Carga el archivo de configuración o lo crea si no existe."""
        if self._loaded:
            return True
            
        if not os.path.exists(self._config_path):
            logging.warning(f"No se encontró '{self._config_path}'. Creando uno nuevo con valores por defecto.")
            self._parser.read_dict(self._default_config)
            self.save()
        else:
            try:
                self._parser.read(self._config_path, encoding='utf-8')
                logging.info(f"Archivo de configuración '{self._config_path}' cargado.")
                self._loaded = True
                return True
            except Exception as e:
                logging.error(f"Error al cargar la configuración: {e}")
                return False
        return True

    def get(self, section: str, option: str, fallback: Optional[str] = None) -> Optional[str]:
        """Obtiene un valor de la configuración como string."""
        try:
            return self._parser.get(section, option, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback

    def get_boolean(self, section: str, option: str, fallback: bool = False) -> bool:
        """Obtiene un valor booleano de la configuración."""
        try:
            return self._parser.getboolean(section, option, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback

    def set(self, section: str, option: str, value: str) -> None:
        """Establece un valor en la configuración."""
        if not self._parser.has_section(section):
            self._parser.add_section(section)
        self._parser.set(section, option, str(value))

    def save(self) -> bool:
        """Guarda la configuración actual en el archivo config.ini."""
        try:
            with open(self._config_path, 'w', encoding='utf-8') as configfile:
                self._parser.write(configfile)
            logging.info(f"Configuración guardada en '{self._config_path}'.")
            return True
        except IOError as e:
            logging.error(f"No se pudo guardar la configuración: {e}")
            return False

# Instancia única
config = Config()
config.load()

# Funciones legacy para retrocompatibilidad con código existente
def load_config() -> bool:
    """Función legacy para compatibilidad."""
    return config.load()

def get_config_value(section: str, option: str, fallback: Optional[str] = None) -> Optional[str]:
    """Función legacy para compatibilidad."""
    return config.get(section, option, fallback=fallback)
