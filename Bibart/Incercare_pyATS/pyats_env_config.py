import logging
import napalm
from UbuntuServerConfig import configure as configure_ubuntu_server

from pyats import aetest
from pyats.aetest.main import AEtest
from pyats.topology import loader

from Bibart.Incercare_pyATS.ssh_connector import SSHConnector
from telnet_connector import TelnetConnector

testbed = loader.load('config.yaml')
topology_addresses = [interf.ipv4.ip.compressed for dev in testbed.devices.values() for interf in dev.interfaces.values() if interf.ipv4]

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, encoding='utf-8')

class ConnectionAttempt(aetest.CommonSetup):
    @aetest.subsection
    def connect_telnet_all(self):
        assert testbed
        if len(testbed.devices) == 0:
            self.failed('No devices connected')
        else:
            try:
                # o sa fie parametru in TestCases si CommonCleanup
                self.parent.parameters['telnet_objects'] = {}
                for name, dev in testbed.devices.items():
                    # conectez la toate dev cu telnet
                    if 'telnet' in dev.connections:
                        telnet_conn = dev.connections.telnet['class'](dev)
                        telnet_conn.connect(connection=dev.connections.telnet)
                        self.parent.parameters['telnet_objects'][name] = telnet_conn
                    # logger.info(f'device {dev.name} successfully connected and has conn of type: {type(conn)}\n')
            except TimeoutError as e:
                self.failed(f'Connection timed out or failed, {e}')
            except KeyError as e:
                self.failed(f'Testbed is invalid. Missing class keyword, {e.with_traceback()}')
            except Exception as e:
                self.failed(f'Other exception occurred, {e}')

class InitialConfigTests(aetest.Testcase):
    @aetest.test
    def IOU1_initial_conf(self, telnet_objects: dict[str,TelnetConnector]):
        telnet_objects['IOU1'].do_initial_config()

    @aetest.test
    def CSR_initial_conf(self, telnet_objects: dict[str, TelnetConnector]):
        telnet_objects['CSR'].do_initial_config()

    @aetest.test
    def V15_initial_conf(self, telnet_objects: dict[str, TelnetConnector]):
        telnet_objects['V15'].do_initial_config()

    @aetest.test
    def UbuntuServer_initial_conf(self, telnet_objects: dict[str, TelnetConnector]):
        configure_ubuntu_server()

class SSHConnectorTests(aetest.Testcase):
    @aetest.test
    def connect_ssh_all(self):
        if self.parent.result.value != 'passed':
            self.fail('Initial Config failure. Failing SSH')
        else:
            self.parameters['ssh_clients'] = {}
            self.parent.parameters['ssh_clients'] = self.parameters['ssh_clients']
            for name, dev in testbed.devices.items():
                if name == 'UbuntuServer':
                    continue
                if 'ssh' in dev.connections:
                    ssh_client = dev.connections.ssh['class'](dev)
                    ssh_client.connect(connection=dev.connections.ssh)
                    self.parameters['ssh_clients'][name] = ssh_client

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
