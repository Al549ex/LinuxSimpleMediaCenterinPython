# RaspIPTV - Media Center for Raspberry Pi

A lightweight, terminal-based media center application for Raspberry Pi with support for local media, IPTV streaming, internet radio, and VPN integration.

## ✨ Features

- 🎬 **Local Media Player**: Browse and play movies from local storage
- 📺 **IPTV Streaming**: M3U playlist support with group organization
- 📻 **Internet Radio**: Manage and play radio stations
- 🔒 **VPN Integration**: Automatic NordVPN connection with token or QR authentication
- 🎨 **Modern TUI**: Built with Textual framework for sleek terminal experience
- 🎯 **TMDb Integration**: Fetch movie metadata and posters (optional)
- ⚡ **Optimized**: Hardware acceleration support for Raspberry Pi

## 📋 Requirements

- Raspberry Pi 3 or higher (recommended)
- Raspberry Pi OS or Debian-based Linux
- Python 3.9+
- MPV media player
- NordVPN CLI (optional, for VPN features)

## 🚀 Quick Start

```bash
# Install system dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip mpv -y

# Clone repository
git clone https://github.com/Al549ex/LinuxSimpleMediaCenterinPython.git
cd LinuxSimpleMediaCenterinPython

# Install Python dependencies
pip3 install -r requirements.txt

# Configure
cp config.ini.example config.ini
nano config.ini

# Run
python3 run.py
```

## 🔐 NordVPN Authentication

### Method 1: Access Token (Recommended) ⭐

**Why use tokens?**
- ✅ Instant authentication - No waiting or QR scanning
- ✅ More reliable - No process synchronization issues
- ✅ Secure - Revocable tokens, no passwords stored
- ✅ Automated - Perfect for headless setups

**Setup:**
1. Get your token: https://my.nordaccount.com/dashboard/nordvpn/access-tokens
2. Add to `config.ini`:
   ```ini
   [VPN]
   access_token = YOUR_TOKEN_HERE
   ```
3. Click "🔐 Authenticate NordVPN" in Settings
4. Done! Instant auth ✨

See [NORDVPN_TOKEN_SETUP.md](NORDVPN_TOKEN_SETUP.md) for detailed instructions.

### Method 2: QR Code (Fallback)

If no token is configured:
1. Click "🔐 Authenticate NordVPN" in Settings
2. Scan QR code with your phone
3. Login in browser
4. App auto-detects (checks every 5s)

## ⚙️ Configuration

### Basic Setup

```ini
[PATHS]
local_media_path = /home/pi/Movies/
iptv_folder_path = /home/pi/M3U/
radio_file_path = radios.json

[VPN]
enabled_for_iptv = yes
country = Spain
access_token = YOUR_TOKEN_HERE

[IPTV]
source_url = https://provider.com/playlist.m3u

[TMDB]
api_key = YOUR_TMDB_KEY
```

### VPN Configuration

**NordVPN CLI Installation:**
```bash
sh <(curl -sSf https://downloads.nordcdn.com/apps/linux/install.sh)

# Recommended: Use NordLynx (faster)
nordvpn set technology nordlynx
```

**Get Access Token:**
- Visit: https://my.nordaccount.com/dashboard/nordvpn/access-tokens
- Generate new token
- Copy to `config.ini`

### TMDb API (Optional)

Get free API key at: https://www.themoviedb.org/settings/api

## 🎮 Usage

### Launch Application
```bash
python3 run.py
```

### Navigation
- **Arrow keys**: Navigate menus
- **Enter**: Select item
- **Escape/Q**: Back/Quit
- **Tab**: Switch UI elements

### Main Menu
1. **Local Movies** - Browse local media
2. **IPTV** - Browse M3U playlists
3. **Radio** - Manage radio stations
4. **Settings** - Configure app & VPN

## 📁 Project Structure

```
RaspIPTV/
├── app/
│   ├── core/              # Core functionality
│   │   ├── config.py      # Configuration manager
│   │   ├── vpn.py         # NordVPN integration
│   │   ├── player.py      # MPV wrapper
│   │   ├── iptv.py        # M3U parser
│   │   ├── radio.py       # Radio manager
│   │   └── tmdb.py        # TMDb API client
│   └── ui/                # User interface
│       ├── app_main.py    # Main app
│       └── screens/       # UI screens
├── config.ini             # Your config (gitignored)
├── config.ini.example     # Example configuration
├── radios.json            # Radio database
├── requirements.txt       # Python dependencies
└── run.py                 # Entry point
```

## 🛠️ Troubleshooting

### VPN Issues

**NordVPN CLI not installed:**
```bash
sh <(curl -sSf https://downloads.nordcdn.com/apps/linux/install.sh)
```

**Token invalid/expired:**
```bash
# Generate new token at my.nordaccount.com
# Update config.ini
```

**Check VPN status:**
```bash
nordvpn status
nordvpn account
```

**Reset authentication:**
```bash
nordvpn logout
# Then use app to re-authenticate
```

### Playback Issues

**No video/audio:**
```bash
# Test MPV
mpv --version
mpv /path/to/video.mp4
```

**Choppy playback:**
- Enable hardware acceleration (auto-enabled)
- Check network speed for streams
- Reduce video quality

### General Issues

**Missing dependencies:**
```bash
pip3 install -r requirements.txt --upgrade
```

**Permission errors:**
```bash
chmod +x run.py
```

## 📝 Adding Content

### Radio Stations (UI)
1. Radio → Manage Radios → Add Radio
2. Enter name and stream URL
3. Save

### Radio Stations (JSON)
Edit `radios.json`:
```json
[
  {
    "name": "Station Name",
    "url": "http://stream-url.com:8000/live"
  }
]
```

### Local Movies
Place video files in configured `local_media_path`

Supported formats: `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`, `.m4v`

### IPTV Playlists
Place `.m3u` files in configured `iptv_folder_path`

## 🎯 Performance Tips

1. **Hardware acceleration**: Automatically configured for RPi
2. **Use NordLynx**: Faster than OpenVPN
   ```bash
   nordvpn set technology nordlynx
   ```
3. **Wired connection**: Ethernet > WiFi for streaming
4. **Optimize buffer**: Auto-configured for smooth playback

## 🔧 Advanced

### Custom MPV Configuration
Edit `app/core/player.py` to customize MPV parameters

### Network Optimization
```bash
# Set DNS
nordvpn set dns 1.1.1.1 1.0.0.1

# Enable kill switch
nordvpn set killswitch on

# Auto-connect
nordvpn set autoconnect on
```

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs via GitHub Issues
- Suggest features
- Submit pull requests

## 📄 License

See [LICENSE](LICENSE) file for details.

## 🔗 Links

- **GitHub**: https://github.com/Al549ex/LinuxSimpleMediaCenterinPython
- **NordVPN**: https://nordvpn.com
- **TMDb**: https://www.themoviedb.org
- **Textual**: https://textual.textualize.io

## 📞 Support

- GitHub Issues: Report bugs and request features
- [NORDVPN_TOKEN_SETUP.md](NORDVPN_TOKEN_SETUP.md) - Token authentication guide
- [NORDVPN_SETUP.md](NORDVPN_SETUP.md) - Initial VPN setup

## 🎉 Built With

- **Textual** - Modern terminal UI framework
- **MPV** - Powerful media player
- **NordVPN** - VPN service
- **TMDb** - Movie database API
- **Python 3.9+** - Programming language

---

**Made with ❤️ for Raspberry Pi enthusiasts**

*Enjoy your media center! 🍿*
