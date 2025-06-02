import logging
from pyats import aetest
from pyats.topology import loader
from pyats.aetest.steps import Steps
from connectors.ssh_connector import SSHConnector

testbed = loader.load('testbed_config.yaml')

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, encoding='utf-8')

class SSHDeviceConfiguration(aetest.Testcase):
    @aetest.test
    def create_ssh_connection_objects(self):
        """Creates SSH connection dictionary to store the objects"""
        self.parent.parameters['ssh_objects'] = {}

    @aetest.test
    def connect_all_devices_via_ssh(self, ssh_objects: dict[str, SSHConnector]):
        """Connects all testbed devices via SSH and stores objects"""
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
    def configure_all_devices(self, steps: Steps, ssh_objects: dict[str, SSHConnector]):
        """Configures all connected devices"""
        for dev_name, connector in ssh_objects.items():
            with steps.start(f"Configuring {dev_name}"):
                log.info(f"Configuring device '{dev_name}'...")
                connector.configure()
                log.info(f"Finished configuring device '{dev_name}'")


if __name__ == '__main__':
    aetest.main()
