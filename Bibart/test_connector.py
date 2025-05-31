"""
Magic Mock testing
"""
# pylint: disable=import-outside-toplevel
# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument
# pylint: disable=protected-access

import unittest
from ipaddress import IPv4Interface
from unittest.mock import MagicMock, patch

# from pyats.datastructures import AttrDict
def get_mocked_ssh_connection_object():
    """
    Returns a mock SSH connection object that would be present
    on a testbed device.
    """
    ssh_connection = MagicMock()
    ssh_connection.credentials.loging.username = "admin"
    ssh_connection.credentials.loging.password = "Cisco@123"
    ssh_connection.protocol = "ssh"
    ssh_connection.port = 22
    ssh_connection.ip = IPv4Interface("192.168.102.2")
    return ssh_connection

def get_mocked_IOU_device():
    """
    Returns a mock IOU device
    """
    dev = MagicMock()
    dev.os = "ios"
    dev.name = "IOU"
    dev.type = "router"
    return dev

def get_mocked_SSHConnector(dev):
    """
    Returns an SSHConnector created with a mock device
    and a mock shell.
    """
    shell = MagicMock()
    shell.closed = False
    shell.recv_ready.return_value = True
    shell.recv.return_value = b'Hello World'

    ssh_client = MagicMock()
    ssh_client.invoke_shell.return_value = shell
    ssh_client.connect.return_value = None
    ssh_client.invoke_shell.return_value = shell

    from connectors_lib.ssh_connector import SSHConnector
    connector = SSHConnector(dev)
    connector._client = ssh_client

    return connector, ssh_client, shell

device = MagicMock()
class TestConnector(unittest.TestCase):
    """
    Includes test cases that use Magic Mock
    """
    def test_connector_create(self):
        """
        Tests telnet connection to device
        """
        from connectors_lib.telnet_connector import TelnetConnector
        self.telnet = TelnetConnector(device)

    @patch('telnetlib.Telnet')
    def test_connector_connect(self, get_mock):
        """
        Mocks a connection.
        """
        get_mock.return_value = MagicMock() # not mandatory for MagicMock, only for Mock
        connection = MagicMock()
        from connectors_lib.telnet_connector import TelnetConnector
        telnet = TelnetConnector(device)
        self.assertRaises(KeyError,telnet.connect)
        self.assertEqual(None, telnet.connect(connection=connection))

    @patch('telnetlib.Telnet')
    def test_connector_enable_rest(self, get_mock):
        """
        Mocks REST connection
        """
        get_mock.return_value = MagicMock()
        from connectors_lib.telnet_connector import TelnetConnector
        telnet = TelnetConnector(device)
        telnet._conn = MagicMock(write=lambda *args, **kwargs: None)
        self.assertEqual(None, telnet.enable_rest())

    @patch('telnetlib.Telnet')
    def test_connector_execute_rest(self, get_mock):
        """
        Mocks telnet connection
        """
        get_mock.return_value = MagicMock()
        from connectors_lib.telnet_connector import TelnetConnector
        telnet = TelnetConnector(device)
        telnet._conn = MagicMock(write=lambda *args, **kwargs: None)
        # telnet.execute = lambda *args, **kwargs: args, kwargs
        # self.assertMultiLineEqual('first', 'second', telnet.enable_rest())

    # def test_ssh_connection(self):
    #     """
    #     Tests SSH connection by mocking a device, ssh_client & ssh_shell
    #     """
    #     iou = get_mocked_IOU_device()
    #     ssh_conn_obj = get_mocked_ssh_connection_object()
    #     ssh_connector, ssh_client, ssh_shell = get_mocked_SSHConnector(iou)
    #     assert ssh_connector._client is ssh_client
    #
    #     ssh_connector.connect(connection=ssh_conn_obj)
    #     assert ssh_connector.username == "admin"
    #     assert ssh_connector.password == "Cisco@123"
    #     assert ssh_connector.hostname == "192.168.102.2"
    #     assert ssh_connector.port == 22
    #     assert ssh_connector._shell == ssh_shell

    def test_ping_helper_test_pings(self):
        """
        Tests the result of the test_pings function
        """
        from ping_helper import test_pings
        topology_addresses=['10.10.10.10', '20.20.20.20', '30.30.30.30']
        device_name = 'fake_router'
        addr_idx = 0
        def read():
            nonlocal addr_idx
            if addr_idx == 2:
                return "Success rate is 0 percent"
            addr_idx += 1
            return "Success rate is 100 percent"
        def execute(command: str, **kwargs):
            return ""
        all_worked, ping_results = test_pings(topology_addresses,execute, read, device_name, os='ios')
        assert all_worked is False
        assert ping_results == {
            '10.10.10.10': True,
            '20.20.20.20': True,
            '30.30.30.30': False,
        }
    def test_ubuntu_server_pings(self):
        """
        Tests if ubuntu server can ping some mock addresses
        """
        from ubuntu_server_ping_all import ping_all
        topology_addresses=['10.10.10.10', '20.20.20.20', '127.0.0.1']
        all_worked, ping_results = ping_all(topology_addresses=topology_addresses)
        assert all_worked is False
        assert ping_results == {
            '10.10.10.10': False,
            '20.20.20.20': False,
            '127.0.0.1': True,
        }
