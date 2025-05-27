import logging
import time
from datetime import date

from napalm.base import NetworkDriver
from pyats import aetest
from pyats.aetest.steps import Steps
from pyats.topology import testbed
from napalm import *
from pyats.topology import loader
import ssl
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, encoding='utf-8')

ssl._create_default_https_context = ssl._create_unverified_context
from connectors_lib.swagger_connector import SwaggerConnector

tb = loader.load('testbeds/config.yaml')

class NapalmTest(aetest.Testcase):
    @aetest.test
    def create_napalm_clients(self):
        self.parent.parameters['napalm_drivers'] = {}

    def conn_device(self, napalm_drivers: dict[str, NetworkDriver], dev_name: str):
        dev = tb.devices[dev_name]
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
    def initiate_FTD_backup(self, steps: Steps):
        with steps.start("Connecting to FTD"):
            device = tb.devices['FTD']
            swagger: SwaggerConnector = device.connections.rest['class'](device)
            swagger.connect(connection=device.connections.rest)
        with steps.start("Iniating backup"):
            c = swagger.client
            model = swagger.client.get_model("BackupImmediate")
            swagger.client.BackupImmediate.addBackupImmediate(
                body=(
                    model(
                        name="BackupMyStuff",
                        # status_code='default'
                    )
                )
            ).result()

            finished_backup = False
            for _ in range(10):
                backups = swagger.client.Job.getJobHistoryBackupList().result().items
                latest_backup = backups[0]
                for backup in backups:
                    latest_backup_date = date.strptime(latest_backup.startDateTime, "%Y-%m-%d %H:%M:%SZ")
                    backup_date = date.strptime(latest_backup.startDateTime, "%Y-%m-%d %H:%M:%SZ")
                    if backup_date > latest_backup_date:
                        latest_backup = backup
                if latest_backup.status == 'SUCCESS':
                    finished_backup = True
                    break
                time.sleep(3)

            if not finished_backup:
                logger.error("Backup failed.")
                return
            else:
                logger.info("Backup successful.")


if __name__ == '__main__':
    aetest.main()