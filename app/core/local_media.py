# core/local_media.py
import os
import logging # <-- Importamos logging
from typing import List

# Lista de extensiones de vídeo que queremos encontrar
VIDEO_EXTENSIONS = {".mkv", ".mp4", ".avi", ".mov", ".wmv"}

def get_local_movie_list(path: str) -> List[str]:
    """
    Escanea una ruta y devuelve una lista de archivos de vídeo.
    """
    
    # Usamos logging en lugar de print()
    logging.info(f"Llamado a get_local_movie_list con la ruta: {path}")
    
    movie_files = []
    
    # 1. Comprobar si la ruta existe y es un directorio
    if not os.path.isdir(path):
        logging.error(f"La ruta '{path}' no es un directorio válido.")
        return movie_files # Devuelve lista vacía

    # 2. Recorrer el directorio recursivamente
    for root, dirs, files in os.walk(path):
        for file in files:
            # --- DEBUG: Imprimimos cada archivo encontrado ---
            logging.debug(f"Analizando archivo -> {os.path.join(root, file)}")
            
            # 3. Comprobar si la extensión es de un vídeo
            if os.path.splitext(file)[1].lower() in VIDEO_EXTENSIONS:
                # 4. Añadir la ruta completa a nuestra lista
                full_path = os.path.join(root, file)
                movie_files.append(full_path)
                
    logging.info(f"Encontrados {len(movie_files)} archivos de vídeo.")
    return movie_files