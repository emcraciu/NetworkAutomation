"""
Configures the UbuntuServer, IOU, V15, CSR & FTD devices
"""
import logging
import time
from pyats import aetest
from pyats.topology import loader

from ubuntu_server_config import configure as configure_ubuntu_server
from connectors_lib.ssh_connector import SSHConnector
from connectors_lib.telnet_connector import TelnetConnector

testbed = loader.load('testbeds/config.yaml')
topology_addresses = [
    interf.ipv4.ip.compressed for dev in testbed.devices.values()
    for interf in dev.interfaces.values() if interf.ipv4
]

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, encoding='utf-8')

class ConfigureEnvironment(aetest.CommonSetup):
    """
    Configures all devices
    """
    @aetest.subsection
    def create_telnet_connection_objects(self):
        """
        Creates telnet connection dictionary
        """
        # o sa fie parametru in TestCases si CommonCleanup
        self.parent.parameters['telnet_objects'] = {}

    def connect_device(self, telnet_objects: dict[str, TelnetConnector], dev_name: str):
        """
        Connects a device with a given name via telnet and places the TelnetConnector inside of the telnet_objects dictionary
        """
        dev = testbed.devices[dev_name]
        telnet_conn = dev.connections.telnet['class'](dev)
        telnet_conn.connect(connection=dev.connections.telnet)
        telnet_objects[dev_name] = telnet_conn

    @aetest.subsection
    def connect_telnet_IOU(self, telnet_objects: dict[str, TelnetConnector]):
        """
        Connects to IOU
        """
        self.connect_device(telnet_objects, 'IOU1')

    @aetest.subsection
    def connect_telnet_CSR(self, telnet_objects: dict[str, TelnetConnector]):
        """
        Connects to CSR
        """
        self.connect_device(telnet_objects, 'CSR')

    @aetest.subsection
    def connect_telnet_V15(self,  telnet_objects: dict[str, TelnetConnector]):
        """
        Connects to V15
        """
        self.connect_device(telnet_objects, 'V15')

    @aetest.subsection
    def connect_telnet_FTD(self, telnet_objects: dict[str, TelnetConnector]):
        """
        Connects to FTD
        """
        self.connect_device(telnet_objects, 'FTD')

class InitialConfigTests(aetest.Testcase):
    """
    Configures the devices through the emulated console interface via Telnet to devices
    that have a telnet connection in the testbed
    """
    @aetest.test
    def ubuntu_server_initial_conf(self):
        """
        Configures the UbuntuServer
        """
        configure_ubuntu_server(testbed.devices['UbuntuServer'])

    @aetest.test
    def IOU1_initial_conf(self, telnet_objects: dict[str,TelnetConnector]):
        """
        Configures the IOU1
        """
        telnet_objects['IOU1'].do_initial_config()

    @aetest.test
    def CSR_initial_conf(self, telnet_objects: dict[str, TelnetConnector]):
        """
        Configures the CSR
        """
        telnet_objects['CSR'].do_initial_config()

    @aetest.test
    def V15_initial_conf(self, telnet_objects: dict[str, TelnetConnector]):
        """
        Configures the V15
        """
        telnet_objects['V15'].do_initial_config()

    @aetest.test
    def FTD_initial_conf(self, telnet_objects: dict[str, TelnetConnector]):
        """
        Configures the FTD
        """
        telnet_objects['FTD'].do_initial_config()

class SSHConnectorTests(aetest.Testcase):
    """
    Connects via SSH to the devices that have an SSH connection in the testbed
    """
    @aetest.test
    def create_ssh_clients_objects(self):
        """
        Creates a ssh_clients dictionary that will store all SSHConnector objects
        """
        self.parent.parameters['ssh_clients'] = {}
        time.sleep(10) # sa se puna interf pe up

    def connect_device(self,  ssh_clients: dict[str, SSHConnector], dev_name: str):
        """
        Connects to a device via SSH and places the SSHConnector inside of the ssh_clients dictionary
        """
        dev = testbed.devices[dev_name]
        ssh_client = dev.connections.ssh['class'](dev)
        ssh_client.connect(connection=dev.connections.ssh)
        ssh_clients[dev_name] = ssh_client

    @aetest.test
    def connect_ssh_IOU(self, ssh_clients: dict[str, SSHConnector]):
        """
        Connects to IOU
        """
        self.connect_device(ssh_clients, 'IOU1')

    @aetest.test
    def connect_ssh_CSR(self, ssh_clients: dict[str, SSHConnector]):
        """
        Connects to CSR
        """
        self.connect_device(ssh_clients, 'CSR')

    @aetest.test
    def connect_ssh_V15(self, ssh_clients: dict[str, SSHConnector]):
        """
        Connects to V15
        """
        self.connect_device(ssh_clients, 'V15')

    @aetest.test
    def config_IOU(self, ssh_clients: dict[str,SSHConnector]):
        """
        Performs the main IOU configuration including enabling interfaces, adding ip addresses,
        adding static routes, enabling routing protocols and creating dhcp pools
        """
        ssh_clients['IOU1'].config()

    @aetest.test
    def config_CSR(self, ssh_clients: dict[str, SSHConnector]):
        """
        Performs the main CSR configuration including enabling interfaces, adding ip addresses,
        adding static routes, enabling routing protocols and creating dhcp pools
        """
        ssh_clients['CSR'].config()

    @aetest.test
    def config_V15(self, ssh_clients: dict[str, SSHConnector]):
        """
        Performs the main V15 configuration including enabling interfaces, adding ip addresses,
        adding static routes, enabling routing protocols
        """
        ssh_clients['V15'].config()

class TestPings(aetest.Testcase):
    """
    Tests pings across all devices
    """
    @aetest.test
    def test_pings(self, ssh_clients: dict[str,SSHConnector]):
        """
        Loops through all devices with an SSH connection in the testbed and
        tests pings to every other device via SSH
        Fails if the previous test failed.
        """
        if self.parent.result.value != 'passed':
            self.fail('Config failure. Failing Pings')
        else:
            for dev_name, client in ssh_clients.items():
                result, failed_addr = client.test_pings(topology_addresses=topology_addresses)
                if result is not True:
                    self.fail(f'Ping failed from device {dev_name} to address: {failed_addr}')

class Cleanup(aetest.CommonCleanup):
    """
    Terminates all of the telnet & SSH connections
    """
    @aetest.subsection
    def disconnect_telnet_all(self, telnet_objects: dict[str, TelnetConnector]):
        """
        Terminates all tenet connections
        """
        for conn in telnet_objects.values():
            if conn.is_connected():
                conn.disconnect()

    @aetest.subsection
    def disconnect_ssh_all(self, ssh_clients: dict[str, SSHConnector]):
        """
        Terminates all ssh connections
        """
        for conn in ssh_clients.values():
            if conn.is_connected():
                conn.disconnect()

if __name__ == '__main__':
    aetest.main()
