import subprocess
import re
import ipaddress

class SystemUtils:

    @staticmethod
    def get_ipv4_interfaces():
        result = subprocess.run(['ip', '-4', 'addr'], capture_output=True, text=True)
        interfaces = []
        current_int= None

        for line in result.stdout.split('\n'):
            if line.startswith(' '):
                match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)/(\d+)', line)
                if match and current_int:
                    ip, subnet = match.groups()
                    interfaces.append({'interface': current_int, 'ip': ip, 'subnet': subnet})

            else:
                match = re.search(r'(\d+): ([^:]+):', line)
                if match:
                    current_int = match.group(2)

        return interfaces

    @staticmethod
    def get_ipv6_interfaces():
        """Returns a list of dictionaries containing IPv6 interfaces details"""
        result = subprocess.run(['ip', '-6', 'addr'], capture_output=True, text=True)
        interfaces = []
        current_iface = None

        for line in result.stdout.split('\n'):
            if line.startswith(' '):
                match = re.search(r'inet6 ([a-fA-F0-9:]+)/([0-9]+)', line)
                if match and current_iface:
                    ip, subnet = match.groups()
                    interfaces.append({'interface': current_iface,'ip': ipaddress.ip_address(ip),'subnet': subnet})
            else:
                match = re.search(r'(\d+): ([^:]+):', line)
                if match:
                    current_iface = match.group(2)

        return interfaces

    @staticmethod
    def get_ipv4_routes():
        """Returns a list of dictionaries containing IPv4 routing information"""
        result = subprocess.run(['ip', '-4', 'route'], capture_output=True, text=True)
        routes = []

        for line in result.stdout.split('\n'):
            parts = line.split()
            if parts:
                route = {'destination': parts[0],'gateway': parts[2] if 'via' in parts else None,'interface': parts[-1]}
                routes.append(route)

        return routes

    @staticmethod
    def get_ipv6_routes():
        """Returns a list of dictionaries containing IPv6 routing information"""
        result = subprocess.run(['ip', '-6', 'route'], capture_output=True, text=True)
        routes = []

        for line in result.stdout.split('\n'):
            parts = line.split()
            if parts:
                route = {'destination': parts[0],'gateway': parts[2] if 'via' in parts else None,'interface': parts[-1]}
                routes.append(route)

        return routes

    @staticmethod
    def get_listening_ports():
        """Retrieves all open (listening) ports without using tabulate"""
        result = subprocess.run(['netstat', '-ln'], capture_output=True, text=True)
        lines = result.stdout.split('\n')[2:]  # Skip the first two header lines

        table = []
        for line in lines:
            parts = re.split(r'\s+', line.strip())  # Splitting line into parts based on spaces
            if len(parts) >= 4:
                proto, local_address, foreign_address, state = parts[:4]
                if state == 'LISTEN':
                    table.append([proto, local_address, foreign_address])

        # Print table manually instead of using tabulate
        print("\nListening Ports:")
        print(f"{'Proto':<10} {'Local Address':<30} {'Foreign Address':<30}")
        print("-" * 70)
        for row in table:
            print(f"{row[0]:<10} {row[1]:<30} {row[2]:<30}")

        return table


if __name__ == "__main__":
    utils = SystemUtils()

    print("\nIPv4 Interfaces:")
    for iface in utils.get_ipv4_interfaces():
        print(f"Interface: {iface['interface']}, IP: {iface['ip']}, Subnet: {iface['subnet']}")

    print("\nIPv6 Interfaces:")
    for iface in utils.get_ipv6_interfaces():
        print(f"Interface: {iface['interface']}, IP: {iface['ip']}, Subnet: {iface['subnet']}")

    print("\nIPv4 Routes:")
    for route in utils.get_ipv4_routes():
        print(f"Destination: {route['destination']}, Gateway: {route['gateway']}, Interface: {route['interface']}")

    print("\nIPv6 Routes:")
    for route in utils.get_ipv6_routes():
        print(f"Destination: {route['destination']}, Gateway: {route['gateway']}, Interface: {route['interface']}")

    utils.get_listening_ports()