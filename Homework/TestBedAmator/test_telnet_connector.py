import unittest
from unittest.mock import MagicMock, patch
from telnet_connector import TelnetConnector


class TestTelnetConnector(unittest.TestCase):
    """
    Test class for TelnetConnector
    """
    def setUp(self):
        self.connector = TelnetConnector()
        self.device_mock = MagicMock()
        self.device_mock.custom = {'hostname': 'TestRouter'}
        self.device_mock.connections = {
            'telnet': MagicMock(ip=MagicMock(compressed='192.168.0.1'), port=23),
            'ssh': {
                'credentials': {
                    'login': {
                        'username': 'admin',
                        'password': MagicMock(plaintext='cisco')
                    }
                }
            }
        }

    @patch('telnet_connector.telnetlib.Telnet')
    def test_connect_method(self, mock_telnet):
        """Test if connect() sets hostname and connection properly"""
        self.connector.connect(self.device_mock)
        self.assertEqual(self.connector.hostname, 'TestRouter')
        mock_telnet.assert_called_once()

    def test_config_ospf(self):
        """Test if config_ospf() sends OSPF commands"""
        self.connector.device = MagicMock()
        self.connector.device.interfaces = {
            'eth0': MagicMock(ipv4='192.168.1.1/24')
        }
        self.connector.hostname = "TestRouter"
        self.connector.connection = MagicMock()

        self.connector.config_ospf()

        self.connector.connection.write.assert_any_call(b'router ospf 1\n')

    def test_config_one_interface(self):
        """Test config_one_interface logic"""
        self.connector.device = MagicMock()
        self.connector.device.interfaces = {
            'eth0': MagicMock(ipv4='192.168.1.1/24', __str__=lambda self: 'Interface GigabitEthernet0/0')
        }
        self.connector.hostname = "TestRouter"
        self.connector.connection = MagicMock()

        self.connector.config_one_interface()

        self.connector.connection.write.assert_any_call(b"no shutdown\n")


if __name__ == '__main__':
    unittest.main()
