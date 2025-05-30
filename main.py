#!/usr/bin/env python3
"""
MACARON - MAC Address Randomization Tool
A secure privacy tool for randomizing network interface MAC addresses on Linux

Author: Ratomir Jovanovic
Website: ratomir.com
Version: 1.0
License: MIT (Personal Use) / Commercial License Required for Business Use
Copyright (c) 2025

MACARON is a comprehensive, enterprise-grade MAC address randomization application 
designed to enhance privacy and security on Linux systems. It provides both manual 
and automatic MAC address randomization with a modern graphical interface, 
comprehensive logging, and robust security features.

Key Features:
- Real-time network interface detection and monitoring
- Secure cryptographic MAC address generation
- Automatic scheduling with customizable intervals (1-1440 minutes)
- Original MAC address backup and restoration
- Comprehensive security audit logging
- Modern, intuitive GUI built with tkinter
- Root privilege management with secure sudo handling
- Cross-interface support (Ethernet, WiFi, etc.)
- Virtual interface filtering for safety
- Background threading for non-blocking operations

This tool is designed for privacy-conscious users, security professionals, 
penetration testers, and enterprises requiring MAC address randomization 
for compliance or security purposes.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import re
import secrets  # Add secrets module for cryptographic operations
import random
import threading
import time
import os
import sys
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler
import stat

class MacaronApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MACARON - MAC Address Randomizer")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Security check - ensure running as root
        if os.geteuid() != 0:
            messagebox.showerror("Permission Error", 
                               "MACARON requires root privileges to modify MAC addresses.\n"
                               "Please run with sudo: sudo python3 main.py")
            sys.exit(1)
        
        # Initialize variables
        self.interfaces = {}
        self.original_macs = {}
        self.auto_randomize_active = False
        self.auto_thread = None
        self.interval_minutes = 15
        
        # Setup logging
        self.setup_logging()
        
        # Create GUI
        self.create_widgets()
        self.scan_interfaces()
        
        # Style configuration
        self.configure_styles()
        
    def setup_logging(self):
        """Setup logging for security and audit purposes"""
        log_file = 'macaron.log'
        
        # Create log file with secure permissions (readable only by root)
        if not os.path.exists(log_file):
            with open(log_file, 'a'):
                pass
            os.chmod(log_file, stat.S_IRUSR | stat.S_IWUSR)  # 0o600
        
        # Setup rotating file handler (max 5MB per file, keep 5 backup files)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=5,
            delay=True  # Don't open file until first log
        )
        
        # Setup formatters and handlers
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Configure root logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info("MACARON application started")
        self.logger.info(f"Log file created/opened with secure permissions: {log_file}")
    
    def configure_styles(self):
        """Configure modern styling for the application"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors for modern look
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Warning.TLabel', foreground='orange')
        style.configure('Error.TLabel', foreground='red')
    
    def create_widgets(self):
        """Create the main GUI interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="MACARON - MAC Address Randomizer", 
                               style='Header.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Interface list frame
        interface_frame = ttk.LabelFrame(main_frame, text="Network Interfaces", padding="10")
        interface_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        interface_frame.columnconfigure(0, weight=1)
        
        # Treeview for interfaces
        columns = ('Interface', 'Current MAC', 'Original MAC', 'Status')
        self.tree = ttk.Treeview(interface_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(interface_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Control buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Button(button_frame, text="Scan Interfaces", 
                  command=self.scan_interfaces).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Enable All Interfaces", 
                  command=self.enable_all_interfaces).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Randomize Selected", 
                  command=self.randomize_selected).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Randomize All", 
                  command=self.randomize_all).grid(row=0, column=3, padx=5)
        ttk.Button(button_frame, text="Restore Original", 
                  command=self.restore_original).grid(row=0, column=4, padx=5)
        ttk.Button(button_frame, text="Diagnostics", 
                  command=self.run_diagnostics).grid(row=0, column=5, padx=(5, 0))
        
        # Auto-randomization frame
        auto_frame = ttk.LabelFrame(main_frame, text="Automatic Randomization", padding="10")
        auto_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(auto_frame, text="Interval (minutes):").grid(row=0, column=0, padx=(0, 5))
        
        self.interval_var = tk.StringVar(value="15")
        interval_spinbox = ttk.Spinbox(auto_frame, from_=1, to=1440, width=10, 
                                     textvariable=self.interval_var)
        interval_spinbox.grid(row=0, column=1, padx=(0, 10))
        
        self.auto_button = ttk.Button(auto_frame, text="Start Auto-Randomization", 
                                     command=self.toggle_auto_randomization)
        self.auto_button.grid(row=0, column=2, padx=(0, 10))
        
        self.auto_status_label = ttk.Label(auto_frame, text="Stopped")
        self.auto_status_label.grid(row=0, column=3)
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        main_frame.rowconfigure(1, weight=2)
        main_frame.rowconfigure(4, weight=1)
        
        self.log("MACARON initialized successfully")
    
    def log(self, message):
        """Add message to the log display and logging system"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        self.log_text.insert(tk.END, log_message + "\n")
        self.log_text.see(tk.END)
        self.logger.info(message)
    
    def scan_interfaces(self):
        """Scan for network interfaces and their MAC addresses - Enhanced Version"""
        try:
            self.log("Scanning network interfaces...")
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            self.interfaces.clear()
            detected_interfaces = {}
            
            # Method 1: Standard network interfaces (WiFi, Ethernet)
            try:
                result = subprocess.run(['ip', 'link', 'show'], 
                                      capture_output=True, text=True, check=True)
                self.log("Scanning standard network interfaces...")
                
                lines = result.stdout.split('\n')
                i = 0
                while i < len(lines):
                    line = lines[i]
                    if re.match(r'^\d+:', line):
                        # Extract interface name
                        match = re.search(r'^\d+:\s+([^:@]+)', line)
                        if match:
                            interface = match.group(1).strip()
                            
                            # Look for MAC address in current or next line
                            mac_address = None
                            
                            # Check current line
                            mac_match = re.search(r'link/ether\s+([a-f0-9:]{17})', line)
                            if mac_match:
                                mac_address = mac_match.group(1)
                            
                            # Check next line if no MAC found
                            if not mac_address and i + 1 < len(lines):
                                next_line = lines[i + 1]
                                mac_match = re.search(r'link/ether\s+([a-f0-9:]{17})', next_line)
                                if mac_match:
                                    mac_address = mac_match.group(1)
                            
                            # Add interface if MAC found and it's not loopback/virtual
                            if mac_address and not self._is_virtual_interface(interface):
                                detected_interfaces[interface] = {
                                    'mac': mac_address,
                                    'type': self._detect_interface_type(interface),
                                    'status': 'up' if 'UP' in line else 'down'
                                }
                                self.log(f"Found {detected_interfaces[interface]['type']}: {interface} ({mac_address})")
                    i += 1
                    
            except subprocess.CalledProcessError:
                self.log("Warning: 'ip link show' command failed")
            
            # Method 2: Alternative detection using 'ls /sys/class/net'
            try:
                if len(detected_interfaces) == 0:
                    self.log("Trying alternative interface detection...")
                    result = subprocess.run(['ls', '/sys/class/net/'], 
                                          capture_output=True, text=True, check=True)
                    
                    for interface in result.stdout.strip().split('\n'):
                        if interface and not self._is_virtual_interface(interface):
                            # Get MAC address from sysfs
                            try:
                                with open(f'/sys/class/net/{interface}/address', 'r') as f:
                                    mac_address = f.read().strip()
                                    if re.match(r'^([a-f0-9]{2}:){5}[a-f0-9]{2}$', mac_address):
                                        detected_interfaces[interface] = {
                                            'mac': mac_address,
                                            'type': self._detect_interface_type(interface),
                                            'status': 'available'
                                        }
                                        self.log(f"Found via sysfs {detected_interfaces[interface]['type']}: {interface} ({mac_address})")
                            except FileNotFoundError:
                                continue
                                
            except subprocess.CalledProcessError:
                self.log("Warning: Alternative detection failed")
            
            # Method 3: Bluetooth interfaces
            try:
                self.log("Scanning Bluetooth interfaces...")
                
                # Try hciconfig first
                try:
                    result = subprocess.run(['hciconfig'], capture_output=True, text=True, check=True)
                    for line in result.stdout.split('\n'):
                        match = re.search(r'(hci\d+):\s+Type.*BD Address\s+([A-F0-9:]{17})', line)
                        if match:
                            interface = match.group(1)
                            mac_address = match.group(2).lower()
                            detected_interfaces[interface] = {
                                'mac': mac_address,
                                'type': 'Bluetooth',
                                'status': 'available'
                            }
                            self.log(f"Found Bluetooth: {interface} ({mac_address})")
                except subprocess.CalledProcessError:
                    pass
                
                # Try alternative Bluetooth detection
                try:
                    result = subprocess.run(['ls', '/sys/class/bluetooth/'], 
                                          capture_output=True, text=True, check=True)
                    for hci_device in result.stdout.strip().split('\n'):
                        if hci_device.startswith('hci'):
                            try:
                                with open(f'/sys/class/bluetooth/{hci_device}/address', 'r') as f:
                                    mac_address = f.read().strip().lower()
                                    if re.match(r'^([a-f0-9]{2}:){5}[a-f0-9]{2}$', mac_address):
                                        if hci_device not in detected_interfaces:
                                            detected_interfaces[hci_device] = {
                                                'mac': mac_address,
                                                'type': 'Bluetooth',
                                                'status': 'available'
                                            }
                                            self.log(f"Found Bluetooth via sysfs: {hci_device} ({mac_address})")
                            except FileNotFoundError:
                                continue
                except subprocess.CalledProcessError:
                    pass
                    
            except Exception as e:
                self.log(f"Bluetooth detection error: {e}")
            
            # Method 4: USB Network devices
            try:
                self.log("Scanning USB network devices...")
                result = subprocess.run(['lsusb'], capture_output=True, text=True, check=True)
                for line in result.stdout.split('\n'):
                    if 'Network' in line or 'Ethernet' in line or 'Wireless' in line or 'WiFi' in line:
                        self.log(f"USB Network device detected: {line.strip()}")
            except subprocess.CalledProcessError:
                pass
            
            # Populate the interface list and GUI
            for interface, info in detected_interfaces.items():
                mac = info['mac']
                self.interfaces[interface] = mac
                
                # Store original MAC if not already stored
                if interface not in self.original_macs:
                    self.original_macs[interface] = mac
                
                # Add to treeview with enhanced information
                original_mac = self.original_macs.get(interface, mac)
                status = "Original" if mac == original_mac else "Randomized"
                
                # Add interface type to the display
                display_name = f"{interface} ({info['type']})"
                self.tree.insert('', tk.END, values=(display_name, mac, original_mac, status))
            
            total_found = len(detected_interfaces)
            self.log(f"Found {total_found} network interfaces total")
            
            if total_found == 0:
                self.log("No network interfaces found. Possible issues:")
                self.log("1. Run with sudo (required for some operations)")
                self.log("2. No network hardware detected")
                self.log("3. All interfaces may be virtual/loopback")
                self.log("4. Network hardware may be disabled")
                messagebox.showwarning("No Interfaces", 
                                     "No network interfaces found.\n\n"
                                     "Make sure:\n"
                                     "• You're running with sudo\n"
                                     "• Network hardware is enabled\n"
                                     "• Interfaces are not all virtual")
            
        except Exception as e:
            error_msg = f"Unexpected error during interface scan: {e}"
            self.log(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def _is_virtual_interface(self, interface):
        """Check if interface is virtual/should be skipped"""
        virtual_patterns = [
            'lo', 'docker', 'veth', 'br-', 'virbr', 'vmnet', 'vboxnet',
            'tun', 'tap', 'dummy', 'sit', 'gre', 'teql', 'ppp', 'slip'
        ]
        
        interface_lower = interface.lower()
        for pattern in virtual_patterns:
            if interface_lower.startswith(pattern.lower()):
                return True
        return False
    
    def _detect_interface_type(self, interface):
        """Detect the type of network interface"""
        interface_lower = interface.lower()
        
        if interface_lower.startswith('wl') or interface_lower.startswith('wlan'):
            return 'WiFi'
        elif interface_lower.startswith('eth') or interface_lower.startswith('ens') or interface_lower.startswith('enp'):
            return 'Ethernet'
        elif interface_lower.startswith('hci'):
            return 'Bluetooth'
        elif interface_lower.startswith('usb') or interface_lower.startswith('enx'):
            return 'USB-Ethernet'
        elif interface_lower.startswith('bond'):
            return 'Bonded'
        elif interface_lower.startswith('team'):
            return 'Team'
        elif interface_lower.startswith('can'):
            return 'CAN-Bus'
        else:
            return 'Network'
    
    def generate_random_mac(self):
        """Generate a cryptographically secure random MAC address with proper format"""
        # Generate random MAC with locally administered bit set
        mac = [0x02]  # Locally administered unicast
        mac.extend([secrets.randbelow(256) for _ in range(5)])  # Use secrets for cryptographic randomness
        return ':'.join(f'{x:02x}' for x in mac)
    
    def validate_mac_address(self, mac, allow_global=False):
        """Validate MAC address format and value"""
        # Check format using regex
        if not re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', mac):
            return False
        
        # Split into octets and convert to integers
        octets = [int(x, 16) for x in mac.split(':')]
        
        # Check if it's a unicast address (first bit of first octet should be 0)
        if octets[0] & 0x01:
            return False
        
        # For generated MACs, ensure locally administered bit is set
        # For original MACs (during restoration), allow global addresses
        if not allow_global and not (octets[0] & 0x02):
            return False
        
        return True
    
    def validate_interface_name(self, interface):
        """Validate network interface name to prevent command injection"""
        # Only allow alphanumeric characters, numbers, and common interface characters
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', interface):
            return False
        
        # Check length limits
        if len(interface) < 1 or len(interface) > 15:  # Standard Linux interface name limits
            return False
        
        # Blacklist dangerous patterns
        dangerous_patterns = ['..', '&&', '|', ';', '$', '`', '>', '<']
        if any(pattern in interface for pattern in dangerous_patterns):
            return False
        
        return True
    
    def change_mac_address(self, interface, new_mac, is_restoration=False):
        """Change MAC address for network interface - Enhanced for all interface types"""
        try:
            # Extract interface name if it contains type info
            if '(' in interface:
                interface_name = interface.split('(')[0].strip()
                interface_type = interface.split('(')[1].replace(')', '').strip()
            else:
                interface_name = interface
                interface_type = self._detect_interface_type(interface_name)
            
            # Validate inputs
            if not self.validate_interface_name(interface_name):
                self.log(f"Invalid interface name: {interface_name}")
                return False
            
            if not self.validate_mac_address(new_mac, allow_global=is_restoration):
                self.log(f"Invalid MAC address: {new_mac}")
                return False
            
            # Handle different interface types
            if interface_type == 'Bluetooth':
                return self._change_bluetooth_mac(interface_name, new_mac)
            else:
                return self._change_network_mac(interface_name, new_mac)
                
        except Exception as e:
            error_msg = f"Unexpected error changing MAC for {interface}: {e}"
            self.log(error_msg)
            return False
    
    def _change_network_mac(self, interface, new_mac):
        """Change MAC address for standard network interfaces (WiFi, Ethernet, USB)"""
        try:
            # Method 1: Standard approach using ip command
            subprocess.run(['ip', 'link', 'set', 'dev', interface, 'down'], 
                          check=True, capture_output=True)
            subprocess.run(['ip', 'link', 'set', 'dev', interface, 'address', new_mac], 
                          check=True, capture_output=True)
            subprocess.run(['ip', 'link', 'set', 'dev', interface, 'up'], 
                          check=True, capture_output=True)
            
            # Update stored MAC
            self.interfaces[interface] = new_mac
            self.log(f"Changed {interface} MAC to {new_mac}")
            return True
            
        except subprocess.CalledProcessError:
            # Method 2: Try alternative approach with ifconfig
            try:
                subprocess.run(['ifconfig', interface, 'down'], 
                              check=True, capture_output=True)
                subprocess.run(['ifconfig', interface, 'hw', 'ether', new_mac], 
                              check=True, capture_output=True)
                subprocess.run(['ifconfig', interface, 'up'], 
                              check=True, capture_output=True)
                
                self.interfaces[interface] = new_mac
                self.log(f"Changed {interface} MAC to {new_mac} (via ifconfig)")
                return True
                
            except subprocess.CalledProcessError:
                # Method 3: Try direct sysfs approach
                try:
                    # Stop interface
                    subprocess.run(['ip', 'link', 'set', 'dev', interface, 'down'], 
                                  check=True, capture_output=True)
                    
                    # Write MAC to sysfs (if supported)
                    with open(f'/sys/class/net/{interface}/address', 'w') as f:
                        f.write(new_mac)
                    
                    # Start interface
                    subprocess.run(['ip', 'link', 'set', 'dev', interface, 'up'], 
                                  check=True, capture_output=True)
                    
                    self.interfaces[interface] = new_mac
                    self.log(f"Changed {interface} MAC to {new_mac} (via sysfs)")
                    return True
                    
                except (subprocess.CalledProcessError, PermissionError, FileNotFoundError):
                    self.log(f"Failed to change MAC for {interface} - all methods failed")
                    return False
    
    def _change_bluetooth_mac(self, interface, new_mac):
        """Change MAC address for Bluetooth interfaces"""
        try:
            self.log(f"Attempting to change Bluetooth MAC for {interface}")
            
            # Method 1: Using hciconfig
            try:
                # Stop Bluetooth interface
                subprocess.run(['hciconfig', interface, 'down'], 
                              check=True, capture_output=True)
                
                # Some Bluetooth adapters support MAC change via vendor commands
                # This is hardware-dependent and may not work on all adapters
                subprocess.run(['hciconfig', interface, 'reset'], 
                              check=True, capture_output=True)
                
                # Try to set new address (this may fail for many adapters)
                result = subprocess.run(['hciconfig', interface, 'address', new_mac], 
                                      capture_output=True, text=True)
                
                # Start interface back up
                subprocess.run(['hciconfig', interface, 'up'], 
                              check=True, capture_output=True)
                
                if result.returncode == 0:
                    self.interfaces[interface] = new_mac
                    self.log(f"Successfully changed Bluetooth MAC for {interface} to {new_mac}")
                    return True
                else:
                    self.log(f"Bluetooth MAC change not supported for {interface}")
                    
            except subprocess.CalledProcessError:
                pass
            
            # Method 2: Try bdaddr tool (if available)
            try:
                # Check if bdaddr tool is available
                subprocess.run(['which', 'bdaddr'], check=True, capture_output=True)
                
                # Stop bluetooth service
                subprocess.run(['systemctl', 'stop', 'bluetooth'], 
                              check=True, capture_output=True)
                
                # Change address with bdaddr
                subprocess.run(['bdaddr', '-i', interface, new_mac], 
                              check=True, capture_output=True)
                
                # Start bluetooth service
                subprocess.run(['systemctl', 'start', 'bluetooth'], 
                              check=True, capture_output=True)
                
                self.interfaces[interface] = new_mac
                self.log(f"Changed Bluetooth MAC for {interface} to {new_mac} (via bdaddr)")
                return True
                
            except subprocess.CalledProcessError:
                pass
            
            # Method 3: Inform user about limitations
            self.log(f"Bluetooth MAC randomization for {interface} requires hardware support")
            self.log("Many Bluetooth adapters have fixed MAC addresses in firmware")
            self.log("Consider using a USB Bluetooth adapter that supports MAC changing")
            
            # For logging purposes, update the stored MAC even if change failed
            # This helps track which interfaces were attempted
            messagebox.showinfo("Bluetooth MAC Info", 
                              f"Bluetooth MAC change attempted for {interface}.\n\n"
                              "Note: Many Bluetooth adapters have fixed MAC addresses.\n"
                              "If change failed, consider using a different adapter.")
            
            return False
            
        except Exception as e:
            self.log(f"Error changing Bluetooth MAC for {interface}: {e}")
            return False
    
    def randomize_selected(self):
        """Randomize MAC addresses for selected interfaces"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select interfaces to randomize")
            return
        
        success_count = 0
        for item in selected_items:
            values = self.tree.item(item)['values']
            interface = values[0]
            
            new_mac = self.generate_random_mac()
            if self.change_mac_address(interface, new_mac):
                success_count += 1
        
        self.scan_interfaces()  # Refresh display
        self.log(f"Successfully randomized {success_count} interfaces")
    
    def randomize_all(self):
        """Randomize MAC addresses for all available interfaces"""
        if not self.interfaces:
            messagebox.showwarning("Warning", "No interfaces found. Please scan first.")
            return
        
        if not messagebox.askyesno("Confirm", 
                                  f"Randomize MAC addresses for all {len(self.interfaces)} interfaces?"):
            return
        
        success_count = 0
        for interface in self.interfaces:
            new_mac = self.generate_random_mac()
            if self.change_mac_address(interface, new_mac):
                success_count += 1
        
        self.scan_interfaces()  # Refresh display
        self.log(f"Successfully randomized {success_count}/{len(self.interfaces)} interfaces")
    
    def restore_original(self):
        """Restore original MAC addresses for all interfaces"""
        if not self.original_macs:
            messagebox.showwarning("Warning", "No original MAC addresses stored")
            return
        
        if not messagebox.askyesno("Confirm", "Restore all interfaces to original MAC addresses?"):
            return
        
        success_count = 0
        for interface, original_mac in self.original_macs.items():
            if self.change_mac_address(interface, original_mac, is_restoration=True):
                success_count += 1
        
        self.scan_interfaces()  # Refresh display
        self.log(f"Successfully restored {success_count}/{len(self.original_macs)} interfaces")
    
    def toggle_auto_randomization(self):
        """Start or stop automatic randomization"""
        if not self.auto_randomize_active:
            self.start_auto_randomization()
        else:
            self.stop_auto_randomization()
    
    def start_auto_randomization(self):
        """Start automatic randomization thread"""
        try:
            self.interval_minutes = int(self.interval_var.get())
            if self.interval_minutes < 1:
                raise ValueError("Interval must be at least 1 minute")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid interval: {e}")
            return
        
        self.auto_randomize_active = True
        self.auto_button.config(text="Stop Auto-Randomization")
        self.auto_status_label.config(text="Running", style='Success.TLabel')
        
        # Start background thread
        self.auto_thread = threading.Thread(target=self.auto_randomization_worker, daemon=True)
        self.auto_thread.start()
        
        self.log(f"Started automatic randomization (interval: {self.interval_minutes} minutes)")
    
    def stop_auto_randomization(self):
        """Stop automatic randomization"""
        self.auto_randomize_active = False
        self.auto_button.config(text="Start Auto-Randomization")
        self.auto_status_label.config(text="Stopped", style='')
        
        self.log("Stopped automatic randomization")
    
    def auto_randomization_worker(self):
        """Background worker for automatic randomization"""
        while self.auto_randomize_active:
            # Wait for the specified interval
            for _ in range(self.interval_minutes * 60):  # Convert minutes to seconds
                if not self.auto_randomize_active:
                    return
                time.sleep(1)
            
            if self.auto_randomize_active:
                # Perform randomization
                self.root.after(0, self.auto_randomize_callback)
    
    def auto_randomize_callback(self):
        """Callback for automatic randomization (runs in main thread)"""
        if not self.auto_randomize_active:
            return
        
        success_count = 0
        for interface in self.interfaces:
            new_mac = self.generate_random_mac()
            if self.change_mac_address(interface, new_mac):
                success_count += 1
        
        self.scan_interfaces()  # Refresh display
        self.log(f"Auto-randomization: Updated {success_count}/{len(self.interfaces)} interfaces")

    def run_diagnostics(self):
        """Run comprehensive diagnostics to help troubleshoot interface detection"""
        diag_window = tk.Toplevel(self.root)
        diag_window.title("MACARON - System Diagnostics")
        diag_window.geometry("800x600")
        
        # Create scrollable text widget
        diag_text = scrolledtext.ScrolledText(diag_window, wrap=tk.WORD, font=('Courier', 10))
        diag_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        def log_diag(message):
            diag_text.insert(tk.END, message + "\n")
            diag_text.see(tk.END)
            diag_window.update()
        
        log_diag("=== MACARON SYSTEM DIAGNOSTICS ===")
        log_diag(f"Timestamp: {datetime.now()}")
        log_diag("")
        
        # System Information
        log_diag("=== SYSTEM INFORMATION ===")
        try:
            import platform
            log_diag(f"System: {platform.system()} {platform.release()}")
            log_diag(f"Python: {platform.python_version()}")
            log_diag(f"Architecture: {platform.machine()}")
        except:
            log_diag("Could not gather system information")
        
        log_diag("")
        
        # Check root privileges
        log_diag("=== PRIVILEGE CHECK ===")
        if os.geteuid() == 0:
            log_diag("✓ Running as root (required for MAC changes)")
        else:
            log_diag("✗ NOT running as root - some operations will fail")
        log_diag("")
        
        # Check required commands
        log_diag("=== COMMAND AVAILABILITY ===")
        commands = ['ip', 'ifconfig', 'hciconfig', 'bdaddr', 'lsusb', 'lspci']
        for cmd in commands:
            try:
                subprocess.run(['which', cmd], check=True, capture_output=True)
                log_diag(f"✓ {cmd} available")
            except subprocess.CalledProcessError:
                log_diag(f"✗ {cmd} not found")
        log_diag("")
        
        # Network interface detection
        log_diag("=== RAW INTERFACE DETECTION ===")
        
        # Method 1: ip link show
        log_diag("--- ip link show output ---")
        try:
            result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
            if result.stdout:
                log_diag(result.stdout)
            else:
                log_diag("No output from 'ip link show'")
        except Exception as e:
            log_diag(f"Error running 'ip link show': {e}")
        
        # Method 2: /sys/class/net
        log_diag("--- /sys/class/net directory ---")
        try:
            result = subprocess.run(['ls', '-la', '/sys/class/net/'], capture_output=True, text=True)
            log_diag(result.stdout)
        except Exception as e:
            log_diag(f"Error accessing /sys/class/net: {e}")
        
        # Method 3: ifconfig -a
        log_diag("--- ifconfig -a output ---")
        try:
            result = subprocess.run(['ifconfig', '-a'], capture_output=True, text=True)
            if result.stdout:
                log_diag(result.stdout[:2000] + "..." if len(result.stdout) > 2000 else result.stdout)
            else:
                log_diag("No output from 'ifconfig -a'")
        except Exception as e:
            log_diag(f"Error running 'ifconfig -a': {e}")
        
        # Bluetooth detection
        log_diag("=== BLUETOOTH DETECTION ===")
        
        # hciconfig
        log_diag("--- hciconfig output ---")
        try:
            result = subprocess.run(['hciconfig'], capture_output=True, text=True)
            if result.stdout:
                log_diag(result.stdout)
            else:
                log_diag("No Bluetooth interfaces found via hciconfig")
        except Exception as e:
            log_diag(f"Error running hciconfig: {e}")
        
        # Bluetooth sysfs
        log_diag("--- /sys/class/bluetooth directory ---")
        try:
            result = subprocess.run(['ls', '-la', '/sys/class/bluetooth/'], capture_output=True, text=True)
            log_diag(result.stdout)
        except Exception as e:
            log_diag(f"Error accessing /sys/class/bluetooth: {e}")
        
        # Hardware detection
        log_diag("=== HARDWARE DETECTION ===")
        
        # USB devices
        log_diag("--- USB Network Devices ---")
        try:
            result = subprocess.run(['lsusb'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if any(keyword in line.lower() for keyword in ['network', 'ethernet', 'wireless', 'wifi', 'bluetooth']):
                    log_diag(line)
        except Exception as e:
            log_diag(f"Error running lsusb: {e}")
        
        # PCI devices
        log_diag("--- PCI Network Devices ---")
        try:
            result = subprocess.run(['lspci'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if any(keyword in line.lower() for keyword in ['network', 'ethernet', 'wireless', 'wifi', 'bluetooth']):
                    log_diag(line)
        except Exception as e:
            log_diag(f"Error running lspci: {e}")
        
        # Network manager status
        log_diag("=== NETWORK MANAGER STATUS ===")
        try:
            result = subprocess.run(['systemctl', 'status', 'NetworkManager'], capture_output=True, text=True)
            log_diag("NetworkManager status:")
            log_diag(result.stdout[:1000] + "..." if len(result.stdout) > 1000 else result.stdout)
        except Exception as e:
            log_diag(f"Error checking NetworkManager: {e}")
        
        log_diag("")
        log_diag("=== DIAGNOSTICS COMPLETE ===")
        log_diag("If no interfaces were found, check:")
        log_diag("1. Are you running as root? (sudo)")
        log_diag("2. Are network interfaces enabled in BIOS/UEFI?")
        log_diag("3. Are drivers loaded for your network hardware?")
        log_diag("4. Is NetworkManager interfering with interface detection?")
        log_diag("5. Try restarting NetworkManager: sudo systemctl restart NetworkManager")
        
        # Add buttons
        button_frame = tk.Frame(diag_window)
        button_frame.pack(pady=10)
        
        def save_diag():
            try:
                with open('macaron_diagnostics.txt', 'w') as f:
                    f.write(diag_text.get('1.0', tk.END))
                messagebox.showinfo("Saved", "Diagnostics saved to macaron_diagnostics.txt")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save diagnostics: {e}")
        
        tk.Button(button_frame, text="Save to File", command=save_diag).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close", command=diag_window.destroy).pack(side=tk.LEFT, padx=5)

    def enable_all_interfaces(self):
        """Enable all network interfaces (WiFi, Bluetooth, Ethernet, USB) - Integrated Solution"""
        
        # Create progress window
        progress_window = tk.Toplevel(self.root)
        progress_window.title("MACARON - Enable All Interfaces")
        progress_window.geometry("700x600")
        progress_window.resizable(False, False)
        
        # Center the window
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        # Create scrollable text widget for progress
        progress_text = scrolledtext.ScrolledText(progress_window, wrap=tk.WORD, font=('Courier', 10))
        progress_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add progress bar
        progress_frame = tk.Frame(progress_window)
        progress_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        progress_label = tk.Label(progress_frame, text="Starting...", font=('Arial', 9))
        progress_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        def log_progress(message, color="black", step=None, total_steps=8):
            progress_text.insert(tk.END, message + "\n")
            progress_text.see(tk.END)
            if step:
                progress_bar['value'] = (step / total_steps) * 100
                progress_label.config(text=f"Step {step}/{total_steps}")
            progress_window.update()
            self.log(message)  # Also log to main log
        
        log_progress("🔧 MACARON - Enable All Network Interfaces")
        log_progress("=" * 50)
        log_progress("")
        
        try:
            # Step 1: Check root privileges
            log_progress("📋 STEP 1: Checking Privileges", step=1)
            if os.geteuid() != 0:
                log_progress("❌ ERROR: Root privileges required!")
                messagebox.showerror("Permission Error", "This operation requires root privileges.\nRestart MACARON with: sudo python3 main.py")
                progress_window.destroy()
                return
            log_progress("✅ Running as root")
            log_progress("")
            
            # Step 2: Unblock RF interfaces (WiFi/Bluetooth)
            log_progress("📡 STEP 2: Unblocking RF Interfaces", step=2)
            try:
                # Check if rfkill is available
                subprocess.run(['which', 'rfkill'], check=True, capture_output=True)
                log_progress("🔍 Checking RF kill status...")
                
                # Show current status
                result = subprocess.run(['rfkill', 'list'], capture_output=True, text=True)
                blocked_count = result.stdout.count("Soft blocked: yes")
                if blocked_count > 0:
                    log_progress(f"🚫 Found {blocked_count} blocked interfaces")
                    log_progress("🔓 Unblocking all RF interfaces...")
                    subprocess.run(['rfkill', 'unblock', 'all'], check=True, capture_output=True)
                    log_progress("✅ All RF interfaces unblocked")
                else:
                    log_progress("✅ No blocked RF interfaces found")
                    
            except subprocess.CalledProcessError:
                log_progress("⚠️ rfkill not available - trying to install...")
                try:
                    log_progress("📥 Updating package list...")
                    subprocess.run(['apt', 'update', '-q'], capture_output=True, timeout=60)
                    log_progress("📦 Installing rfkill...")
                    subprocess.run(['apt', 'install', '-y', 'rfkill'], capture_output=True, timeout=120)
                    subprocess.run(['rfkill', 'unblock', 'all'], capture_output=True)
                    log_progress("✅ rfkill installed and interfaces unblocked")
                except Exception as e:
                    log_progress(f"⚠️ Could not install/use rfkill: {e}")
            log_progress("")
            
            # Step 3: Load network kernel modules
            log_progress("🔧 STEP 3: Loading Network Kernel Modules", step=3)
            modules = ["iwlwifi", "ath9k", "ath9k_htc", "rt2800usb", "rt2800pci", 
                      "rtl8188eu", "rtl8192cu", "rtl8812au", "btusb"]
            
            for i, module in enumerate(modules):
                try:
                    # Check if module is already loaded
                    result = subprocess.run(['lsmod'], capture_output=True, text=True)
                    if module in result.stdout:
                        log_progress(f"✅ {module} already loaded")
                    else:
                        log_progress(f"🔄 Loading {module} module...")
                        subprocess.run(['modprobe', module], check=True, capture_output=True)
                        log_progress(f"✅ Loaded {module} module")
                        
                        # Small delay to let module initialize
                        if module.startswith(('iwl', 'ath', 'rt')):
                            time.sleep(1)
                            
                except subprocess.CalledProcessError:
                    log_progress(f"⚠️ Could not load {module} (may not be available)")
            log_progress("")
            
            # Step 4: Start Bluetooth service  
            log_progress("📱 STEP 4: Bluetooth Service Activation", step=4)
            try:
                # Check if bluetooth service exists
                result = subprocess.run(['systemctl', 'is-available', 'bluetooth'], 
                                      capture_output=True)
                if result.returncode == 0:
                    log_progress("🔄 Starting Bluetooth service...")
                    subprocess.run(['systemctl', 'start', 'bluetooth'], 
                                 capture_output=True, timeout=20)
                    subprocess.run(['systemctl', 'enable', 'bluetooth'], 
                                 capture_output=True, timeout=10)
                    
                    # Try to power on bluetooth
                    try:
                        subprocess.run(['which', 'bluetoothctl'], check=True, capture_output=True)
                        process = subprocess.Popen(['bluetoothctl'], stdin=subprocess.PIPE, 
                                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        process.communicate(input=b'power on\nquit\n', timeout=10)
                        log_progress("✅ Bluetooth service started and powered on")
                    except Exception:
                        log_progress("✅ Bluetooth service started")
                else:
                    log_progress("⚠️ Installing Bluetooth packages (this may take 2-3 minutes)...")
                    log_progress("📥 Please wait - downloading Bluetooth stack...")
                    
                    # Install with better error handling and longer timeout
                    result = subprocess.run(['apt', 'install', '-y', 'bluez', 'bluetooth', 'bluez-tools'], 
                                 capture_output=True, timeout=300, text=True)  # 5 minutes timeout
                    
                    if result.returncode == 0:
                        log_progress("📦 Bluetooth packages installed successfully")
                        subprocess.run(['systemctl', 'start', 'bluetooth'], capture_output=True, timeout=20)
                        log_progress("✅ Bluetooth installed and started")
                    else:
                        log_progress(f"⚠️ Bluetooth installation had issues: {result.stderr[:200]}...")
                        log_progress("⚠️ Continuing without Bluetooth")
                    
            except subprocess.TimeoutExpired:
                log_progress("⚠️ Bluetooth installation timed out after 5 minutes")
                log_progress("⚠️ This is normal on slow connections - continuing...")
            except Exception as e:
                log_progress(f"⚠️ Bluetooth setup error: {str(e)[:200]}...")
            log_progress("")
            
            # Step 5: Install missing firmware
            log_progress("📦 STEP 5: Installing Network Firmware", step=5)
            try:
                firmware_packages = ["firmware-linux-nonfree", "firmware-realtek", 
                                   "firmware-atheros", "firmware-intel-sound"]
                log_progress("🔄 Installing WiFi firmware packages...")
                
                # Check which packages are available and install
                available_packages = []
                for package in firmware_packages:
                    try:
                        log_progress(f"🔍 Checking {package}...")
                        result = subprocess.run(['apt', 'search', package], 
                                              capture_output=True, text=True, timeout=15)
                        if package in result.stdout:
                            available_packages.append(package)
                            log_progress(f"   ✅ {package} available")
                    except Exception:
                        log_progress(f"   ⚠️ Could not check {package}")
                        continue
                
                if available_packages:
                    log_progress(f"📥 Installing firmware packages (may take 2-3 minutes)...")
                    cmd = ['apt', 'install', '-y'] + available_packages
                    result = subprocess.run(cmd, capture_output=True, timeout=300, text=True)  # 5 minutes
                    
                    if result.returncode == 0:
                        log_progress(f"✅ Installed firmware: {', '.join(available_packages)}")
                    else:
                        log_progress(f"⚠️ Some firmware installation issues - continuing...")
                else:
                    log_progress("⚠️ No additional firmware packages found")
                    
            except subprocess.TimeoutExpired:
                log_progress("⚠️ Firmware installation timed out - continuing...")
            except Exception as e:
                log_progress(f"⚠️ Firmware installation warning: {str(e)[:200]}...")
            log_progress("")
            
            # Step 6: Force WiFi interface detection
            log_progress("📡 STEP 6: Force WiFi Interface Detection", step=6)
            try:
                log_progress("🔄 Scanning for WiFi hardware...")
                
                # Method 1: Check iwconfig output
                try:
                    result = subprocess.run(['iwconfig'], capture_output=True, text=True, timeout=10)
                    wifi_interfaces = []
                    for line in result.stdout.split('\n'):
                        if 'IEEE 802.11' in line or 'ESSID:' in line:
                            interface = line.split()[0]
                            if interface and not interface.startswith('lo'):
                                wifi_interfaces.append(interface)
                    
                    for wifi_iface in set(wifi_interfaces):
                        log_progress(f"📡 Found WiFi interface: {wifi_iface}")
                        try:
                            subprocess.run(['ip', 'link', 'set', wifi_iface, 'up'], 
                                         capture_output=True, timeout=5)
                            log_progress(f"✅ Activated WiFi: {wifi_iface}")
                        except Exception:
                            log_progress(f"⚠️ Could not activate {wifi_iface}")
                            
                except Exception:
                    log_progress("⚠️ iwconfig not available")
                
                # Method 2: Check for wlan interfaces in /sys/class/net
                try:
                    if os.path.exists("/sys/class/net"):
                        for interface in os.listdir("/sys/class/net"):
                            if interface.startswith(('wlan', 'wlp', 'wlx')):
                                log_progress(f"📡 Found WiFi interface: {interface}")
                                try:
                                    subprocess.run(['ip', 'link', 'set', interface, 'up'], 
                                                 capture_output=True, timeout=5)
                                    log_progress(f"✅ Activated WiFi: {interface}")
                                except Exception:
                                    log_progress(f"⚠️ Could not activate {interface}")
                except Exception:
                    log_progress("⚠️ Could not scan /sys/class/net")
                    
            except Exception as e:
                log_progress(f"⚠️ WiFi detection error: {e}")
            log_progress("")
            
            # Step 7: Activate all network interfaces
            log_progress("🌐 STEP 7: Activating All Network Interfaces", step=7)
            activated_interfaces = []
            
            # Find all available interfaces
            try:
                if os.path.exists("/sys/class/net"):
                    for interface in os.listdir("/sys/class/net"):
                        if interface == "lo":  # Skip loopback
                            continue
                        if any(interface.startswith(prefix) for prefix in 
                              ["docker", "veth", "br-", "virbr", "tun", "tap"]):  # Skip virtual
                            continue
                        
                        try:
                            # Try to bring interface up
                            log_progress(f"🔄 Activating {interface}...")
                            subprocess.run(['ip', 'link', 'set', 'dev', interface, 'up'], 
                                         check=True, capture_output=True, timeout=10)
                            
                            # Get interface info
                            if os.path.exists(f"/sys/class/net/{interface}/address"):
                                with open(f"/sys/class/net/{interface}/address", 'r') as f:
                                    mac = f.read().strip()
                                
                                # Detect interface type
                                interface_type = "Network"
                                if interface.startswith(('wl', 'wlan')):
                                    interface_type = "WiFi"
                                elif interface.startswith(('eth', 'en')):
                                    interface_type = "Ethernet"
                                elif interface.startswith('usb'):
                                    interface_type = "USB"
                                
                                log_progress(f"✅ {interface} ({interface_type}) - MAC: {mac}")
                                activated_interfaces.append((interface, interface_type, mac))
                                
                        except Exception as e:
                            log_progress(f"⚠️ Could not activate {interface}: {e}")
                            
            except Exception as e:
                log_progress(f"❌ Error accessing network interfaces: {e}")
            log_progress("")
            
            # Step 8: Activate Bluetooth interfaces
            log_progress("📱 STEP 8: Activating Bluetooth Interfaces", step=8)
            bluetooth_found = False
            try:
                # Try hciconfig approach
                result = subprocess.run(['hciconfig'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and result.stdout:
                    import re
                    for line in result.stdout.split('\n'):
                        match = re.search(r'(hci\d+):', line)
                        if match:
                            bt_interface = match.group(1)
                            try:
                                log_progress(f"🔄 Activating {bt_interface}...")
                                subprocess.run(['hciconfig', bt_interface, 'up'], 
                                             capture_output=True, timeout=10)
                                subprocess.run(['hciconfig', bt_interface, 'piscan'], 
                                             capture_output=True, timeout=5)
                                log_progress(f"✅ Bluetooth: {bt_interface}")
                                bluetooth_found = True
                            except Exception:
                                log_progress(f"⚠️ Could not activate {bt_interface}")
                
                # Check sysfs approach
                if os.path.exists("/sys/class/bluetooth"):
                    for bt_device in os.listdir("/sys/class/bluetooth"):
                        if bt_device.startswith("hci"):
                            bt_mac_file = f"/sys/class/bluetooth/{bt_device}/address"
                            if os.path.exists(bt_mac_file):
                                with open(bt_mac_file, 'r') as f:
                                    bt_mac = f.read().strip()
                                log_progress(f"✅ Bluetooth: {bt_device} - MAC: {bt_mac}")
                                bluetooth_found = True
                
                if not bluetooth_found:
                    log_progress("⚠️ No Bluetooth interfaces found")
                    
            except Exception as e:
                log_progress(f"⚠️ Bluetooth activation error: {e}")
            log_progress("")
            
            # Final steps: Restart network services
            log_progress("🔄 FINAL: Restarting Network Services")
            try:
                # Restart NetworkManager
                result = subprocess.run(['systemctl', 'is-active', 'NetworkManager'], 
                                      capture_output=True)
                if result.returncode == 0:
                    log_progress("🔄 Restarting NetworkManager...")
                    subprocess.run(['systemctl', 'restart', 'NetworkManager'], 
                                 capture_output=True, timeout=20)
                    log_progress("✅ NetworkManager restarted")
                
                # Restart wpa_supplicant if active
                result = subprocess.run(['systemctl', 'is-active', 'wpa_supplicant'], 
                                      capture_output=True)
                if result.returncode == 0:
                    subprocess.run(['systemctl', 'restart', 'wpa_supplicant'], 
                                 capture_output=True, timeout=15)
                    log_progress("✅ wpa_supplicant restarted")
                    
            except Exception as e:
                log_progress(f"⚠️ Service restart warning: {e}")
            log_progress("")
            
            # Final summary
            progress_bar['value'] = 100
            progress_label.config(text="Complete!")
            log_progress("✅ ACTIVATION COMPLETE!")
            log_progress("=" * 50)
            total_interfaces = len(activated_interfaces) + (1 if bluetooth_found else 0)
            log_progress(f"🎉 Found and activated {total_interfaces} network interfaces!")
            log_progress("")
            log_progress("📋 Summary:")
            for iface, itype, mac in activated_interfaces:
                log_progress(f"   • {iface} ({itype}) - {mac}")
            if bluetooth_found:
                log_progress(f"   • Bluetooth interfaces activated")
            log_progress("")
            log_progress("🔄 Now click 'Close & Scan Interfaces' to see all available interfaces!")
            log_progress("")
            log_progress("💡 TIP: If WiFi still not visible, try:")
            log_progress("   • Check if WiFi hardware is present: lspci | grep -i wireless")
            log_progress("   • Manual activation: sudo ip link set wlan0 up")
            log_progress("   • Alternative: nmcli device wifi list")
            
            # Add Close button
            button_frame = tk.Frame(progress_window)
            button_frame.pack(pady=10)
            
            def close_and_scan():
                progress_window.destroy()
                # Wait a moment for interfaces to settle
                time.sleep(2)
                self.scan_interfaces()
            
            tk.Button(button_frame, text="Close & Scan Interfaces", 
                     command=close_and_scan, bg='lightgreen', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
            tk.Button(button_frame, text="Close", 
                     command=progress_window.destroy, font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            progress_bar['value'] = 0
            progress_label.config(text="Error!")
            log_progress(f"❌ CRITICAL ERROR: {e}")
            log_progress("Please check the logs and try manual activation.")
            messagebox.showerror("Error", f"Interface activation failed: {e}")
            
            # Add Close button for error case
            button_frame = tk.Frame(progress_window)
            button_frame.pack(pady=10)
            tk.Button(button_frame, text="Close", 
                     command=progress_window.destroy).pack()

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = MacaronApp(root)
    
    # Handle window closing
    def on_closing():
        if app.auto_randomize_active:
            app.stop_auto_randomization()
        
        # Cleanup and final logging
        app.logger.info("Performing cleanup before exit...")
        
        # Close log handlers
        for handler in app.logger.handlers[:]:
            handler.close()
            app.logger.removeHandler(handler)
        
        # Clear sensitive data
        app.interfaces.clear()
        app.original_macs.clear()
        
        app.logger.info("MACARON application closed")
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 