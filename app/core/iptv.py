# app/core/iptv.py

import os
import logging
import re
from collections import namedtuple
from typing import List

from app.core.config import config

# Estructura para los canales
Channel = namedtuple('Channel', ['name', 'logo', 'url', 'group'])

# Compilar expresiones regulares una sola vez (optimización)
_RE_LOGO = re.compile(r'tvg-logo="([^"]*)"')
_RE_GROUP = re.compile(r'group-title="([^"]*)"')

def get_m3u_files() -> List[str]:
    """
    Obtiene una lista ordenada de archivos .m3u de la carpeta configurada.
    """
    path = config.get("PATHS", "iptv_folder_path")
    
    if not path or not os.path.isdir(path):
        logging.warning(f"Ruta IPTV '{path}' no es un directorio válido.")
        return []
    
    try:
        files = [f for f in os.listdir(path) if f.lower().endswith('.m3u')]
        files.sort()
        return files
    except OSError as e:
        logging.error(f"Error al leer directorio '{path}': {e}")
        return []

def parse_m3u_file(file_path: str) -> List[Channel]:
    """
    Parsea un archivo M3U optimizado con expresiones regulares.
    """
    channels = []
    
    if not os.path.exists(file_path):
        logging.error(f"Archivo M3U no existe: {file_path}")
        return channels

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        logging.error(f"No se pudo leer {file_path}: {e}")
        return channels

    # Dividir en líneas y procesar
    lines = content.splitlines()
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('#EXTINF:'):
            try:
                # Extraer nombre
                parts = line.split(',', 1)
                if len(parts) < 2:
                    i += 1
                    continue
                    
                name = parts[1].strip()
                metadata = parts[0]
                
                # Extraer logo y grupo con regex (mucho más rápido)
                logo_match = _RE_LOGO.search(metadata)
                group_match = _RE_GROUP.search(metadata)
                
                logo = logo_match.group(1) if logo_match else ''
                group = group_match.group(1) if group_match else ''
                
                # La siguiente línea debe ser la URL
                i += 1
                if i < len(lines):
                    url = lines[i].strip()
                    if url.startswith(('http://', 'https://')):
                        channels.append(Channel(
                            name=name,
                            logo=logo,
                            url=url,
                            group=group
                        ))
            except Exception as e:
                logging.warning(f"Línea mal formada: {line[:50]}... - {e}")
        
        i += 1
    
    logging.info(f"Parseados {len(channels)} canales de {file_path}")
    return channels