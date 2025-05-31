import re

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