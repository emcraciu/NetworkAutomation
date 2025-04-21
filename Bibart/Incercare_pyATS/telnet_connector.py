import ipaddress
import logging
import telnetlib
import time
from typing import Optional

from netmiko.base_connection import TelnetConnection
from pyats.datastructures import AttrDict
from pyats.topology import Device

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class TelnetConnector:
    def __init__(self, device: Device, **kwargs):
        self.device = device
        self._conn: Optional[telnetlib.Telnet] = None
        self.connection: Optional[AttrDict] = None

    def connect(self, **kwargs):
        self.connection = kwargs['connection']
        self._conn = telnetlib.Telnet(
            host=self.connection.ip.compressed,
            port=self.connection.port,
        )

    def read(self) -> str:
        return self._conn.read_very_eager().decode()

    # modificat aici
    def contains(self, pattern: list[str]) -> bool:
        """
        Returns true if any of the strings in pattern are present.
        """
        out = self._conn.read_very_eager().decode()
        if any(p in out for p in pattern):
            return True
        return False

    def disconnect(self):
        self._conn.close()

    def write(self, command: str) -> None:
        self._conn.write(command.encode()+b'\n')

    # modificat aici
    def execute(self, command, **kwargs):
        prompt: list[bytes] = list(map(lambda s: s.encode(), kwargs['prompt']))
        self._conn.write(f'{command}\n'.encode())
        if kwargs.get('timeout'):
            time.sleep(kwargs['timeout'])
        response = self._conn.expect(prompt)
        if type(response) == tuple:
            return response[2].decode('utf8')
        return response

    def try_write_enable_pass(self, last_out: str):
        if 'Password:' in last_out:
            logger.warning("HERE DJ")
            self.execute(self.device.credentials.default.enable_password.plaintext + '\r',prompt=[r'\(config\)#', r'\w+#', r'\w+\>'])

    def try_skip_initial_config_dialog(self, last_out: str):
        if 'initial configuration dialog?' in last_out:
            self.execute('no', prompt=[r'terminate autoinstall\? \[yes\]:'])
            # logger.info('1 is one')
            self.execute('yes\r', prompt=[r'successfully'])
            # logger.info('4 is one')
            self.write('\r')
            self.execute('', prompt=[r'\w+\>'])

    def move_to_global_config(self):
        self.write('\r')
        time.sleep(2)
        out = self.read()
        self.try_skip_initial_config_dialog(out)
        self.write('en')
        time.sleep(1)
        out = self.read()
        self.try_write_enable_pass(out)
        self.execute('conf t', prompt=[r'\(config\)#'])

    def configure_ssh(self):
        # ssh
        self.execute('ip ssh version 2', prompt=[r'\(config\)#'])
        username = self.device.connections.ssh.credentials.login.username
        password = self.device.connections.ssh.credentials.login.password.plaintext

        self.execute(f'username {username} privilege 15 secret {password}', prompt=[r'\(config\)#'])

        self.execute('ip domain name cisco.com', prompt=[r'\(config\)#'])
        self.execute('crypto key generate rsa modulus 2048', prompt=[r'\(config\)#'])

        self.execute('line vty 0 4', prompt=[r'\(config-line\)#'])
        self.execute('transport input ssh', prompt=[r'\(config-line\)#'])
        self.execute('login local', prompt=[r'\(config-line\)#'])
        # self.execute('privilege level 15', prompt=[r'\(config-line\)#'])
        self.execute('exit', prompt=[r'\(config\)#'])

    def configure_scp_server(self):
        self.execute('ip scp server enable', prompt=[r'\(config\)#'])

    def configure_initial_interface(self):
        interface = self.device.interfaces['initial']
        self.execute(f'interface {interface.name}', prompt=[r'\(config-if\)#'])
        ip = interface.ipv4.ip.compressed
        mask = interface.ipv4.network.netmask.exploded
        self.execute(f'ip add {ip} {mask}', prompt=[r'\(config-if\)#'])
        self.execute('no sh', prompt=[r'\(config-if\)#'])
        self.execute('exit', prompt=[r'\(config\)#'])

    def enable_rest(self):
        self.execute('conf t', prompt=[r'\(config\)#'])
        self.execute("ip http secure-server", prompt=[r'\(config\)#'])
        self.execute('restconf', prompt=[r'\(config\)#'])

    def save_config(self):
        self.execute('end', prompt=[r'\w+#'])
        self.write('write')
        if self.contains(['Continue? [no]:', '[confirm]']):
            self.execute('yes', prompt=[r'\w+#'])
        self.execute('', prompt=[r'\w+#'])

    def do_initial_config(self):
        if self.device.os == 'ios' or self.device.os == 'iosxe':
            self.move_to_global_config()
            self.configure_initial_interface()
            self.configure_ssh()
            # for napalm
            self.configure_scp_server()

            # enable secret
            if self.device.platform == 'iou':
                logger.warning(f'En pass : {self.device.credentials.default.enable_password.plaintext}')
                self.execute(f'enable secret {self.device.credentials.default.enable_password.plaintext}', prompt=[r'\(config\)#'])

            self.save_config()

    def is_connected(self):
        return not self._conn.eof
