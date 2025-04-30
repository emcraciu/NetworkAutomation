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
            self.execute('conf t', prompt=[r'\(config\)#'])
            interface = self.device.interfaces['initial']
            ip = interface.ipv4.ip.compressed
            mask = interface.ipv4.network.netmask.exploded
            self.execute(f"int {interface.name}", prompt=[r'\(config-if\)#'])
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

        elif self.device.os == "iosxe":

            hostname = self.device.custom.hostname
            password = self.device.connections.ssh.credentials.login.password.plaintext

            ip = self.device.interfaces['initial'].ipv4.ip.compressed
            mask = self.device.interfaces['initial'].ipv4.network.netmask.exploded

            self._conn.expect([rb"management setup\? \[yes/no\]:"])
            self._conn.write(b"yes\n")

            self._conn.expect([rb"host name \[Router\]:"])
            self._conn.write(f"{hostname}\n".encode())

            self._conn.expect([rb"Enter enable secret:"])
            self._conn.write(f"{password}\n".encode())

            self._conn.expect([rb"Enter enable password:"])
            self._conn.write(f"{password}\n".encode())

            self._conn.expect([rb"Enter virtual terminal password:"])
            self._conn.write(f"{password}\n".encode())

            self._conn.expect([rb"SNMP Network Management\? \[yes\]:"])
            self._conn.write(b"no\n")

            self._conn.expect([rb"interface summary:"])
            self._conn.write(b"GigabitEthernet1\n")

            self._conn.expect([rb"IP on this interface\? \[yes\]:"])
            self._conn.write(b"yes\n")

            self._conn.expect([rb"IP address for this interface:"])
            self._conn.write(f"{ip}\n".encode())

            self._conn.expect([rb"mask for this interface \[255.255.255.0\] :"])
            self._conn.write(f"{mask}\n".encode())

            self._conn.expect([rb"Enter your selection \[2\]:"])
            self._conn.write(b"2\n")

            time.sleep(25)
            self._conn.write(b" \n")
            time.sleep(25)
            self._conn.write(b" \n")

            self._conn.expect([rb"Router>"])
            self._conn.write(b"en\n")
            self._conn.expect([rb"Password:"])
            self._conn.write(f"{password}\n".encode())
            self._conn.expect([rb"Router#"])

            self._conn.write(b"conf t\n")
            self._conn.expect([rb"Router\(config\)#"])

            self._conn.write(b"ip route 192.168.11.0 255.255.255.0 192.168.102.1\n")
            self._conn.expect([rb"Router\(config\)#"])
            self._conn.write(b"ip route 192.168.101.0 255.255.255.0 192.168.102.1\n")
            self._conn.expect([rb"Router\(config\)#"])

    def disconnect(self):
        self._conn.close()

    def execute(self, command, **kwargs):
        prompt: list[bytes] = list(map(lambda _: _.encode(), kwargs['prompt']))
        self._conn.write(f'{command}\n'.encode())
        response = self._conn.expect(prompt)
        return response

    def configure(self, command, **kwargs):
        return "config output"

    def is_connected(self):
        return not self._conn.eof
