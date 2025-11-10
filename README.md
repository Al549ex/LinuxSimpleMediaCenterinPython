# 🎬 RaspIPTV Media Center

Un centro multimedia completo y optimizado para **Raspberry Pi 4**, construido con Python y Textual. Reproduce películas locales, IPTV con integración de VPN, radio en streaming y más.

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%204-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## ✨ Características

### 🎥 Biblioteca de Películas
- **Integración con TMDB**: Búsqueda automática de información de películas
- **Detalles completos**: Sinopsis, reparto, director, géneros, puntuación
- **Guardar y reanudar**: Retoma desde donde lo dejaste
- **Interfaz elegante**: Diseño tipo biblioteca con toda la información

### 📺 IPTV
- **Reproducción de canales**: Soporte para archivos `.m3u`
- **Actualización automática**: Descarga y divide listas IPTV por grupos
- **Integración VPN**: Conecta automáticamente a NordVPN para streaming
- **Gestión inteligente**: Organización alfabética de grupos de canales

### 📻 Radio en Streaming
- **Reproducción en segundo plano**: Escucha radio mientras ves IPTV
- **Gestión de emisoras**: Añade, elimina y organiza tus radios favoritas
- **Controles completos**: Pausa/reanudar desde cualquier pantalla
- **Silenciado inteligente**: Audio de video se silencia automáticamente

### 🔐 VPN
- **Integración NordVPN**: Conexión/desconexión automática
- **Configurable**: Activa/desactiva VPN para IPTV desde la configuración
- **Gestión inteligente**: Solo se conecta cuando es necesario

### ⚙️ Configuración
- **Interfaz gráfica**: Todo configurable desde la aplicación
- **Validación de rutas**: Verifica y crea directorios automáticamente
- **Persistencia**: Configuración guardada en `config.ini`

---

## 🚀 Instalación

### Requisitos previos
- **Raspberry Pi 4** (recomendado) o cualquier sistema Linux/macOS
- **Python 3.9+**
- **mpv** (reproductor multimedia)
- **NordVPN** instalado (opcional, solo para funciones VPN)

### 1. Instalar MPV

**En Raspberry Pi / Debian / Ubuntu:**
```bash
sudo apt update
sudo apt install mpv
```

**En macOS:**
```bash
brew install mpv
```

### 2. Clonar el repositorio

```bash
git clone https://github.com/tuusuario/RaspIPTV.git
cd RaspIPTV
```

### 3. Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Configuración inicial

Copia el archivo de configuración de ejemplo:
```bash
cp config.ini.example config.ini
```

Edita `config.ini` o usa la interfaz gráfica de la aplicación para configurar:
- Rutas de películas y archivos M3U
- Credenciales de VPN (si usas NordVPN)
- API Key de TMDB (opcional, para información de películas)

---

## 🎮 Uso

### Iniciar la aplicación

```bash
python3 run.py
```

### Obtener API Key de TMDB (opcional pero recomendado)

1. Ve a [https://www.themoviedb.org/](https://www.themoviedb.org/)
2. Crea una cuenta gratuita
3. Ve a **Settings → API**
4. Solicita una API Key (aprobación instantánea)
5. Copia tu **API Key (v3 auth)**
6. Pégala en la aplicación: **Configuración → API Key de TMDB**

### Estructura de archivos esperada

```
RaspIPTV/
├── run.py                 # Archivo principal
├── config.ini             # Configuración (se crea automáticamente)
├── radios.json            # Lista de radios (se crea automáticamente)
├── Peliculas/             # Carpeta de películas (configurable)
│   ├── pelicula1.mp4
│   ├── pelicula2.mkv
│   └── ...
├── Archivos M3U/          # Carpeta de listas IPTV (configurable)
│   ├── deportes.m3u
│   ├── noticias.m3u
│   └── ...
└── app/                   # Código fuente
```

---

## 🎯 Navegación

### Menú Principal
- **Ver Películas (Local)**: Accede a tu biblioteca de películas
- **IPTV**: Navega por tus canales de TV
- **Actualizar Canales IPTV**: Descarga y actualiza tu lista IPTV
- **Gestionar Radios**: Añade/elimina emisoras de radio
- **Configuración**: Ajusta todas las opciones

### Atajos de teclado
- `q` o `Ctrl+C`: Salir de la pantalla actual
- `Esc`: Volver atrás
- `Tab`: Navegar entre elementos
- `Enter`: Seleccionar

---

## 🛠️ Optimizaciones para Raspberry Pi 4

El proyecto está específicamente optimizado para funcionar en Raspberry Pi 4:

### Reproductor MPV
- **Decodificación por hardware**: `--hwdec=rpi-copy`
- **GPU optimizado**: `--vo=gpu --gpu-context=drm`
- **Caché inteligente**: Buffer de 50MB para streaming
- **Perfil de bajo consumo**: `--profile=fast`

### Código Python
- **Workers asíncronos**: Operaciones pesadas en hilos separados
- **Caché de datos**: Reduce búsquedas repetitivas
- **Expresiones regulares compiladas**: Parseo M3U ultra-rápido
- **Gestión eficiente de memoria**: Liberación correcta de recursos

---

## 📁 Estructura del proyecto

```
RaspIPTV/
├── run.py                          # Punto de entrada
├── requirements.txt                # Dependencias Python
├── config.ini                      # Configuración (gitignored)
├── README.md                       # Este archivo
│
├── app/
│   ├── core/                       # Lógica de negocio
│   │   ├── config.py              # Gestión de configuración
│   │   ├── iptv.py                # Parseo de M3U
│   │   ├── iptv_refresher.py     # Actualización de canales
│   │   ├── local_media.py         # Escaneo de películas
│   │   ├── player.py              # Interfaz con MPV
│   │   ├── progress.py            # Guardar/reanudar películas
│   │   ├── radio.py               # Gestión de radios
│   │   ├── tmdb.py                # API de The Movie Database
│   │   └── vpn.py                 # Control de NordVPN
│   │
│   └── ui/                         # Interfaz de usuario (Textual)
│       ├── screens/               # Pantallas de la aplicación
│       │   ├── movie_list_screen.py
│       │   ├── movie_detail_screen.py
│       │   ├── iptv_list_screen.py
│       │   ├── m3u_list_screen.py
│       │   ├── now_playing_screen.py
│       │   ├── radio_manager_screen.py
│       │   ├── settings_screen.py
│       │   └── ...
│       └── widgets/               # Componentes reutilizables
```

---

## 🔧 Configuración avanzada

### Formato del archivo `config.ini`

```ini
[PATHS]
local_media_path = ./Peliculas/
iptv_folder_path = ./Archivos M3U/
radio_file_path = radios.json

[VPN]
enabled_for_iptv = no
country = Spain
username = tu_usuario_vpn
password = tu_password_vpn

[IPTV]
source_url = https://tu-proveedor.com/lista.m3u

[TMDB]
api_key = tu_api_key_de_tmdb
```

### Formato del archivo `radios.json`

```json
[
  {
    "name": "Radio Nacional",
    "url": "https://radio.example.com/stream.mp3"
  },
  {
    "name": "Radio Clásica",
    "url": "https://clasica.example.com/live"
  }
]
```

---

## 🐛 Solución de problemas

### MPV no se encuentra
```bash
# Verifica que mpv esté instalado
which mpv

# Si no está, instálalo
sudo apt install mpv
```

### La VPN no se conecta
- Verifica que NordVPN esté instalado: `nordvpn --version`
- Asegúrate de haber iniciado sesión: `nordvpn login`
- Comprueba tus credenciales en `config.ini`

### Las películas no se muestran
- Verifica la ruta en Configuración
- Asegúrate de que la carpeta contenga archivos de video
- Formatos soportados: `.mp4`, `.mkv`, `.avi`, `.mov`, etc.

### No aparece información de películas
- Verifica que hayas configurado la API Key de TMDB
- Comprueba tu conexión a internet
- Los nombres de archivo muy modificados pueden no encontrarse

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si quieres mejorar el proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/MiFeature`)
3. Commit tus cambios (`git commit -m 'Añadir MiFeature'`)
4. Push a la rama (`git push origin feature/MiFeature`)
5. Abre un Pull Request

---

## 📝 TODO / Roadmap

- [ ] Soporte para portadas de películas en la UI
- [ ] Sistema de favoritos para canales IPTV
- [ ] Subtítulos automáticos
- [ ] Integración con Trakt.tv
- [ ] Control remoto desde móvil
- [ ] Soporte para múltiples perfiles de usuario
- [ ] Scraping de EPG para guía de canales

---

## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

## 👏 Créditos

- **Textual**: Framework TUI por [Textualize](https://github.com/Textualize/textual)
- **MPV**: Reproductor multimedia por [mpv.io](https://mpv.io/)
- **TMDB**: API de películas por [The Movie Database](https://www.themoviedb.org/)
- **NordVPN Switcher**: Por [kl4mm](https://github.com/kl4mm/NordVPN-switcher)

---

## 📧 Contacto

¿Preguntas? ¿Sugerencias? ¿Encontraste un bug?

- Abre un [Issue](https://github.com/tuusuario/RaspIPTV/issues)
- Envía un [Pull Request](https://github.com/tuusuario/RaspIPTV/pulls)

---

<div align="center">
  
**Hecho con ❤️ para la comunidad Raspberry Pi**

⭐ Si te gusta el proyecto, ¡dale una estrella!

</div>
