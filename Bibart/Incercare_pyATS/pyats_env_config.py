import logging
from logging import Logger
from typing import Optional

from pyats import aetest
from pyats.aereport.testscript import TestResult
from pyats.aetest.main import AEtest
from pyats.topology import loader

from Bibart.Incercare_pyATS.ssh_connector import SSHConnector
from telnet_connector import TelnetConnector

testbed = loader.load('config.yaml')

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

class ConfigTests(aetest.Testcase):
    #TODO: fa si pentru server si guest configurile

    @aetest.test
    def IOU1_initial_conf(self, telnet_objects: dict[str,TelnetConnector]):
        # logger.info(telnet_objects)
        for name, conn in telnet_objects.items():
            if name == 'IOU1':
                conn.do_initial_config()

    @aetest.test
    def CSR_initial_conf(self, telnet_objects: dict[str, TelnetConnector]):
        for name, conn in telnet_objects.items():
            if name == 'CSR':
                conn.do_initial_config()

class SSHConnectorTests(aetest.Testcase):
    @aetest.test
    def connect_ssh_all(self):
        if self.parent.result.value != 'passed':
            self.fail('Config failure. Failing SSH')
        else:
            logger.info('Attempting SSHConnector tests')
            self.parameters['ssh_clients'] = {}
            self.parent.parameters['ssh_clients'] = self.parameters['ssh_clients']
            for name, dev in testbed.devices.items():
                if 'ssh' in dev.connections:
                    ssh_client = dev.connections.ssh['class'](dev)
                    ssh_client.connect(connection=dev.connections.ssh)
                    self.parameters['ssh_clients'][name] = ssh_client

    @aetest.test
    def test_some_commands(self, ssh_clients: dict[str, SSHConnector]):
        for dev_name, ssh_client in ssh_clients.items():
            ssh_client.get_device_details()

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
