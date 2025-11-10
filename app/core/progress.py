# app/core/progress.py

import logging
import os
from pathlib import Path
import re

MPV_WATCH_LATER_DIR = Path.home() / ".config" / "mpv" / "watch_later"

def _find_progress_file(video_path: str) -> Path | None:
    if not MPV_WATCH_LATER_DIR.exists():
        return None
        
    normalized_video_path = os.path.realpath(video_path)
    
    for progress_file in MPV_WATCH_LATER_DIR.iterdir():
        try:
            content = progress_file.read_text()
            first_line = content.splitlines()[0]
            
            if first_line.startswith("# ") and os.path.realpath(first_line[2:].strip()) == normalized_video_path:
                return progress_file
        except (IOError, IndexError):
            continue
    return None

def get_progress(file_path: str) -> float | None:
    progress_file = _find_progress_file(file_path)
    if not progress_file:
        return None
        
    try:
        content = progress_file.read_text()
        match = re.search(r"^start=([\d\.]+)", content, re.MULTILINE)
        if match:
            return float(match.group(1))
    except Exception as e:
        logging.error(f"Error al parsear el archivo de progreso '{progress_file.name}': {e}")
    return None

def clear_progress(file_path: str) -> None:
    progress_file = _find_progress_file(file_path)
    if progress_file and progress_file.exists():
        try:
            progress_file.unlink()
        except Exception as e:
            logging.error(f"No se pudo eliminar el archivo de progreso '{progress_file.name}': {e}")

def clear_all_progress() -> int:
    if not MPV_WATCH_LATER_DIR.exists():
        return 0
    
    count = 0
    for progress_file in MPV_WATCH_LATER_DIR.iterdir():
        try:
            progress_file.unlink()
            count += 1
        except Exception as e:
            logging.error(f"No se pudo eliminar el archivo de progreso '{progress_file.name}': {e}")
    return count