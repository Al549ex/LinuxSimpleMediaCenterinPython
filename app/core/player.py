# app/core/player.py

import logging
import subprocess
import sys
import os
from typing import Optional

def play_video(
    file_path: str,
    start_position: float = 0.0,
    save_progress_flag: bool = False,
    mute_video: bool = False
) -> Optional[subprocess.Popen]:
    """
    Inicia la reproducción con mpv optimizado para Raspberry Pi 4.
    """
    try:
        # Detectar si es streaming
        is_streaming = file_path.startswith(("http://", "https://"))
        
        # Base del comando con optimizaciones para RPi4
        command = [
            "mpv",
            "--fullscreen",
        ]

        # Optimizaciones específicas para streaming
        if is_streaming:
            logging.info("Streaming detectado. Aplicando optimizaciones de red.")
            command.extend([
                "--cache=yes",
                "--cache-secs=10",           # 10 segundos de buffer
                "--demuxer-max-bytes=50M",   # 50MB de buffer máximo
                "--demuxer-readahead-secs=5", # Pre-buffer de 5 segundos
                "--stream-buffer-size=512k",  # Buffer de red de 512KB
                "--network-timeout=15",       # Timeout de red de 15s
            ])
        else:
            # Para archivos locales, deshabilitar caché innecesaria
            command.append("--cache=no")

        # Añadimos el archivo o URL
        command.append(file_path)

        # Silenciar audio si se solicita
        if mute_video:
            command.append("--no-audio")
            logging.info("Vídeo silenciado (--no-audio).")

        # Posición de inicio
        if start_position > 0:
            command.append(f"--start={start_position}")

        # Guardar progreso
        if save_progress_flag:
            command.append("--save-position-on-quit")
            config_dir = (
                os.path.expanduser("~/Library/Application Support/mpv")
                if sys.platform == "darwin"
                else os.path.expanduser("~/.config/mpv")
            )
            watch_later_dir = os.path.join(config_dir, "watch_later")
            os.makedirs(watch_later_dir, exist_ok=True)

        logging.info(f"Comando mpv: {' '.join(command)}")
        
        # Iniciar proceso
        process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return process

    except FileNotFoundError:
        logging.error("mpv no está instalado o no se encuentra en el PATH.")
        return None
    except Exception as e:
        logging.error(f"Error al iniciar mpv: {e}")
        return None
