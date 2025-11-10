# 🎬 RaspIPTV Media Center

A complete media center optimized for **Raspberry Pi 4**, built with Python and Textual. Play local movies, IPTV with VPN integration, streaming radio and more.

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%204-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## ✨ Features

### 🎥 Movie Library
- **TMDB Integration**: Automatic movie information lookup
- **Complete Details**: Synopsis, cast, director, genres, ratings
- **Save and Resume**: Pick up where you left off
- **Elegant Interface**: Library-style design with all information

### 📺 IPTV
- **Channel Playback**: Support for `.m3u` files
- **Automatic Updates**: Downloads and splits IPTV lists by groups
- **VPN Integration**: Automatically connects to NordVPN for streaming
- **Smart Management**: Alphabetical organization of channel groups

### 📻 Streaming Radio
- **Background Playback**: Listen to radio while watching IPTV
- **Station Management**: Add, remove and organize your favorite stations
- **Full Controls**: Pause/resume from any screen
- **Smart Muting**: Video audio mutes automatically

### 🔐 VPN
- **NordVPN Integration**: Automatic connection/disconnection
- **Configurable**: Enable/disable VPN for IPTV from settings
- **Smart Management**: Only connects when needed

### ⚙️ Settings
- **Graphical Interface**: Everything configurable from the app
- **Path Validation**: Verifies and creates directories automatically
- **Persistence**: Configuration saved in `config.ini`

---

## 🚀 Installation

### Prerequisites
- **Raspberry Pi 4** (recommended) or any Linux/macOS system
- **Python 3.9+**
- **mpv** (media player)
- **NordVPN** installed (optional, only for VPN features)

### 1. Install MPV

**On Raspberry Pi / Debian / Ubuntu:**
```bash
sudo apt update
sudo apt install mpv
```

**On macOS:**
```bash
brew install mpv
```

### 2. Clone the repository

```bash
git clone https://github.com/yourusername/RaspIPTV.git
cd RaspIPTV
```

### 3. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Initial configuration

Copy the example configuration file:
```bash
cp config.ini.example config.ini
```

Edit `config.ini` or use the app's graphical interface to configure:
- Movie and M3U file paths
- VPN credentials (if using NordVPN)
- TMDB API Key (optional, for movie information)

---

## 🎮 Usage

### Start the application

```bash
python3 run.py
```

### Get TMDB API Key (optional but recommended)

1. Go to [https://www.themoviedb.org/](https://www.themoviedb.org/)
2. Create a free account
3. Go to **Settings → API**
4. Request an API Key (instant approval)
5. Copy your **API Key (v3 auth)**
6. Paste it in the app: **Settings → TMDB API Key**

### Expected file structure

```
RaspIPTV/
├── run.py                 # Main file
├── config.ini             # Configuration (auto-created)
├── radios.json            # Radio list (auto-created)
├── Movies/                # Movies folder (configurable)
│   ├── movie1.mp4
│   ├── movie2.mkv
│   └── ...
├── M3U Files/             # IPTV lists folder (configurable)
│   ├── sports.m3u
│   ├── news.m3u
│   └── ...
└── app/                   # Source code
```

---

## 🎯 Navigation

### Main Menu
- **Watch Movies (Local)**: Access your movie library
- **IPTV**: Browse your TV channels
- **Update IPTV Channels**: Download and update your IPTV list
- **Manage Radio Stations**: Add/remove radio stations
- **Settings**: Adjust all options

### Keyboard shortcuts
- `q` or `Ctrl+C`: Exit current screen
- `Esc`: Go back
- `Tab`: Navigate between elements
- `Enter`: Select

---

## 🛠️ Raspberry Pi 4 Optimizations

The project is specifically optimized to run on Raspberry Pi 4:

### MPV Player
- **Hardware decoding**: `--hwdec=rpi-copy`
- **Optimized GPU**: `--vo=gpu --gpu-context=drm`
- **Smart cache**: 50MB buffer for streaming
- **Low power profile**: `--profile=fast`

### Python Code
- **Async workers**: Heavy operations in separate threads
- **Data caching**: Reduces repetitive lookups
- **Compiled regular expressions**: Ultra-fast M3U parsing
- **Efficient memory management**: Proper resource cleanup

---

## 📁 Project structure

```
RaspIPTV/
├── run.py                          # Entry point
├── requirements.txt                # Python dependencies
├── config.ini                      # Configuration (gitignored)
├── README.md                       # This file
│
├── app/
│   ├── core/                       # Business logic
│   │   ├── config.py              # Configuration management
│   │   ├── iptv.py                # M3U parsing
│   │   ├── iptv_refresher.py     # Channel updates
│   │   ├── local_media.py         # Movie scanning
│   │   ├── player.py              # MPV interface
│   │   ├── progress.py            # Save/resume movies
│   │   ├── radio.py               # Radio management
│   │   ├── tmdb.py                # The Movie Database API
│   │   └── vpn.py                 # NordVPN control
│   │
│   └── ui/                         # User interface (Textual)
│       ├── screens/               # Application screens
│       │   ├── movie_list_screen.py
│       │   ├── movie_detail_screen.py
│       │   ├── iptv_list_screen.py
│       │   ├── m3u_list_screen.py
│       │   ├── now_playing_screen.py
│       │   ├── radio_manager_screen.py
│       │   ├── settings_screen.py
│       │   └── ...
│       └── widgets/               # Reusable components
```

---

## 🔧 Advanced configuration

### `config.ini` file format

```ini
[PATHS]
local_media_path = ./Movies/
iptv_folder_path = ./M3U Files/
radio_file_path = radios.json

[VPN]
enabled_for_iptv = no
country = Spain
username = your_vpn_username
password = your_vpn_password

[IPTV]
source_url = https://your-provider.com/list.m3u

[TMDB]
api_key = your_tmdb_api_key
```

### `radios.json` file format

```json
[
  {
    "name": "National Radio",
    "url": "https://radio.example.com/stream.mp3"
  },
  {
    "name": "Classical Radio",
    "url": "https://clasica.example.com/live"
  }
]
```

---

## 🐛 Troubleshooting

### MPV not found
```bash
# Verify mpv is installed
which mpv

# If not installed, install it
sudo apt install mpv
```

### VPN won't connect
- Verify NordVPN is installed: `nordvpn --version`
- Make sure you're logged in: `nordvpn login`
- Check your credentials in `config.ini`

### Movies don't show up
- Verify the path in Settings
- Make sure the folder contains video files
- Supported formats: `.mp4`, `.mkv`, `.avi`, `.mov`, etc.

### Movie information doesn't appear
- Verify you've configured the TMDB API Key
- Check your internet connection
- Heavily modified filenames may not be found

---

## 🤝 Contributing

Contributions are welcome! If you want to improve the project:

1. Fork the repository
2. Create a branch for your feature (`git checkout -b feature/MyFeature`)
3. Commit your changes (`git commit -m 'Add MyFeature'`)
4. Push to the branch (`git push origin feature/MyFeature`)
5. Open a Pull Request

---

## 📝 TODO / Roadmap

- [ ] Support for movie posters in the UI
- [ ] Favorites system for IPTV channels
- [ ] Automatic subtitles
- [ ] Trakt.tv integration
- [ ] Mobile remote control
- [ ] Multiple user profiles support
- [ ] EPG scraping for channel guide

---

## 📜 License

This project is under the MIT License. See the `LICENSE` file for more details.

---

## 👏 Credits

- **Textual**: TUI Framework by [Textualize](https://github.com/Textualize/textual)
- **MPV**: Media player by [mpv.io](https://mpv.io/)
- **TMDB**: Movie API by [The Movie Database](https://www.themoviedb.org/)
- **NordVPN Switcher**: By [kl4mm](https://github.com/kl4mm/NordVPN-switcher)

---

## 📧 Contact

Questions? Suggestions? Found a bug?

- Open an [Issue](https://github.com/yourusername/RaspIPTV/issues)
- Send a [Pull Request](https://github.com/yourusername/RaspIPTV/pulls)

---

<div align="center">
  
**Made with ❤️ for the Raspberry Pi community**

⭐ If you like the project, give it a star!

</div>
