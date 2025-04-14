import time
from typing import Optional
import logging
import re
from paramiko import SSHClient
from paramiko.client import AutoAddPolicy
from pyats.topology import Device
from pyats.utils.secret_strings import SecretString

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SSHConnector:

    def __init__(self, device: Device):
        self.device = device
        self.hostname = None
        self.port = 22
        self.username = None
        self.password = None
        self._client: SSHClient = SSHClient()
        self._client.set_missing_host_key_policy(AutoAddPolicy())

    def connect(self, **kwargs):
        conn_details = kwargs['connection']
        self.username = conn_details.credentials.default.username
        self.password = conn_details.credentials.default.password.plaintext
        self.hostname = conn_details.ip.compressed
        logger.warning(f'hostname is {self.hostname}')
        self.port =  conn_details.port if conn_details.port else 22
        self._client.connect(hostname=self.hostname, port=self.port, username=self.username, password=self.password)

    def get_device_details(self, *args, **kwargs):
        if self.device.os not in ['ios', 'iosxe']:
            return
        out = self.execute('show version', prompt=[r'System image file is'])
        logger.warning(out)

    def do_initial_configuration(self):
        pass

    def is_connected(self):
        """
        Nu stiu daca merge asta
        """
        try:
            self._client.exec_command('\n', timeout=5)
            return True
        except:
            return False

    def execute(self, command, **kwargs):
        """
        If length of prompt is 0, does not check for pattern
        """
        prompt: list[bytes] = list(map(lambda s: s.encode(), kwargs['prompt']))
        in_, out, err = self._client.exec_command(f'{command}\n')
        out = out.read()
        if kwargs.get('timeout'):
            time.sleep(kwargs['timeout'])

        exists_match = any(re.search(p, out) != None for p in prompt)
        if exists_match or len(prompt) == 0:
            return out.decode()
        raise Exception(f"Prompts: {prompt} were not matched in {out.decode()}")

    def disconnect(self):
        self._client.close()