import os
import subprocess
import ipaddress
import pprint
class SystemUtils:
    @staticmethod
    def get_ipv4_interfaces():
        List = []
        interfaceName = ''
        output = subprocess.run(['ifconfig', '-a'], capture_output=True, text=True)
        for line in output.stdout.splitlines():
            try:
                if line[0] != " ":
                    interfaceName = line.split(":")[0]
                    List.append({"Name": line.split(":")[0]})

                if line[8:13] == "inet ":
                    line = line[8:]
                    line = line.replace("  ", " ")
                    line = line.split(" ")
                    for dict in List:
                        if dict["Name"] == interfaceName:
                            dict["IP"] = ipaddress.ip_address(line[1])
                            # Convert the subnet mask to an ipaddress object if possible
                            dict["Subnet"] = ipaddress.ip_address(line[3])
                if line[8:13] == "ether":
                    line = line[8:]
                    line = line.replace("  ", " ")
                    line = line.split(" ")
                    for dict in List:
                        if dict["Name"] == interfaceName:
                            dict["MAC"] = line[1]
            except:
                pass
        return List

    @staticmethod
    def get_ipv4_routes():
        List = []
        output = subprocess.run(['route'], capture_output=True, text=True)
        i = 0

        for line in output.stdout.splitlines():
            i = i + 1
            line = line.split(" ")
            for element in line:
                while '' in line:
                    line.remove('')
            if i > 2:
                try:
                    destination = ipaddress.ip_address(line[0])
                except ValueError:
                    destination = line[0]
                try:
                    gateway = ipaddress.ip_address(line[1])
                except ValueError:
                    gateway = line[1]
                List.append({"Destination": destination, "Gateway": gateway, "Iface": line[7]})
        return List

    @staticmethod
    def get_ipv6_interfaces():
        List = []
        interfaceName = ''
        output = subprocess.run(['ifconfig', '-a'], capture_output=True, text=True)
        for line in output.stdout.splitlines():
            try:
                if line[0] != " ":
                    interfaceName = line.split(":")[0]
                    List.append({"Name": line.split(":")[0]})

                if line[8:14] == "inet6 ":
                    line = line[8:]
                    line = line.replace("  ", " ")
                    line = line.split(" ")
                    for dict in List:
                        if dict["Name"] == interfaceName:
                            dict["IPv6"] = ipaddress.ip_address(line[1])
                            dict["Subnet"] = ipaddress.ip_address(line[3])
                if line[8:13] == "ether":
                    line = line[8:]
                    line = line.replace("  ", " ")
                    line = line.split(" ")
                    for dict in List:
                        if dict["Name"] == interfaceName:
                            dict["MAC"] = line[1]
            except:
                pass
        return List

    @staticmethod
    def get_ipv6_routes():
        List = []
        output = subprocess.run(['route', '-6'], capture_output=True, text=True)
        i = 0

        for line in output.stdout.splitlines():
            i = i + 1
            line = line.split(" ")
            for element in line:
                while '' in line:
                    line.remove('')
            if i > 2:
                try:
                    destination = ipaddress.ip_network(line[0])
                except ValueError:
                    destination = line[0]
                try:
                    next_hop = ipaddress.ip_address(line[1])
                except ValueError:
                    next_hop = line[1]
                List.append({"Destination": destination, "Next Hop": next_hop, "Iface": line[6]})
        return List

    @staticmethod
    def get_listening_ports():
        List = []
        output = subprocess.run(['netstat', '-ln'], capture_output=True, text=True)
        lines = output.stdout.splitlines()

        # The first line is assumed to be the header; use it to get column keys.
        header = lines[0].split()

        # Process every line after the header
        for line in lines[1:]:
            if not line.strip():
                continue  # skip empty lines
            parts = line.split()
            row = {}
            # Map each header key to its corresponding part.
            for i, key in enumerate(header):
                row[key] = parts[i] if i < len(parts) else ""
            # Attempt ipaddress conversion for each value in the row where possible
            for key, value in row.items():
                try:
                    row[key] = ipaddress.ip_address(value)
                except ValueError:
                    pass
            List.append(row)
        return List


interfaces = SystemUtils.get_ipv4_interfaces()
for interface in interfaces:
    pprint.pprint(interface)

interfaces = SystemUtils.get_ipv4_routes()
for route in interfaces:
    pprint.pprint(route)