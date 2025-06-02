import unittest
from unittest.mock import patch, MagicMock
from ssh_connector import SSHConnector


class TestSSHConnector(unittest.TestCase):
    """
    Test for SSHConnector class
    """
    def setUp(self):
        self.connector = SSHConnector()
        self.device_mock = MagicMock()
        self.device_mock.custom = {'hostname': 'test-device'}
        self.device_mock.credentials.enable.password.plaintext = 'enablepass'
        self.device_mock.os = 'iosv'
        self.device_mock.interfaces = {}

    @patch('ssh_connector.ConnectHandler')
    def test_connect_success(self, mock_connect_handler):
        """
        Test successful SSH connection
        """
        mock_ip = MagicMock()
        mock_ip.compressed = '192.168.1.1'

        conn_mock = MagicMock()
        conn_mock.ip = mock_ip
        conn_mock.port = 22
        conn_mock.credentials = {
            'login': {
                'username': 'admin',
                'password': MagicMock(plaintext='cisco')
            }
        }

        self.device_mock.connections = {'ssh': conn_mock}

        self.connector.connect(self.device_mock)

        mock_connect_handler.assert_called_once_with(
            device_type='cisco_ios',
            ip='192.168.1.1',
            port=22,
            username='admin',
            password='cisco',
            secret='enablepass'
        )

    def test_config_interfaces_empty(self):
        """
        Test ssh interface configuration
        """
        self.connector.connection = MagicMock()
        self.connector.device = MagicMock()
        self.connector.device.os = 'iosv'
        self.connector.device.interfaces = {}

        self.connector.connection.enable = MagicMock()
        self.connector.config_interfaces()
        self.connector.connection.enable.assert_called_once()


if __name__ == '__main__':
    unittest.main()
