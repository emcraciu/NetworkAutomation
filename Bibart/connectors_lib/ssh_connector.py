"""
Manages SSH connection
"""
import ipaddress
import time
import logging
import re
from typing import Tuple

from paramiko import SSHClient
from paramiko.client import AutoAddPolicy
from pyats.topology import Device

from Bibart.ping_helper import test_pings as ping_helper_test_pings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SSHConnector:
    """
    Manages SSH connection
    """
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
        """
        Connects to device
        Args:
            kwargs:
                connection(pyats.Connection): testbed connection object used
        """
        conn_details = kwargs['connection']
        self.username = conn_details.credentials.login.username
        self.password = conn_details.credentials.login.password.plaintext
        self.hostname = conn_details.ip.compressed
        self.port =  conn_details.port if conn_details.port else 22
        self._client.connect(hostname=self.hostname, port=self.port, username=self.username, password=self.password)
        self._shell = self._client.invoke_shell()

    def enable_rest(self):
        """
        Enables REST server on the device
        """
        self.execute('en', prompt=[r'\w+#', r'\(config\)#'])
        self.execute('conf t', prompt=[r'\(config\)#'])
        self.execute('ip http secure-server ', prompt=[r'\(config\)#'])
        self.execute('restconf', prompt=[r'\(config\)#'])

    def move_to_global_conf(self):
        """
        Expects device to be in user exec or privileged exec.
        Moves to global configuration mode.
        """
        self.execute('en', prompt=[r'\w+#', r'\(config\)#'])
        self.execute('conf t', prompt=[r'\(config\)#'])
        hostname = self.device.custom.hostname
        self.execute(f'hostname {hostname}', prompt=[rf'{hostname}\(config\)#'])

    def configure_interfaces(self):
        """
        Expects device to be in global configuration.
        Adds ipv4 addresses to interfaces statically or via dhcp based on testbed values.
        """
        for _, interface in self.device.interfaces.items():
            self.execute(f'interface {interface.name}', prompt=[r'\(config-if\)#'])

            if interface.ipv4:
                ip = interface.ipv4.ip.compressed
                mask = interface.ipv4.network.netmask.exploded
                self.execute(f'ip add {ip} {mask}', prompt=[r'\(config-if\)#'])
            else:
                self.execute('ip add dhcp', prompt=[r'\(config-if\)#'])
            self.execute('no sh', prompt=[r'\(config-if\)#'])
            self.execute('exit', prompt=[r'\(config\)#'])

    def configure_routes(self):
        """
        Configures static routes based on testbed values.
        """
        if self.device.custom.get('routes'):
            for _, route in self.device.custom['routes'].items():
                to_ip = ipaddress.IPv4Network(route['to_ip'])
                self.execute(f'ip route {to_ip.network_address} {to_ip.netmask.exploded} {route['via']}',
                             prompt=[r'\(config\)#'])

    def configure_rip(self):
        """
        Configures RIP routing based on testbed values.
        """
        if self.device.type == 'router' and self.device.custom.get('rip'):
            rip_dict = self.device.custom['rip']
            self.execute('router rip', prompt=[r'\(config-router\)#'])
            self.execute('version 2', prompt=[r'\(config-router\)#'])
            self.execute('no auto-summary', prompt=[r'\(config-router\)#'])
            networks = [ipaddress.IPv4Network(str_addr) for str_addr in  rip_dict.get('networks')]
            for network in networks:
                self.execute(f'network {network.network_address}', prompt=[r'\(config-router\)#'])
            if rip_dict.get('passive-interfaces'):
                for passive_interface in rip_dict.get('passive-interfaces'):
                    self.execute(f'passive-interface {passive_interface}', prompt=[r'\(config-router\)#'])
            self.execute('exit', prompt=[r'\(config\)#'])

    def configure_ospf(self):
        """
        Configures OSPF routing based on testbed values.
        """
        if self.device.type == 'router' and self.device.custom.get('ospf'):
            ospf_dict = self.device.custom['ospf']
            ospf_process_id = ospf_dict.get('process_id')
            self.execute(f"router ospf {ospf_process_id}", prompt=[r'\(config-router\)#'])
            for network in ospf_dict.get('networks').values():
                self.execute(f'network {network['address']} {network['wildcard']} area {network['area']}',
                             prompt=[r'\(config-router\)#'])
            if ospf_dict.get('passive-interfaces'):
                for passive_interface in ospf_dict.get('passive-interfaces'):
                    self.execute(f'passive-interface {passive_interface}', prompt=[r'\(config-router\)#'])
            self.execute('exit', prompt=[r'\(config\)#'])

    def configure_dhcp_pools(self):
        """
        Configures DHCP pools based on testbed values.
        """
        if self.device.custom.get('dhcp_pools'):
            for pool_name, pool in self.device.custom['dhcp_pools'].items():
                self.execute(f'ip dhcp pool {pool_name}', prompt=[r'\(dhcp-config\)#'])
                network_ip = ipaddress.IPv4Network(pool['network'])
                self.execute(f'network {network_ip.network_address.compressed} {network_ip.netmask.exploded}',
                             prompt=[r'\(dhcp-config\)#'])
                self.execute(f'default-router {pool['default_router']}', prompt=[r'\(dhcp-config\)#'])
                if pool.get('domain_name'):
                    self.execute(f'domain-name {pool['domain_name']}', prompt=[r'\(dhcp-config\)#'])
                if pool.get('dns_server'):
                    self.execute(f'dns-server {pool['dns_server']}', prompt=[r'\(dhcp-config\)#'])
                self.execute('exit', prompt=[r'\(config\)#'])
                if pool.get('excluded_address_ranges'):
                    for r in pool['excluded_address_ranges']:
                        start, end = r['start'], r['end']
                        self.execute(f'ip dhcp excluded-address {start} {end}', prompt=[r'\(config\)#'])

    def save_config(self):
        """
        Writes to startup configuration file.
        """
        self.execute('end', prompt=[r'\w+#'])
        out = self.execute('write', prompt=[], timeout=5)
        if 'Continue? [no]:' in out or '[confirm]' in out:
            self.execute('yes', prompt=[r'\w+#'])
        self.execute('', prompt=[r'\w+#'])

    def config(self):
        """
        Initiates the specific configuration based on device type
        """
        if self.device.os in ('ios','iosxe'):
            self.execute('\r', prompt=[])
            self.move_to_global_conf()
            self.configure_interfaces()
            self.configure_routes()
            self.configure_rip()
            self.configure_ospf()
            self.configure_dhcp_pools()
            # REST enable
            if self.device.name == 'CSR':
                self.enable_rest()
            self.save_config()

    def read(self) -> str:
        """
        Reads values from connection.
        Returns the output.
        """
        if self._shell.recv_ready():
            return str(self._shell.recv(999999999))
        return ''

    def test_pings(self, topology_addresses: list[str]) -> Tuple[bool, dict[str, bool]]:
        """
        Performs pings to all addresses in topology_addresses.(All interface ips in the testbed)
        Returns:
            (result: bool, dict):
                result: True if all pings succeeded, False otherwise
                dict: Target ip, Result of ping to said Ip
        """
        return ping_helper_test_pings(
            topology_addresses,
            execute=self.execute,
            read=self.read,
            device_name=self.device.name,
            os=self.device.os,
        )

    def is_connected(self)-> bool:
        """
        Returns connection status.
        """
        return self._shell.closed is False

    def execute(self, command, **kwargs) -> str:
        """
        Executes the command, then waits until the output matches at least one
        regex pattern from a list.
        If length of prompt is 0, does not check for pattern.
        Returns
            The output of the command until the matched part(inclusive)
        Args:
            kwargs
                prompt(List[str]): the list of regex patterns to try match
                timeout(int): Amount of time in seconds to wait after issuing the command.
                The output is read after the timeout. (0 by default)
        """
        prompt: list[bytes] = list(map(lambda s: s.encode(), kwargs['prompt']))
        self._shell.send(f'{command}\n')
        time.sleep(.5)
        if kwargs.get('timeout'):
            time.sleep(kwargs['timeout'])
        out = self._shell.recv(999999999)

        exists_match = any(re.search(p, out) is not None for p in prompt)
        if exists_match or len(prompt) == 0:
            return out.decode()
        raise RuntimeError(f"Prompts: {prompt} were not matched in {out.decode()}")

    def disconnect(self):
        """
        Terminates the connection.
        """
        self._client.close()
