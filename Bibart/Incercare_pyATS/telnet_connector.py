import logging
import telnetlib
import time
import re
from typing import Optional
import ipaddress

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

    # @return str
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

    def write_raw(self, command: str) -> None:
        """
        Writes the exact command, without adding a \n
        """
        self._conn.write(command.encode())
        out = self._conn.read_very_eager().decode()
        return out

    #
    def execute(self, command,**kwargs):
        if not self._conn:
            logger.error('Connection object changed to none before execute statement')
            raise RuntimeError('Connection object changed to none before execute statement')
            return
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
            # logger.warning("HERE DJ")
            self.execute(self.device.credentials.default.enable_password.plaintext + '\r',prompt=[r'\(config\)#', r'\w+#', r'\w+\>'])

    def try_skip_initial_config_dialog(self, last_out: str):
        if 'initial configuration dialog?' in last_out:
            self.execute('no', prompt=[r'terminate autoinstall\? \[yes\]:'])
            # logger.info('1 is one')
            self.execute('yes\r', prompt=[r'successfully'])
            # logger.info('4 is one')
            self.write('\r')
            self.execute('', prompt=[r'\w+\>'])

    def _initial_config_ftd(self):
        username = self.device.credentials.login.username
        password = self.device.credentials.login.password.plaintext
        management_ip = self.device.interfaces['management'].ipv4.ip.compressed
        management_ip_mask = self.device.interfaces['management'].ipv4.network.netmask.exploded
        management_gateway = ipaddress.ip_address(self.device.custom['management_gateway']).compressed
        dns = ipaddress.ip_address(self.device.custom['dns']).compressed
        domain = self.device.custom['domain']
        default_username = self.device.credentials.default.username
        default_password = self.device.credentials.default.password.plaintext
        # self.execute('\n', prompt=[r'firepower login:'])
        self.write('\n')
        time.sleep(2)
        out = self.read()
        pattern = r'(?:FTD login\:\s*$)|(?:Password\:\s*$)|(?:firepower login\:)'
        re_match = re.findall(pattern, out)
        if re_match:
            # need to login
            match = re_match[-1]
            if 'Password:' in match:
                self.execute('\n', prompt=[r'FTD login\:'])
            self.write(default_username)
            time.sleep(3)
            out = self.read()
            if 'Enter new password:' in out:
                self.write(password)
                time.sleep(1)
                out = self.read()
            else:
                self.write(default_password)
                time.sleep(10)
                out = self.read()

        if ('Press <ENTER> to display the EULA:' in out
                or 'You must change the password' in out
                or '--More--' in out):
            # Need to go through agreement
            if 'Press <ENTER> to display the EULA:' in out or '--More--' in out:
                out = self.execute(' \n\r', prompt=[r'\-\-More\-\-'])
                # Initial Startup
                for _ in range(20):
                    if 'AGREE to EULA' in out:
                        break
                    out = self.write_raw(' ')
                    time.sleep(.3)
                self.execute('YES', prompt=[r'Enter new password\:'])

            self.execute(password, prompt=[r'Confirm new password:'])
            self.execute(password, prompt=[r'IPv4\? \(y/n\) \[y\]:'])
            self.execute('y', prompt=[r'IPv6\? \(y/n\) \[n\]:'])
            self.execute('n', prompt=[r'\(dhcp\/manual\) \[manual\]:'])
            self.execute('manual', prompt=[r'management interface \[.*\]:'])
            self.execute(management_ip, prompt=[r'netmask for the management interface \[.*\]:'])
            self.execute(management_ip_mask, prompt=[r'gateway for the management interface \[.*\]:'])
            self.execute(management_gateway, prompt=[r'fully qualified hostname for this system \[.*\]:'])
            self.execute('firepower', prompt=[r'comma\-separated list of DNS servers or \'none\' \[.*\]:'])
            self.execute(dns, prompt=[r'comma\-separated list of search domains or \'none\' \[\]:'])
            self.execute(domain, prompt=[r'Manage the device locally\? \(yes\/no\) \[yes\]:'])
            self.write('yes')

            # Wait for setup to finish
            for _ in range(5):
                time.sleep(1)
                out = self.read()
                if '>' in out:
                    break
            else:
                logger.error('FTD Config failed after entering all initial config details and waiting to load.')
                return

        # Already configured -> need to wipe current config
        elif 'Login incorrect' in out:
            logger.error("LOGIN INCORRECT. Tried default password")
        else:
        #     self.execute('configure manager delete',prompt=[r'Do you want to continue\[yes\/no\]\:'])
        #     self.execute('yes', prompt=[r'\> '])
        #     self.execute('reboot', prompt=[r"Please enter \'YES\' or \'NO\'\:"])
        #     self.write('YES')
        #     for i in range(5):
        #         out = self.read()
        #         if 'FTD login:' in out:
        #             break
        #     else:
        #         raise RuntimeError('FTD did not finish reboot')
        #     self.execute('configure fierewall routed', prompt=[r'\> '])
        # TODO:
            """
            configure network management-data-interface 
            > Unable to access DetectionEngine::bulkLoad
            """
            self.execute(f'configure network ipv4 manual {management_ip} {management_ip_mask} {management_gateway}', prompt=[r'\> '])

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
                # logger.warning(f'En pass : {self.device.credentials.default.enable_password.plaintext}')
                self.execute(f'enable secret {self.device.credentials.default.enable_password.plaintext}', prompt=[r'\(config\)#'])

            self.save_config()
        elif self.device.os == 'ftd':
            self._initial_config_ftd()

    def is_connected(self):
        return not self._conn.eof
