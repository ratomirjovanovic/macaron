#!/bin/bash

# MACARON - Linux Installer
# Professional installation script for MAC Address Randomization Tool
#
# Author: Ratomir Jovanovic
# Website: ratomir.com
# Version: 1.0
# License: MIT (Personal Use) / Commercial License Required for Business Use
# Copyright (c) 2025

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Installation paths
INSTALL_DIR="/usr/local/bin"
APP_DIR="/usr/local/share/macaron"
DESKTOP_DIR="/usr/share/applications"
DOC_DIR="/usr/local/share/doc/macaron"
MAN_DIR="/usr/local/share/man/man1"

# Function to print colored output
print_header() {
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    MACARON INSTALLER                         ║${NC}"
    echo -e "${CYAN}║              MAC Address Randomization Tool                  ║${NC}"
    echo -e "${CYAN}║                                                              ║${NC}"
    echo -e "${CYAN}║  Author: Ratomir Jovanovic (ratomir.com)                    ║${NC}"
    echo -e "${CYAN}║  Version: 1.0                                               ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
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
        print_status "Usage: sudo ./install.sh"
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python 3
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        print_status "Install with: apt install python3 (Ubuntu/Debian)"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION detected"
    
    # Check tkinter
    if ! python3 -c "import tkinter" &> /dev/null; then
        print_warning "tkinter not found, attempting to install..."
        if command -v apt &> /dev/null; then
            apt update && apt install -y python3-tk
        elif command -v yum &> /dev/null; then
            yum install -y tkinter
        elif command -v pacman &> /dev/null; then
            pacman -S --noconfirm tk
        else
            print_error "Could not install tkinter automatically"
            print_status "Please install tkinter manually and run installer again"
            exit 1
        fi
    fi
    print_success "tkinter available"
    
    # Check iproute2
    if ! command -v ip &> /dev/null; then
        print_warning "iproute2 not found, attempting to install..."
        if command -v apt &> /dev/null; then
            apt install -y iproute2
        elif command -v yum &> /dev/null; then
            yum install -y iproute2
        elif command -v pacman &> /dev/null; then
            pacman -S --noconfirm iproute2
        else
            print_error "Could not install iproute2 automatically"
            exit 1
        fi
    fi
    print_success "iproute2 available"
}

# Create directories
create_directories() {
    print_status "Creating installation directories..."
    
    mkdir -p "$APP_DIR"
    mkdir -p "$DOC_DIR"
    mkdir -p "$MAN_DIR"
    
    print_success "Directories created"
}

# Install application files
install_files() {
    print_status "Installing application files..."
    
    # Copy main application
    cp main.py "$APP_DIR/"
    chmod 755 "$APP_DIR/main.py"
    
    # Copy test files
    cp test_macaron.py "$APP_DIR/"
    cp run_tests.py "$APP_DIR/"
    chmod 755 "$APP_DIR/run_tests.py"
    
    # Create wrapper script in /usr/local/bin
    cat > "$INSTALL_DIR/macaron" << 'EOF'
#!/bin/bash
# MACARON wrapper script
cd /usr/local/share/macaron
exec python3 main.py "$@"
EOF
    chmod 755 "$INSTALL_DIR/macaron"
    
    # Create test runner in /usr/local/bin
    cat > "$INSTALL_DIR/macaron-test" << 'EOF'
#!/bin/bash
# MACARON test runner
cd /usr/local/share/macaron
exec python3 run_tests.py "$@"
EOF
    chmod 755 "$INSTALL_DIR/macaron-test"
    
    print_success "Application files installed"
}

# Install documentation
install_documentation() {
    print_status "Installing documentation..."
    
    # Copy documentation files
    cp README.md "$DOC_DIR/"
    cp LICENSE "$DOC_DIR/"
    cp INSTALL.md "$DOC_DIR/"
    cp PROJECT_SUMMARY.md "$DOC_DIR/"
    cp CODE_REVIEW.md "$DOC_DIR/"
    cp TECHNICAL_DOCUMENTATION.md "$DOC_DIR/"
    
    # Create man page
    cat > "$MAN_DIR/macaron.1" << 'EOF'
.TH MACARON 1 "2025" "1.0" "MAC Address Randomization Tool"
.SH NAME
macaron \- MAC Address Randomization Tool for privacy enhancement
.SH SYNOPSIS
.B macaron
.SH DESCRIPTION
MACARON is a comprehensive, enterprise-grade MAC address randomization application 
designed to enhance privacy and security on Linux systems. It provides both manual 
and automatic MAC address randomization with a modern graphical interface.

The application prevents device tracking, enhances location privacy, and protects 
against behavioral profiling by randomizing Media Access Control (MAC) addresses 
of network interfaces.
.SH FEATURES
.TP
.B Real-time interface detection
Automatically discovers and monitors network hardware
.TP
.B Secure MAC generation
Cryptographically secure random MAC address generation
.TP
.B Automatic scheduling
User-configurable randomization intervals (1-1440 minutes)
.TP
.B Original MAC backup
Automatic storage and restoration capability
.TP
.B Comprehensive logging
Security audit trails and activity monitoring
.TP
.B Modern GUI
Responsive, user-friendly interface built with tkinter
.SH REQUIREMENTS
.TP
Root privileges are required to modify MAC addresses. Run with sudo.
.TP
Python 3.6+ with tkinter support
.TP
iproute2 package for network interface management
.SH EXAMPLES
.TP
.B sudo macaron
Launch the GUI application
.TP
.B macaron-test
Run the test suite (as root)
.SH FILES
.TP
.I /usr/local/share/macaron/
Application directory
.TP
.I /usr/local/share/doc/macaron/
Documentation directory
.TP
.I ./macaron.log
Activity log file (created in working directory)
.SH AUTHOR
Ratomir Jovanovic (ratomir.com)
.SH LICENSE
MIT License for personal use. Commercial use requires separate license.
.SH SEE ALSO
.BR ip (8),
.BR ifconfig (8)
EOF

    # Compress man page
    gzip -f "$MAN_DIR/macaron.1"
    
    print_success "Documentation installed"
}

# Install desktop integration
install_desktop_integration() {
    print_status "Installing desktop integration..."
    
    # Update desktop file with correct paths
    cat > "$DESKTOP_DIR/macaron.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=MACARON
GenericName=MAC Address Randomizer
Comment=Secure MAC address randomization tool for privacy enhancement
Keywords=mac;address;randomizer;privacy;security;network;
Icon=network-wired
Exec=pkexec macaron
Terminal=false
StartupNotify=true
Categories=System;Security;Network;
MimeType=
StartupWMClass=MACARON
X-GNOME-Autostart-enabled=false

# Security settings
X-GNOME-UsesNotifications=true
X-Ubuntu-Touch=false

# Additional metadata
X-AppStream-Ignore=false
EOF

    # Update desktop database
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$DESKTOP_DIR" &> /dev/null || true
    fi
    
    print_success "Desktop integration installed"
}

# Create uninstaller
create_uninstaller() {
    print_status "Creating uninstaller..."
    
    cat > "$APP_DIR/uninstall.sh" << 'EOF'
#!/bin/bash
# MACARON Uninstaller

echo "Uninstalling MACARON..."

# Remove files
rm -f /usr/local/bin/macaron
rm -f /usr/local/bin/macaron-test
rm -rf /usr/local/share/macaron
rm -rf /usr/local/share/doc/macaron
rm -f /usr/local/share/man/man1/macaron.1.gz
rm -f /usr/share/applications/macaron.desktop

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database /usr/share/applications &> /dev/null || true
fi

echo "MACARON has been successfully uninstalled."
echo "Note: Log files in user directories are not removed."
EOF

    chmod 755 "$APP_DIR/uninstall.sh"
    
    print_success "Uninstaller created at $APP_DIR/uninstall.sh"
}

# Main installation function
main() {
    print_header
    
    print_status "Starting MACARON installation..."
    echo ""
    
    # Perform checks
    check_root
    check_requirements
    
    echo ""
    print_status "Installing MACARON to system directories..."
    
    # Install components
    create_directories
    install_files
    install_documentation
    install_desktop_integration
    create_uninstaller
    
    echo ""
    print_success "Installation completed successfully!"
    echo ""
    print_status "MACARON has been installed to your system."
    print_status "You can now run it with: sudo macaron"
    print_status "Or find it in your applications menu under System/Security"
    echo ""
    print_status "Additional commands:"
    print_status "  sudo macaron-test    - Run test suite"
    print_status "  man macaron          - View manual page"
    print_status "  $APP_DIR/uninstall.sh - Uninstall MACARON"
    echo ""
    print_warning "Remember: MACARON requires root privileges to modify MAC addresses"
    print_status "Always run with sudo: sudo macaron"
    echo ""
    print_success "Installation complete! Enjoy enhanced privacy with MACARON!"
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "MACARON Linux Installer"
        echo ""
        echo "Usage: sudo ./install.sh [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --version, -v  Show version information"
        echo ""
        echo "This installer sets up MACARON as a system application with"
        echo "proper integration into the Linux desktop environment."
        exit 0
        ;;
    --version|-v)
        echo "MACARON Installer v1.0"
        echo "Author: Ratomir Jovanovic (ratomir.com)"
        echo "License: MIT (Personal) / Commercial License Required"
        exit 0
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        print_error "Use --help for usage information"
        exit 1
        ;;
esac 