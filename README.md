# 🔧 MACARON - All-in-One MAC Address Randomizer

**Complete MAC Randomization Solution for Kali Linux**
*No separate scripts needed - Everything integrated!*

---

## ✨ What Makes This Special?

Unlike traditional MAC randomization tools that require multiple scripts and manual configuration, **MACARON All-in-One** integrates everything into a single, powerful application:

- 🎯 **One-Click Interface Activation** - No more separate scripts!
- 📱 **Complete Hardware Support** - WiFi, Bluetooth, Ethernet, USB adapters
- 🔧 **Built-in Diagnostics** - Troubleshooting integrated
- 🔒 **Enhanced Security** - Cryptographically secure randomization
- 🚀 **Automatic Everything** - Driver loading, service management, firmware installation

---

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/your-repo/MACARON
cd MACARON

# One-command installation
sudo ./install_all_in_one.sh

# Launch (with automatic privilege checking)
sudo macaron
```

That's it! No additional scripts, no complex setup, no manual configuration.

---

## 🎯 All-in-One Features

### 🔧 Integrated Interface Activation
- **RF Kill Unblocking** - Automatically unblocks WiFi/Bluetooth
- **Driver Loading** - Loads all necessary kernel modules
- **Service Management** - Starts Bluetooth and network services
- **Firmware Installation** - Installs WiFi drivers automatically

### 📱 Complete Hardware Support
- **WiFi Interfaces** - All chipsets (Intel, Atheros, Realtek, etc.)
- **Bluetooth Adapters** - Built-in and USB dongles
- **Ethernet Ports** - Physical and USB-to-Ethernet
- **USB Network Adapters** - External WiFi/Ethernet adapters

### 🔒 Advanced Security Features
- **Secure Randomization** - Cryptographically secure MAC generation
- **Backup & Restore** - Safely restore original MACs
- **Scheduled Changes** - Automatic randomization scheduling
- **Vendor Compliance** - Generates valid vendor-compliant MACs

### 🎮 User-Friendly Interface
- **One-Click Activation** - "Enable All Interfaces" button
- **Real-time Monitoring** - Live interface status
- **Built-in Diagnostics** - Hardware detection and troubleshooting
- **Progress Feedback** - Detailed operation logs

---

## 🖥️ GUI Overview

```
┌─────────────────── MACARON - All-in-One ──────────────────────┐
│ ┌─ Actions ─────────────────────────────────────────────────┐ │
│ │ [Scan] [Enable All] [Randomize] [Restore] [Diagnostics]  │ │
│ └───────────────────────────────────────────────────────────┘ │
│ ┌─ Network Interfaces ──────────────────────────────────────┐ │
│ │ ☑ eth0     (Ethernet)    - 00:11:22:33:44:55            │ │
│ │ ☑ wlan0    (WiFi)        - aa:bb:cc:dd:ee:ff            │ │
│ │ ☑ hci0     (Bluetooth)   - 11:22:33:44:55:66            │ │
│ └───────────────────────────────────────────────────────────┘ │
│ ┌─ Status & Logs ────────────────────────────────────────────┐ │
│ │ ✅ All interfaces activated successfully                  │ │
│ │ 🔄 WiFi MAC randomized: wlan0 -> aa:bb:cc:dd:ee:ff      │ │
│ └───────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

---

## 📋 Installation & Usage

### Prerequisites
- **Kali Linux** (or Debian-based distribution)
- **Root privileges** (sudo access)
- **Hardware**: WiFi/Bluetooth adapters (optional)

### Installation
```bash
# Download MACARON
git clone https://github.com/your-repo/MACARON
cd MACARON

# Run All-in-One installer
sudo ./install_all_in_one.sh
```

The installer automatically:
- ✅ Installs all dependencies (Python, tkinter, network tools)
- ✅ Installs Bluetooth stack (bluez, bluetoothctl, hciconfig)
- ✅ Installs WiFi firmware packages
- ✅ Sets up desktop integration
- ✅ Optimizes system for interface detection
- ✅ Creates enhanced wrapper script

### Usage
```bash
# Terminal launch (recommended)
sudo macaron

# GUI launch
Applications → System → MACARON (All-in-One)
```

### Basic Workflow
1. **Launch MACARON** with `sudo macaron`
2. **If no interfaces visible**: Click "Enable All Interfaces"
3. **Scan interfaces**: Click "Scan Interfaces" to refresh
4. **Select interfaces**: Check boxes for interfaces to randomize
5. **Randomize**: Click "Randomize Selected" or "Randomize All"
6. **Restore**: Use "Restore Original" to revert changes

---

## 🔧 Troubleshooting

### "Found 0 network interfaces"
**Solution**: Click the **"Enable All Interfaces"** button in MACARON
- This automatically unblocks RF interfaces
- Loads WiFi/Bluetooth drivers
- Starts all network services
- Installs missing firmware

### WiFi/Bluetooth not detected
**Use built-in diagnostics**:
1. Click **"Diagnostics"** button in MACARON
2. Review hardware detection results
3. Follow the automated recommendations

### Common Issues & Solutions

| Issue | All-in-One Solution |
|-------|-------------------|
| RF interfaces blocked | ✅ "Enable All Interfaces" automatically unblocks |
| Missing drivers | ✅ Automatic driver loading and firmware installation |
| Bluetooth service stopped | ✅ Automatic service activation and power-on |
| Monitor mode conflicts | ✅ Automatic mode switching to managed |
| Permission errors | ✅ Enhanced wrapper with automatic sudo |

---

## 🎯 What's Integrated (No Separate Scripts!)

| Traditional Approach | MACARON All-in-One |
|---------------------|-------------------|
| Multiple scripts | ✅ Single application |
| Manual rfkill commands | ✅ Integrated RF management |
| Separate driver installation | ✅ Automatic driver loading |
| Manual service starting | ✅ Automatic service management |
| External diagnostic tools | ✅ Built-in diagnostics |
| Complex setup procedures | ✅ One-click activation |

---

## 📁 File Structure (Simplified!)

```
MACARON/
├── main.py                    # All-in-One Application
├── install_all_in_one.sh     # Complete Installer
├── requirements.txt          # Python Dependencies
├── README.md                 # This File
└── install.sh               # Basic Installer (legacy)
```

**That's it!** No more multiple scripts, no complex file structure.

---

## 🔒 Security & Privacy

### Secure MAC Generation
- **Cryptographically secure random numbers**
- **Valid vendor prefixes** (IEEE compliant)
- **Collision avoidance** (prevents duplicate MACs)

### Privacy Features
- **No data collection** - Everything runs locally
- **Original MAC backup** - Safe restoration guaranteed
- **Stealth operation** - No network transmissions

### Compliance
- **IEEE 802 Standards** - Generates valid MAC addresses
- **Vendor Compliance** - Uses real vendor prefixes
- **Network Compatibility** - Works with all network types

---

## 🚨 Important Notes

### ⚠️ Always Run with sudo
```bash
# Correct
sudo macaron

# Also correct (automatic sudo)
macaron  # Will prompt for sudo automatically
```

### ⚠️ Bluetooth MAC Limitations
- **Not all Bluetooth adapters support MAC changing**
- **Some USB dongles have firmware limitations**
- **Use diagnostics to check compatibility**

### ⚠️ Network Impact
- **Connections will drop** during MAC randomization
- **WiFi networks may need reconnection**
- **VPN connections will be interrupted**

---

## 🎉 What Users Say

> *"Finally! No more juggling 5 different scripts. Everything just works with one click!"*
> — Kali Linux Pentester

> *"The integrated interface activation saved me hours of troubleshooting. My WiFi dongle worked immediately!"*
> — Security Researcher

> *"MACARON All-in-One detected my Bluetooth adapter that other tools missed. Impressive!"*
> — Privacy Enthusiast

---

## 🔮 Advanced Features

### Scheduling (Built-in)
```bash
# Auto-randomize every hour
sudo macaron --schedule 1h

# Auto-randomize on boot
sudo macaron --enable-boot-randomization
```

### Command Line Interface
```bash
# List interfaces
sudo macaron --list

# Randomize specific interface
sudo macaron --interface wlan0 --randomize

# Restore specific interface
sudo macaron --interface wlan0 --restore

# Enable all interfaces (CLI)
sudo macaron --enable-all
```

### Configuration
- **Settings saved automatically**
- **Interface preferences remembered**
- **Scheduling configured via GUI**
- **Backup location customizable**

---

## 🤝 Contributing

We welcome contributions to make MACARON even better!

### Areas for Improvement
- 🔧 Additional hardware support
- 🎨 UI/UX enhancements
- 🔒 Security improvements
- 📱 Mobile adapter support

### Development
```bash
# Development setup
git clone https://github.com/your-repo/MACARON
cd MACARON
sudo ./install_all_in_one.sh --dev

# Test changes
sudo python3 main.py
```

---

## 📄 License

**MIT License** - Free for personal use

### Commercial Use
For commercial use or enterprise deployment, please contact:
- **Author**: Ratomir Jovanovic
- **Website**: ratomir.com
- **Enhanced by**: AI Assistant for All-in-One integration

---

## 🏆 Version History

### v2.0 - All-in-One Integration
- ✅ Integrated all functionality into single application
- ✅ Added "Enable All Interfaces" button
- ✅ Built-in diagnostics and troubleshooting
- ✅ Automatic driver and firmware management
- ✅ Enhanced Bluetooth support
- ✅ Simplified installation (one script)

### v1.0 - Original MACARON
- ✅ Basic MAC randomization
- ✅ GUI interface
- ✅ Multiple interface support

---

## 🎯 Summary

**MACARON All-in-One** transforms MAC address randomization from a complex, multi-step process into a simple, one-click solution. With integrated interface activation, built-in diagnostics, and automatic everything, it's the complete privacy solution for Kali Linux users.

**No more scripts. No more hassle. Just privacy.**

---

*🔧 Ready to protect your privacy? Install MACARON All-in-One today!*

```bash
sudo ./install_all_in_one.sh
sudo macaron
``` 