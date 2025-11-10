# app/core/vpn.py

import logging
import platform
from enum import Enum
from nordvpn_switcher import initialize_VPN, rotate_VPN, terminate_VPN

# Importamos nuestra configuración
from app.core.config import get_config_value

# --- Definimos los posibles estados de la operación VPN ---
class VPNStatus(Enum):
    SUCCESS = 0
    SKIPPED = 1
    FAILED = 2 # <-- El nombre correcto es FAILED, no FAILURE

# Esta variable guardará las instrucciones de la VPN una vez inicializada
vpn_instructions = None

def connect_vpn() -> VPNStatus:
    """
    Inicializa y se conecta a NordVPN usando el país del config.
    Devuelve un estado para indicar éxito, omisión o fallo.
    """
    global vpn_instructions

    # Comprobamos si el sistema es Linux. Si no, lo simulamos.
    if platform.system() != "Linux":
        logging.warning("Plataforma no compatible (se requiere Linux). Se simulará la conexión VPN.")
        return VPNStatus.SKIPPED
    
    # Si ya tenemos instrucciones y estamos conectados, no hacemos nada.
    if vpn_instructions:
        logging.info("La sesión de VPN ya está inicializada.")
        return VPNStatus.SUCCESS

    country = get_config_value("VPN", "country")
    if not country:
        logging.error("No se ha especificado un país en la configuración para la VPN.")
        return VPNStatus.FAILURE

    try:
        logging.info("Inicializando sesión de VPN...")
        init_instructions = initialize_VPN(area_input=[country], skip_settings=1)
        
        if not init_instructions:
            raise ValueError("La inicialización de la VPN no devolvió instrucciones.")

        logging.info(f"Conectando a la VPN en '{country}'...")
        rotate_VPN(init_instructions)
        
        vpn_instructions = init_instructions
        logging.info("Conexión VPN establecida con éxito.")
        return VPNStatus.SUCCESS

    except Exception as e:
        logging.error(f"Error durante el proceso de conexión VPN: {e}")
        vpn_instructions = None
        return VPNStatus.FAILURE

def disconnect_vpn() -> VPNStatus:
    """
    Se desconecta de NordVPN usando las instrucciones guardadas.
    """
    global vpn_instructions

    # Comprobamos si el sistema es Linux. Si no, lo simulamos.
    if platform.system() != "Linux":
        logging.warning("Plataforma no compatible. Se simulará la desconexión de la VPN.")
        return VPNStatus.SKIPPED
    
    if not vpn_instructions:
        logging.warning("No hay una sesión de VPN activa para desconectar.")
        return VPNStatus.SUCCESS
        
    try:
        logging.info("Desconectando de la VPN...")
        terminate_VPN(vpn_instructions)
        vpn_instructions = None
        logging.info("VPN desconectada con éxito.")
        return VPNStatus.SUCCESS
    except Exception as e:
        logging.error(f"Error durante la desconexión de la VPN: {e}")
        return VPNStatus.FAILURE
