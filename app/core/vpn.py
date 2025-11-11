# app/core/vpn.py

import logging
import subprocess
import platform
from enum import Enum

from app.core.config import config

# --- Definimos los posibles estados de la operación VPN ---
class VPNStatus(Enum):
    SUCCESS = 0
    SKIPPED = 1
    FAILED = 2

def _run_nordvpn_command(args: list[str]) -> tuple[bool, str]:
    """
    Ejecuta un comando del CLI de NordVPN y devuelve el resultado.
    
    Returns:
        tuple[bool, str]: (éxito, salida_del_comando)
    """
    try:
        result = subprocess.run(
            ["nordvpn"] + args,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout.strip()
    except subprocess.TimeoutExpired:
        logging.error("El comando de NordVPN ha tardado demasiado tiempo.")
        return False, "Timeout"
    except FileNotFoundError:
        logging.error("NordVPN CLI no está instalado o no se encuentra en el PATH.")
        return False, "NordVPN not found"
    except Exception as e:
        logging.error(f"Error al ejecutar comando de NordVPN: {e}")
        return False, str(e)

def get_vpn_status() -> dict:
    """
    Obtiene el estado actual de la conexión VPN.
    
    Returns:
        dict: Estado de la VPN con claves 'connected' (bool) y 'info' (str)
    """
    success, output = _run_nordvpn_command(["status"])
    
    if not success:
        return {"connected": False, "info": "Error checking status"}
    
    # Buscar la línea "Status: Connected" o "Status: Disconnected"
    is_connected = "Status: Connected" in output
    
    return {
        "connected": is_connected,
        "info": output
    }

def connect_vpn() -> VPNStatus:
    """
    Se conecta a NordVPN usando el CLI oficial.
    Usa el país configurado en config.ini si está especificado.
    
    Returns:
        VPNStatus: Estado de la operación
    """
    # Verificar plataforma
    if platform.system() not in ["Linux", "Darwin"]:  # Darwin = macOS
        logging.warning("Plataforma no compatible (se requiere Linux o macOS).")
        return VPNStatus.SKIPPED
    
    # Verificar si ya está conectado
    status = get_vpn_status()
    if status["connected"]:
        logging.info("Ya hay una conexión VPN activa.")
        return VPNStatus.SUCCESS
    
    # Obtener país de configuración
    country = config.get("VPN", "country", fallback="").strip()
    
    # Construir comando
    if country:
        logging.info(f"Conectando a NordVPN en '{country}'...")
        success, output = _run_nordvpn_command(["connect", country])
    else:
        logging.info("Conectando a NordVPN (servidor automático)...")
        success, output = _run_nordvpn_command(["connect"])
    
    if success:
        logging.info(f"✅ Conexión VPN establecida: {output}")
        return VPNStatus.SUCCESS
    else:
        logging.error(f"❌ Error al conectar VPN: {output}")
        return VPNStatus.FAILED

def disconnect_vpn() -> VPNStatus:
    """
    Se desconecta de NordVPN usando el CLI oficial.
    
    Returns:
        VPNStatus: Estado de la operación
    """
    # Verificar plataforma
    if platform.system() not in ["Linux", "Darwin"]:
        logging.warning("Plataforma no compatible.")
        return VPNStatus.SKIPPED
    
    # Verificar si hay conexión activa
    status = get_vpn_status()
    if not status["connected"]:
        logging.info("No hay conexión VPN activa.")
        return VPNStatus.SUCCESS
    
    logging.info("Desconectando de NordVPN...")
    success, output = _run_nordvpn_command(["disconnect"])
    
    if success:
        logging.info(f"✅ VPN desconectada: {output}")
        return VPNStatus.SUCCESS
    else:
        logging.error(f"❌ Error al desconectar VPN: {output}")
        return VPNStatus.FAILED
