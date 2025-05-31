vor = True
import asyncio
import logging
from typing import Dict

from pyats import aetest
from pyats.aetest.steps import Steps
from pyats.topology import loader
from pyats.topology.device import Device

from connectors.ssh_connector import SSHConnector
from connectors.telnet_connector import TelnetConnector
from ubuntu_config import configure as configure_ubuntu_server

# Load testbed
testbed = loader.load('testbed_config.yaml')

# Setup logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, encoding='utf-8')


class SetupTelnetConnections(aetest.CommonSetup):
    """Common Setup: Initializes and connects to devices via Telnet.
        Contributors: Dusca Alexandru
    """

    @aetest.subsection
    def initialize_telnet_objects(self) -> None:
        """Initializes a dictionary to store TelnetConnector objects."""
        self.parent.parameters['telnet_objects'] = {}

    @aetest.subsection
    def connect_telnet_devices(self, telnet_objects: Dict[str, TelnetConnector]) -> None:
        """
        Connects to all devices that support Telnet in the testbed.

        Args:
            telnet_objects (Dict[str, TelnetConnector]): Dictionary to store Telnet connections.
        """
        for dev_name, dev in testbed.devices.items():
            if 'telnet' not in dev.connections:
                log.info(f"[SKIP] No Telnet connection for '{dev_name}'")
                continue

            telnet_class = dev.connections.telnet.get('class')
            if not telnet_class:
                log.warning(f"[SKIP] Telnet class not defined for '{dev_name}'")
                continue

            try:
                log.info(f"Connecting to '{dev_name}' via Telnet...")
                conn = telnet_class(dev)
                conn.connect(connection=dev.connections.telnet)
                telnet_objects[dev_name] = conn
                log.info(f"Successfully connected to '{dev_name}'")
            except Exception as e:
                log.error(f"[ERROR] Could not connect to '{dev_name}': {e}")


class TelnetDeviceConfiguration(aetest.Testcase):
    """Testcase: Configure all devices connected via Telnet."""

    @aetest.test
    def configure_ubuntu_first(self, steps: Steps) -> None:
        """Configures the Ubuntu Server before other Telnet devices."""
        with steps.start("Configure Ubuntu Server"):
            try:
                configure_ubuntu_server(testbed.devices['UbuntuServer'])
                log.info("Ubuntu Server configured successfully")
            except Exception as e:
                log.error(f"Ubuntu Server configuration failed: {e}")
                self.failed("Failed to configure Ubuntu Server", goto=['next_tc'])

    @aetest.test
    def configure_telnet_devices(self, steps: Steps, telnet_objects: Dict[str, TelnetConnector]) -> None:
        """
        Configures Telnet-connected devices using their appropriate configuration method.

        Args:
            steps (Steps): Test step context manager.
            telnet_objects (Dict[str, TelnetConnector]): Dictionary of Telnet connections.
        """
        for dev_name, connector in telnet_objects.items():
            with steps.start(f"Configuring {dev_name}"):
                try:
                    if connector.device.os == 'ftd':
                        connector.configure_ftd()
                    else:
                        connector.do_initial_config()
                    log.info(f"Successfully configured '{dev_name}'")
                except Exception as e:
                    log.error(f"Failed to configure '{dev_name}': {e}")
                    # steps.failed(f"Configuration failed for {dev_name}")


class SSHDeviceConfiguration(aetest.Testcase):
    """Testcase: Configure all router devices via SSH."""

    @aetest.test
    def create_ssh_connection_objects(self) -> None:
        """Initializes the dictionary for SSHConnector objects."""
        self.parent.parameters['ssh_objects'] = {}

    @aetest.test
    def connect_all_devices_via_ssh(self, ssh_objects: Dict[str, SSHConnector]) -> None:
        """
        Establishes SSH connections to all router-type devices in the testbed.

        Args:
            ssh_objects (Dict[str, SSHConnector]): Dictionary to store SSH connections.
        """
        for dev_name, dev in testbed.devices.items():
            if dev.type != 'router':
                log.info(f"[SKIP] Device '{dev_name}' is type '{dev.type}', skipping SSH connection")
                continue
            if 'ssh' not in dev.connections:
                log.warning(f"Device '{dev_name}' has no SSH connection defined, skipping")
                continue
            try:
                ssh_class = dev.connections.ssh.get('class', None)
                if not ssh_class:
                    log.warning(f"Device '{dev_name}' SSH connection has no 'class' defined, skipping")
                    continue

                log.info(f"Connecting to device '{dev_name}' via SSH...")
                ssh_conn = ssh_class(dev)
                ssh_conn.connect(connection=dev.connections.ssh)
                ssh_objects[dev_name] = ssh_conn
                log.info(f"Successfully connected to device '{dev_name}'")
            except Exception as e:
                log.error(f"Failed to connect to device '{dev_name}' via SSH: {e}")

    @aetest.test
    def configure_all_devices(self, steps: Steps, ssh_objects: Dict[str, SSHConnector]) -> None:
        """
        Configures all connected router devices using SSH.

        Args:
            steps (Steps): Test step context manager.
            ssh_objects (Dict[str, SSHConnector]): Dictionary of connected SSHConnector instances.
        """
        for dev_name, connector in ssh_objects.items():
            with steps.start(f"Configuring {dev_name}"):
                log.info(f"Configuring device '{dev_name}'...")
                connector.configure()
                log.info(f"Finished configuring device '{dev_name}'")

    # class ConnectionToFTD(aetest.testcase):
    #     @aetest.test
    #     def create_ftd_ssh_connection_objects(self):
    #         """Creates SSH connection dictionary to store the objects"""
    #         self.parent.parameters['ssh_objects'] = {}


class CommonCleanup(aetest.CommonCleanup):
    """Cleanup: Disconnect SSH connections after configuration is done."""

    @aetest.subsection
    def disconnect_ssh(self, ssh_objects: Dict[str, SSHConnector]) -> None:
        """
        Disconnects all SSH sessions stored in ssh_objects.

        Args:
            ssh_objects (Dict[str, SSHConnector]): Dictionary of SSH connections to close.
        """
        for name, conn in ssh_objects.items():
            conn.disconnect()


if __name__ == '__main__':
    aetest.main()
