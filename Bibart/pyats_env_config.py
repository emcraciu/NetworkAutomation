"""
Configures the UbuntuServer, IOU, V15, CSR & FTD devices
"""
import asyncio
import json
import logging
import time
from threading import Thread
from pyats import aetest
from pyats.topology import loader
from pyats.aetest.steps import Steps

from ubuntu_server_config import configure as configure_ubuntu_server
from ubuntu_server_ping_all import ping_all
from connectors_lib.ssh_connector import SSHConnector
from connectors_lib.telnet_connector import TelnetConnector
from configure_fdm_via_rest import configure_fdm

testbed = loader.load('testbeds/config.yaml')
topology_addresses = [
    interf.ipv4.ip.compressed for dev in testbed.devices.values()
    for interf in dev.interfaces.values() if interf.ipv4
]

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, encoding='utf-8')
PING_RESULTS_FILE = 'ping_results.json'

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

    async def ubuntu_server_initial_conf(self, steps: Steps):
        """
        Configures the UbuntuServer
        """
        with steps.start("Configuring Ubuntu Server"):
            configure_ubuntu_server(testbed.devices['UbuntuServer'])

    async def IOU1_initial_conf(self, steps: Steps, telnet_connector: TelnetConnector):
        """
        Configures the IOU1
        """
        with steps.start("Performing IOU Initial Configuration"):
            telnet_connector.do_initial_config()

    async def CSR_initial_conf(self, steps: Steps, telnet_connector: TelnetConnector):
        """
        Configures the CSR
        """
        with steps.start("Performing CSR Initial Configuration"):
            telnet_connector.do_initial_config()

    async def V15_initial_conf(self, steps: Steps, telnet_connector: TelnetConnector):
        """
        Configures the V15
        """
        with steps.start("Performing V15 Initial Configuration"):
            telnet_connector.do_initial_config()

    async def FTD_initial_conf(self, steps: Steps, telnet_connector: TelnetConnector):
        """
        Configures the FTD
        """
        with steps.start("Performing FTD Initial Configuration"):
            telnet_connector.do_initial_config()

    async def asyncio_main(self, steps: Steps, telnet_objects: dict[str, TelnetConnector]):
        """
        Calls all initial_configuration functions
        """
        await asyncio.gather(
            self.ubuntu_server_initial_conf(steps),
            self.IOU1_initial_conf(steps, telnet_objects['IOU1']),
            self.CSR_initial_conf(steps, telnet_objects['CSR']),
            self.V15_initial_conf(steps, telnet_objects['V15']),
            self.FTD_initial_conf(steps, telnet_objects['FTD'])
        )

    @aetest.test
    def initial_configuration_all_devices(self, steps: Steps, telnet_objects: dict[str, TelnetConnector]):
        """
        Calls asyncio_main which schedules all async initial configuration functions
        """
        asyncio.run(self.asyncio_main(steps, telnet_objects))

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

    def thread_config_CSR(self, steps: Steps, ssh_connector: SSHConnector):
        """
        Performs the main CSR configuration including enabling interfaces, adding ip addresses,
        adding static routes, enabling routing protocols and creating dhcp pools
        """
        with steps.start("Configuring CSR in parallel with V15"):
            ssh_connector.config()

    def thread_config_V15(self, steps: Steps, ssh_connector: SSHConnector):
        """
        Performs the main V15 configuration including enabling interfaces, adding ip addresses,
        adding static routes, enabling routing protocols
        """
        with steps.start("Configuring V15 in parallel with CSR"):
            ssh_connector.config()

    @aetest.test
    def config_CSR_and_V15_parallel(self, steps: Steps, ssh_clients: dict[str, SSHConnector]):
        """
        Configures CSR & V15 in parallel
        """
        csr_thread = Thread(target=self.thread_config_CSR, args=(steps, ssh_clients['CSR']))
        v15_thread = Thread(target=self.thread_config_V15, args=(steps, ssh_clients['V15']))
        csr_thread.start()
        v15_thread.start()
        csr_thread.join()
        v15_thread.join()

    @aetest.test
    def configure_FTD_swagger(self, steps: Steps):
        """
        Configures FTD via FDM and swagger client
        """
        configure_fdm(steps)

class TestPings(aetest.Testcase):
    """
    Tests pings from all devices to all other
    """
    @aetest.test
    def test_pings(self, ssh_clients: dict[str,SSHConnector]):
        """
        Loops through all devices with an SSH connection in the testbed and
        tests pings to every other device via SSH
        """
        ping_results = {}
        for dev_name, client in ssh_clients.items():
            ping_results[dev_name] = {}
            _, device_ping_results = client.test_pings(topology_addresses=topology_addresses)
            ping_results[dev_name] = device_ping_results
        _, ubuntu_server_ping_results = ping_all()
        ping_results['UbuntuServer'] = ubuntu_server_ping_results
        with open(PING_RESULTS_FILE, 'w', encoding='utf-8') as fh:
            json.dump(ping_results,fh,indent=4)

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
