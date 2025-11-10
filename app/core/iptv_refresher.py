# app/core/iptv_refresher.py

import requests
import os
import logging
from collections import defaultdict

# --- REFACTORIZACIÓN: Importamos el nuevo config ---
from app.core.config import config

def refresh_channels(source_url: str, output_dir: str) -> tuple[int, int]:
    """
    Descarga un archivo M3U maestro, lo divide por grupos y guarda los archivos.
    """
    if not source_url:
        raise ValueError("La URL de origen no puede estar vacía.")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    logging.info(f"Descargando lista maestra de canales desde {source_url}")
    response = requests.get(source_url, headers=headers, timeout=60)
    response.raise_for_status()  # Lanza una excepción si hay un error HTTP

    master_content = response.text
    groups = defaultdict(list)
    total_channels = 0

    lines = master_content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            group_title = 'General'  # Grupo por defecto
            if 'group-title="' in line:
                start = line.find('group-title="') + len('group-title="')
                end = line.find('"', start)
                group_title = line[start:end].strip()

            channel_info = [line]
            i += 1
            # La siguiente línea es la URL
            if i < len(lines) and (lines[i].strip().startswith('http')):
                channel_info.append(lines[i].strip())
                groups[group_title].extend(channel_info)
                total_channels += 1
        i += 1

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Directorio de salida creado: {output_dir}")

    # Limpiar archivos .m3u antiguos
    for item in os.listdir(output_dir):
        if item.endswith(".m3u"):
            os.remove(os.path.join(output_dir, item))
    logging.info("Archivos .m3u antiguos eliminados.")

    # Guardar nuevos archivos
    for group_title, content_lines in groups.items():
        # Limpiar el nombre del archivo para evitar caracteres no válidos
        safe_filename = "".join(c for c in group_title if c.isalnum() or c in (' ', '-')).rstrip()
        file_path = os.path.join(output_dir, f"{safe_filename}.m3u")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            f.write('\n'.join(content_lines))
            f.write('\n')
    
    num_groups = len(groups)
    logging.info(f"Proceso completado. {total_channels} canales divididos en {num_groups} grupos.")
    return num_groups, total_channels