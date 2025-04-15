import ipaddress
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
        self._shell = None

    def connect(self, **kwargs):
        conn_details = kwargs['connection']
        self.username = conn_details.credentials.default.username
        self.password = conn_details.credentials.default.password.plaintext
        self.hostname = conn_details.ip.compressed
        self.port =  conn_details.port if conn_details.port else 22
        self._client.connect(hostname=self.hostname, port=self.port, username=self.username, password=self.password)
        self._shell = self._client.invoke_shell()

    def config(self):
        if self.device.os == 'ios' or self.device.os == 'iosxe':
            self.execute('\r', prompt=[])
            self.execute('en', prompt=[r'\w+#', r'\(config\)#'])
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
                    self.execute(f'ip route {to_ip.network_address} {to_ip.netmask.exploded} {route['via']}',
                                 prompt=[r'\(config\)#'])

            # rip
            if self.device.type == 'router' and self.device.custom.get('rip'):
                rip_dict = self.device.custom['rip']
                self.execute('router rip', prompt=[r'\(config-router\)#'])
                self.execute('version 2', prompt=[r'\(config-router\)#'])
                self.execute('no auto-summary', prompt=[r'\(config-router\)#'])
                networks = list(map(lambda str_addr: ipaddress.IPv4Network(str_addr), rip_dict.get('networks')))
                for network in networks:
                    self.execute(f'network {network.network_address}', prompt=[r'\(config-router\)#'])
                self.execute('exit', prompt=[r'\(config\)#'])

            # dhcp pools
            if self.device.custom.get('dhcp_pools'):
                for pool_name, pool in self.device.custom['dhcp_pools'].items():
                    self.execute(f'ip dhcp pool {pool_name}', prompt=[r'\(dhcp-config\)#'])
                    network_ip = ipaddress.IPv4Network(pool['network'])
                    self.execute(f'network {network_ip.network_address.compressed} {network_ip.netmask.exploded}',
                                 prompt=[r'\(dhcp-config\)#'])
                    self.execute(f'default-router {pool['default_router']}', prompt=[r'\(dhcp-config\)#'])
                    if (pool.get('domain_name')):
                        self.execute(f'domain-name {pool['domain_name']}', prompt=[r'\(dhcp-config\)#'])
                    if (pool.get('dns_server')):
                        self.execute(f'dns-server {pool['dns_server']}', prompt=[r'\(dhcp-config\)#'])
                    self.execute('exit', prompt=[r'\(config\)#'])
                    if pool.get('excluded_address_ranges'):
                        for r in pool['excluded_address_ranges']:
                            start, end = r['start'], r['end']
                            self.execute(f'ip dhcp excluded-address {start} {end}', prompt=[r'\(config\)#'])

            # save
            self.execute('end', prompt=[r'\w+#'])
            out = self.execute('write', prompt=[], timeout=5)
            if 'Continue? [no]:' in out or '[confirm]' in out:
                self.execute('yes', prompt=[r'\w+#'])
            self.execute('', prompt=[r'\w+#'])

    def read(self) -> str:
        if self._shell.recv_ready():
            return self._shell.recv(999999999)
        return ''

    # modificat aici
    def test_pings(self, topology_addresses: list[str]):
        pattern = r'Success rate is (\d{1,3}) percent'
        self.execute('\r', prompt=[r'\w+#'])
        for addr in topology_addresses:
            out = self.execute(f'ping {addr}', prompt=[])
            matched_regex = False
            percentage = 0
            for _ in range(8):
                time.sleep(1)
                if _ == 0:
                    out = out + self.read()
                else:
                    out = self.read()
                match = re.search(pattern, out)
                if not match:
                    continue
                else:
                    matched_regex = True
                    percentage = int(match.group(1))
                    break
            if not matched_regex:
                raise Exception('Regex was not matched at ping')
            if percentage == 0:
               return False, addr
            else:
                logger.warning(f'Ping from {self.device} to {addr} succeeded\n')
        return True, None


    def get_device_details(self, *args, **kwargs):
        out = ''
        if self.device.os in ['ubuntu']:
            out = self.execute('ip addr show', prompt=[r'.*'])
        elif self.device.os in ['ios', 'iosxe']:
            out = self.execute('show version', prompt=[r'System image file is'])
        logger.warning(out)

    def do_initial_configuration(self):
        pass

    def is_connected(self):
        try:
            self._client.exec_command('\n', timeout=5)
            return True
        except:
            return False

    def execute(self, command, **kwargs) -> str:
        """
        If length of prompt is 0, does not check for pattern
        """
        prompt: list[bytes] = list(map(lambda s: s.encode(), kwargs['prompt']))
        self._shell.send(f'{command}\n')
        time.sleep(.5)
        if kwargs.get('timeout'):
            time.sleep(kwargs['timeout'])
        out = self._shell.recv(999999999)

        exists_match = any(re.search(p, out) != None for p in prompt)
        if exists_match or len(prompt) == 0:
            return out.decode()
        raise Exception(f"Prompts: {prompt} were not matched in {out.decode()}")

    def disconnect(self):
        self._client.close()