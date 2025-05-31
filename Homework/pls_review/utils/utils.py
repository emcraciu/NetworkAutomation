import re
import ipaddress

"""
    Given an ipaddress.IPv4Interface object, return a tuple of:
    - IP as string
    - Subnet mask as string

    Example:
        IPv4Interface('192.168.1.1/24') → ('192.168.1.1', '255.255.255.0')
    """

def parse_ip_and_mask(interface: ipaddress.IPv4Interface) -> tuple[str, str]:
    ip = str(interface.ip)
    mask = str(interface.network.netmask)
    return ip, mask


def infer_next_hop_from_testbed(device, interface_name: str) -> str:
    interface_obj = device.device.interfaces[interface_name]
    link = interface_obj.link

    if not link:
        raise ValueError(f"No link found for interface {interface_name}")

    # Find the peer interface
    peer_intf = next(
        (intf for intf in link.interfaces if intf.device.name != device.name),
        None
    )
    if not peer_intf:
        raise ValueError(f"No peer interface found for {interface_name}")

    # Extract the peer's IP address from testbed definition
    ip = peer_intf.ipv4
    if not ip:
        raise ValueError(f"No IPv4 address found for peer {peer_intf.device.name}:{peer_intf.name}")

    return ip.split('/')[0]  # Remove CIDR mask


def get_interfaces_without_ip(device):
    output = device.execute("show ip interface brief")
    interfaces_missing_ip = []

    for line in output.splitlines():
        match = re.match(r'(\S+)\s+(\S+)\s+\S+\s+\S+\s+(up|down|administratively down)\s+(up|down)', line)
        if match:
            intf, ip, status, protocol = match.groups()

            if ip.lower() == 'unassigned' and status == 'up' and protocol == 'up':
                interfaces_missing_ip.append(intf)

    return interfaces_missing_ip