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

def check_cli_available() -> bool:
    """
    Verifica si el CLI de NordVPN está disponible.
    
    Returns:
        bool: True si el CLI está disponible
    """
    try:
        result = subprocess.run(
            ["nordvpn", "--version"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def login_with_token(token: str) -> tuple[bool, str]:
    """
    Inicia sesión en NordVPN usando un token de acceso.
    
    Args:
        token: Token de acceso de NordVPN
        
    Returns:
        tuple[bool, str]: (éxito, mensaje)
    """
    # Verificar plataforma
    if platform.system() not in ["Linux", "Darwin"]:
        return False, "Plataforma no compatible (se requiere Linux o macOS)"
    
    if not token or not token.strip():
        return False, "Token vacío"
    
    try:
        logging.info("Iniciando login con token de acceso...")
        result = subprocess.run(
            ["nordvpn", "login", "--token", token.strip()],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        full_output = result.stdout + "\n" + result.stderr
        logging.info(f"Resultado del login con token: {full_output}")
        
        if result.returncode == 0:
            # Login exitoso
            logging.info("✅ Login con token exitoso")
            
            # Verificar el estado
            is_logged_in, message = check_login_status()
            if is_logged_in:
                return True, f"Autenticación exitosa: {message}"
            else:
                return True, "Login completado"
        else:
            # Error en el login
            error_msg = full_output.strip()
            if "invalid" in error_msg.lower() or "expired" in error_msg.lower():
                return False, "Token inválido o expirado. Genera un nuevo token en https://my.nordaccount.com"
            return False, f"Error al autenticar con token: {error_msg}"
            
    except subprocess.TimeoutExpired:
        logging.error("El comando nordvpn login --token tardó demasiado tiempo.")
        return False, "Timeout: el login tardó más de 30 segundos"
    except FileNotFoundError:
        return False, "NordVPN CLI no está instalado"
    except Exception as e:
        logging.error(f"Error al ejecutar nordvpn login --token: {e}")
        return False, f"Error: {str(e)}"

def login_vpn() -> tuple[bool, str]:
    """
    Inicia el proceso de login de NordVPN.
    Si hay un token configurado, lo usa. Si no, genera una URL de autenticación.
    
    Returns:
        tuple[bool, str]: (éxito, url_o_mensaje)
    """
    # Verificar si hay un token configurado
    token = config.get("VPN", "access_token", fallback="").strip()
    
    if token:
        # Intentar login con token
        logging.info("Token encontrado en configuración, usando login con token...")
        return login_with_token(token)
    
    # Si no hay token, usar el método de URL
    logging.info("No hay token configurado, usando método de URL...")
    
    # Verificar plataforma
    if platform.system() not in ["Linux", "Darwin"]:
        return False, "Plataforma no compatible (se requiere Linux o macOS)"
    
    try:
        # Ejecutar nordvpn login y capturar toda la salida
        logging.info("Iniciando proceso de login de NordVPN...")
        result = subprocess.run(
            ["nordvpn", "login"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Combinar stdout y stderr (NordVPN puede usar stderr para la URL)
        full_output = result.stdout + "\n" + result.stderr
        output_lines = [line.strip() for line in full_output.splitlines() if line.strip()]
        
        logging.info(f"Salida completa de nordvpn login:\n{full_output}")
        logging.info(f"Return code: {result.returncode}")
        
        # Buscar la URL en toda la salida con múltiples patrones
        import re
        url = None
        
        # Patrón 1: URL completa en cualquier línea
        url_pattern = re.compile(r'https://[^\s\)\]\>]+')
        for line in output_lines:
            matches = url_pattern.findall(line)
            if matches:
                url = matches[0].rstrip('.,;:\'"')
                logging.info(f"✅ URL encontrada (patrón 1): {url}")
                break
        
        # Patrón 2: Si no encontramos, buscar en toda la salida completa
        if not url:
            matches = url_pattern.findall(full_output)
            if matches:
                url = matches[0].rstrip('.,;:\'"')
                logging.info(f"✅ URL encontrada (patrón 2): {url}")
        
        # Verificar si ya está autenticado
        if "already logged in" in full_output.lower() or "you are already logged in" in full_output.lower():
            return True, "Ya estás autenticado en NordVPN"
        
        if url:
            # Limpiar la URL de posibles caracteres ANSI o de escape
            url = re.sub(r'\x1b\[[0-9;]*m', '', url)  # Eliminar códigos ANSI
            url = url.strip()
            logging.info(f"✅ URL final limpia: {url}")
            return True, url
        elif output_lines:
            # Devolver toda la salida para debugging
            logging.warning("No se encontró URL en la salida")
            return False, f"No se encontró URL. Salida completa:\n{full_output}"
        else:
            return False, "No se obtuvo respuesta de nordvpn login"
            
    except subprocess.TimeoutExpired:
        logging.error("El comando nordvpn login tardó demasiado tiempo.")
        return False, "Timeout: nordvpn login tardó más de 30 segundos"
    except FileNotFoundError:
        logging.error("NordVPN CLI no está instalado.")
        
        # Mensaje específico por plataforma
        if platform.system() == "Darwin":  # macOS
            return False, (
                "❌ NordVPN CLI no disponible en macOS\n\n"
                "💡 Opciones:\n"
                "1. Usa la app GUI de NordVPN (recomendado)\n"
                "   - Abre NordVPN desde Aplicaciones\n"
                "   - Conecta manualmente antes de usar IPTV\n\n"
                "2. El CLI funciona mejor en Linux/Raspberry Pi\n\n"
                "Consulta MACOS_VPN_NOTE.md para más info"
            )
        else:  # Linux
            return False, (
                "❌ NordVPN CLI no está instalado\n\n"
                "Instala con:\n"
                "sh <(curl -sSf https://downloads.nordcdn.com/apps/linux/install.sh)\n\n"
                "O visita: nordvpn.com/download/linux"
            )
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
