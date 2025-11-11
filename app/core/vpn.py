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

def login_vpn() -> tuple[bool, str]:
    """
    Inicia el proceso de login de NordVPN y devuelve la URL de autenticación.
    
    Returns:
        tuple[bool, str]: (éxito, url_o_mensaje)
    """
    # Verificar plataforma
    if platform.system() not in ["Linux", "Darwin"]:
        return False, "Plataforma no compatible (se requiere Linux o macOS)"
    
    try:
        # Ejecutar nordvpn login
        logging.info("Iniciando proceso de login de NordVPN...")
        process = subprocess.Popen(
            ["nordvpn", "login"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Leer la salida en tiempo real para capturar la URL
        url = None
        output_lines = []
        
        # Leer stdout
        if process.stdout:
            for line in process.stdout:
                output_lines.append(line.strip())
                logging.debug(f"NordVPN login output: {line.strip()}")
                
                # Buscar la URL en la salida
                if "https://" in line:
                    # Extraer la URL
                    import re
                    url_match = re.search(r'https://[^\s]+', line)
                    if url_match:
                        url = url_match.group(0)
                        logging.info(f"URL de autenticación encontrada: {url}")
        
        # Esperar a que termine el proceso (con timeout)
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            logging.warning("El proceso de login tardó demasiado.")
        
        if url:
            return True, url
        elif output_lines:
            # Si no encontramos URL pero hay salida, devolverla
            full_output = "\n".join(output_lines)
            if "already logged in" in full_output.lower():
                return True, "Ya estás autenticado en NordVPN"
            return True, full_output
        else:
            return False, "No se pudo obtener la URL de autenticación"
            
    except FileNotFoundError:
        logging.error("NordVPN CLI no está instalado.")
        return False, "NordVPN CLI no está instalado. Instálalo con 'brew install nordvpn' (macOS) o desde nordvpn.com/download (Linux)"
    except Exception as e:
        logging.error(f"Error al ejecutar nordvpn login: {e}")
        return False, f"Error: {str(e)}"

def check_login_status() -> tuple[bool, str]:
    """
    Verifica si el usuario está autenticado en NordVPN.
    
    Returns:
        tuple[bool, str]: (autenticado, mensaje_o_email)
    """
    success, output = _run_nordvpn_command(["account"])
    
    if success and "You are not logged in" not in output:
        # Extraer el email si está presente
        import re
        email_match = re.search(r'Email Address:\s*(\S+)', output)
        if email_match:
            return True, email_match.group(1)
        return True, "Autenticado"
    else:
        return False, "No autenticado"
