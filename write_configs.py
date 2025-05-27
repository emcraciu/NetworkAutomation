"""
Saves device configurations to a file
"""
import logging
import ssl
import time
from datetime import date

from napalm.base import NetworkDriver
from napalm import get_network_driver
from pyats import aetest
from pyats.aetest.steps import Steps
from pyats.topology import loader
from connectors_lib.swagger_connector import SwaggerConnector

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, encoding='utf-8')

ssl._create_default_https_context = ssl._create_unverified_context


tb = loader.load('testbeds/config.yaml')

class SaveConfigs(aetest.Testcase):
    """
    Saves device configurations to a file
    """
    @aetest.test
    def create_napalm_clients(self):
        """
        Create napalm client objects
        """
        self.parent.parameters['napalm_drivers'] = {}

    def conn_device(self, napalm_drivers: dict[str, NetworkDriver], dev_name: str):
        """
        Connects to devices via napalm
        """
        dev = tb.devices[dev_name]
        conn = dev.connections.ssh
        username = conn.credentials.login.username
        password = conn.credentials.login.password.plaintext
        driver_class = get_network_driver('ios')
        driver = driver_class(str(conn.ip), username, password)
        driver.open()
        napalm_drivers[dev_name] = driver

    @aetest.test
    def conn_IOU(self, napalm_drivers: dict[str, NetworkDriver]):
        """
        Connects to IOU via napalm
        """
        self.conn_device(napalm_drivers, 'IOU1')

    @aetest.test
    def conn_CSR(self, napalm_drivers: dict[str, NetworkDriver]):
        """
        Connects to CSR via napalm
        """
        self.conn_device(napalm_drivers, 'CSR')

    @aetest.test
    def conn_V15(self, napalm_drivers: dict[str, NetworkDriver]):
        """
        Connects to V15 via napalm
        """
        self.conn_device(napalm_drivers, 'V15')

    def write_config_to_file(self, napalm_drivers: dict[str, NetworkDriver], dev_name: str):
        """
        Writes the configuration to a file in the configs directory
        """
        with open(f'configs/{dev_name}.cfg', 'w+', encoding='UTF-8') as f:
            f.write(napalm_drivers[dev_name].get_config()['startup'])

    @aetest.test
    def write_IOU1_config_to_file(self, napalm_drivers: dict[str, NetworkDriver]):
        """
        Writes the IOU1 configuration to a file in the configs directory
        """
        self.write_config_to_file(napalm_drivers, 'IOU1')

    @aetest.test
    def write_CSR_config_to_file(self, napalm_drivers: dict[str, NetworkDriver]):
        """
        Writes the CSR configuration to a file in the configs directory
        """
        self.write_config_to_file(napalm_drivers, 'CSR')

    @aetest.test
    def write_V15_config_to_file(self, napalm_drivers: dict[str, NetworkDriver]):
        """
        Writes the V15 configuration to a file in the configs directory
        """
        self.write_config_to_file(napalm_drivers, 'V15')

    @aetest.test
    def initiate_FTD_backup(self, steps: Steps):
        """
        Initiates a backup task on the FTD and downloads the backup file with SCP
        """
        with steps.start("Connecting to FTD"):
            device = tb.devices['FTD']
            swagger: SwaggerConnector = device.connections.rest['class'](device)
            swagger.connect(connection=device.connections.rest)
        with steps.start("Iniating backup"):
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
                    latest_backup_date = date.strftime(latest_backup.startDateTime, "%Y-%m-%d %H:%M:%SZ")
                    backup_date = date.strftime(latest_backup.startDateTime, "%Y-%m-%d %H:%M:%SZ")
                    if backup_date > latest_backup_date:
                        latest_backup = backup
                if latest_backup.status == 'SUCCESS':
                    finished_backup = True
                    break
                time.sleep(3)

            if not finished_backup:
                logger.error("Backup failed.")
                return
            logger.info("Backup successful.")

if __name__ == '__main__':
    aetest.main()
