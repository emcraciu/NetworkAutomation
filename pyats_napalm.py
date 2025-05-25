import logging

from napalm.base import NetworkDriver
from pyats import aetest
from pyats.topology import testbed
from napalm import *
from pyats.topology import loader

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, encoding='utf-8')

testbed = loader.load('config.yaml')

class NapalmTest(aetest.Testcase):
    @aetest.test
    def create_napalm_clients(self):
        self.parent.parameters['napalm_drivers'] = {}

    def conn_device(self, napalm_drivers: dict[str, NetworkDriver], dev_name: str):
        dev = testbed.devices[dev_name]
        conn = dev.connections.ssh
        username = conn.credentials.login.username
        password = conn.credentials.login.password.plaintext
        driverClass = get_network_driver('ios')
        driver = driverClass(str(conn.ip), username, password)
        driver.open()
        napalm_drivers[dev_name] = driver

    @aetest.test
    def conn_IO1(self, napalm_drivers: dict[str, NetworkDriver]):
        self.conn_device(napalm_drivers, 'IOU1')

    @aetest.test
    def conn_CSR(self, napalm_drivers: dict[str, NetworkDriver]):
        self.conn_device(napalm_drivers, 'CSR')

    @aetest.test
    def conn_V15(self, napalm_drivers: dict[str, NetworkDriver]):
        self.conn_device(napalm_drivers, 'V15')

    def write_config_to_file(self, napalm_drivers: dict[str, NetworkDriver], dev_name: str):
        with open(f'configs/{dev_name}.cfg', 'w+') as f:
            f.write(napalm_drivers[dev_name].get_config()['startup'])

    @aetest.test
    def write_IOU1_config_to_file(self, napalm_drivers: dict[str, NetworkDriver]):
        self.write_config_to_file(napalm_drivers, 'IOU1')

    @aetest.test
    def write_CSR_config_to_file(self, napalm_drivers: dict[str, NetworkDriver]):
        self.write_config_to_file(napalm_drivers, 'CSR')

    @aetest.test
    def write_V15_config_to_file(self, napalm_drivers: dict[str, NetworkDriver]):
        self.write_config_to_file(napalm_drivers, 'V15')

    @aetest.test
    def modify_IOU1_config(self, napalm_drivers: dict[str, NetworkDriver]):
        d = napalm_drivers['IOU1']
        # ?
        d.load_merge_candidate(config='''interface Ethernet0/1
 ip address 192.168.102.1 255.255.255.0
        ''')
        d.commit_config()

if __name__ == '__main__':
    aetest.main()