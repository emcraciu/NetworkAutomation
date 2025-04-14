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
        return response

    def do_initial_config(self):
        if self.device.os == 'ios' or self.device.os == 'iosxe':
            self.write('\r')
            time.sleep(2)
            if self.contains(['initial configuration dialog?']):
                # TODO: de ce se blocheaza ??
                self.execute('no', prompt=[rf'terminate autoinstall? [yes]:'])
                logger.info('1 is one')
                self.execute('yes\r', prompt=[r'successful'])
                logger.info('2 is one')
                self.execute('yes\r', prompt=[r''])
                logger.info('3 is one')
                self.execute('', prompt=[r'\w+\>'], timeout=60)
                logger.info('4 is one')

            self.execute('en', prompt=[r'#', r'\(config\)#'])
            self.execute('conf t', prompt=[r'\(config\)#'])
            hostname = self.device.custom.hostname
            self.execute(f'hostname {hostname}', prompt=[rf'{hostname}\(config\)#'])

            # interfete
            for iname, interface in self.device.interfaces.items():
                self.execute(f'interface {interface.name}', prompt=[r'\(config-if\)#'])

                if interface.ipv4:
                    ip = interface.ipv4.ip.compressed
                    mask = interface.ipv4.network.netmask.exploded
                    self.execute(f'ip add {ip} {mask}', prompt=[r'\(config-if\)#'])
                else:
                    self.execute('ip add dhcp', prompt=[r'\(config-if\)#'])
                self.execute(f'no sh', prompt=[r'\(config-if\)#'])
                self.execute('exit', prompt=[r'\(config\)#'])

            # rute
            if self.device.custom.get('routes'):
                for r_name, route in self.device.custom['routes'].items():
                    to_ip = ipaddress.IPv4Network(route['to_ip'])
                    self.execute(f'ip route {to_ip.network_address} {to_ip.netmask.exploded} {route['via']}', prompt=[r'\(config\)#'])

            # rip
            if self.device.type == 'router' and self.device.custom.get('rip'):
                rip_dict = self.device.custom['rip']
                self.execute('router rip', prompt=[r'\(config-router\)#'])
                self.execute('version 2', prompt=[r'\(config-router\)#'])
                self.execute('no auto-summary', prompt=[r'\(config-router\)#'])
                networks = list(map(lambda str_addr : ipaddress.IPv4Network(str_addr), rip_dict.get('networks')))
                for network in networks:
                    self.execute(f'network {network.network_address}', prompt=[r'\(config-router\)#'])
                self.execute('exit', prompt=[r'\(config\)#'])

            # dhcp pools
            if self.device.custom.get('dhcp_pools'):
                for pool_name, pool in self.device.custom['dhcp_pools'].items():
                    self.execute(f'ip dhcp pool {pool_name}', prompt=[r'\(dhcp-config\)#'])
                    network_ip = ipaddress.IPv4Network(pool['network'])
                    self.execute(f'network {network_ip.network_address.compressed} {network_ip.netmask.exploded}', prompt=[r'\(dhcp-config\)#'])
                    self.execute(f'default-router {pool['default_router']}', prompt=[r'\(dhcp-config\)#'])
                    if(pool.get('domain_name')):
                        self.execute(f'domain-name {pool['domain_name']}', prompt=[r'\(dhcp-config\)#'])
                    if(pool.get('dns_server')):
                        self.execute(f'dns-server {pool['dns_server']}', prompt=[r'\(dhcp-config\)#'])
                    self.execute('exit', prompt=[r'\(config\)#'])
                    if pool.get('excluded_address_ranges'):
                        for r in pool['excluded_address_ranges']:
                            start, end = r['start'], r['end']
                            self.execute(f'ip dhcp excluded-address {start} {end}', prompt=[r'\(config\)#'])

            # ssh
            self.execute('ip ssh version 2',prompt=[r'\(config\)#'])
            username = self.device.connections.ssh.credentials.default.username
            password = self.device.connections.ssh.credentials.default.password.plaintext

            # TODO: De ce nu merge?? Parola nu e buna??
            self.execute(f'username {username} privilege 15 secret {password}', prompt=[r'\(config\)#'])

            self.execute('ip domain name cisco.com', prompt=[r'\(config\)#'])
            self.execute('crypto key generate rsa modulus 2048', prompt=[r'\(config\)#'])

            self.execute('line vty 0 4', prompt=[r'\(config-line\)#'])
            self.execute('transport input ssh', prompt=[r'\(config-line\)#'])
            self.execute('login local', prompt=[r'\(config-line\)#'])
            self.execute('privilege level 15', prompt=[r'\(config-line\)#'])
            self.execute('exit', prompt=[r'\(config\)#'])

            # save
            self.execute('end', prompt=[rf'{hostname}#'])
            self.write('write')
            if self.contains(['Continue? [no]:', '[confirm]']):
                self.execute('yes', prompt=[rf'#{hostname}#'])
            self.execute('', prompt=[rf'{hostname}#'])


    def configure(self, command, **kwargs):
        return "config output"

    def is_connected(self):
        # TODO: verifica
        try:
            self._conn.write('')
            return True
        except:
            return False
