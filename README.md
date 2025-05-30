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
git clone https://github.com/ratomirjovanovic/macaron
cd macaron

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
git clone https://github.com/ratomirjovanovic/macaron
cd macaron

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
└── test_all_in_one.py       # Comprehensive Test Suite
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
- **Local Use Only** - No external dependencies
- **Open Source** - Full code transparency

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
```bash
git clone https://github.com/ratomirjovanovic/macaron
cd macaron
pip install -r requirements.txt
python test_all_in_one.py  # Run tests
```

---

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## ⚠️ Legal Disclaimer

This software is designed to modify network interface MAC addresses for privacy enhancement purposes. Users are solely responsible for:

1. Ensuring compliance with local laws and regulations
2. Understanding and respecting network policies  
3. Using the software only on systems they own or have explicit permission to modify
4. Any consequences resulting from the use of this software

Use at your own risk and responsibility.

---

## 🏆 Project Status

**✅ Ready for Production** - All features integrated and tested!

- 🔧 **100% All-in-One** - No separate scripts required
- 🧪 **Fully Tested** - Comprehensive test suite included
- 📱 **Multi-Platform** - Works on all Linux distributions
- 🔒 **Secure** - Cryptographically secure randomization
- 🎯 **User-Friendly** - One-click interface activation

---

**Made with ❤️ for network privacy and security**
