# MACARON - Makefile
# Professional Makefile for MAC Address Randomization Tool
#
# Author: Ratomir Jovanovic
# Website: ratomir.com
# Version: 1.0
# License: MIT (Personal Use) / Commercial License Required for Business Use
# Copyright (c) 2025

# Installation directories
PREFIX ?= /usr/local
BINDIR = $(PREFIX)/bin
APPDIR = $(PREFIX)/share/macaron
DOCDIR = $(PREFIX)/share/doc/macaron
MANDIR = $(PREFIX)/share/man/man1
DESKTOPDIR = /usr/share/applications

# Application information
APP_NAME = macaron
VERSION = 1.0
AUTHOR = Ratomir Jovanovic

# File lists
APP_FILES = main.py test_macaron.py run_tests.py
DOC_FILES = README.md LICENSE INSTALL.md PROJECT_SUMMARY.md CODE_REVIEW.md TECHNICAL_DOCUMENTATION.md
SCRIPTS = macaron.sh

# Colors for output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

.PHONY: all install uninstall clean test help check-root check-deps package

# Default target
all: help

# Help target
help:
	@echo -e "$(BLUE)MACARON - MAC Address Randomization Tool$(NC)"
	@echo -e "$(BLUE)Author: $(AUTHOR)$(NC)"
	@echo -e "$(BLUE)Version: $(VERSION)$(NC)"
	@echo ""
	@echo "Available targets:"
	@echo "  install    - Install MACARON to system directories"
	@echo "  uninstall  - Remove MACARON from system"
	@echo "  test       - Run test suite"
	@echo "  clean      - Clean temporary files"
	@echo "  package    - Create distribution package"
	@echo "  check-deps - Check system dependencies"
	@echo ""
	@echo "Usage:"
	@echo "  sudo make install    # Install MACARON"
	@echo "  sudo make uninstall  # Remove MACARON"
	@echo "  make test           # Run tests"

# Check if running as root for installation
check-root:
	@if [ "$$(id -u)" != "0" ]; then \
		echo -e "$(RED)[ERROR]$(NC) Installation requires root privileges"; \
		echo -e "$(BLUE)[INFO]$(NC) Run with: sudo make install"; \
		exit 1; \
	fi

# Check system dependencies
check-deps:
	@echo -e "$(BLUE)[INFO]$(NC) Checking system dependencies..."
	@if ! command -v python3 >/dev/null 2>&1; then \
		echo -e "$(RED)[ERROR]$(NC) Python 3 is not installed"; \
		exit 1; \
	fi
	@if ! python3 -c "import tkinter" >/dev/null 2>&1; then \
		echo -e "$(YELLOW)[WARNING]$(NC) tkinter not available"; \
		echo -e "$(BLUE)[INFO]$(NC) Install with: apt install python3-tk"; \
	fi
	@if ! command -v ip >/dev/null 2>&1; then \
		echo -e "$(YELLOW)[WARNING]$(NC) iproute2 not available"; \
		echo -e "$(BLUE)[INFO]$(NC) Install with: apt install iproute2"; \
	fi
	@echo -e "$(GREEN)[SUCCESS]$(NC) Dependencies check completed"

# Install target
install: check-root check-deps
	@echo -e "$(BLUE)[INFO]$(NC) Installing MACARON v$(VERSION)..."
	
	# Create directories
	@mkdir -p $(APPDIR)
	@mkdir -p $(DOCDIR)
	@mkdir -p $(MANDIR)
	
	# Install application files
	@cp $(APP_FILES) $(APPDIR)/
	@chmod 755 $(APPDIR)/main.py
	@chmod 755 $(APPDIR)/run_tests.py
	
	# Create wrapper scripts
	@echo '#!/bin/bash' > $(BINDIR)/$(APP_NAME)
	@echo '# MACARON wrapper script' >> $(BINDIR)/$(APP_NAME)
	@echo 'cd $(APPDIR)' >> $(BINDIR)/$(APP_NAME)
	@echo 'exec python3 main.py "$$@"' >> $(BINDIR)/$(APP_NAME)
	@chmod 755 $(BINDIR)/$(APP_NAME)
	
	@echo '#!/bin/bash' > $(BINDIR)/$(APP_NAME)-test
	@echo '# MACARON test runner' >> $(BINDIR)/$(APP_NAME)-test
	@echo 'cd $(APPDIR)' >> $(BINDIR)/$(APP_NAME)-test
	@echo 'exec python3 run_tests.py "$$@"' >> $(BINDIR)/$(APP_NAME)-test
	@chmod 755 $(BINDIR)/$(APP_NAME)-test
	
	# Install documentation
	@cp $(DOC_FILES) $(DOCDIR)/
	
	# Create and install man page
	@echo '.TH MACARON 1 "2025" "$(VERSION)" "MAC Address Randomization Tool"' > $(MANDIR)/$(APP_NAME).1
	@echo '.SH NAME' >> $(MANDIR)/$(APP_NAME).1
	@echo '$(APP_NAME) \\- MAC Address Randomization Tool for privacy enhancement' >> $(MANDIR)/$(APP_NAME).1
	@echo '.SH SYNOPSIS' >> $(MANDIR)/$(APP_NAME).1
	@echo '.B $(APP_NAME)' >> $(MANDIR)/$(APP_NAME).1
	@echo '.SH DESCRIPTION' >> $(MANDIR)/$(APP_NAME).1
	@echo 'MACARON is a comprehensive MAC address randomization application.' >> $(MANDIR)/$(APP_NAME).1
	@echo '.SH AUTHOR' >> $(MANDIR)/$(APP_NAME).1
	@echo '$(AUTHOR) (ratomir.com)' >> $(MANDIR)/$(APP_NAME).1
	@gzip -f $(MANDIR)/$(APP_NAME).1
	
	# Install desktop file
	@echo '[Desktop Entry]' > $(DESKTOPDIR)/$(APP_NAME).desktop
	@echo 'Version=1.0' >> $(DESKTOPDIR)/$(APP_NAME).desktop
	@echo 'Type=Application' >> $(DESKTOPDIR)/$(APP_NAME).desktop
	@echo 'Name=MACARON' >> $(DESKTOPDIR)/$(APP_NAME).desktop
	@echo 'GenericName=MAC Address Randomizer' >> $(DESKTOPDIR)/$(APP_NAME).desktop
	@echo 'Comment=Secure MAC address randomization tool' >> $(DESKTOPDIR)/$(APP_NAME).desktop
	@echo 'Icon=network-wired' >> $(DESKTOPDIR)/$(APP_NAME).desktop
	@echo 'Exec=pkexec $(APP_NAME)' >> $(DESKTOPDIR)/$(APP_NAME).desktop
	@echo 'Categories=System;Security;Network;' >> $(DESKTOPDIR)/$(APP_NAME).desktop
	
	# Update desktop database
	@if command -v update-desktop-database >/dev/null 2>&1; then \
		update-desktop-database $(DESKTOPDIR) 2>/dev/null || true; \
	fi
	
	# Create uninstaller
	@echo '#!/bin/bash' > $(APPDIR)/uninstall.sh
	@echo '# MACARON uninstaller' >> $(APPDIR)/uninstall.sh
	@echo 'echo "Uninstalling MACARON..."' >> $(APPDIR)/uninstall.sh
	@echo 'rm -f $(BINDIR)/$(APP_NAME)' >> $(APPDIR)/uninstall.sh
	@echo 'rm -f $(BINDIR)/$(APP_NAME)-test' >> $(APPDIR)/uninstall.sh
	@echo 'rm -rf $(APPDIR)' >> $(APPDIR)/uninstall.sh
	@echo 'rm -rf $(DOCDIR)' >> $(APPDIR)/uninstall.sh
	@echo 'rm -f $(MANDIR)/$(APP_NAME).1.gz' >> $(APPDIR)/uninstall.sh
	@echo 'rm -f $(DESKTOPDIR)/$(APP_NAME).desktop' >> $(APPDIR)/uninstall.sh
	@echo 'echo "MACARON uninstalled successfully"' >> $(APPDIR)/uninstall.sh
	@chmod 755 $(APPDIR)/uninstall.sh
	
	@echo -e "$(GREEN)[SUCCESS]$(NC) MACARON installed successfully!"
	@echo -e "$(BLUE)[INFO]$(NC) Run with: sudo $(APP_NAME)"
	@echo -e "$(BLUE)[INFO]$(NC) Manual: man $(APP_NAME)"
	@echo -e "$(BLUE)[INFO]$(NC) Tests: $(APP_NAME)-test"

# Uninstall target
uninstall: check-root
	@echo -e "$(BLUE)[INFO]$(NC) Uninstalling MACARON..."
	@rm -f $(BINDIR)/$(APP_NAME)
	@rm -f $(BINDIR)/$(APP_NAME)-test
	@rm -rf $(APPDIR)
	@rm -rf $(DOCDIR)
	@rm -f $(MANDIR)/$(APP_NAME).1.gz
	@rm -f $(DESKTOPDIR)/$(APP_NAME).desktop
	@if command -v update-desktop-database >/dev/null 2>&1; then \
		update-desktop-database $(DESKTOPDIR) 2>/dev/null || true; \
	fi
	@echo -e "$(GREEN)[SUCCESS]$(NC) MACARON uninstalled successfully"

# Test target
test:
	@echo -e "$(BLUE)[INFO]$(NC) Running MACARON test suite..."
	@if [ -f test_macaron.py ]; then \
		python3 run_tests.py; \
	else \
		echo -e "$(RED)[ERROR]$(NC) Test files not found"; \
		exit 1; \
	fi

# Clean target
clean:
	@echo -e "$(BLUE)[INFO]$(NC) Cleaning temporary files..."
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@rm -f *.log
	@echo -e "$(GREEN)[SUCCESS]$(NC) Cleanup completed"

# Package target
package:
	@echo -e "$(BLUE)[INFO]$(NC) Creating distribution package..."
	@mkdir -p dist
	@tar -czf dist/macaron-$(VERSION).tar.gz \
		$(APP_FILES) $(DOC_FILES) $(SCRIPTS) \
		Makefile install.sh requirements.txt \
		--transform 's,^,macaron-$(VERSION)/,'
	@echo -e "$(GREEN)[SUCCESS]$(NC) Package created: dist/macaron-$(VERSION).tar.gz"

# Show installation status
status:
	@echo -e "$(BLUE)[INFO]$(NC) MACARON Installation Status:"
	@if [ -f $(BINDIR)/$(APP_NAME) ]; then \
		echo -e "$(GREEN)[INSTALLED]$(NC) Binary: $(BINDIR)/$(APP_NAME)"; \
	else \
		echo -e "$(RED)[NOT FOUND]$(NC) Binary: $(BINDIR)/$(APP_NAME)"; \
	fi
	@if [ -d $(APPDIR) ]; then \
		echo -e "$(GREEN)[INSTALLED]$(NC) Application: $(APPDIR)"; \
	else \
		echo -e "$(RED)[NOT FOUND]$(NC) Application: $(APPDIR)"; \
	fi
	@if [ -f $(MANDIR)/$(APP_NAME).1.gz ]; then \
		echo -e "$(GREEN)[INSTALLED]$(NC) Manual: $(MANDIR)/$(APP_NAME).1.gz"; \
	else \
		echo -e "$(RED)[NOT FOUND]$(NC) Manual: $(MANDIR)/$(APP_NAME).1.gz"; \
	fi 