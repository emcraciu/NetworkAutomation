import ipaddress
from core.renderer import render_template
from utils.utils import parse_ip_and_mask
from utils.logger import setup_logger

logger = setup_logger("renderables")


class InterfaceConfig:
    def __init__(self, interface_obj, shutdown=False):
        """
        :param interface_obj: A pyATS Interface object (e.g., device.interfaces["Gig0/0"])
        """
        self.interface_obj = interface_obj
        self.shutdown = shutdown
        if not interface_obj.ipv4:
            logger.error(f"Interface {self.interface_obj.name} has no IPv4 address in testbed.")
            raise ValueError(f"Interface {self.interface_obj.name} has no IPv4 address in testbed.")

        self.ip_interface = ipaddress.IPv4Interface(interface_obj.ipv4)
        self.ip, self.mask = parse_ip_and_mask(self.ip_interface)
        self.network = self.ip_interface.network


    def get_peer_ip(self) -> str:
        link = self.interface_obj.link
        if not link:
            raise ValueError(f"No link found for interface {self.interface_obj.name}")
        # Get the peer interface object
        peer_intf = next((intf for intf in link.interfaces if intf is not self.interface_obj), None)
        if not peer_intf or not peer_intf.ipv4:
            raise ValueError(f"No valid peer IP found for {self.interface_obj.name}")

        logger.debug(f"{peer_intf}")

        return peer_intf.ipv4.split("/")[0]


    def render(self):
        return render_template("interface_config", {
            "interface": self.name,
            "ip": self.ip,
            "mask": self.mask,
            "shutdown": self.shutdown
        })


class StaticRoute:
    def __init__(self, interface_config: InterfaceConfig):
        self.destination = str(interface_config.network.network_address)
        self.mask = str(interface_config.network.netmask)
        self.next_hop = interface_config.get_peer_ip()

    def render(self):
        return render_template("static_route", {
            "network": self.destination,
            "mask": self.mask,
            "next_hop": self.next_hop
        })

class SSHConfig:
    pass