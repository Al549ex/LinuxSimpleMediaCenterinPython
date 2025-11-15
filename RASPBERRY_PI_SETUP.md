# Configuración de Raspberry Pi para Pantalla Completa Sin Bordes

Este documento te guiará para configurar Openbox y LXTerminal para que la aplicación Python se vea como una app nativa sin bordes de ventana.

## 📋 Requisitos Previos

Ya deberías tener instalado:
- Raspberry Pi OS Lite
- X11 + Openbox
- LXTerminal
- Python 3 y la aplicación RaspIPTV

## 🎯 Configuración para App Sin Bordes

### 1. Configurar Openbox (Sin Decoraciones)

Edita el archivo de configuración de Openbox:

```bash
mkdir -p ~/.config/openbox
nano ~/.config/openbox/rc.xml
```

**Contenido del archivo `~/.config/openbox/rc.xml`:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<openbox_config xmlns="http://openbox.org/3.4/rc">
  <applications>
    <!-- LXTerminal: Fullscreen, sin bordes, sin decoraciones -->
    <application name="lxterminal" class="LXTerminal">
      <decor>no</decor>
      <maximized>yes</maximized>
      <focus>yes</focus>
      <layer>above</layer>
      <skip_pager>yes</skip_pager>
      <skip_taskbar>yes</skip_taskbar>
      <fullscreen>yes</fullscreen>
    </application>
  </applications>

  <keyboard>
    <!-- Ctrl+Alt+Backspace: Cerrar X11 -->
    <keybind key="C-A-BackSpace">
      <action name="Exit" />
    </keybind>
    
    <!-- Ctrl+Alt+F2: Cambiar a TTY2 (SSH) -->
    <keybind key="C-A-F2">
      <action name="Execute">
        <command>chvt 2</command>
      </action>
    </keybind>
  </keyboard>

  <mouse>
    <!-- Desactivar menú del escritorio con clic derecho -->
    <context name="Root">
      <mousebind button="Right" action="Press" />
    </context>
  </mouse>

  <!-- Tema oscuro minimalista -->
  <theme>
    <name>Onyx</name>
  </theme>

  <!-- Sin bordes de ventana -->
  <focus>
    <focusNew>yes</focusNew>
  </focus>
</openbox_config>
```

### 2. Configurar LXTerminal (Aspecto Limpio)

Edita la configuración de LXTerminal:

```bash
mkdir -p ~/.config/lxterminal
nano ~/.config/lxterminal/lxterminal.conf
```

**Contenido del archivo `~/.config/lxterminal/lxterminal.conf`:**

```ini
[general]
fontname=Monospace 12
selchars=-A-Za-z0-9,./?%&#:_
scrollback=1000
bgcolor=rgb(0,0,0)
fgcolor=rgb(255,255,255)
palette_color_0=rgb(0,0,0)
palette_color_1=rgb(205,0,0)
palette_color_2=rgb(0,205,0)
palette_color_3=rgb(205,205,0)
palette_color_4=rgb(0,0,238)
palette_color_5=rgb(205,0,205)
palette_color_6=rgb(0,205,205)
palette_color_7=rgb(229,229,229)
palette_color_8=rgb(127,127,127)
palette_color_9=rgb(255,0,0)
palette_color_10=rgb(0,255,0)
palette_color_11=rgb(255,255,0)
palette_color_12=rgb(92,92,255)
palette_color_13=rgb(255,0,255)
palette_color_14=rgb(0,255,255)
palette_color_15=rgb(255,255,255)
color_preset=Custom
disallowbold=false
cursorblinks=true
cursorunderline=false
audiblebell=false
visualbell=false
tabpos=top
geometry_columns=120
geometry_rows=30
hidescrollbar=true
hidemenubar=true
hideclosebutton=true
disablef10=true
disablealt=true
```

### 3. Script de Auto-Inicio de Openbox

Edita el archivo de auto-inicio:

```bash
nano ~/.config/openbox/autostart
```

**Contenido del archivo `~/.config/openbox/autostart`:**

```bash
#!/bin/bash

# Ocultar cursor del ratón (instalar primero: sudo apt install unclutter)
unclutter -idle 0.1 -root &

# Desactivar salvapantallas
xset s off
xset -dpms
xset s noblank

# Esperar a que X11 se inicialice completamente
sleep 3

# IMPORTANTE: Ajusta la ruta a donde está tu proyecto
# Opción 1: Si está en Desktop
# lxterminal --geometry=200x100 -e "bash -c 'cd ~/Desktop/Programación/IPTV/RaspIPTV && python3 run.py; exec bash'" &

# Opción 2: Si lo clonaste con git en el home
# lxterminal --geometry=200x100 -e "bash -c 'cd ~/LinuxSimpleMediaCenterinPython && python3 run.py; exec bash'" &

# Opción 3: Ruta absoluta (RECOMENDADO - reemplaza con tu ruta real)
lxterminal --geometry=200x100 -e "bash -c 'cd /home/RaspiAlex/Desktop/Programación/IPTV/RaspIPTV && python3 run.py; exec bash'" &
```

Dale permisos de ejecución:

```bash
chmod +x ~/.config/openbox/autostart
```

### 4. Configurar Auto-Login (Sin Pedir Contraseña)

```bash
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
sudo nano /etc/systemd/system/getty@tty1.service.d/autologin.conf
```

**Contenido del archivo:**

```ini
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin RaspiAlex --noclear %I $TERM
```

### 5. Auto-Inicio de X11 al Encender

Edita tu `.bash_profile`:

```bash
nano ~/.bash_profile
```

**Añade al final:**

```bash
# Auto-start X11 on tty1
if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
    startx
fi
```

### 6. Configurar ~/.xinitrc (Inicio de X11)

```bash
nano ~/.xinitrc
```

**Contenido:**

```bash
#!/bin/bash

# Iniciar Openbox
exec openbox-session
```

Dale permisos de ejecución:

```bash
chmod +x ~/.xinitrc
```

## 🎨 Personalización Adicional

### Cambiar Tamaño de Fuente

Edita `~/.config/lxterminal/lxterminal.conf`:

```ini
fontname=Monospace 14  # Aumentar para mejor lectura en TV
```

### Colores Personalizados

Puedes cambiar los colores en el mismo archivo:

```ini
bgcolor=rgb(15,15,30)     # Fondo azul oscuro
fgcolor=rgb(200,200,255)  # Texto azul claro
```

## 🔧 Comandos Útiles

### Reiniciar X11
```bash
# Desde la aplicación: Ctrl+Alt+Backspace
# O desde SSH:
pkill X
```

### Cambiar a TTY2 (Terminal SSH)
```bash
# Ctrl+Alt+F2 (configurado en rc.xml)
```

### Volver a TTY1 (X11)
```bash
# Ctrl+Alt+F1
```

### Probar Configuración
```bash
# Cerrar X11 si está activo
pkill X

# Iniciar X11 manualmente
startx

# La aplicación debería aparecer en pantalla completa sin bordes
```

## 📝 Verificación

Después de aplicar todos los cambios:

1. **Reinicia la Raspberry Pi:**
   ```bash
   sudo reboot
   ```

2. **Deberías ver:**
   - Login automático
   - X11 se inicia automáticamente
   - LXTerminal en pantalla completa SIN bordes
   - La aplicación Python iniciada automáticamente
   - Cursor del ratón oculto
   - Pantalla completamente negra con solo la app visible

## 🚨 PANTALLA NEGRA - Solución de Problemas

### Diagnóstico Rápido

Si solo ves la pantalla negra, conéctate por SSH desde otro ordenador:

```bash
ssh RaspiAlex@raspberrypi.local
```

O cambia a TTY2 presionando **Ctrl+Alt+F2** en la Raspberry Pi.

### 1. Verificar que X11 y Openbox están corriendo

```bash
# Verifica procesos
ps aux | grep openbox
ps aux | grep lxterminal

# Si no aparecen, reinicia X11
pkill X
startx
```

### 2. Probar la Ruta de la Aplicación Manualmente

```bash
# Prueba si puedes ejecutar la app directamente
cd ~/Desktop/Programación/IPTV/RaspIPTV
python3 run.py

# Si da error "No such file or directory", encuentra la ruta real:
find ~ -name "run.py" -type f 2>/dev/null
```

### 3. Corregir el Archivo Autostart

Una vez que sepas la ruta correcta, edita:

```bash
nano ~/.config/openbox/autostart
```

Reemplaza la última línea con la ruta correcta. Por ejemplo:

```bash
# Si tu proyecto está aquí:
lxterminal --geometry=200x100 -e "bash -c 'cd /home/RaspiAlex/Desktop/Programación/IPTV/RaspIPTV && python3 run.py; exec bash'" &

# O si está en otro lugar (usa la ruta que encontraste con 'find'):
lxterminal --geometry=200x100 -e "bash -c 'cd /ruta/completa/a/tu/proyecto && python3 run.py; exec bash'" &
```

### 4. Verificar que config.ini Existe

```bash
cd ~/Desktop/Programación/IPTV/RaspIPTV
ls -la config.ini

# Si no existe, cópialo del ejemplo:
cp config.ini.example config.ini
nano config.ini  # Edita con tus datos
```

### 5. Verificar Dependencias de Python

```bash
cd ~/Desktop/Programación/IPTV/RaspIPTV
pip3 install -r requirements.txt
```

### 6. Probar LXTerminal Manualmente (Desde SSH)

```bash
# Exportar DISPLAY
export DISPLAY=:0

# Intentar abrir LXTerminal
lxterminal -e "bash -c 'cd /home/RaspiAlex/Desktop/Programación/IPTV/RaspIPTV && python3 run.py'" &
```

### 7. Ver Logs de Errores

```bash
# Crea un log en el autostart para ver errores
nano ~/.config/openbox/autostart
```

Modifica la última línea para capturar errores:

```bash
lxterminal --geometry=200x100 -e "bash -c 'cd /home/RaspiAlex/Desktop/Programación/IPTV/RaspIPTV && python3 run.py 2>&1 | tee ~/app_error.log; exec bash'" &
```

Luego reinicia y mira el log:

```bash
cat ~/app_error.log
```

### 8. Script de Autostart Completo y Probado

Usa este archivo **completo** para `~/.config/openbox/autostart`:

```bash
#!/bin/bash

# Log para debug
exec > ~/.openbox_autostart.log 2>&1
echo "Autostart iniciado: $(date)"

# Ocultar cursor
which unclutter && unclutter -idle 0.1 -root &

# Desactivar salvapantallas
xset s off
xset -dpms
xset s noblank

echo "Esperando 3 segundos para que X11 se estabilice..."
sleep 3

# Encuentra la ruta del proyecto (ajusta según tu instalación)
PROJECT_PATH="/home/RaspiAlex/Desktop/Programación/IPTV/RaspIPTV"

# Verifica que existe
if [ -d "$PROJECT_PATH" ]; then
    echo "Proyecto encontrado en: $PROJECT_PATH"
    
    # Verifica que run.py existe
    if [ -f "$PROJECT_PATH/run.py" ]; then
        echo "Lanzando aplicación..."
        lxterminal --geometry=200x100 -e "bash -c 'cd $PROJECT_PATH && python3 run.py; echo Presiona Enter para cerrar; read'" &
        echo "LXTerminal lanzado"
    else
        echo "ERROR: No se encuentra run.py en $PROJECT_PATH"
        lxterminal -e "bash -c 'echo ERROR: No se encuentra run.py; echo Revisa la ruta en autostart; exec bash'" &
    fi
else
    echo "ERROR: No se encuentra el directorio $PROJECT_PATH"
    lxterminal -e "bash -c 'echo ERROR: Directorio del proyecto no encontrado; echo Revisa ~/.config/openbox/autostart; exec bash'" &
fi

echo "Autostart completado: $(date)"
```

Después de guardar, dale permisos:

```bash
chmod +x ~/.config/openbox/autostart
```

### 9. Reiniciar y Verificar Logs

```bash
sudo reboot
```

Después del reinicio, conéctate por SSH y revisa:

```bash
# Ver log de autostart
cat ~/.openbox_autostart.log

# Ver si hay errores de Python
cat ~/app_error.log
```

## ⚠️ Solución de Problemas Adicionales

### La ventana tiene bordes
```bash
# Verifica que Openbox esté usando tu configuración:
cat ~/.config/openbox/rc.xml | grep -A 5 "LXTerminal"

# Reinicia Openbox:
openbox --reconfigure
```

### El cursor del ratón se ve
```bash
# Instala unclutter:
sudo apt install unclutter

# Verifica que esté en autostart
cat ~/.config/openbox/autostart | grep unclutter
```

### La app no se inicia automáticamente
```bash
# Verifica el script de autostart:
cat ~/.config/openbox/autostart

# Comprueba permisos:
ls -la ~/.config/openbox/autostart

# Debería mostrar: -rwxr-xr-x (ejecutable)
```

### SSH no funciona
```bash
# Cambia a TTY2 con Ctrl+Alt+F2
# O desde otro ordenador:
ssh RaspiAlex@raspberrypi.local

# Verifica servicio SSH:
sudo systemctl status ssh
```

## 🎯 Resultado Final

Tu Raspberry Pi ahora funcionará como un centro multimedia dedicado:
- ✅ Pantalla completamente negra
- ✅ Solo visible la aplicación Python (Textual)
- ✅ Sin bordes de ventana
- ✅ Sin cursor del ratón
- ✅ Inicio automático al encender
- ✅ Aspecto de aplicación nativa/profesional
- ✅ Perfecto para conectar a TV

## 🔗 Archivos de Configuración Relacionados

- `~/.config/openbox/rc.xml` - Configuración principal de Openbox
- `~/.config/openbox/autostart` - Script de auto-inicio
- `~/.config/lxterminal/lxterminal.conf` - Configuración del terminal
- `~/.xinitrc` - Configuración de inicio de X11
- `~/.bash_profile` - Auto-inicio de X11 en TTY1
- `/etc/systemd/system/getty@tty1.service.d/autologin.conf` - Auto-login

---

**¡Disfruta de tu centro multimedia sin bordes! 📺🎬**
