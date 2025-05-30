#!/bin/bash

# ALL-IN-ONE MACARON INSTALLER for Kali Linux
# Complete MAC Address Randomization Solution
# No separate scripts needed - everything integrated!

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_header() {
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                ALL-IN-ONE MACARON INSTALLER                  ║${NC}"
    echo -e "${CYAN}║            Complete MAC Randomization Solution              ║${NC}"
    echo -e "${CYAN}║                                                              ║${NC}"
    echo -e "${CYAN}║  🔧 Integrated interface activation                         ║${NC}"
    echo -e "${CYAN}║  📱 WiFi, Bluetooth, Ethernet support                      ║${NC}"
    echo -e "${CYAN}║  🔒 Enhanced security and privacy                          ║${NC}"
    echo -e "${CYAN}║  🎯 One-click solution for Kali Linux                     ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${PURPLE}✨ NO SEPARATE SCRIPTS NEEDED - EVERYTHING IS INTEGRATED! ✨${NC}"
    echo ""
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This installer must be run as root (use sudo)"
        print_status "Usage: sudo ./install_all_in_one.sh"
        exit 1
    fi
}

# Install all dependencies
install_dependencies() {
    print_status "Installing ALL required dependencies..."
    
    # Update package list
    apt update -y
    
    # Core Python dependencies
    print_status "Installing Python and GUI components..."
    apt install -y python3 python3-tk python3-pip iproute2
    print_success "✅ Python and GUI components installed"
    
    # Network tools
    print_status "Installing network management tools..."
    apt install -y net-tools wireless-tools rfkill
    print_success "✅ Network tools installed"
    
    # Bluetooth complete stack
    print_status "Installing Bluetooth stack..."
    apt install -y bluez bluetooth bluez-tools
    print_success "✅ Bluetooth stack installed"
    
    # Hardware detection tools
    print_status "Installing hardware detection tools..."
    apt install -y pciutils usbutils
    print_success "✅ Hardware detection tools installed"
    
    # WiFi firmware packages
    print_status "Installing WiFi firmware packages..."
    firmware_packages=("firmware-linux-nonfree" "firmware-realtek" "firmware-atheros" "firmware-intel-sound")
    for package in "${firmware_packages[@]}"; do
        if apt search "$package" 2>/dev/null | grep -q "$package"; then
            apt install -y "$package" 2>/dev/null && print_success "✅ $package installed" || print_warning "⚠️ Could not install $package"
        fi
    done
    
    # Optional advanced tools
    print_status "Installing advanced network tools..."
    apt install -y aircrack-ng macchanger 2>/dev/null || print_warning "⚠️ Some advanced tools not available"
    
    print_success "🎉 ALL DEPENDENCIES INSTALLED!"
    echo ""
}

# Test system compatibility
test_system_comprehensive() {
    print_status "Performing comprehensive system compatibility test..."
    
    # Test Python and modules
    if python3 --version >/dev/null 2>&1; then
        PYTHON_VERSION=$(python3 --version 2>&1)
        print_success "✅ Python: $PYTHON_VERSION"
    else
        print_error "❌ Python 3 not found"
        exit 1
    fi
    
    if python3 -c "import tkinter" >/dev/null 2>&1; then
        print_success "✅ tkinter GUI framework available"
    else
        print_error "❌ tkinter not available"
        exit 1
    fi
    
    # Test network commands
    local commands=("ip" "ifconfig" "rfkill" "lsusb" "lspci" "iwconfig")
    for cmd in "${commands[@]}"; do
        if command -v "$cmd" >/dev/null 2>&1; then
            print_success "✅ $cmd command available"
        else
            print_warning "⚠️ $cmd command not found"
        fi
    done
    
    # Test Bluetooth
    local bt_commands=("hciconfig" "bluetoothctl")
    for cmd in "${bt_commands[@]}"; do
        if command -v "$cmd" >/dev/null 2>&1; then
            print_success "✅ Bluetooth $cmd available"
        else
            print_warning "⚠️ Bluetooth $cmd not found"
        fi
    done
    
    # Test hardware detection
    wifi_hardware=$(lspci | grep -E -i "wireless|wifi" | wc -l)
    bt_hardware=$(lspci | grep -E -i "bluetooth" | wc -l)
    usb_wifi=$(lsusb | grep -E -i "wireless|wifi" | wc -l)
    usb_bt=$(lsusb | grep -E -i "bluetooth" | wc -l)
    
    print_status "Hardware Detection Summary:"
    echo "   • WiFi Hardware (PCI): $wifi_hardware"
    echo "   • WiFi Hardware (USB): $usb_wifi"
    echo "   • Bluetooth Hardware (PCI): $bt_hardware"
    echo "   • Bluetooth Hardware (USB): $usb_bt"
    
    print_success "🔍 System compatibility test completed!"
    echo ""
}

# Install the All-in-One MACARON
install_all_in_one_macaron() {
    print_status "Installing All-in-One MACARON..."
    
    # Create application directories
    mkdir -p /usr/local/share/macaron
    mkdir -p /usr/local/bin
    mkdir -p /usr/local/share/doc/macaron
    mkdir -p /usr/local/share/man/man1
    
    # Copy main application
    if [[ -f "main.py" ]]; then
        cp main.py /usr/local/share/macaron/
        chmod 755 /usr/local/share/macaron/main.py
        print_success "✅ All-in-One MACARON application installed"
    else
        print_error "❌ main.py not found in current directory"
        print_status "Make sure you're running this from the MACARON directory"
        exit 1
    fi
    
    # Create enhanced wrapper script
    cat > /usr/local/bin/macaron << 'EOF'
#!/bin/bash
# All-in-One MACARON Wrapper Script
# Enhanced with automatic privilege checking

MACARON_DIR="/usr/local/share/macaron"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 MACARON - All-in-One MAC Address Randomizer${NC}"
echo "=============================================="

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}⚠️  Root privileges required for MAC address changes${NC}"
    echo ""
    echo "Restarting with sudo..."
    exec sudo "$0" "$@"
fi

echo -e "${GREEN}✅ Running with proper privileges${NC}"
echo ""

# Change to application directory and run
cd "$MACARON_DIR"
exec python3 main.py "$@"
EOF
    
    chmod 755 /usr/local/bin/macaron
    print_success "✅ Enhanced wrapper script created"
    
    # Create documentation
    cat > /usr/local/share/doc/macaron/README << 'EOF'
MACARON - All-in-One MAC Address Randomizer
==========================================

FEATURES:
- Integrated interface activation (no separate scripts needed!)
- WiFi, Bluetooth, Ethernet, and USB adapter support
- One-click "Enable All Interfaces" button
- Advanced diagnostics and troubleshooting
- Secure MAC randomization with backup/restore
- Automatic scheduling support

USAGE:
- Run: sudo macaron
- Click "Enable All Interfaces" if interfaces not visible
- Select interfaces and click "Randomize Selected"
- Use "Diagnostics" for troubleshooting

INTEGRATED FUNCTIONALITY:
✅ RF Kill unblocking (replaces rfkill commands)
✅ Kernel module loading (automatic driver loading)
✅ Bluetooth service activation
✅ WiFi firmware installation
✅ Network service management
✅ Comprehensive hardware detection

NO ADDITIONAL SCRIPTS NEEDED!
EOF
    
    print_success "✅ Documentation created"
}

# Create desktop integration
create_enhanced_desktop_integration() {
    print_status "Creating enhanced desktop integration..."
    
    cat > /usr/share/applications/macaron.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=MACARON (All-in-One)
GenericName=MAC Address Randomizer
Comment=Complete MAC randomization solution with integrated interface activation
Keywords=mac;address;randomizer;privacy;security;network;bluetooth;wifi;ethernet;
Icon=network-wired
Exec=pkexec macaron
Terminal=false
StartupNotify=true
Categories=System;Security;Network;
MimeType=
StartupWMClass=MACARON
X-GNOME-Autostart-enabled=false

# Additional metadata
X-GNOME-FullName=MACARON All-in-One MAC Randomizer
X-GNOME-UsesNotifications=true
EOF
    
    # Update desktop database
    update-desktop-database /usr/share/applications 2>/dev/null || true
    
    print_success "✅ Enhanced desktop integration created"
    
    # Create man page
    cat > /usr/local/share/man/man1/macaron.1 << 'EOF'
.TH MACARON 1 "2025" "2.0" "All-in-One MAC Address Randomizer"
.SH NAME
macaron \- All-in-One MAC Address Randomization Tool
.SH SYNOPSIS
.B sudo macaron
.SH DESCRIPTION
MACARON is a comprehensive, all-in-one MAC address randomization tool designed to enhance privacy and security on Linux systems. Unlike traditional tools, MACARON integrates all functionality into a single application with no separate scripts required.

.SH INTEGRATED FEATURES
.TP
.B Interface Activation
Automatically unblocks RF interfaces, loads drivers, and activates WiFi/Bluetooth
.TP
.B Complete Hardware Support  
Supports WiFi, Bluetooth, Ethernet, and USB network adapters
.TP
.B One-Click Operation
"Enable All Interfaces" button activates everything automatically
.TP
.B Advanced Diagnostics
Built-in troubleshooting and hardware detection tools
.TP
.B Secure Randomization
Cryptographically secure MAC generation with backup/restore

.SH USAGE
Launch MACARON with root privileges:
.B sudo macaron

If interfaces are not visible, click "Enable All Interfaces" button.

.SH FILES
.TP
.I /usr/local/share/macaron/
Application directory
.TP
.I /usr/local/share/doc/macaron/
Documentation directory
.SH AUTHOR
Ratomir Jovanovic (ratomir.com) - Enhanced by AI Assistant
.SH LICENSE
MIT License for personal use.
EOF
    
    gzip -f /usr/local/share/man/man1/macaron.1
    print_success "✅ Manual page created"
}

# Perform initial system optimization
optimize_system() {
    print_status "Performing system optimization for network interfaces..."
    
    # Unblock all RF interfaces
    if command -v rfkill >/dev/null 2>&1; then
        rfkill unblock all 2>/dev/null || true
        print_success "✅ RF interfaces unblocked"
    fi
    
    # Start essential services
    systemctl enable bluetooth 2>/dev/null || true
    systemctl start bluetooth 2>/dev/null || true
    print_success "✅ Bluetooth service activated"
    
    # Load common WiFi modules
    modules=("iwlwifi" "ath9k" "rtl8188eu" "rtl8192cu")
    for module in "${modules[@]}"; do
        modprobe "$module" 2>/dev/null || true
    done
    print_success "✅ Common WiFi modules loaded"
    
    print_success "🚀 System optimization completed!"
    echo ""
}

# Show final usage instructions
show_final_instructions() {
    print_success "🎉 ALL-IN-ONE MACARON INSTALLATION COMPLETED!"
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                     USAGE INSTRUCTIONS                      ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    print_status "🚀 TO START MACARON:"
    echo -e "   ${GREEN}sudo macaron${NC}                    # Launch from terminal"
    echo -e "   ${GREEN}Applications → System → MACARON${NC}  # Launch from GUI"
    echo ""
    
    print_status "🔧 ALL-IN-ONE FEATURES:"
    echo "   ✅ No separate scripts needed!"
    echo "   ✅ Click 'Enable All Interfaces' to activate WiFi/Bluetooth"
    echo "   ✅ Built-in diagnostics and troubleshooting"
    echo "   ✅ Automatic driver loading and service management"
    echo "   ✅ Support for all interface types (WiFi, Bluetooth, Ethernet, USB)"
    echo ""
    
    print_status "📋 QUICK START GUIDE:"
    echo "   1. Run: sudo macaron"
    echo "   2. Click 'Enable All Interfaces' (if interfaces not visible)"
    echo "   3. Click 'Scan Interfaces' to refresh"
    echo "   4. Select interfaces and click 'Randomize Selected'"
    echo "   5. Use 'Diagnostics' for any troubleshooting"
    echo ""
    
    print_status "🎯 WHAT'S INTEGRATED:"
    echo "   • RF Kill unblocking"
    echo "   • Kernel module loading"
    echo "   • Bluetooth service activation"
    echo "   • WiFi firmware management"
    echo "   • Network service restart"
    echo "   • Hardware detection and activation"
    echo ""
    
    print_warning "💡 IMPORTANT NOTES:"
    echo "   • Always run with sudo (automatic privilege checking included)"
    echo "   • Bluetooth MAC changing depends on hardware support"
    echo "   • All functionality is integrated - no external scripts needed!"
    echo ""
    
    echo -e "${GREEN}🎉 ENJOY YOUR ALL-IN-ONE MAC RANDOMIZATION SOLUTION! 🎉${NC}"
    echo ""
}

# Main installation process
main() {
    print_header
    
    print_status "Starting All-in-One MACARON installation for Kali Linux..."
    echo ""
    
    # Installation steps
    check_root
    install_dependencies
    test_system_comprehensive
    install_all_in_one_macaron
    create_enhanced_desktop_integration
    optimize_system
    
    echo ""
    show_final_instructions
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "All-in-One MACARON Installer"
        echo "Usage: sudo ./install_all_in_one.sh"
        echo ""
        echo "This installer creates a complete MAC randomization solution"
        echo "with all functionality integrated into a single application."
        exit 0
        ;;
    --version|-v)
        echo "All-in-One MACARON Installer v2.0"
        exit 0
        ;;
esac

# Run main installation
main "$@" 