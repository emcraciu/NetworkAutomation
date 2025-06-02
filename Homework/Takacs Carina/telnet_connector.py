# telnet_connector.py
import telnetlib
import time
from typing import Optional

from pyats.datastructures import AttrDict
from pyats.topology import Device


class TelnetConnector:

    def __init__(self, device: Device, **kwargs):
        self._conn: Optional[telnetlib.Telnet] = None
        self.device = device
        self.connection: Optional[AttrDict] = None

    def connect(self, **kwargs):
        self.connection = kwargs['connection']
        self._conn = telnetlib.Telnet(
            host=self.connection.ip.compressed,
            port=self.connection.port
        )

    def do_initial_configuration(self):
        if self.device.os == 'ios':
            # Existing IOS configuration procedure
            self.execute('conf t', prompt=[r'\(config\)#'])
            interface = self.device.interfaces['initial']
            self.execute(f"int {interface.name}", prompt=[r'\(config-if\)#'])
            ip = interface.ipv4.ip.compressed
            mask = interface.ipv4.network.netmask.exploded
            self.execute(f"ip add {ip} {mask}", prompt=[r'\(config-if\)#'])
            self.execute('no shut', prompt=[r'\(config-if\)#'])
            self.execute('exit', prompt=[r'\(config\)#'])
            hostname = self.device.custom.hostname
            self.execute(f'hostname {hostname}', prompt=[r'\(config\)#'])
            self.execute('crypto key generate rsa', prompt=[r'\(config\)#'])
            username = self.device.connections.ssh.credentials.login.username
            password = self.device.connections.ssh.credentials.login.password.plaintext
            self.execute(f'username {username} privilege 15 secret {password}', prompt=[r'\(config\)#'])
            self.execute('line vty 0 4', prompt=[r'\(config-line\)#'])
            self.execute("transport input ssh", prompt=[r'\(config-line\)#'])
            self.execute("login local", prompt=[r'\(config-line\)#'])
            self.execute('exit', prompt=[r'\(config\)#'])
            self.execute('ip ssh version 2', prompt=[r'\(config\)#'])
            self.execute('end', prompt=[rf'{hostname}#'])
            self.execute('write', prompt=[rf'\[confirm\]|{hostname}#'])
            self.execute('', prompt=[rf'{hostname}#'])
        elif self.device.os == 'csr':
            # New CSR initial configuration branch
            #
            # Trigger the initial configuration dialog
            self._conn.write(b'\n')
            response = self._conn.read_until(b"[yes/no]:", timeout=10)
            if b'initial configuration dialog? [yes/no]' in response:
                # Respond "yes" to start initial configuration
                self._conn.write(b'yes\n')
                self._conn.read_until(b"management setup? [yes/no]:", timeout=10)
                self._conn.write(b'yes\n')
                self._conn.read_until(b"host name [Router]:", timeout=10)
                # Send custom hostname from testbed
                hostname = self.device.custom.hostname
                self._conn.write(f'{hostname}\n'.encode())
                self._conn.read_until(b"Enter enable secret:", timeout=10)
                password = self.device.connections.ssh.credentials.login.password.plaintext
                self._conn.write(f'{password}\n'.encode())
                self._conn.read_until(b"Enter enable password:", timeout=10)
                self._conn.write(f'{password}\n'.encode())
                self._conn.read_until(b"Enter virtual terminal password:", timeout=10)
                self._conn.write(f'{password}\n'.encode())
                self._conn.read_until(b"SNMP Network Management? [yes]:", timeout=10)
                self._conn.write(b'no\n')
                self._conn.read_until(b"interface summary:", timeout=10)
                self._conn.write(b'GigabitEthernet1\n')
                self._conn.read_until(b"IP on this interface? [yes]:", timeout=10)
                self._conn.write(b'yes\n')
                self._conn.read_until(b"IP address for this interface:", timeout=10)
                # Use a fixed IP for the interface (adjust if necessary)
                self._conn.write(b'192.168.102.2\n')
                self._conn.read_until(b"mask for this interface [255.255.255.0] :", timeout=10)
                self._conn.write(b'255.255.255.0\n')
                self._conn.read_until(b"Enter your selection [2]:", timeout=10)
                self._conn.write(b'2\n')
                # Optionally, send a few newlines to flush the dialog
                for _ in range(3):
                    time.sleep(5)
                    self._conn.write(b'\n')
            elif b'Router>' in response:
                print("CSR Router is already configured.")

    def disconnect(self):
        self._conn.close()

    def execute(self, command, **kwargs):
        # This method is used by the IOS branch.
        prompt: list[bytes] = list(map(lambda p: p.encode() if isinstance(p, str) else p, kwargs['prompt']))
        self._conn.write(f'{command}\n'.encode())
        response = self._conn.expect(prompt)
        return response

    def configure(self, command, **kwargs):
        # Send configuration commands; placeholder implementation.
        return "config output"

    def is_connected(self):
        return not self._conn.eof
