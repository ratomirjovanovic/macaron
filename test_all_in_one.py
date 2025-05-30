#!/usr/bin/env python3
"""
ALL-IN-ONE MACARON TEST SUITE
Complete testing of the integrated MACARON application
"""

import sys
import os
import importlib
import unittest.mock
import subprocess
import tempfile

def print_test_header():
    """Print test header"""
    print("🔧" + "=" * 60 + "🔧")
    print("🧪  ALL-IN-ONE MACARON COMPREHENSIVE TEST SUITE  🧪")
    print("🔧" + "=" * 60 + "🔧")
    print()

def test_imports():
    """Test all required imports"""
    print("📦 TESTING IMPORTS & DEPENDENCIES")
    print("-" * 40)
    
    required_modules = [
        'tkinter', 'subprocess', 're', 'secrets', 'random', 
        'threading', 'time', 'os', 'sys', 'datetime', 
        'logging', 'stat'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module} - OK")
        except ImportError as e:
            print(f"❌ {module} - FAILED: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ FAILED IMPORTS: {failed_imports}")
        return False
    else:
        print("\n✅ ALL IMPORTS SUCCESSFUL!")
        return True

def test_main_module():
    """Test main.py module import and basic functionality"""
    print("\n🔧 TESTING MAIN MODULE")
    print("-" * 40)
    
    try:
        import main
        print("✅ main.py imports successfully")
        
        # Test class exists
        if hasattr(main, 'MacaronApp'):
            print("✅ MacaronApp class found")
        else:
            print("❌ MacaronApp class not found")
            return False
            
        # Test main function exists
        if hasattr(main, 'main'):
            print("✅ main() function found")
        else:
            print("❌ main() function not found")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error importing main.py: {e}")
        return False

def test_macaron_app_methods():
    """Test MacaronApp class methods"""
    print("\n🎯 TESTING MACARON APP METHODS")
    print("-" * 40)
    
    try:
        import main
        import tkinter as tk
        
        # Mock os.geteuid to simulate root
        with unittest.mock.patch('os.geteuid', return_value=0):
            root = tk.Tk()
            root.withdraw()  # Hide the window
            
            try:
                app = main.MacaronApp(root)
                print("✅ MacaronApp initializes successfully")
                
                # Test required methods
                required_methods = [
                    'scan_interfaces', 'enable_all_interfaces', 'randomize_selected',
                    'randomize_all', 'restore_original', 'run_diagnostics',
                    'generate_random_mac', 'change_mac_address'
                ]
                
                method_tests_passed = True
                for method in required_methods:
                    if hasattr(app, method):
                        print(f"✅ {method}() method exists")
                    else:
                        print(f"❌ {method}() method missing")
                        method_tests_passed = False
                
                # Test MAC generation
                try:
                    mac = app.generate_random_mac()
                    if len(mac) == 17 and mac.count(':') == 5:
                        print(f"✅ MAC generation works: {mac}")
                    else:
                        print(f"❌ Invalid MAC format: {mac}")
                        method_tests_passed = False
                except Exception as e:
                    print(f"❌ MAC generation failed: {e}")
                    method_tests_passed = False
                
                root.destroy()
                return method_tests_passed
                
            except Exception as e:
                print(f"❌ Error creating MacaronApp: {e}")
                root.destroy()
                return False
                
    except Exception as e:
        print(f"❌ Error in method testing: {e}")
        return False

def test_security_features():
    """Test security-related features"""
    print("\n🔒 TESTING SECURITY FEATURES")
    print("-" * 40)
    
    try:
        import main
        
        # Test MAC validation
        with unittest.mock.patch('os.geteuid', return_value=0):
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            
            app = main.MacaronApp(root)
            
            # Test valid MAC addresses
            valid_macs = [
                "02:11:22:33:44:55",  # Locally administered
                "00:11:22:33:44:55"   # Global (for restoration)
            ]
            
            invalid_macs = [
                "invalid",
                "02:11:22:33:44",      # Too short
                "02:11:22:33:44:55:66", # Too long
                "01:11:22:33:44:55"     # Multicast
            ]
            
            security_tests_passed = True
            
            for mac in valid_macs:
                if app.validate_mac_address(mac, allow_global=True):
                    print(f"✅ Valid MAC accepted: {mac}")
                else:
                    print(f"❌ Valid MAC rejected: {mac}")
                    security_tests_passed = False
            
            for mac in invalid_macs:
                if not app.validate_mac_address(mac):
                    print(f"✅ Invalid MAC rejected: {mac}")
                else:
                    print(f"❌ Invalid MAC accepted: {mac}")
                    security_tests_passed = False
            
            # Test interface name validation
            valid_interfaces = ["eth0", "wlan0", "hci0"]
            invalid_interfaces = ["../../../etc/passwd", "interface; rm -rf /", "test&&malicious"]
            
            for interface in valid_interfaces:
                if app.validate_interface_name(interface):
                    print(f"✅ Valid interface accepted: {interface}")
                else:
                    print(f"❌ Valid interface rejected: {interface}")
                    security_tests_passed = False
            
            for interface in invalid_interfaces:
                if not app.validate_interface_name(interface):
                    print(f"✅ Invalid interface rejected: {interface}")
                else:
                    print(f"❌ Invalid interface accepted: {interface}")
                    security_tests_passed = False
            
            root.destroy()
            return security_tests_passed
            
    except Exception as e:
        print(f"❌ Error in security testing: {e}")
        return False

def test_installer_script():
    """Test installer script syntax and structure"""
    print("\n📦 TESTING INSTALLER SCRIPT")
    print("-" * 40)
    
    installer_file = "install_all_in_one.sh"
    
    if not os.path.exists(installer_file):
        print(f"❌ Installer script not found: {installer_file}")
        return False
    
    try:
        with open(installer_file, 'r') as f:
            content = f.read()
        
        # Test for required functions
        required_functions = [
            'check_root', 'install_dependencies', 'test_system_comprehensive',
            'install_all_in_one_macaron', 'create_enhanced_desktop_integration',
            'optimize_system', 'show_final_instructions'
        ]
        
        installer_tests_passed = True
        
        for func in required_functions:
            if f"{func}()" in content:
                print(f"✅ Function found: {func}()")
            else:
                print(f"❌ Function missing: {func}()")
                installer_tests_passed = False
        
        # Test for shebang
        if content.startswith("#!/bin/bash"):
            print("✅ Proper shebang found")
        else:
            print("❌ Missing or incorrect shebang")
            installer_tests_passed = False
        
        # Test for error handling
        if "set -e" in content:
            print("✅ Error handling enabled (set -e)")
        else:
            print("❌ Error handling not enabled")
            installer_tests_passed = False
        
        return installer_tests_passed
        
    except Exception as e:
        print(f"❌ Error reading installer script: {e}")
        return False

def test_file_structure():
    """Test file structure and completeness"""
    print("\n📁 TESTING FILE STRUCTURE")
    print("-" * 40)
    
    required_files = {
        'main.py': 'Main application file',
        'install_all_in_one.sh': 'All-in-one installer',
        'README.md': 'Documentation',
        'requirements.txt': 'Python dependencies'
    }
    
    structure_tests_passed = True
    
    for filename, description in required_files.items():
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✅ {filename} ({description}) - {size} bytes")
        else:
            print(f"❌ {filename} missing")
            structure_tests_passed = False
    
    # Check if old separate scripts are removed
    old_scripts = [
        'enable_all_interfaces.sh',
        'check_hardware.sh', 
        'fix_interface_detection.sh',
        'install_enhanced_macaron.sh'
    ]
    
    for script in old_scripts:
        if not os.path.exists(script):
            print(f"✅ Old script properly removed: {script}")
        else:
            print(f"⚠️  Old script still exists: {script} (should be removed)")
    
    return structure_tests_passed

def test_integration_features():
    """Test integration features"""
    print("\n🔧 TESTING INTEGRATION FEATURES")
    print("-" * 40)
    
    try:
        import main
        
        with unittest.mock.patch('os.geteuid', return_value=0):
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            
            app = main.MacaronApp(root)
            
            # Test if enable_all_interfaces method exists and is callable
            if hasattr(app, 'enable_all_interfaces') and callable(getattr(app, 'enable_all_interfaces')):
                print("✅ enable_all_interfaces() method integrated")
            else:
                print("❌ enable_all_interfaces() method missing")
                root.destroy()
                return False
            
            # Test interface type detection
            test_interfaces = {
                'eth0': 'Ethernet',
                'wlan0': 'WiFi', 
                'hci0': 'Bluetooth',
                'usb0': 'USB-Ethernet'
            }
            
            interface_detection_passed = True
            for interface, expected_type in test_interfaces.items():
                detected_type = app._detect_interface_type(interface)
                if expected_type.lower() in detected_type.lower():
                    print(f"✅ Interface type detection: {interface} -> {detected_type}")
                else:
                    print(f"❌ Interface type detection failed: {interface} -> {detected_type} (expected: {expected_type})")
                    interface_detection_passed = False
            
            # Test virtual interface filtering
            virtual_interfaces = ['docker0', 'veth123', 'br-456', 'lo']
            for interface in virtual_interfaces:
                if app._is_virtual_interface(interface):
                    print(f"✅ Virtual interface correctly identified: {interface}")
                else:
                    print(f"❌ Virtual interface not identified: {interface}")
                    interface_detection_passed = False
            
            root.destroy()
            return interface_detection_passed
            
    except Exception as e:
        print(f"❌ Error testing integration features: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print_test_header()
    
    tests = [
        ("Import & Dependencies", test_imports),
        ("Main Module", test_main_module),
        ("MacaronApp Methods", test_macaron_app_methods),
        ("Security Features", test_security_features),
        ("Installer Script", test_installer_script),
        ("File Structure", test_file_structure),
        ("Integration Features", test_integration_features)
    ]
    
    passed_tests = []
    failed_tests = []
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests.append(test_name)
            else:
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            failed_tests.append(test_name)
    
    # Print summary
    print("\n" + "🏆" + "=" * 60 + "🏆")
    print("📊  TEST SUMMARY")
    print("🏆" + "=" * 60 + "🏆")
    
    print(f"\n✅ PASSED TESTS ({len(passed_tests)}):")
    for test in passed_tests:
        print(f"   • {test}")
    
    if failed_tests:
        print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
        for test in failed_tests:
            print(f"   • {test}")
    
    total_tests = len(tests)
    success_rate = (len(passed_tests) / total_tests) * 100
    
    print(f"\n📊 SUCCESS RATE: {success_rate:.1f}% ({len(passed_tests)}/{total_tests})")
    
    if success_rate == 100:
        print("\n🎉 ALL TESTS PASSED! MACARON ALL-IN-ONE IS PERFECT! 🎉")
        return True
    elif success_rate >= 90:
        print("\n🌟 EXCELLENT! MACARON ALL-IN-ONE IS READY!")
        return True
    elif success_rate >= 80:
        print("\n✅ GOOD! Minor issues need fixing.")
        return False
    else:
        print("\n⚠️  NEEDS WORK! Major issues detected.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 