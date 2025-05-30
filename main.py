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
        """Configure modern styling for the application - Enhanced Modern Theme"""
        style = ttk.Style()
        
        # Choose a modern theme base
        try:
            style.theme_use('clam')
        except:
            style.theme_use('default')
        
        # Modern Color Palette
        self.colors = {
            'bg_primary': '#1e1e2e',      # Dark background
            'bg_secondary': '#313244',    # Secondary dark
            'bg_tertiary': '#45475a',     # Tertiary dark
            'accent_primary': '#89b4fa',  # Blue accent
            'accent_success': '#a6e3a1',  # Green success
            'accent_warning': '#f9e2af',  # Yellow warning
            'accent_error': '#f38ba8',    # Red error
            'text_primary': '#cdd6f4',    # Light text
            'text_secondary': '#bac2de',  # Secondary text
            'text_muted': '#9399b2',      # Muted text
            'border': '#6c7086',          # Border color
            'shadow': '#11111b'           # Shadow color
        }
        
        # Configure ttk styles with modern colors
        style.configure('Modern.TFrame', 
                       background=self.colors['bg_primary'],
                       borderwidth=0)
        
        style.configure('Card.TFrame', 
                       background=self.colors['bg_secondary'],
                       relief='flat',
                       borderwidth=1)
        
        style.configure('Header.TLabel', 
                       background=self.colors['bg_primary'],
                       foreground=self.colors['accent_primary'],
                       font=('Segoe UI', 18, 'bold'))
        
        style.configure('Subheader.TLabel', 
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 12, 'bold'))
        
        style.configure('Modern.TLabel', 
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10))
        
        style.configure('Success.TLabel', 
                       background=self.colors['bg_primary'],
                       foreground=self.colors['accent_success'],
                       font=('Segoe UI', 10, 'bold'))
        
        style.configure('Warning.TLabel', 
                       background=self.colors['bg_primary'],
                       foreground=self.colors['accent_warning'],
                       font=('Segoe UI', 10, 'bold'))
        
        style.configure('Error.TLabel', 
                       background=self.colors['bg_primary'],
                       foreground=self.colors['accent_error'],
                       font=('Segoe UI', 10, 'bold'))
        
        # Modern button styles
        style.configure('Modern.TButton',
                       background=self.colors['accent_primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 10, 'bold'),
                       padding=(20, 10))
        
        style.map('Modern.TButton',
                 background=[('active', self.colors['accent_primary']),
                           ('pressed', '#74c0fc')])
        
        style.configure('Success.TButton',
                       background=self.colors['accent_success'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 10, 'bold'),
                       padding=(20, 10))
        
        style.configure('Warning.TButton',
                       background=self.colors['accent_warning'],
                       foreground='black',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 10, 'bold'),
                       padding=(20, 10))
        
        style.configure('Danger.TButton',
                       background=self.colors['accent_error'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 10, 'bold'),
                       padding=(20, 10))
        
        # Modern treeview
        style.configure('Modern.Treeview',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       fieldbackground=self.colors['bg_secondary'],
                       borderwidth=0,
                       font=('Segoe UI', 10))
        
        style.configure('Modern.Treeview.Heading',
                       background=self.colors['bg_tertiary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=0,
                       font=('Segoe UI', 11, 'bold'))
        
        # Modern progress bar
        style.configure('Modern.Horizontal.TProgressbar',
                       background=self.colors['accent_primary'],
                       troughcolor=self.colors['bg_tertiary'],
                       borderwidth=0,
                       lightcolor=self.colors['accent_primary'],
                       darkcolor=self.colors['accent_primary'])
        
        # Modern spinbox and entry
        style.configure('Modern.TSpinbox',
                       fieldbackground=self.colors['bg_secondary'],
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       insertcolor=self.colors['text_primary'])
        
        # Modern labelframe
        style.configure('Modern.TLabelframe',
                       background=self.colors['bg_primary'],
                       borderwidth=1,
                       relief='flat')
        
        style.configure('Modern.TLabelframe.Label',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['accent_primary'],
                       font=('Segoe UI', 12, 'bold'))
    
    def create_widgets(self):
        """Create the modern GUI interface"""
        # Set window background
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Main frame with modern styling
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'], padx=20, pady=20)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Modern header with gradient effect
        header_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'], height=80)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)
        
        # Title with modern styling
        title_label = tk.Label(header_frame, 
                              text="🎯 MACARON", 
                              bg=self.colors['bg_primary'],
                              fg=self.colors['accent_primary'],
                              font=('Segoe UI', 24, 'bold'))
        title_label.grid(row=0, column=0)
        
        subtitle_label = tk.Label(header_frame, 
                                 text="Advanced MAC Address Randomization Tool",
                                 bg=self.colors['bg_primary'],
                                 fg=self.colors['text_secondary'],
                                 font=('Segoe UI', 12))
        subtitle_label.grid(row=1, column=0, pady=(5, 0))
        
        # Status indicator
        self.status_frame = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        self.status_frame.grid(row=0, column=1, rowspan=2, padx=(20, 0))
        
        self.status_indicator = tk.Label(self.status_frame,
                                        text="🟢",
                                        bg=self.colors['bg_primary'],
                                        font=('Segoe UI', 16))
        self.status_indicator.grid(row=0, column=0)
        
        self.status_text = tk.Label(self.status_frame,
                                   text="Ready",
                                   bg=self.colors['bg_primary'],
                                   fg=self.colors['accent_success'],
                                   font=('Segoe UI', 10, 'bold'))
        self.status_text.grid(row=1, column=0)
        
        # Interface list frame - Modern card design
        interface_card = tk.Frame(main_frame, bg=self.colors['bg_secondary'], 
                                 relief='flat', bd=1)
        interface_card.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        interface_card.columnconfigure(0, weight=1)
        
        # Card header
        card_header = tk.Frame(interface_card, bg=self.colors['bg_tertiary'], height=50)
        card_header.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=1, pady=1)
        card_header.columnconfigure(0, weight=1)
        
        interface_title = tk.Label(card_header,
                                  text="🌐 Network Interfaces",
                                  bg=self.colors['bg_tertiary'],
                                  fg=self.colors['text_primary'],
                                  font=('Segoe UI', 14, 'bold'))
        interface_title.grid(row=0, column=0, padx=20, pady=15, sticky=tk.W)
        
        # Interface count badge
        self.interface_count = tk.Label(card_header,
                                       text="0",
                                       bg=self.colors['accent_primary'],
                                       fg='white',
                                       font=('Segoe UI', 10, 'bold'),
                                       padx=10, pady=5)
        self.interface_count.grid(row=0, column=1, padx=20, pady=15, sticky=tk.E)
        
        # Treeview container
        tree_container = tk.Frame(interface_card, bg=self.colors['bg_secondary'])
        tree_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=(0, 20))
        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)
        
        # Modern treeview
        columns = ('Interface', 'Current MAC', 'Original MAC', 'Status')
        self.tree = ttk.Treeview(tree_container, columns=columns, show='headings', 
                                height=8, style='Modern.Treeview')
        
        # Configure columns with modern headers
        column_configs = {
            'Interface': {'width': 200, 'text': '🔌 Interface'},
            'Current MAC': {'width': 150, 'text': '🏷️ Current MAC'},
            'Original MAC': {'width': 150, 'text': '🔄 Original MAC'},
            'Status': {'width': 120, 'text': '📊 Status'}
        }
        
        for col, config in column_configs.items():
            self.tree.heading(col, text=config['text'])
            self.tree.column(col, width=config['width'])
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Modern scrollbar
        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Modern control buttons
        button_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        button_frame.grid(row=2, column=0, pady=(0, 20))
        
        # Button configurations with icons and colors
        button_configs = [
            {"text": "🔍 Scan", "command": self.scan_interfaces, "style": "Modern.TButton"},
            {"text": "⚡ Enable All", "command": self.enable_all_interfaces, "style": "Warning.TButton"},
            {"text": "🎲 Random Selected", "command": self.randomize_selected, "style": "Success.TButton"},
            {"text": "🎯 Random All", "command": self.randomize_all, "style": "Success.TButton"},
            {"text": "🔄 Restore", "command": self.restore_original, "style": "Modern.TButton"},
            {"text": "🔧 Diagnostics", "command": self.run_diagnostics, "style": "Modern.TButton"}
        ]
        
        for i, config in enumerate(button_configs):
            btn = ttk.Button(button_frame, **config)
            btn.grid(row=0, column=i, padx=8, pady=5)
        
        # Auto-randomization card
        auto_card = tk.Frame(main_frame, bg=self.colors['bg_secondary'], relief='flat', bd=1)
        auto_card.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        auto_card.columnconfigure(1, weight=1)
        
        # Auto card header
        auto_header = tk.Frame(auto_card, bg=self.colors['bg_tertiary'])
        auto_header.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), padx=1, pady=1)
        
        auto_title = tk.Label(auto_header,
                             text="⏰ Automatic Randomization",
                             bg=self.colors['bg_tertiary'],
                             fg=self.colors['text_primary'],
                             font=('Segoe UI', 14, 'bold'))
        auto_title.grid(row=0, column=0, padx=20, pady=15, sticky=tk.W)
        
        # Auto controls
        auto_controls = tk.Frame(auto_card, bg=self.colors['bg_secondary'])
        auto_controls.grid(row=1, column=0, columnspan=4, padx=20, pady=20, sticky=(tk.W, tk.E))
        
        interval_label = tk.Label(auto_controls,
                                 text="⏱️ Interval (minutes):",
                                 bg=self.colors['bg_secondary'],
                                 fg=self.colors['text_primary'],
                                 font=('Segoe UI', 11))
        interval_label.grid(row=0, column=0, padx=(0, 15), sticky=tk.W)
        
        self.interval_var = tk.StringVar(value="15")
        interval_spinbox = ttk.Spinbox(auto_controls, from_=1, to=1440, width=10,
                                     textvariable=self.interval_var,
                                     style='Modern.TSpinbox',
                                     font=('Segoe UI', 10))
        interval_spinbox.grid(row=0, column=1, padx=(0, 20))
        
        self.auto_button = ttk.Button(auto_controls, 
                                     text="▶️ Start Auto-Randomization",
                                     command=self.toggle_auto_randomization,
                                     style='Success.TButton')
        self.auto_button.grid(row=0, column=2, padx=(0, 20))
        
        # Auto status with modern indicator
        auto_status_frame = tk.Frame(auto_controls, bg=self.colors['bg_secondary'])
        auto_status_frame.grid(row=0, column=3, sticky=tk.E)
        
        self.auto_status_indicator = tk.Label(auto_status_frame,
                                             text="⏹️",
                                             bg=self.colors['bg_secondary'],
                                             font=('Segoe UI', 14))
        self.auto_status_indicator.grid(row=0, column=0)
        
        self.auto_status_label = tk.Label(auto_status_frame,
                                         text="Stopped",
                                         bg=self.colors['bg_secondary'],
                                         fg=self.colors['text_muted'],
                                         font=('Segoe UI', 10, 'bold'))
        self.auto_status_label.grid(row=0, column=1, padx=(5, 0))
        
        # Modern log frame
        log_card = tk.Frame(main_frame, bg=self.colors['bg_secondary'], relief='flat', bd=1)
        log_card.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_card.columnconfigure(0, weight=1)
        log_card.rowconfigure(1, weight=1)
        
        # Log header
        log_header = tk.Frame(log_card, bg=self.colors['bg_tertiary'])
        log_header.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=1, pady=1)
        log_header.columnconfigure(0, weight=1)
        
        log_title = tk.Label(log_header,
                            text="📝 Activity Log",
                            bg=self.colors['bg_tertiary'],
                            fg=self.colors['text_primary'],
                            font=('Segoe UI', 14, 'bold'))
        log_title.grid(row=0, column=0, padx=20, pady=15, sticky=tk.W)
        
        # Log clear button
        clear_log_btn = tk.Button(log_header,
                                 text="🗑️ Clear",
                                 bg=self.colors['accent_error'],
                                 fg='white',
                                 font=('Segoe UI', 9, 'bold'),
                                 borderwidth=0,
                                 padx=15, pady=5,
                                 command=self.clear_log)
        clear_log_btn.grid(row=0, column=1, padx=20, pady=15, sticky=tk.E)
        
        # Log text area
        log_container = tk.Frame(log_card, bg=self.colors['bg_secondary'])
        log_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=(0, 20))
        log_container.columnconfigure(0, weight=1)
        log_container.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_container, 
                               height=8, 
                               bg=self.colors['bg_primary'],
                               fg=self.colors['text_primary'],
                               font=('Cascadia Code', 10),
                               borderwidth=0,
                               insertbackground=self.colors['accent_primary'],
                               selectbackground=self.colors['accent_primary'],
                               wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Log scrollbar
        log_scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        # Configure grid weights for responsive design
        main_frame.rowconfigure(1, weight=2)  # Interface list takes more space
        main_frame.rowconfigure(4, weight=1)  # Log area
        
        # Configure text tags for colored log output
        self.log_text.tag_configure("success", foreground=self.colors['accent_success'])
        self.log_text.tag_configure("warning", foreground=self.colors['accent_warning'])
        self.log_text.tag_configure("error", foreground=self.colors['accent_error'])
        self.log_text.tag_configure("info", foreground=self.colors['accent_primary'])
        self.log_text.tag_configure("timestamp", foreground=self.colors['text_muted'])
        
        self.log("🚀 MACARON initialized successfully", "success")
        self.update_status("Ready", "success")
    
    def clear_log(self):
        """Clear the log display"""
        self.log_text.delete('1.0', tk.END)
        self.log("📝 Log cleared", "info")
    
    def update_status(self, message, status_type="info"):
        """Update the status indicator"""
        status_configs = {
            "success": {"icon": "🟢", "color": self.colors['accent_success']},
            "warning": {"icon": "🟡", "color": self.colors['accent_warning']},
            "error": {"icon": "🔴", "color": self.colors['accent_error']},
            "info": {"icon": "🔵", "color": self.colors['accent_primary']},
            "working": {"icon": "⚪", "color": self.colors['text_secondary']}
        }
        
        config = status_configs.get(status_type, status_configs["info"])
        self.status_indicator.config(text=config["icon"])
        self.status_text.config(text=message, fg=config["color"])
    
    def log(self, message, log_type="info"):
        """Add message to the log display with modern formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Insert timestamp
        self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Add appropriate emoji and styling based on message content
        if any(keyword in message.lower() for keyword in ['success', '✅', 'completed', 'installed']):
            log_type = "success"
            if not message.startswith('✅'):
                message = f"✅ {message}"
        elif any(keyword in message.lower() for keyword in ['warning', '⚠️', 'timeout', 'failed']):
            log_type = "warning"
            if not message.startswith('⚠️'):
                message = f"⚠️ {message}"
        elif any(keyword in message.lower() for keyword in ['error', '❌', 'critical']):
            log_type = "error"
            if not message.startswith('❌'):
                message = f"❌ {message}"
        elif any(keyword in message.lower() for keyword in ['info', '📝', 'scanning', 'checking']):
            log_type = "info"
            if not message.startswith(('📝', '🔍', '📊')):
                message = f"📝 {message}"
        
        # Insert message with appropriate styling
        self.log_text.insert(tk.END, message + "\n", log_type)
        self.log_text.see(tk.END)
        
        # Also log to file
        self.logger.info(message)
    
    def scan_interfaces(self):
        """Scan for network interfaces with modern UI updates"""
        self.update_status("Scanning interfaces...", "working")
        
        try:
            self.log("🔍 Scanning network interfaces...", "info")
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            self.interfaces.clear()
            detected_interfaces = {}
            
            # Method 1: Standard network interfaces (WiFi, Ethernet)
            try:
                result = subprocess.run(['ip', 'link', 'show'], 
                                      capture_output=True, text=True, check=True)
                self.log("📡 Scanning standard network interfaces...")
                
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
                                interface_type = detected_interfaces[interface]['type']
                                type_icon = self._get_interface_icon(interface_type)
                                self.log(f"{type_icon} Found {interface_type}: {interface} ({mac_address})")
                    i += 1
                    
            except subprocess.CalledProcessError:
                self.log("⚠️ 'ip link show' command failed", "warning")
            
            # Method 2: Alternative detection using 'ls /sys/class/net'
            try:
                if len(detected_interfaces) == 0:
                    self.log("🔄 Trying alternative interface detection...")
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
                                        interface_type = detected_interfaces[interface]['type']
                                        type_icon = self._get_interface_icon(interface_type)
                                        self.log(f"{type_icon} Found via sysfs {interface_type}: {interface} ({mac_address})")
                            except FileNotFoundError:
                                continue
                                
            except subprocess.CalledProcessError:
                self.log("⚠️ Alternative detection failed", "warning")
            
            # Method 3: Bluetooth interfaces
            try:
                self.log("📱 Scanning Bluetooth interfaces...")
                
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
                            self.log(f"📱 Found Bluetooth: {interface} ({mac_address})")
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
                                            self.log(f"📱 Found Bluetooth via sysfs: {hci_device} ({mac_address})")
                            except FileNotFoundError:
                                continue
                except subprocess.CalledProcessError:
                    pass
                    
            except Exception as e:
                self.log(f"📱 Bluetooth detection error: {e}", "error")
            
            # Method 4: USB Network devices
            try:
                self.log("🔌 Scanning USB network devices...")
                result = subprocess.run(['lsusb'], capture_output=True, text=True, check=True)
                for line in result.stdout.split('\n'):
                    if 'Network' in line or 'Ethernet' in line or 'Wireless' in line or 'WiFi' in line:
                        self.log(f"🔌 USB Network device detected: {line.strip()}")
            except subprocess.CalledProcessError:
                pass
            
            # Populate the interface list and GUI
            for interface, info in detected_interfaces.items():
                mac = info['mac']
                self.interfaces[interface] = mac
                
                # Store original MAC if not already stored
                if interface not in self.original_macs:
                    self.original_macs[interface] = mac
                
                # Add to treeview with enhanced information and icons
                original_mac = self.original_macs.get(interface, mac)
                status = "🟢 Original" if mac == original_mac else "🔄 Randomized"
                
                # Add interface with icon
                type_icon = self._get_interface_icon(info['type'])
                display_name = f"{type_icon} {interface}"
                
                self.tree.insert('', tk.END, values=(display_name, mac, original_mac, status))
            
            # Update interface count badge
            total_found = len(detected_interfaces)
            self.interface_count.config(text=str(total_found))
            
            if total_found > 0:
                self.log(f"🎉 Found {total_found} network interfaces total", "success")
                self.update_status(f"Found {total_found} interfaces", "success")
            else:
                self.log("❌ No network interfaces found", "error")
                self.update_status("No interfaces found", "error")
                messagebox.showwarning("No Interfaces", 
                                     "No network interfaces found.\n\n"
                                     "Make sure:\n"
                                     "• You're running with sudo\n"
                                     "• Network hardware is enabled\n"
                                     "• Interfaces are not all virtual")
            
        except Exception as e:
            error_msg = f"Unexpected error during interface scan: {e}"
            self.log(error_msg, "error")
            self.update_status("Scan failed", "error")
            messagebox.showerror("Error", error_msg)
    
    def _get_interface_icon(self, interface_type):
        """Get appropriate icon for interface type"""
        icons = {
            'WiFi': '📶',
            'Ethernet': '🌐',
            'Bluetooth': '📱',
            'USB-Ethernet': '🔌',
            'Bonded': '🔗',
            'Team': '👥',
            'CAN-Bus': '🚗',
            'Network': '💻'
        }
        return icons.get(interface_type, '💻')
    
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
                self.log(f"Invalid interface name: {interface_name}", "error")
                return False
            
            if not self.validate_mac_address(new_mac, allow_global=is_restoration):
                self.log(f"Invalid MAC address: {new_mac}", "error")
                return False
            
            # Handle different interface types
            if interface_type == 'Bluetooth':
                return self._change_bluetooth_mac(interface_name, new_mac)
            else:
                return self._change_network_mac(interface_name, new_mac)
                
        except Exception as e:
            error_msg = f"Unexpected error changing MAC for {interface}: {e}"
            self.log(error_msg, "error")
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
            self.log(f"Changed {interface} MAC to {new_mac}", "success")
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
                self.log(f"Changed {interface} MAC to {new_mac} (via ifconfig)", "success")
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
                    self.log(f"Changed {interface} MAC to {new_mac} (via sysfs)", "success")
                    return True
                    
                except (subprocess.CalledProcessError, PermissionError, FileNotFoundError):
                    self.log(f"Failed to change MAC for {interface} - all methods failed", "error")
                    return False
    
    def _change_bluetooth_mac(self, interface, new_mac):
        """Change MAC address for Bluetooth interfaces"""
        try:
            self.log(f"🖇 Attempting to change Bluetooth MAC for {interface}")
            
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
                    self.log(f"🖇 Successfully changed Bluetooth MAC for {interface} to {new_mac}", "success")
                    return True
                else:
                    self.log(f"🖇 Bluetooth MAC change not supported for {interface}", "warning")
                    
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
                self.log(f"🖇 Changed Bluetooth MAC for {interface} to {new_mac} (via bdaddr)", "success")
                return True
                
            except subprocess.CalledProcessError:
                pass
            
            # Method 3: Inform user about limitations
            self.log(f"🖇 Bluetooth MAC randomization for {interface} requires hardware support")
            self.log("🖇 Many Bluetooth adapters have fixed MAC addresses in firmware")
            self.log("🖇 Consider using a USB Bluetooth adapter that supports MAC changing")
            
            # For logging purposes, update the stored MAC even if change failed
            # This helps track which interfaces were attempted
            messagebox.showinfo("Bluetooth MAC Info", 
                              f"Bluetooth MAC change attempted for {interface}.\n\n"
                              "Note: Many Bluetooth adapters have fixed MAC addresses.\n"
                              "If change failed, consider using a different adapter.")
            
            return False
            
        except Exception as e:
            self.log(f"🖇 Error changing Bluetooth MAC for {interface}: {e}", "error")
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
        self.log(f"🎉 Successfully randomized {success_count} interfaces", "success")
    
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
        self.log(f"🎉 Successfully randomized {success_count}/{len(self.interfaces)} interfaces", "success")
    
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
        self.log(f"🎉 Successfully restored {success_count}/{len(self.original_macs)} interfaces", "success")
    
    def toggle_auto_randomization(self):
        """Start or stop automatic randomization"""
        if not self.auto_randomize_active:
            self.start_auto_randomization()
        else:
            self.stop_auto_randomization()
    
    def start_auto_randomization(self):
        """Start automatic randomization with modern UI updates"""
        try:
            self.interval_minutes = int(self.interval_var.get())
            if self.interval_minutes < 1:
                raise ValueError("Interval must be at least 1 minute")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid interval: {e}")
            return
        
        self.auto_randomize_active = True
        self.auto_button.config(text="⏹️ Stop Auto-Randomization", style='Danger.TButton')
        self.auto_status_indicator.config(text="🔄")
        self.auto_status_label.config(text="Running", fg=self.colors['accent_success'])
        
        # Start background thread
        self.auto_thread = threading.Thread(target=self.auto_randomization_worker, daemon=True)
        self.auto_thread.start()
        
        self.log(f"▶️ Started automatic randomization (interval: {self.interval_minutes} minutes)", "success")
        self.update_status("Auto-randomization active", "working")
    
    def stop_auto_randomization(self):
        """Stop automatic randomization with modern UI updates"""
        self.auto_randomize_active = False
        self.auto_button.config(text="▶️ Start Auto-Randomization", style='Success.TButton')
        self.auto_status_indicator.config(text="⏹️")
        self.auto_status_label.config(text="Stopped", fg=self.colors['text_muted'])
        
        self.log("⏹️ Stopped automatic randomization", "info")
        self.update_status("Ready", "success")
    
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
        self.log(f"🎉 Auto-randomization: Updated {success_count}/{len(self.interfaces)} interfaces", "success")

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
        """Enable all network interfaces (WiFi, Bluetooth, Ethernet, USB) - Enhanced with Real-time Progress"""
        
        # Create progress window
        progress_window = tk.Toplevel(self.root)
        progress_window.title("MACARON - Enable All Interfaces")
        progress_window.geometry("750x650")
        progress_window.resizable(False, False)
        
        # Center the window
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        # Create scrollable text widget for progress
        progress_text = scrolledtext.ScrolledText(progress_window, wrap=tk.WORD, font=('Courier', 9))
        progress_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Enhanced progress frame
        progress_frame = tk.Frame(progress_window)
        progress_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        # Main progress bar
        main_progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        main_progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Step progress bar (for sub-operations)
        step_progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate', length=50)
        step_progress_bar.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Status labels
        status_frame = tk.Frame(progress_window)
        status_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        main_status_label = tk.Label(status_frame, text="Initializing...", font=('Arial', 10, 'bold'))
        main_status_label.pack(anchor=tk.W)
        
        sub_status_label = tk.Label(status_frame, text="", font=('Arial', 9))
        sub_status_label.pack(anchor=tk.W)
        
        # Animation control
        animation_active = False
        
        def start_step_animation():
            nonlocal animation_active
            animation_active = True
            step_progress_bar.start(10)
        
        def stop_step_animation():
            nonlocal animation_active
            animation_active = False
            step_progress_bar.stop()
            
        def log_progress(message, step=None, total_steps=8, substep=None):
            timestamp = datetime.now().strftime("%H:%M:%S")
            progress_text.insert(tk.END, f"[{timestamp}] {message}\n")
            progress_text.see(tk.END)
            
            if step:
                main_progress_bar['value'] = (step / total_steps) * 100
                main_status_label.config(text=f"Step {step}/{total_steps}")
            
            if substep:
                sub_status_label.config(text=substep)
            
            progress_window.update()
            self.log(message)
        
        def run_command_with_progress(cmd, description, timeout=60):
            """Run command with real-time progress feedback"""
            start_step_animation()
            sub_status_label.config(text=f"Executing: {description}")
            progress_window.update()
            
            try:
                # For apt commands, show more detailed progress
                if cmd[0] == 'apt':
                    return run_apt_with_progress(cmd, description, timeout)
                else:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
                    stop_step_animation()
                    return result
            except subprocess.TimeoutExpired:
                stop_step_animation()
                log_progress(f"⚠️ {description} timed out after {timeout} seconds")
                return None
            except Exception as e:
                stop_step_animation()
                log_progress(f"⚠️ Error in {description}: {e}")
                return None
        
        def run_apt_with_progress(cmd, description, timeout):
            """Run apt command with detailed progress"""
            try:
                # Start the process
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True,
                    env={**os.environ, 'DEBIAN_FRONTEND': 'noninteractive'}
                )
                
                start_time = time.time()
                output_lines = []
                error_lines = []
                
                # Monitor the process
                while process.poll() is None:
                    # Check timeout
                    if time.time() - start_time > timeout:
                        process.terminate()
                        log_progress(f"⚠️ {description} timed out after {timeout} seconds")
                        stop_step_animation()
                        return None
                    
                    # Read output
                    try:
                        stdout_line = process.stdout.readline()
                        if stdout_line:
                            line = stdout_line.strip()
                            output_lines.append(line)
                            
                            # Parse apt output for progress
                            if 'Reading package lists' in line:
                                sub_status_label.config(text="📖 Reading package lists...")
                            elif 'Building dependency tree' in line:
                                sub_status_label.config(text="🔧 Building dependency tree...")
                            elif 'Reading state information' in line:
                                sub_status_label.config(text="📊 Reading state information...")
                            elif 'The following NEW packages will be installed' in line:
                                sub_status_label.config(text="📦 Preparing new packages...")
                            elif 'Need to get' in line:
                                # Extract download size
                                if 'B' in line:
                                    size_info = line.split('Need to get ')[1].split(' ')[0]
                                    sub_status_label.config(text=f"📥 Downloading {size_info}...")
                            elif 'Get:' in line and 'http' in line:
                                # Show which package is being downloaded
                                try:
                                    package = line.split()[3] if len(line.split()) > 3 else "packages"
                                    sub_status_label.config(text=f"📥 Downloading {package}...")
                                except:
                                    sub_status_label.config(text="📥 Downloading packages...")
                            elif 'Unpacking' in line:
                                try:
                                    package = line.split()[1] if len(line.split()) > 1 else "package"
                                    sub_status_label.config(text=f"📦 Unpacking {package}...")
                                except:
                                    sub_status_label.config(text="📦 Unpacking packages...")
                            elif 'Setting up' in line:
                                try:
                                    package = line.split()[2] if len(line.split()) > 2 else "package"
                                    sub_status_label.config(text=f"⚙️ Setting up {package}...")
                                except:
                                    sub_status_label.config(text="⚙️ Setting up packages...")
                            
                            progress_window.update()
                    except:
                        pass
                    
                    time.sleep(0.1)
                
                # Get final output
                stdout, stderr = process.communicate(timeout=5)
                if stdout:
                    output_lines.extend(stdout.strip().split('\n'))
                if stderr:
                    error_lines.extend(stderr.strip().split('\n'))
                
                stop_step_animation()
                
                # Create mock result object
                class MockResult:
                    def __init__(self, returncode, stdout, stderr):
                        self.returncode = returncode
                        self.stdout = '\n'.join(output_lines) if output_lines else ''
                        self.stderr = '\n'.join(error_lines) if error_lines else ''
                
                return MockResult(process.returncode, '\n'.join(output_lines), '\n'.join(error_lines))
                
            except Exception as e:
                stop_step_animation()
                log_progress(f"⚠️ Error in {description}: {e}")
                return None
        
        log_progress("🔧 MACARON - Enable All Network Interfaces")
        log_progress("=" * 60)
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
            time.sleep(0.5)
            log_progress("")
            
            # Step 2: Unblock RF interfaces (WiFi/Bluetooth)
            log_progress("📡 STEP 2: Unblocking RF Interfaces", step=2)
            try:
                # Check if rfkill is available
                subprocess.run(['which', 'rfkill'], check=True, capture_output=True)
                log_progress("🔍 Checking RF kill status...", substep="Scanning RF devices...")
                
                # Show current status
                result = subprocess.run(['rfkill', 'list'], capture_output=True, text=True)
                blocked_count = result.stdout.count("Soft blocked: yes")
                if blocked_count > 0:
                    log_progress(f"🚫 Found {blocked_count} blocked interfaces")
                    log_progress("🔓 Unblocking all RF interfaces...", substep="Unblocking RF kill...")
                    subprocess.run(['rfkill', 'unblock', 'all'], check=True, capture_output=True)
                    log_progress("✅ All RF interfaces unblocked")
                else:
                    log_progress("✅ No blocked RF interfaces found")
                    
            except subprocess.CalledProcessError:
                log_progress("⚠️ rfkill not available - installing...", substep="Installing rfkill...")
                
                # Update package list first
                result = run_command_with_progress(['apt', 'update', '-q'], "Updating package list", 90)
                if result and result.returncode == 0:
                    log_progress("✅ Package list updated")
                    
                    # Install rfkill
                    result = run_command_with_progress(['apt', 'install', '-y', 'rfkill'], "Installing rfkill", 120)
                    if result and result.returncode == 0:
                        subprocess.run(['rfkill', 'unblock', 'all'], capture_output=True)
                        log_progress("✅ rfkill installed and interfaces unblocked")
                    else:
                        log_progress("⚠️ Could not install rfkill")
                else:
                    log_progress("⚠️ Could not update package list")
                    
            log_progress("")
            
            # Step 3: Load network kernel modules
            log_progress("🔧 STEP 3: Loading Network Kernel Modules", step=3)
            modules = ["iwlwifi", "ath9k", "ath9k_htc", "rt2800usb", "rt2800pci", 
                      "rtl8188eu", "rtl8192cu", "rtl8812au", "btusb"]
            
            for i, module in enumerate(modules):
                sub_status_label.config(text=f"Checking module {i+1}/{len(modules)}: {module}")
                progress_window.update()
                
                try:
                    # Check if module is already loaded
                    result = subprocess.run(['lsmod'], capture_output=True, text=True)
                    if module in result.stdout:
                        log_progress(f"✅ {module} already loaded")
                    else:
                        log_progress(f"🔄 Loading {module} module...", substep=f"Loading {module}...")
                        start_step_animation()
                        subprocess.run(['modprobe', module], check=True, capture_output=True)
                        stop_step_animation()
                        log_progress(f"✅ Loaded {module} module")
                        
                        # Small delay to let module initialize
                        if module.startswith(('iwl', 'ath', 'rt')):
                            sub_status_label.config(text=f"Initializing {module}...")
                            progress_window.update()
                            time.sleep(1)
                            
                except subprocess.CalledProcessError:
                    stop_step_animation()
                    log_progress(f"⚠️ Could not load {module} (may not be available)")
                    
            sub_status_label.config(text="")
            log_progress("")
            
            # Step 4: Bluetooth service activation
            log_progress("📱 STEP 4: Bluetooth Service Activation", step=4)
            try:
                # Check if bluetooth service exists
                result = subprocess.run(['systemctl', 'is-available', 'bluetooth'], capture_output=True)
                if result.returncode == 0:
                    log_progress("🔄 Starting Bluetooth service...", substep="Starting bluetooth.service...")
                    start_step_animation()
                    subprocess.run(['systemctl', 'start', 'bluetooth'], capture_output=True, timeout=20)
                    subprocess.run(['systemctl', 'enable', 'bluetooth'], capture_output=True, timeout=10)
                    stop_step_animation()
                    
                    # Try to power on bluetooth
                    try:
                        subprocess.run(['which', 'bluetoothctl'], check=True, capture_output=True)
                        sub_status_label.config(text="Powering on Bluetooth...")
                        progress_window.update()
                        process = subprocess.Popen(['bluetoothctl'], stdin=subprocess.PIPE, 
                                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        process.communicate(input=b'power on\nquit\n', timeout=10)
                        log_progress("✅ Bluetooth service started and powered on")
                    except Exception:
                        log_progress("✅ Bluetooth service started")
                else:
                    log_progress("⚠️ Bluetooth not installed - installing complete stack...")
                    
                    # Install Bluetooth with detailed progress
                    bluetooth_packages = ['bluez', 'bluetooth', 'bluez-tools']
                    log_progress(f"📦 Installing packages: {', '.join(bluetooth_packages)}")
                    
                    result = run_command_with_progress(
                        ['apt', 'install', '-y'] + bluetooth_packages, 
                        "Installing Bluetooth stack", 
                        300
                    )
                    
                    if result and result.returncode == 0:
                        log_progress("📦 Bluetooth packages installed successfully")
                        
                        # Start the service
                        start_step_animation()
                        subprocess.run(['systemctl', 'start', 'bluetooth'], capture_output=True, timeout=20)
                        stop_step_animation()
                        log_progress("✅ Bluetooth installed and started")
                    else:
                        if result and result.stderr:
                            log_progress(f"⚠️ Bluetooth installation issues: {result.stderr[:100]}...")
                        log_progress("⚠️ Continuing without Bluetooth")
                    
            except subprocess.TimeoutExpired:
                stop_step_animation()
                log_progress("⚠️ Bluetooth installation timed out")
                log_progress("⚠️ Continuing to next step...")
            except Exception as e:
                stop_step_animation()
                log_progress(f"⚠️ Bluetooth setup error: {str(e)[:200]}...")
                
            sub_status_label.config(text="")
            log_progress("")
            
            # Step 5: Install missing firmware
            log_progress("📦 STEP 5: Installing Network Firmware", step=5)
            firmware_packages = ["firmware-linux-nonfree", "firmware-realtek", 
                               "firmware-atheros", "firmware-intel-sound"]
            
            log_progress("🔍 Checking available firmware packages...")
            available_packages = []
            
            for i, package in enumerate(firmware_packages):
                sub_status_label.config(text=f"Checking {package} ({i+1}/{len(firmware_packages)})")
                progress_window.update()
                
                try:
                    result = subprocess.run(['apt', 'search', package], capture_output=True, text=True, timeout=15)
                    if package in result.stdout:
                        available_packages.append(package)
                        log_progress(f"   ✅ {package} available")
                    else:
                        log_progress(f"   ⚠️ {package} not found")
                except Exception:
                    log_progress(f"   ⚠️ Could not check {package}")
            
            if available_packages:
                log_progress(f"📥 Installing {len(available_packages)} firmware packages...")
                log_progress(f"Packages: {', '.join(available_packages)}")
                
                result = run_command_with_progress(
                    ['apt', 'install', '-y'] + available_packages,
                    "Installing firmware packages",
                    300
                )
                
                if result and result.returncode == 0:
                    log_progress(f"✅ Successfully installed firmware packages")
                else:
                    if result and result.stderr:
                        log_progress(f"⚠️ Some firmware issues: {result.stderr[:100]}...")
                    log_progress("⚠️ Continuing anyway...")
            else:
                log_progress("⚠️ No additional firmware packages found")
            
            sub_status_label.config(text="")
            log_progress("")
            
            # Step 6: Force WiFi interface detection
            log_progress("📡 STEP 6: Force WiFi Interface Detection", step=6)
            sub_status_label.config(text="Scanning for WiFi hardware...")
            progress_window.update()
            
            wifi_found = False
            
            # Method 1: Liberate interfaces from NetworkManager first
            try:
                log_progress("🔓 Liberating interfaces from NetworkManager...")
                
                # Get list of managed interfaces
                result = subprocess.run(['nmcli', 'device', 'status'], capture_output=True, text=True)
                if result.returncode == 0:
                    managed_interfaces = []
                    for line in result.stdout.split('\n')[1:]:  # Skip header
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 3:
                                interface = parts[0]
                                state = parts[2] if len(parts) > 2 else ""
                                if any(interface.startswith(prefix) for prefix in ['wl', 'wlan', 'wlp']):
                                    managed_interfaces.append(interface)
                                    log_progress(f"📶 Found managed WiFi: {interface} (state: {state})")
                    
                    # Temporarily unmanage WiFi interfaces
                    for interface in managed_interfaces:
                        try:
                            sub_status_label.config(text=f"Unmanaging {interface}...")
                            progress_window.update()
                            subprocess.run(['nmcli', 'device', 'set', interface, 'managed', 'no'], 
                                         capture_output=True, timeout=10)
                            log_progress(f"🔓 Unmanaged {interface} from NetworkManager")
                            time.sleep(1)
                        except Exception:
                            log_progress(f"⚠️ Could not unmanage {interface}")
                            
            except subprocess.CalledProcessError:
                log_progress("⚠️ nmcli not available - skipping NetworkManager liberation")
            
            # Method 2: Stop interfering services temporarily
            try:
                log_progress("⏸️ Temporarily stopping interfering services...")
                
                services_to_stop = ['wpa_supplicant', 'NetworkManager', 'connman']
                stopped_services = []
                
                for service in services_to_stop:
                    try:
                        # Check if service is active
                        result = subprocess.run(['systemctl', 'is-active', service], 
                                              capture_output=True, text=True)
                        if result.returncode == 0:  # Service is active
                            sub_status_label.config(text=f"Stopping {service}...")
                            progress_window.update()
                            
                            subprocess.run(['systemctl', 'stop', service], 
                                         capture_output=True, timeout=15)
                            stopped_services.append(service)
                            log_progress(f"⏸️ Stopped {service}")
                            time.sleep(2)  # Let service fully stop
                    except Exception:
                        pass
                
                log_progress(f"⏸️ Stopped {len(stopped_services)} interfering services")
                
            except Exception as e:
                log_progress(f"⚠️ Service management warning: {str(e)[:100]}...")
            
            # Method 3: Force hardware detection with multiple approaches
            try:
                log_progress("🔍 Scanning WiFi hardware with multiple methods...")
                
                # Approach 1: Direct hardware scan via lspci
                try:
                    result = subprocess.run(['lspci'], capture_output=True, text=True)
                    wifi_hw_found = False
                    for line in result.stdout.split('\n'):
                        if any(keyword in line.lower() for keyword in 
                              ['wireless', 'wifi', '802.11', 'wlan', 'atheros', 'intel', 'broadcom', 'realtek']):
                            log_progress(f"🔍 WiFi Hardware: {line.strip()}")
                            wifi_hw_found = True
                    
                    if wifi_hw_found:
                        log_progress("✅ WiFi hardware detected - proceeding with interface activation")
                    else:
                        log_progress("⚠️ No WiFi hardware found in PCI scan")
                        
                except Exception:
                    log_progress("⚠️ Could not scan PCI hardware")
                    
                # Approach 2: Kernel module based detection
                try:
                    result = subprocess.run(['lsmod'], capture_output=True, text=True)
                    wifi_modules = []
                    for line in result.stdout.split('\n'):
                        module_name = line.split()[0] if line.strip() else ""
                        if any(module_name.startswith(prefix) for prefix in 
                              ['iwl', 'ath', 'rt2', 'rtl', 'brcm', 'mt7']):
                            wifi_modules.append(module_name)
                            log_progress(f"📡 WiFi module loaded: {module_name}")
                    
                    if wifi_modules:
                        log_progress(f"✅ Found {len(wifi_modules)} WiFi kernel modules")
                    else:
                        log_progress("⚠️ No WiFi kernel modules detected")
                        
                except Exception:
                    log_progress("⚠️ Could not scan kernel modules")
                    
                # Approach 3: Scan /sys/class/net with DOWN interfaces
                interfaces_found = []
                try:
                    if os.path.exists("/sys/class/net"):
                        for interface in os.listdir("/sys/class/net"):
                            if any(interface.startswith(prefix) for prefix in ['wl', 'wlan', 'wlp', 'wlx']):
                                try:
                                    # Check if interface exists but is down
                                    operstate_file = f"/sys/class/net/{interface}/operstate"
                                    if os.path.exists(operstate_file):
                                        with open(operstate_file, 'r') as f:
                                            state = f.read().strip()
                                        
                                            # Get MAC address
                                            with open(f"/sys/class/net/{interface}/address", 'r') as f:
                                                mac = f.read().strip()
                                        
                                                interfaces_found.append((interface, mac, state))
                                                log_progress(f"📶 Found WiFi interface: {interface} - MAC: {mac} - State: {state}")
                                        
                                except Exception:
                                    continue
                                    
                    log_progress(f"🔍 Found {len(interfaces_found)} WiFi interfaces in sysfs")
                    
                except Exception:
                    log_progress("⚠️ Could not scan /sys/class/net")
                    
                # Approach 4: Force UP any found WiFi interfaces
                for interface, mac, state in interfaces_found:
                    try:
                        sub_status_label.config(text=f"Activating {interface}...")
                        progress_window.update()
                        
                        # Force interface UP
                        log_progress(f"🔄 Forcing {interface} UP...")
                        subprocess.run(['ip', 'link', 'set', interface, 'up'], 
                                     capture_output=True, timeout=10)
                        
                        # Verify it's up
                        time.sleep(2)
                        result = subprocess.run(['ip', 'link', 'show', interface], 
                                              capture_output=True, text=True)
                        if 'UP' in result.stdout:
                            log_progress(f"✅ Successfully activated WiFi: {interface}")
                            wifi_found = True
                        else:
                            log_progress(f"⚠️ {interface} still DOWN after activation attempt")
                            
                    except Exception as e:
                        log_progress(f"⚠️ Could not activate {interface}: {str(e)[:50]}...")
                    
                # Approach 5: iw/iwconfig scan as last resort
                try:
                    # Try iw first (newer tool)
                    for interface, mac, state in interfaces_found:
                        try:
                            result = subprocess.run(['iw', 'dev', interface, 'scan'], 
                                                  capture_output=True, text=True, timeout=15)
                            if result.returncode == 0:
                                log_progress(f"📡 {interface} scan successful - interface is functional")
                                wifi_found = True
                            else:
                                log_progress(f"⚠️ {interface} scan failed - may need firmware")
                        except Exception:
                            # Try iwconfig as fallback
                            try:
                                result = subprocess.run(['iwconfig', interface], 
                                                      capture_output=True, text=True)
                                if 'IEEE 802.11' in result.stdout:
                                    log_progress(f"📡 {interface} detected via iwconfig")
                                    wifi_found = True
                            except Exception:
                                pass
                                
                except Exception:
                    log_progress("⚠️ Could not perform wireless scan")
                    
            except Exception as e:
                log_progress(f"⚠️ WiFi detection error: {str(e)[:100]}...")
                
            # Method 4: Restart services we stopped
            try:
                log_progress("🔄 Restarting network services...")
                
                # Restart stopped services in reverse order
                for service in reversed(stopped_services):
                    try:
                        sub_status_label.config(text=f"Restarting {service}...")
                        progress_window.update()
                        
                        subprocess.run(['systemctl', 'start', service], 
                                     capture_output=True, timeout=20)
                        log_progress(f"▶️ Restarted {service}")
                        time.sleep(2)
                    except Exception:
                        log_progress(f"⚠️ Could not restart {service}")
                    
                # Re-manage interfaces in NetworkManager
                try:
                    if 'NetworkManager' in stopped_services:
                        time.sleep(3)  # Let NetworkManager start
                        for interface in managed_interfaces:
                            try:
                                subprocess.run(['nmcli', 'device', 'set', interface, 'managed', 'yes'], 
                                             capture_output=True, timeout=10)
                                log_progress(f"🔗 Re-managed {interface} in NetworkManager")
                            except Exception:
                                pass
                except Exception:
                    pass
                    
            except Exception as e:
                log_progress(f"⚠️ Service restart warning: {str(e)[:100]}...")
                
            if not wifi_found:
                log_progress("⚠️ No functional WiFi interfaces detected")
                log_progress("💡 This may be due to:")
                log_progress("   • Missing WiFi drivers/firmware")
                log_progress("   • Hardware disabled in BIOS")
                log_progress("   • USB WiFi adapter not connected")
                log_progress("   • Interface in rfkill blocked state")
            else:
                log_progress("🎉 WiFi interfaces successfully detected and activated!")
                
            sub_status_label.config(text="")
            log_progress("")
            
            # Step 7: Activate all network interfaces
            log_progress("🌐 STEP 7: Activating All Network Interfaces", step=7)
            activated_interfaces = []
            
            sub_status_label.config(text="Scanning network interfaces...")
            progress_window.update()
            
            try:
                if os.path.exists("/sys/class/net"):
                    interfaces = [i for i in os.listdir("/sys/class/net") 
                                if i != "lo" and not any(i.startswith(p) for p in 
                                ["docker", "veth", "br-", "virbr", "tun", "tap"])]
                    
                    for i, interface in enumerate(interfaces):
                        sub_status_label.config(text=f"Activating interface {i+1}/{len(interfaces)}: {interface}")
                        progress_window.update()
                        
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
                            log_progress(f"⚠️ Could not activate {interface}: {str(e)[:50]}...")
                            
            except Exception as e:
                log_progress(f"❌ Error accessing network interfaces: {e}")
                
            sub_status_label.config(text="")
            log_progress("")
            
            # Step 8: Activate Bluetooth interfaces
            log_progress("📱 STEP 8: Activating Bluetooth Interfaces", step=8)
            bluetooth_found = False
            
            sub_status_label.config(text="Scanning Bluetooth devices...")
            progress_window.update()
            
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
                                sub_status_label.config(text=f"Activating {bt_interface}...")
                                progress_window.update()
                                
                                subprocess.run(['hciconfig', bt_interface, 'up'], capture_output=True, timeout=10)
                                subprocess.run(['hciconfig', bt_interface, 'piscan'], capture_output=True, timeout=5)
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
                    log_progress("💡 This may be normal if no Bluetooth hardware is present")
                    
            except Exception as e:
                log_progress(f"⚠️ Bluetooth activation error: {str(e)[:100]}...")
                
            sub_status_label.config(text="")
            log_progress("")
            
            # Final step: Restart network services
            log_progress("🔄 FINAL: Restarting Network Services")
            try:
                # Restart NetworkManager
                result = subprocess.run(['systemctl', 'is-active', 'NetworkManager'], capture_output=True)
                if result.returncode == 0:
                    log_progress("🔄 Restarting NetworkManager...", substep="Restarting NetworkManager...")
                    start_step_animation()
                    subprocess.run(['systemctl', 'restart', 'NetworkManager'], capture_output=True, timeout=20)
                    stop_step_animation()
                    log_progress("✅ NetworkManager restarted")
                
                # Restart wpa_supplicant if active
                result = subprocess.run(['systemctl', 'is-active', 'wpa_supplicant'], capture_output=True)
                if result.returncode == 0:
                    sub_status_label.config(text="Restarting wpa_supplicant...")
                    progress_window.update()
                    subprocess.run(['systemctl', 'restart', 'wpa_supplicant'], capture_output=True, timeout=15)
                    log_progress("✅ wpa_supplicant restarted")
                    
            except Exception as e:
                stop_step_animation()
                log_progress(f"⚠️ Service restart warning: {str(e)[:100]}...")
            
            # Final summary
            main_progress_bar['value'] = 100
            main_status_label.config(text="✅ COMPLETE!")
            sub_status_label.config(text="All operations finished")
            
            log_progress("✅ ACTIVATION COMPLETE!")
            log_progress("=" * 60)
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
            
            if not activated_interfaces or len(activated_interfaces) <= 1:
                log_progress("")
                log_progress("💡 TROUBLESHOOTING TIPS:")
                log_progress("   • Check hardware: lspci | grep -i wireless")
                log_progress("   • Manual WiFi check: nmcli device wifi list")
                log_progress("   • Check dmesg: dmesg | grep -i wifi")
                log_progress("   • Verify drivers: lsmod | grep -E '(iwl|ath|rt)'")
            
            # Add enhanced buttons
            button_frame = tk.Frame(progress_window)
            button_frame.pack(pady=15)
            
            def close_and_scan():
                progress_window.destroy()
                # Wait for interfaces to settle
                time.sleep(3)
                self.scan_interfaces()
            
            # Styled buttons
            scan_button = tk.Button(button_frame, text="✅ Close & Scan Interfaces", 
                                  command=close_and_scan, bg='#4CAF50', fg='white', 
                                  font=('Arial', 11, 'bold'), padx=20, pady=8)
            scan_button.pack(side=tk.LEFT, padx=5)
            
            close_button = tk.Button(button_frame, text="Close", 
                                   command=progress_window.destroy, 
                                   font=('Arial', 10), padx=15, pady=8)
            close_button.pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            stop_step_animation()
            main_progress_bar['value'] = 0
            main_status_label.config(text="❌ ERROR!")
            sub_status_label.config(text=str(e)[:50] + "...")
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