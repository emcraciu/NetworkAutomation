import ipaddress
import subprocess
import re

class SystemUtils:

    def get_ipv4_interfaces(self):

        result = subprocess.Popen(['ifconfig'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = result.communicate()
        pattern = r'(?m)^(\S+):.*?\n\s+inet\s+(\d+\.\d+\.\d+\.\d+)\s+netmask\s+(\d+\.\d+\.\d+\.\d+)(?:.*\n)*?\s+ether\s+([0-9a-fA-F:]{17})'
        output = output.decode("utf-8")
        found = re.findall(pattern, output)

        interfaces = []
        for matches in found:
            interfaces_dict = {
                "interface": matches[0],
                "ip_address": ipaddress.ip_address(matches[1]),
                "netmask": ipaddress.ip_network(matches[2]),
                "mac": matches[3],
            }
            interfaces.append(interfaces_dict)
        print(interfaces)

    def get_ipv4_routes(self):
        #destination, gateway, interface
        result = subprocess.Popen(['ip', 'route'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = result.communicate()
        pattern = r'(\S+)(?:\s+via\s+(\S+))?\s+dev\s+(\S+)'

        matches = re.findall(pattern, output.decode("utf-8"))
        print(matches)
        routes = []
        for dest, gateway, iface in matches:
            if any(char.isdigit() for char in dest):
                try:
                    dest = ipaddress.ip_network(dest, strict=False)
                except ValueError:
                    pass

            if gateway and any(char.isdigit() for char in gateway):
                try:
                    gateway = ipaddress.ip_address(gateway)
                except ValueError:
                    pass

            routes.append({
                "destination": dest,
                "gateway": gateway,
                "interface": iface
            })

        print(routes)

    def get_ipv6_interfaces(self):

        result = subprocess.Popen(['ifconfig'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = result.communicate()
        pattern = r'(?m)^(\S+):(?:.*\n)*?\s+inet6\s+([0-9a-fA-F:]+)\s+prefixlen\s+(\d+)(?:.*\n)*?\s+ether\s+([0-9a-fA-F:]{2}(?::[0-9a-fA-F]{2}){5})'
        output = output.decode("utf-8")
        found = re.findall(pattern, output)

        interfaces = []
        for matches in found:
            interfaces_dict = {
                "interface": matches[0],
                "ip_address": ipaddress.IPv6Address(matches[1]),
                "netmask": ipaddress.IPv6Network(f"{matches[1]}/{matches[2]}", strict=False),
                "mac": matches[3],
            }
            interfaces.append(interfaces_dict)
        print(interfaces)


    def get_ipv6_routes(self):
        result = subprocess.Popen(['ip', '-6', 'route'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = result.communicate()
        pattern = r'^(\S+)(?:\s+via\s+(\S+))?\s+dev\s+(\S+)'

        matches = re.findall(pattern, output.decode("utf-8"))
        print(matches)
        routes = []
        for dest, gateway, iface in matches:
            if dest == "default":
                destination = "default"
            else:
                try:
                    destination = ipaddress.IPv6Network(dest, strict=False)
                except ValueError:
                    pass

            gateway_obj = None
            if gateway:
                try:
                    gateway_obj = ipaddress.IPv6Address(gateway)
                except ValueError:
                    pass

            routes.append({
                "destination": destination,
                "gateway": gateway_obj,
                "interface": iface
            })


        print(routes)

    def get_listening_ports(self):
        result = subprocess.run(['netstat', '-ln'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')

        headers = ["Proto", "Recv-Q", "Send-Q", "Local Address", "Foreign Address", "State"]
        rows = []

        for line in lines[2:]:
            parts = line.split()
            if len(parts) == 6:
                proto, recv_q, send_q, local, foreign, state = parts
            elif len(parts) == 5:
                proto, recv_q, send_q, local, foreign = parts
                state = ""
            else:
                continue

            rows.append([proto, recv_q, send_q, local, foreign, state])


        #print part
        col_widths = [len(header) for header in headers]
        for row in rows:
            for i, val in enumerate(row):
                col_widths[i] = max(col_widths[i], len(val))

        row_format = "  ".join(f"{{:<{w}}}" for w in col_widths)
        print(row_format.format(*headers))
        print("-" * (sum(col_widths) + 2 * (len(headers) - 1)))
        for row in rows:
            print(row_format.format(*row))


cv = SystemUtils()
cv.get_listening_ports()