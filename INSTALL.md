# MACARON - Installation Guide

**Author:** Ratomir Jovanovic  
**Website:** [ratomir.com](https://ratomir.com)  
**Version:** 1.0  
**License:** MIT (Personal Use) / Commercial License Required for Business Use

## 🚀 Installation Methods

MACARON offers multiple installation methods to suit different preferences and system configurations.

### Method 1: Automated Installer (Recommended)

The easiest way to install MACARON with full system integration:

```bash
# Make installer executable
chmod +x install.sh

# Run installer (requires root privileges)
sudo ./install.sh
```

**What this does:**
- ✅ Checks and installs all dependencies automatically
- ✅ Installs MACARON to standard system directories
- ✅ Creates command-line tools (`macaron`, `macaron-test`)
- ✅ Installs manual pages (`man macaron`)
- ✅ Sets up desktop integration (Applications menu)
- ✅ Creates uninstaller for easy removal

**After installation, run:**
```bash
sudo macaron          # Launch GUI application
man macaron           # View manual page
macaron-test          # Run test suite
```

### Method 2: Makefile Installation

For users who prefer traditional Unix-style installation:

```bash
# Install using Makefile
sudo make install

# Check installation status
make status

# Run tests
make test

# Uninstall
sudo make uninstall
```

**Makefile targets:**
- `make install` - Install MACARON system-wide
- `make uninstall` - Remove MACARON from system
- `make test` - Run comprehensive test suite
- `make clean` - Clean temporary files
- `make package` - Create distribution package
- `make status` - Check installation status

### Method 3: Manual Installation

For advanced users or custom setups:

```bash
# Copy files to desired location
sudo cp main.py /usr/local/bin/
sudo chmod +x /usr/local/bin/main.py

# Run directly
sudo python3 /usr/local/bin/main.py
```

### Method 4: In-Place Execution

Run MACARON directly from source directory:

```bash
# Using the launcher script
chmod +x macaron.sh
./macaron.sh

# Or directly with Python
sudo python3 main.py
```

## 📋 System Requirements

### Operating System
- **Linux** (any modern distribution)
  - Ubuntu 18.04+ / Debian 10+
  - CentOS 8+ / RHEL 8+ / Fedora 30+
  - Arch Linux / Manjaro
  - openSUSE / SUSE Linux
  - And other Linux distributions

### Software Dependencies
- **Python 3.6+** (required)
- **python3-tk** (tkinter GUI framework)
- **iproute2** (network interface management)
- **Root privileges** (sudo access required)

### Hardware Requirements
- **RAM:** 50MB minimum
- **Storage:** 10MB disk space
- **Network:** At least one network interface

## 🔧 Dependency Installation

### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install python3 python3-tk iproute2
```

### CentOS/RHEL/Fedora:
```bash
# CentOS/RHEL
sudo yum install python3 python3-tkinter iproute2

# Fedora
sudo dnf install python3 python3-tkinter iproute2
```

### Arch Linux:
```bash
sudo pacman -S python tk iproute2
```

### openSUSE:
```bash
sudo zypper install python3 python3-tk iproute2
```

## 📦 Package Installation (Future)

**Debian/Ubuntu (.deb packages):**
```bash
# Will be available in future releases
sudo dpkg -i macaron_1.0_all.deb
sudo apt-get install -f  # Fix dependencies if needed
```

**RedHat/CentOS/Fedora (.rpm packages):**
```bash
# Will be available in future releases
sudo rpm -ivh macaron-1.0-1.noarch.rpm
# or
sudo dnf install macaron-1.0-1.noarch.rpm
```

## ✅ Post-Installation Verification

After installation, verify MACARON is working correctly:

### 1. Check Installation
```bash
# Check if command is available
which macaron
# Output: /usr/local/bin/macaron

# Check version and help
macaron --help  # Should show usage information
```

### 2. Verify Dependencies
```bash
# Run dependency check
macaron-test --check
# or
python3 -c "import tkinter; import subprocess; print('Dependencies OK')"
```

### 3. Run Test Suite
```bash
# Run comprehensive tests (as root)
sudo macaron-test
```

### 4. First Launch
```bash
# Launch MACARON GUI
sudo macaron
```

## 🔒 Security Considerations

### Root Privileges
MACARON requires root privileges to modify MAC addresses. This is a Linux kernel requirement, not a limitation of MACARON.

**Always run with sudo:**
```bash
sudo macaron        # Correct
macaron            # Will fail with permission error
```

### File Permissions
The installer automatically sets secure permissions:
- Application files: 755 (executable by all, writable by root)
- Log files: 600 (readable/writable by root only)
- Configuration: 644 (readable by all, writable by root)

## 🗑️ Uninstallation

### Using Installer
```bash
# Run the uninstaller created during installation
sudo /usr/local/share/macaron/uninstall.sh
```

### Using Makefile
```bash
sudo make uninstall
```

### Manual Removal
```bash
# Remove all MACARON files
sudo rm -f /usr/local/bin/macaron
sudo rm -f /usr/local/bin/macaron-test
sudo rm -rf /usr/local/share/macaron
sudo rm -rf /usr/local/share/doc/macaron
sudo rm -f /usr/local/share/man/man1/macaron.1.gz
sudo rm -f /usr/share/applications/macaron.desktop

# Update desktop database
sudo update-desktop-database /usr/share/applications
```

## 🚨 Troubleshooting

### Common Issues

**Permission Denied:**
```bash
# Ensure you're running with sudo
sudo macaron
```

**Python 3 Not Found:**
```bash
# Install Python 3
sudo apt install python3  # Ubuntu/Debian
sudo yum install python3  # CentOS/RHEL
```

**tkinter Not Available:**
```bash
# Install tkinter
sudo apt install python3-tk  # Ubuntu/Debian
sudo yum install python3-tkinter  # CentOS/RHEL
```

**iproute2 Not Found:**
```bash
# Install iproute2
sudo apt install iproute2  # Most distributions
```

**GUI Not Displaying:**
```bash
# Check X11 forwarding (if using SSH)
ssh -X username@hostname

# Check DISPLAY variable
echo $DISPLAY

# Install X11 packages if needed
sudo apt install xorg  # Ubuntu/Debian
```

### Log Files

Check MACARON logs for detailed error information:
```bash
# View current session logs
tail -f macaron.log

# View all logs
cat macaron.log
```

### System Compatibility

MACARON has been tested on:
- ✅ Ubuntu 20.04, 22.04
- ✅ Debian 11, 12
- ✅ CentOS 8, 9
- ✅ Fedora 35, 36, 37
- ✅ Arch Linux (latest)
- ✅ openSUSE Leap 15.4

## 📞 Support

For installation issues:

1. **Check system requirements** above
2. **Run dependency check:** `macaron-test --check`
3. **Check logs:** `cat macaron.log`
4. **Verify permissions:** Ensure running with `sudo`
5. **Consult documentation:** `man macaron`

## 🎯 Next Steps

After successful installation:

1. **Read the manual:** `man macaron`
2. **Run tests:** `sudo macaron-test`
3. **Launch MACARON:** `sudo macaron`
4. **Scan interfaces:** Click "Scan Interfaces" in the GUI
5. **Test randomization:** Select interfaces and click "Randomize Selected"

---

**MACARON is now ready to enhance your privacy and security!** 