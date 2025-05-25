import logging
import time
from UbuntuServerConfig import configure as configure_ubuntu_server
from pyats import aetest
from pyats.aetest.main import AEtest
from pyats.topology import loader
from connectors_lib.ssh_connector import SSHConnector
from connectors_lib.telnet_connector import TelnetConnector

testbed = loader.load('testbeds/config.yaml')
topology_addresses = [interf.ipv4.ip.compressed for dev in testbed.devices.values() for interf in dev.interfaces.values() if interf.ipv4]

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, encoding='utf-8')

class ConnectionAttempt(aetest.CommonSetup):
    @aetest.subsection
    def create_telnet_connection_objects(self):
        # o sa fie parametru in TestCases si CommonCleanup
        self.parent.parameters['telnet_objects'] = {}

    def connect_device(self, telnet_objects: dict[str, TelnetConnector], dev_name: str):
        dev = testbed.devices[dev_name]
        telnet_conn = dev.connections.telnet['class'](dev)
        telnet_conn.connect(connection=dev.connections.telnet)
        telnet_objects[dev_name] = telnet_conn

    @aetest.subsection
    def connect_telnet_IOU(self, telnet_objects: dict[str, TelnetConnector]):
        self.connect_device(telnet_objects, 'IOU1')

    @aetest.subsection
    def connect_telnet_CSR(self, telnet_objects: dict[str, TelnetConnector]):
        self.connect_device(telnet_objects, 'CSR')

    @aetest.subsection
    def connect_telnet_V15(self,  telnet_objects: dict[str, TelnetConnector]):
        self.connect_device(telnet_objects, 'V15')

class InitialConfigTests(aetest.Testcase):
    @aetest.test
    def UbuntuServer_initial_conf(self, telnet_objects: dict[str, TelnetConnector]):
        configure_ubuntu_server(testbed.devices['UbuntuServer'])

    @aetest.test
    def IOU1_initial_conf(self, telnet_objects: dict[str,TelnetConnector]):
        telnet_objects['IOU1'].do_initial_config()

    @aetest.test
    def CSR_initial_conf(self, telnet_objects: dict[str, TelnetConnector]):
        telnet_objects['CSR'].do_initial_config()

    @aetest.test
    def V15_initial_conf(self, telnet_objects: dict[str, TelnetConnector]):
        telnet_objects['V15'].do_initial_config()

class SSHConnectorTests(aetest.Testcase):
    @aetest.test
    def create_ssh_clients_objects(self):
        self.parent.parameters['ssh_clients'] = {}
        time.sleep(10) # sa se puna interf pe up

    def connect_device(self,  ssh_clients: dict[str, SSHConnector], dev_name: str):
        dev = testbed.devices[dev_name]
        ssh_client = dev.connections.ssh['class'](dev)
        ssh_client.connect(connection=dev.connections.ssh)
        ssh_clients[dev_name] = ssh_client

    @aetest.test
    def connect_ssh_IOU(self, ssh_clients: dict[str, SSHConnector]):
        self.connect_device(ssh_clients, 'IOU1')

    @aetest.test
    def connect_ssh_CSR(self, ssh_clients: dict[str, SSHConnector]):
        self.connect_device(ssh_clients, 'CSR')

    @aetest.test
    def connect_ssh_V15(self, ssh_clients: dict[str, SSHConnector]):
        self.connect_device(ssh_clients, 'V15')

    @aetest.test
    def config_IOU(self, ssh_clients: dict[str,SSHConnector]):
        ssh_clients['IOU1'].config()

    @aetest.test
    def config_CSR(self, ssh_clients: dict[str, SSHConnector]):
        ssh_clients['CSR'].config()

    @aetest.test
    def config_V15(self, ssh_clients: dict[str, SSHConnector]):
        ssh_clients['V15'].config()

class TestPings(aetest.Testcase):
    @aetest.test
    def test_pings(self, ssh_clients: dict[str,SSHConnector]):
        if self.parent.result.value != 'passed':
            self.fail('Config failure. Failing Pings')
        else:
            for dev_name, client in ssh_clients.items():
                result, failed_addr = client.test_pings(topology_addresses=topology_addresses)
                if result != True:
                    self.fail(f'Ping failed from device {dev_name} to address: {failed_addr}')

class Cleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect_telnet_all(self, telnet_objects: dict[str, TelnetConnector]):
        for conn in telnet_objects.values():
           if conn.is_connected():
               conn.disconnect()

    @aetest.subsection
    def disconnect_ssh_all(self, ssh_clients: dict[str, SSHConnector]):
        for conn in ssh_clients.values():
            if conn.is_connected():
                conn.disconnect()

if __name__ == '__main__':
    aetest.main()
