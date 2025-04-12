# test_telnet_initial_configuration.py
import unittest
import time
from pyats.datastructures import AttrDict
from pyats.topology import Device
from telnet_connector import TelnetConnector

# Dummy telnet class for IOS configuration branch
class DummyTelnetIOS:
    def __init__(self):
        self.log = []  # Log all writes for inspection

    def write(self, data):
        self.log.append(data)

    def expect(self, prompt_list, timeout=10):
        # In a real session, expect would wait for a prompt.
        # Here, just return a dummy response.
        return (0, None, b"dummy prompt")

    def close(self):
        pass

    @property
    def eof(self):
        return False

# Dummy telnet class for CSR configuration branch
class DummyTelnetCSR:
    def __init__(self):
        self.log = []
        # Predefined responses that simulate the CSR device dialog
        self.responses = [
            b"initial configuration dialog? [yes/no]",
            b"management setup? [yes/no]:",
            b"host name [Router]:",
            b"Enter enable secret:",
            b"Enter enable password:",
            b"Enter virtual terminal password:",
            b"SNMP Network Management? [yes]:",
            b"interface summary:",
            b"IP on this interface? [yes]:",
            b"IP address for this interface:",
            b"mask for this interface [255.255.255.0] :",
            b"Enter your selection [2]:"
        ]
        self.response_index = 0

    def write(self, data):
        self.log.append(data)

    def read_until(self, expected, timeout=10):
        # Each call returns the next response in our list regardless of "expected"
        if self.response_index < len(self.responses):
            response = self.responses[self.response_index]
            self.response_index += 1
            return response
        return b""

    def expect(self, prompt_list, timeout=10):
        # Not used in the CSR branch of our configuration, so just return dummy data.
        return (0, None, b"dummy prompt")

    def close(self):
        pass

    @property
    def eof(self):
        return False

class TestTelnetInitialConfiguration(unittest.TestCase):
    def setUp(self):
        # Setup for IOS device test
        self.ios_device = Device(name="ios_device")
        self.ios_device.os = "ios"
        self.ios_device.interfaces = {
            "initial": AttrDict({
                "name": "GigabitEthernet0/0",
                "ipv4": AttrDict({
                    "ip": AttrDict({"compressed": "10.0.0.1"}),
                    "network": AttrDict({
                        "netmask": AttrDict({"exploded": "255.255.255.0"})
                    })
                })
            })
        }
        self.ios_device.custom = AttrDict({"hostname": "IOS-Router"})
        self.ios_device.connections = AttrDict({
            "ssh": AttrDict({
                "credentials": AttrDict({
                    "login": AttrDict({
                        "username": "admin",
                        "password": AttrDict({"plaintext": "pass"})
                    })
                })
            })
        })

        # Setup for CSR device test
        self.csr_device = Device(name="csr_device")
        self.csr_device.os = "csr"
        # In a CSR initial configuration the hostname is taken from the device.custom attribute
        self.csr_device.custom = AttrDict({"hostname": "CSR-Router"})
        self.csr_device.connections = AttrDict({
            "ssh": AttrDict({
                "credentials": AttrDict({
                    "login": AttrDict({
                        "username": "admin",
                        "password": AttrDict({"plaintext": "pass"})
                    })
                })
            })
        })
        # The CSR branch does not use the interface information in our telnet_connector

    def test_ios_initial_configuration(self):
        connector = TelnetConnector(self.ios_device)
        dummy_conn = DummyTelnetIOS()
        # Create a dummy connection info with a dummy IP and port
        connection = AttrDict({
            "ip": AttrDict({"compressed": "127.0.0.1"}),
            "port": 23
        })
        connector.connection = connection
        connector._conn = dummy_conn

        # Execute the initial configuration
        connector.do_initial_configuration()

        # Combine the log entries for easier searching
        log_output = b"".join(dummy_conn.log)
        # Check that some key IOS commands are present
        self.assertIn(b'conf t', log_output)
        self.assertIn(b'hostname IOS-Router', log_output)
        self.assertIn(b'crypto key generate rsa', log_output)

    def test_csr_initial_configuration(self):
        connector = TelnetConnector(self.csr_device)
        dummy_conn = DummyTelnetCSR()
        connection = AttrDict({
            "ip": AttrDict({"compressed": "127.0.0.1"}),
            "port": 23
        })
        connector.connection = connection
        connector._conn = dummy_conn

        connector.do_initial_configuration()

        log_output = b"".join(dummy_conn.log)
        # Check that the dialog answers were sent by verifying that expected responses appear in the log.
        # For example, the CSR configuration process should send "yes\n" to confirm starting configuration.
        self.assertIn(b'yes\n', log_output)
        # Check that the interface name "GigabitEthernet1" is sent in the CSR branch.
        self.assertIn(b'GigabitEthernet1\n', log_output)
        # Check that the subnet mask is provided.
        self.assertIn(b'255.255.255.0\n', log_output)
        # Verify that our custom hostname, "CSR-Router", was sent when prompted.
        self.assertIn(b'CSR-Router\n', log_output)

if __name__ == "__main__":
    unittest.main()
