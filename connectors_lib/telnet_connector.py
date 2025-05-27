"""
Manages Telnet a connection
"""
import logging
# pylint: disable=deprecated-module
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
    """
    Manages a telnet connection
    """
    def __init__(self, device: Device):
        self.device = device
        self._conn: Optional[telnetlib.Telnet] = None
        self.connection: Optional[AttrDict] = None

    def connect(self, **kwargs):
        """
        Connects to the device based on the connection object passed.
        Arguments:
            kwargs:
                connection(pyats.Connection)
        """
        self.connection = kwargs['connection']
        self._conn = telnetlib.Telnet(
            host=self.connection.ip.compressed,
            port=self.connection.port,
        )

    def read(self) -> str:
        """
        Performs a read_very_eager
        Return:
            The output of th read
        """
        return self._conn.read_very_eager().decode()

    def contains(self, pattern: list[str]) -> bool:
        """
        Returns true if any of the strings in pattern are present.
        """
        out = self._conn.read_very_eager().decode()
        if any(p in out for p in pattern):
            return True
        return False

    def disconnect(self):
        """
        Closes the connection.
        """
        self._conn.close()

    def write(self, command: str) -> None:
        """
        Sends a command to the device.
        """
        self._conn.write(command.encode()+b'\n')

    def write_raw(self, command: str) -> str:
        """
        Writes the exact command, without adding a \n
        """
        self._conn.write(command.encode())
        out = self._conn.read_very_eager().decode()
        return out

    def execute(self, command: str,**kwargs):
        """
        Executes the command and waits until the output matches at least one given regex.
        A \n character is added to the end of the command string.
            Args:
                command(str): The command to execute.
                kwargs:
                    prompt(List[str]): A list of the regex expressions to be tested against the output of the command
            Raises:
                RuntimeError: If the telnet connection is closed.
            Returns:
                The output of the command until (including) the regex match
        """
        if not self._conn:
            logger.error('Connection object changed to none before execute statement')
            raise RuntimeError('Connection object changed to none before execute statement')
        prompt: list[bytes] = list(map(lambda s: s.encode(), kwargs['prompt']))
        self._conn.write(f'{command}\n'.encode())
        if kwargs.get('timeout'):
            time.sleep(kwargs['timeout'])
        response = self._conn.expect(prompt)
        if isinstance(response, tuple):
            return response[2].decode('utf8')
        return response

    def try_write_enable_pass(self, last_out: str):
        """
        Writes the enable password if the prompt matches. Otherwise, does nothing.
            Args:
                last_out(str): The last output on the console
        """
        if 'Password:' in last_out:
            self.execute(self.device.credentials.default.enable_password.plaintext
                         + '\r',prompt=[r'\(config\)#', r'\w+#', r'\w+\>'])

    def try_skip_initial_config_dialog(self, last_out: str):
        """
        Checks if autoconfiguration is in progress and cancels if so
            Args:
                last_out(str): The last output on the console
        """
        if 'initial configuration dialog?' in last_out:
            self.execute('no', prompt=[r'terminate autoinstall\? \[yes\]:'])
            self.execute('yes\r', prompt=[r'successfully'])
            self.write('\r')
            self.execute('', prompt=[r'\w+\>'])

    def _initial_config_ftd(self):
        """
        Goes through the initial setup wizard
        If the default credentials of admin/Admin123 don't match, does nothing
        """
        # username = self.device.credentials.login.username
        password = self.device.credentials.login.password.plaintext
        management_ip = self.device.interfaces['management'].ipv4.ip.compressed
        management_ip_mask = self.device.interfaces['management'].ipv4.network.netmask.exploded
        management_gateway = ipaddress.ip_address(self.device.custom['management_gateway']).compressed
        dns = ipaddress.ip_address(self.device.custom['dns']).compressed
        domain = self.device.custom['domain']
        default_username = self.device.credentials.default.username
        default_password = self.device.credentials.default.password.plaintext
        self.write('\n\r')
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
            logger.error("Device is already configured. Default password and username did not work.")
        else:
            return

    def move_to_global_config(self):
        """
        Expects the connection to be in privileged exec
        Moves to global config by writing the enable password if necessary
        """
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
        """
        Configures ssh version 2
        Sets the domain name to cisco.com
        """
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
        """
        Configures scp server.
        Used for fetching the startup configuration
        """
        self.execute('ip scp server enable', prompt=[r'\(config\)#'])

    def configure_initial_interface(self):
        """
        Adds an ip address to the interface with the 'initial' alias
        """
        interface = self.device.interfaces['initial']
        self.execute(f'interface {interface.name}', prompt=[r'\(config-if\)#'])
        ip = interface.ipv4.ip.compressed
        mask = interface.ipv4.network.netmask.exploded
        self.execute(f'ip add {ip} {mask}', prompt=[r'\(config-if\)#'])
        self.execute('no sh', prompt=[r'\(config-if\)#'])
        self.execute('exit', prompt=[r'\(config\)#'])

    def enable_rest(self):
        """
        Enables a rest server
        """
        self.execute('conf t', prompt=[r'\(config\)#'])
        self.execute("ip http secure-server", prompt=[r'\(config\)#'])
        self.execute('restconf', prompt=[r'\(config\)#'])

    def save_config(self):
        """
        Saves the running configuration to startup configuration file
        """
        self.execute('end', prompt=[r'\w+#'])
        self.write('write')
        if self.contains(['Continue? [no]:', '[confirm]']):
            self.execute('yes', prompt=[r'\w+#'])
        self.execute('', prompt=[r'\w+#'])

    def do_initial_config(self):
        """
        Performs the initial configuration on the emulated console interface
        """
        if self.device.os in ('ios', 'iosxe'):
            self.move_to_global_config()
            self.configure_initial_interface()
            self.configure_ssh()
            # for napalm
            self.configure_scp_server()
            # enable secret
            if self.device.platform == 'iou':
                # logger.warning(f'En pass : {self.device.credentials.default.enable_password.plaintext}')
                self.execute(
                    f'enable secret {self.device.credentials.default.enable_password.plaintext}',
                             prompt=[r'\(config\)#']
                )
            self.save_config()
        elif self.device.os == 'ftd':
            self._initial_config_ftd()

    def is_connected(self)-> bool:
        """
        Returns the current status of the telnet connection
        """
        return not self._conn.eof
