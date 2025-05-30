Name:           macaron
Version:        1.0
Release:        1%{?dist}
Summary:        MAC Address Randomization Tool for Privacy Enhancement
License:        MIT (Personal Use) / Commercial License Required for Business Use
URL:            https://ratomir.com
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

Requires:       python3 >= 3.6
Requires:       python3-tkinter
Requires:       iproute2

%description
MACARON is a comprehensive, enterprise-grade MAC address randomization
application designed to enhance privacy and security on Linux systems.

The application provides both manual and automatic MAC address randomization
with a modern graphical interface, comprehensive logging, and robust security
features.

Key Features:
* Real-time network interface detection and monitoring
* Secure cryptographic MAC address generation
* Automatic scheduling with customizable intervals (1-1440 minutes)
* Original MAC address backup and restoration
* Comprehensive security audit logging
* Modern, intuitive GUI built with tkinter
* Root privilege management with secure sudo handling
* Cross-interface support (Ethernet, WiFi, etc.)
* Virtual interface filtering for safety

This tool is designed for privacy-conscious users, security professionals,
penetration testers, and enterprises requiring MAC address randomization
for compliance or security purposes.

%prep
%setup -q

%build
# Nothing to build - Python application

%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/macaron
mkdir -p %{buildroot}%{_docdir}/macaron
mkdir -p %{buildroot}%{_mandir}/man1
mkdir -p %{buildroot}%{_datadir}/applications

# Install application files
cp main.py test_macaron.py run_tests.py %{buildroot}%{_datadir}/macaron/

# Create wrapper scripts
cat > %{buildroot}%{_bindir}/macaron << 'EOF'
#!/bin/bash
cd %{_datadir}/macaron
exec python3 main.py "$@"
EOF

cat > %{buildroot}%{_bindir}/macaron-test << 'EOF'
#!/bin/bash
cd %{_datadir}/macaron
exec python3 run_tests.py "$@"
EOF

chmod 755 %{buildroot}%{_bindir}/macaron
chmod 755 %{buildroot}%{_bindir}/macaron-test

# Install documentation
cp README.md LICENSE INSTALL.md PROJECT_SUMMARY.md CODE_REVIEW.md TECHNICAL_DOCUMENTATION.md %{buildroot}%{_docdir}/macaron/

# Install man page
cat > %{buildroot}%{_mandir}/man1/macaron.1 << 'EOF'
.TH MACARON 1 "2025" "1.0" "MAC Address Randomization Tool"
.SH NAME
macaron \- MAC Address Randomization Tool for privacy enhancement
.SH SYNOPSIS
.B macaron
.SH DESCRIPTION
MACARON is a comprehensive MAC address randomization application.
.SH AUTHOR
Ratomir Jovanovic (ratomir.com)
EOF

gzip %{buildroot}%{_mandir}/man1/macaron.1

# Install desktop file
cat > %{buildroot}%{_datadir}/applications/macaron.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=MACARON
GenericName=MAC Address Randomizer
Comment=Secure MAC address randomization tool
Icon=network-wired
Exec=pkexec macaron
Categories=System;Security;Network;
EOF

%files
%{_bindir}/macaron
%{_bindir}/macaron-test
%{_datadir}/macaron/
%{_docdir}/macaron/
%{_mandir}/man1/macaron.1.gz
%{_datadir}/applications/macaron.desktop

%changelog
* Sun Jan 01 2025 Ratomir Jovanovic <contact@ratomir.com> - 1.0-1
- Initial release of MACARON
- Comprehensive MAC address randomization tool
- Enterprise-grade security features
- Modern GUI interface
- Automatic scheduling capabilities 