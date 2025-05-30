#!/bin/bash

# MACARON - MAC Address Randomization Tool
# Convenient launcher script with privilege checking
#
# Author: Ratomir Jovanovic
# Website: ratomir.com
# Version: 1.0
# License: MIT (Personal Use) / Commercial License Required for Business Use
# Copyright (c) 2025

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_SCRIPT="$SCRIPT_DIR/main.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[MACARON]${NC} $1"
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
    if [[ $EUID -eq 0 ]]; then
        return 0
    else
        return 1
    fi
}

# Check if Python 3 is available
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_status "Found Python $PYTHON_VERSION"
        return 0
    else
        print_error "Python 3 is not installed or not in PATH"
        return 1
    fi
}

# Check if tkinter is available
check_tkinter() {
    if python3 -c "import tkinter" &> /dev/null; then
        print_status "tkinter GUI framework is available"
        return 0
    else
        print_error "tkinter is not available"
        print_error "Install with: sudo apt install python3-tk (Ubuntu/Debian)"
        print_error "             sudo yum install tkinter (CentOS/RHEL)"
        print_error "             sudo pacman -S tk (Arch Linux)"
        return 1
    fi
}

# Check if required system commands are available
check_system_commands() {
    local commands=("ip")
    local missing=()
    
    for cmd in "${commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            missing+=("$cmd")
        fi
    done
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        print_error "Missing required system commands: ${missing[*]}"
        print_error "Install with: sudo apt install iproute2 (Ubuntu/Debian)"
        return 1
    fi
    
    print_status "System commands available"
    return 0
}

# Main execution
main() {
    echo ""
    echo "======================================"
    echo "    MACARON - MAC Address Randomizer  "
    echo "======================================"
    echo ""
    
    # Check if main script exists
    if [[ ! -f "$MAIN_SCRIPT" ]]; then
        print_error "main.py not found in $SCRIPT_DIR"
        exit 1
    fi
    
    # Perform system checks
    print_status "Performing system checks..."
    
    if ! check_python; then
        exit 1
    fi
    
    if ! check_tkinter; then
        exit 1
    fi
    
    if ! check_system_commands; then
        exit 1
    fi
    
    # Check root privileges
    if check_root; then
        print_success "Running with root privileges"
        print_status "Starting MACARON..."
        echo ""
        
        # Run the main application
        cd "$SCRIPT_DIR"
        python3 "$MAIN_SCRIPT"
        
    else
        print_warning "MACARON requires root privileges to modify MAC addresses"
        print_status "Attempting to restart with sudo..."
        echo ""
        
        # Check if sudo is available
        if command -v sudo &> /dev/null; then
            cd "$SCRIPT_DIR"
            exec sudo python3 "$MAIN_SCRIPT"
        else
            print_error "sudo is not available. Please run as root:"
            print_error "su -c 'python3 $MAIN_SCRIPT'"
            exit 1
        fi
    fi
}

# Handle script arguments
case "${1:-}" in
    -h|--help)
        echo "MACARON - MAC Address Randomization Tool"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  -h, --help     Show this help message"
        echo "  -v, --version  Show version information"
        echo "  --check        Run system compatibility check only"
        echo ""
        echo "This script launches MACARON with proper privilege checking."
        echo "MACARON requires root privileges to modify MAC addresses."
        exit 0
        ;;
    -v|--version)
        echo "MACARON MAC Address Randomizer v1.0"
        echo "Author: Ratomir Jovanovic (ratomir.com)"
        echo "Built for Linux systems"
        exit 0
        ;;
    --check)
        print_status "Running compatibility check..."
        check_python && check_tkinter && check_system_commands
        if [[ $? -eq 0 ]]; then
            print_success "All system checks passed!"
        else
            print_error "Some system checks failed"
            exit 1
        fi
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