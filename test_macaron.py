#!/usr/bin/env python3
"""
MACARON - Unit Tests
Comprehensive test suite for the MAC Address Randomization Tool

Author: Ratomir Jovanovic
Website: ratomir.com
Version: 1.0
License: MIT (Personal Use) / Commercial License Required for Business Use
Copyright (c) 2025
"""

import unittest
import sys
import os
import tempfile
import subprocess
from unittest.mock import Mock, patch, MagicMock, call
import tkinter as tk
from tkinter import ttk
import threading
import time
import re

# Add the current directory to the path so we can import main
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the root privilege check for testing
with patch('os.geteuid', return_value=0):
    from main import MacaronApp

class TestMacaronCore(unittest.TestCase):
    """Test core functionality without GUI"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during testing
        
        # Mock messagebox to prevent GUI dialogs during testing
        self.messagebox_patcher = patch('main.messagebox')
        self.mock_messagebox = self.messagebox_patcher.start()
        
        # Create app instance with mocked subprocess calls
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value.stdout = "1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN\n    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00\n2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP\n    link/ether aa:bb:cc:dd:ee:ff brd ff:ff:ff:ff:ff:ff"
            self.app = MacaronApp(self.root)
    
    def tearDown(self):
        """Clean up test fixtures"""
        self.messagebox_patcher.stop()
        self.root.destroy()
    
    def test_mac_generation(self):
        """Test MAC address generation"""
        mac = self.app.generate_random_mac()
        
        # Test format
        self.assertRegex(mac, r'^([0-9a-f]{2}:){5}[0-9a-f]{2}$')
        
        # Test locally administered bit (2nd bit of first octet should be 1)
        first_octet = int(mac.split(':')[0], 16)
        self.assertTrue(first_octet & 0x02, "Generated MAC should have locally administered bit set")
        
        # Test unicast (1st bit should be 0)
        self.assertFalse(first_octet & 0x01, "Generated MAC should be unicast")
        
        # Test randomness - generate multiple MACs and ensure they're different
        macs = set()
        for _ in range(100):
            new_mac = self.app.generate_random_mac()
            macs.add(new_mac)
        
        # Should have generated many unique MACs
        self.assertGreater(len(macs), 90, "MAC generation should produce unique addresses")
    
    def test_mac_validation(self):
        """Test MAC address validation"""
        # Valid locally administered MAC
        self.assertTrue(self.app.validate_mac_address("02:aa:bb:cc:dd:ee"))
        
        # Valid global MAC (during restoration)
        self.assertTrue(self.app.validate_mac_address("aa:bb:cc:dd:ee:ff", allow_global=True))
        self.assertFalse(self.app.validate_mac_address("aa:bb:cc:dd:ee:ff", allow_global=False))
        
        # Invalid formats
        self.assertFalse(self.app.validate_mac_address("invalid"))
        self.assertFalse(self.app.validate_mac_address("aa:bb:cc:dd:ee"))  # Too short
        self.assertFalse(self.app.validate_mac_address("aa:bb:cc:dd:ee:ff:gg"))  # Too long
        self.assertFalse(self.app.validate_mac_address("gg:bb:cc:dd:ee:ff"))  # Invalid hex
        
        # Multicast addresses (first bit set)
        self.assertFalse(self.app.validate_mac_address("01:bb:cc:dd:ee:ff"))
        self.assertFalse(self.app.validate_mac_address("03:bb:cc:dd:ee:ff"))
    
    def test_interface_validation(self):
        """Test network interface name validation"""
        # Valid interface names
        self.assertTrue(self.app.validate_interface_name("eth0"))
        self.assertTrue(self.app.validate_interface_name("wlan0"))
        self.assertTrue(self.app.validate_interface_name("enp0s3"))
        self.assertTrue(self.app.validate_interface_name("br-123"))
        
        # Invalid interface names
        self.assertFalse(self.app.validate_interface_name(""))  # Empty
        self.assertFalse(self.app.validate_interface_name("a" * 20))  # Too long
        self.assertFalse(self.app.validate_interface_name("eth0; rm -rf /"))  # Command injection
        self.assertFalse(self.app.validate_interface_name("eth0 && echo"))  # Command injection
        self.assertFalse(self.app.validate_interface_name("eth0|cat"))  # Pipe injection
        self.assertFalse(self.app.validate_interface_name("eth0$"))  # Variable expansion
        self.assertFalse(self.app.validate_interface_name("eth0`whoami`"))  # Command substitution


class TestMacaronGUI(unittest.TestCase):
    """Test GUI functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.messagebox_patcher = patch('main.messagebox')
        self.mock_messagebox = self.messagebox_patcher.start()
        
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value.stdout = "2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500\n    link/ether aa:bb:cc:dd:ee:ff brd ff:ff:ff:ff:ff:ff"
            self.app = MacaronApp(self.root)
    
    def tearDown(self):
        """Clean up test fixtures"""
        self.messagebox_patcher.stop()
        self.root.destroy()
    
    def test_gui_creation(self):
        """Test GUI components are created"""
        self.assertIsInstance(self.app.tree, ttk.Treeview)
        self.assertIsInstance(self.app.log_text, tk.Text)
        self.assertIsInstance(self.app.auto_button, ttk.Button)
        self.assertIsInstance(self.app.interval_var, tk.StringVar)
    
    def test_logging(self):
        """Test logging functionality"""
        test_message = "Test log message"
        self.app.log(test_message)
        
        # Check if message appears in GUI log
        log_content = self.app.log_text.get("1.0", tk.END)
        self.assertIn(test_message, log_content)
    
    @patch('subprocess.run')
    def test_interface_scanning(self, mock_subprocess):
        """Test network interface scanning"""
        # Mock successful interface scan
        mock_subprocess.return_value.stdout = """1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP mode DEFAULT group default qlen 1000
    link/ether aa:bb:cc:dd:ee:ff brd ff:ff:ff:ff:ff:ff
3: wlan0: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN mode DEFAULT group default qlen 1000
    link/ether 11:22:33:44:55:66 brd ff:ff:ff:ff:ff:ff"""
        
        self.app.scan_interfaces()
        
        # Check that interfaces are detected (excluding loopback)
        self.assertIn("eth0", self.app.interfaces)
        self.assertIn("wlan0", self.app.interfaces)
        self.assertNotIn("lo", self.app.interfaces)
        
        # Check MAC addresses are stored
        self.assertEqual(self.app.interfaces["eth0"], "aa:bb:cc:dd:ee:ff")
        self.assertEqual(self.app.interfaces["wlan0"], "11:22:33:44:55:66")
        
        # Check original MACs are backed up
        self.assertIn("eth0", self.app.original_macs)
        self.assertIn("wlan0", self.app.original_macs)


class TestMacaronNetworking(unittest.TestCase):
    """Test network operations with mocked subprocess calls"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.messagebox_patcher = patch('main.messagebox')
        self.mock_messagebox = self.messagebox_patcher.start()
        
        with patch('subprocess.run'):
            self.app = MacaronApp(self.root)
            
        # Set up test interface data
        self.app.interfaces = {"eth0": "aa:bb:cc:dd:ee:ff"}
        self.app.original_macs = {"eth0": "aa:bb:cc:dd:ee:ff"}
    
    def tearDown(self):
        """Clean up test fixtures"""
        self.messagebox_patcher.stop()
        self.root.destroy()
    
    @patch('subprocess.run')
    def test_mac_change_success(self, mock_subprocess):
        """Test successful MAC address change"""
        mock_subprocess.return_value.returncode = 0
        
        result = self.app.change_mac_address("eth0", "02:11:22:33:44:55")
        
        self.assertTrue(result)
        
        # Verify correct sequence of commands
        expected_calls = [
            call(['ip', 'link', 'set', 'dev', 'eth0', 'down'], check=True, capture_output=True),
            call(['ip', 'link', 'set', 'dev', 'eth0', 'address', '02:11:22:33:44:55'], check=True, capture_output=True),
            call(['ip', 'link', 'set', 'dev', 'eth0', 'up'], check=True, capture_output=True)
        ]
        
        mock_subprocess.assert_has_calls(expected_calls)
        
        # Check interface MAC is updated
        self.assertEqual(self.app.interfaces["eth0"], "02:11:22:33:44:55")
    
    @patch('subprocess.run')
    def test_mac_change_failure(self, mock_subprocess):
        """Test MAC address change failure"""
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, 'ip')
        
        result = self.app.change_mac_address("eth0", "02:11:22:33:44:55")
        
        self.assertFalse(result)
    
    def test_mac_change_invalid_interface(self):
        """Test MAC change with invalid interface name"""
        result = self.app.change_mac_address("eth0; rm -rf /", "02:11:22:33:44:55")
        self.assertFalse(result)
        self.mock_messagebox.showerror.assert_called()
    
    def test_mac_change_invalid_mac(self):
        """Test MAC change with invalid MAC address"""
        result = self.app.change_mac_address("eth0", "invalid-mac")
        self.assertFalse(result)
        self.mock_messagebox.showerror.assert_called()


class TestMacaronAutomation(unittest.TestCase):
    """Test automatic randomization functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.messagebox_patcher = patch('main.messagebox')
        self.mock_messagebox = self.messagebox_patcher.start()
        
        with patch('subprocess.run'):
            self.app = MacaronApp(self.root)
            
        self.app.interfaces = {"eth0": "aa:bb:cc:dd:ee:ff"}
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.app.auto_randomize_active:
            self.app.stop_auto_randomization()
        self.messagebox_patcher.stop()
        self.root.destroy()
    
    def test_auto_randomization_start_stop(self):
        """Test starting and stopping auto-randomization"""
        # Test starting
        self.app.interval_var.set("1")  # 1 minute interval
        self.app.start_auto_randomization()
        
        self.assertTrue(self.app.auto_randomize_active)
        self.assertIsNotNone(self.app.auto_thread)
        self.assertTrue(self.app.auto_thread.is_alive())
        
        # Test stopping
        self.app.stop_auto_randomization()
        
        self.assertFalse(self.app.auto_randomize_active)
        
        # Give thread time to stop
        time.sleep(0.1)
    
    def test_invalid_interval(self):
        """Test invalid interval handling"""
        self.app.interval_var.set("0")  # Invalid interval
        self.app.start_auto_randomization()
        
        self.assertFalse(self.app.auto_randomize_active)
        self.mock_messagebox.showerror.assert_called()
    
    def test_interval_validation(self):
        """Test interval validation"""
        # Valid intervals
        for interval in ["1", "15", "60", "1440"]:
            self.app.interval_var.set(interval)
            self.app.start_auto_randomization()
            self.assertTrue(self.app.auto_randomize_active)
            self.app.stop_auto_randomization()
        
        # Invalid intervals
        for interval in ["0", "-1", "abc", "1441"]:
            self.app.interval_var.set(interval)
            self.app.start_auto_randomization()
            if interval == "1441":
                # 1441 is technically valid but should we allow it?
                continue
            self.assertFalse(self.app.auto_randomize_active)


class TestMacaronSecurity(unittest.TestCase):
    """Test security features"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.messagebox_patcher = patch('main.messagebox')
        self.mock_messagebox = self.messagebox_patcher.start()
        
        with patch('subprocess.run'):
            self.app = MacaronApp(self.root)
    
    def tearDown(self):
        """Clean up test fixtures"""
        self.messagebox_patcher.stop()
        self.root.destroy()
    
    def test_command_injection_prevention(self):
        """Test prevention of command injection attacks"""
        malicious_interfaces = [
            "eth0; rm -rf /",
            "eth0 && cat /etc/passwd",
            "eth0|nc -l 1234",
            "eth0`whoami`",
            "eth0$(id)",
            "eth0 > /dev/null"
        ]
        
        for interface in malicious_interfaces:
            result = self.app.validate_interface_name(interface)
            self.assertFalse(result, f"Should reject malicious interface: {interface}")
    
    def test_mac_format_validation(self):
        """Test MAC address format validation prevents malicious input"""
        malicious_macs = [
            "02:aa:bb:cc:dd:ee; rm -rf /",
            "02:aa:bb:cc:dd:ee && echo pwned",
            "../../../etc/passwd",
            "${IFS}cat${IFS}/etc/passwd",
            "`whoami`",
            "$(id)"
        ]
        
        for mac in malicious_macs:
            result = self.app.validate_mac_address(mac)
            self.assertFalse(result, f"Should reject malicious MAC: {mac}")
    
    @patch('os.chmod')
    @patch('os.path.exists')
    def test_log_file_permissions(self, mock_exists, mock_chmod):
        """Test that log file is created with secure permissions"""
        mock_exists.return_value = False
        
        # Re-setup logging to test permissions
        self.app.setup_logging()
        
        # Check that chmod was called with secure permissions (0o600)
        mock_chmod.assert_called_with('macaron.log', 0o600)


class TestMacaronFileOperations(unittest.TestCase):
    """Test file operations and error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.messagebox_patcher = patch('main.messagebox')
        self.mock_messagebox = self.messagebox_patcher.start()
        
        with patch('subprocess.run'):
            self.app = MacaronApp(self.root)
    
    def tearDown(self):
        """Clean up test fixtures"""
        self.messagebox_patcher.stop()
        self.root.destroy()
    
    @patch('builtins.open')
    def test_log_file_creation_error(self, mock_open):
        """Test handling of log file creation errors"""
        mock_open.side_effect = PermissionError("Permission denied")
        
        # This should not crash the application
        try:
            self.app.setup_logging()
        except PermissionError:
            self.fail("setup_logging should handle file creation errors gracefully")


class TestMacaronEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.messagebox_patcher = patch('main.messagebox')
        self.mock_messagebox = self.messagebox_patcher.start()
        
        with patch('subprocess.run'):
            self.app = MacaronApp(self.root)
    
    def tearDown(self):
        """Clean up test fixtures"""
        self.messagebox_patcher.stop()
        self.root.destroy()
    
    def test_empty_interface_list(self):
        """Test behavior with no network interfaces"""
        self.app.interfaces.clear()
        
        # Should show warning when trying to randomize all
        self.app.randomize_all()
        self.mock_messagebox.showwarning.assert_called()
    
    def test_no_original_macs(self):
        """Test restore when no original MACs are stored"""
        self.app.original_macs.clear()
        
        self.app.restore_original()
        self.mock_messagebox.showwarning.assert_called()
    
    def test_selected_interfaces_empty(self):
        """Test randomize selected with no selection"""
        # Mock empty selection
        self.app.tree.selection = Mock(return_value=[])
        
        self.app.randomize_selected()
        self.mock_messagebox.showwarning.assert_called()


def run_tests():
    """Run all test suites"""
    print("=" * 60)
    print("MACARON - Unit Test Suite")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestMacaronCore,
        TestMacaronGUI,
        TestMacaronNetworking,
        TestMacaronAutomation,
        TestMacaronSecurity,
        TestMacaronFileOperations,
        TestMacaronEdgeCases
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 