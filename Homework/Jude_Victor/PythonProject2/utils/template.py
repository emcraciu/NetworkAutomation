# config/ubuntu_config.py

import logging
from ipaddress import ip_interface, IPv4Interface
from subprocess import Popen, PIPE
from typing import Optional, Tuple, Dict

from pyats import aetest


class UbuntuServerConfig(aetest.Testcase):
    """
    Aetest Testcase to configure Ubuntu interfaces and routes
    based on the testbed topology. It assigns IPs and adds static routes
    to peer router devices (like IOU1) if present.
    """

    testbed = None
    device = None
    password: Optional[str] = None
    topology: Optional[dict] = None

    @aetest.setup
    def setup(self) -> None:
        """
        Retrieves testbed, device, and password from parent parameters.
        Also loads topology if defined under testbed.custom.
        """
        self.testbed = self.parent.parameters['testbed']
        device_name = self.parent.parameters['device_name']
        self.device = self.testbed.devices[device_name]
        self.password = self.device.credentials.get('default', {}).get('password')

        self.topology = getattr(self.testbed, 'topology', self.testbed.custom.get('topology', {}))

    def get_interfaces(self) -> Tuple[dict, dict]:
        """
        Extracts the interface configuration and topology for the device.

        Returns:
            Tuple containing interface config for this device and full topology.
        """
        device_topology = self.topology.get(self.device.name, {})
        interfaces = device_topology.get('interfaces', {})
        return interfaces, self.topology

    def find_router_ip(self, ubuntu_ip_interface: IPv4Interface, topology: dict) -> Optional[str]:
        """
        Identifies the router IP in the same subnet as the Ubuntu interface.

        Args:
            ubuntu_ip_interface: IP address object from Ubuntu device
            topology: Full testbed topology

        Returns:
            IP of the peer router in the same network, if found.
        """
        for other_device_name, other_device_data in topology.items():
            if other_device_name == self.device.name or other_device_name != "IOU1":
                continue

            interfaces = other_device_data.get('interfaces', {})
            for peer_iface_data in interfaces.values():
                peer_ip = peer_iface_data.get('ipv4')
                if not peer_ip:
                    continue
                try:
                    peer_ip_interface = ip_interface(peer_ip)
                    if ubuntu_ip_interface.network == peer_ip_interface.network and \
                       ubuntu_ip_interface.ip != peer_ip_interface.ip:
                        return str(peer_ip_interface.ip)
                except ValueError:
                    continue
        return None

    @aetest.test
    def configure(self) -> None:
        """
        Main configuration logic that sets IP addresses and adds static routes
        on UbuntuServer based on the testbed topology.
        """
        interfaces, topology = self.get_interfaces()

        for iface_name, iface_data in interfaces.items():
            ipv4 = iface_data.get('ipv4')
            if not ipv4:
                continue

            ubuntu_ip_interface = ip_interface(ipv4)
            router_ip = self.find_router_ip(ubuntu_ip_interface, topology)

            if not router_ip:
                continue

            commands: Dict[str, list[str]] = {
                "set_ip": f"sudo ip address add {ubuntu_ip_interface.ip}/{ubuntu_ip_interface.network.prefixlen} dev {iface_name}".split(),
                "remove_ip": f"sudo ip address del {ubuntu_ip_interface.ip}/{ubuntu_ip_interface.network.prefixlen} dev {iface_name}".split(),
                "remove_route": f"sudo ip route del {str(ubuntu_ip_interface.network)}".split(),
                "add_route": f"sudo ip route add {str(ubuntu_ip_interface.network)} via {router_ip}".split(),
                "interface_up": f"sudo ip link set dev {iface_name} up".split()
            }

            for name in ['interface_up', 'remove_ip', 'set_ip', 'remove_route', 'add_route']:
                cmd = commands.get(name)
                if not cmd:
                    self.failed(f"Missing command: {name}")
                    continue

                if cmd[0] == 'sudo':
                    cmd = ['sudo', '-S'] + cmd[1:]

                self.log.info(f"Running: {' '.join(cmd)}")
                try:
                    proc = Popen(cmd, stdout=PIPE, stderr=PIPE, text=True)
                    stdout, stderr = proc.communicate(input=self.password + '\n')

                    if proc.returncode != 0:
                        self.failed(f"Command {name} failed:\n{stderr}")
                    else:
                        self.log.info(f"{name} succeeded:\n{stdout}")
                except Exception as e:
                    logging.error(f"Failed to run command {name}: {e}")
