from ipaddress import ip_address, ip_interface
from tabulate import tabulate
import re
from subprocess import Popen, PIPE
class SystemUtils():
    def run_command(self, command):
        command = command.split(' ')
        res = Popen(command, stdout=PIPE,stderr=PIPE)
        res = res.communicate()[0].decode('utf-8')
        return res
    def get_ipv4_interfaces(self):
        res = []
        command_res = self.run_command('ifconfig')
        pattern = r'(?s)([^:\n]+):(?:[^i]+?inet (\d+.\d+.\d+.\d+)  netmask (\d+.\d+.\d+.\d+))?(?:[^\n]+)?(?:[^e]+?ether ([^\s]+)?)?.*?(\n\n|$)'
        matches = re.findall(pattern, command_res)
        for match in matches:
            int_name = match[0]
            ipv4 = match[1]
            subnet_mask = match[2]
            mac = match[3]
            d = {'name': int_name}
            if ipv4:
                d['ipv4'] = ip_address(ipv4)
            if subnet_mask:
                d['subnet_mask'] = subnet_mask
            if mac:
                d['mac'] = mac
            res.append(d)
        return res
    def get_ipv4_routes(self):
        res = []
        command_res = self.run_command("route")
        pattern = r'([^\s]+?)\s+([^\s]+?)\s+([^\s]+?)\s+(?:[^\s]+?)\s+(?:[^\s]+?)\s+(?:[^\s]+?)\s+(?:[^\s]+?)\s+([^\s\n$]+)'
        for idx,line in enumerate(command_res.splitlines()):
            if idx < 4:
                continue
            match = re.match(pattern, line)
            if match:
                ro = {
                    'address': ip_address(match.group(1)),
                    'dest': match.group(1)+'/'+match.group(3),
                    'gateway': match.group(2),
                    'interface':match.group(4)
                }
                res.append(ro)
        return res
    def get_ipv6_interfaces(self):
        res = []
        command_res = self.run_command('ifconfig')
        iname_pattern = r'([^:\n]+): '
        mac_pattern = r'[^e]*ether ([^\s]+)'
        ipv6_pattern = r'[^i]*inet6 ([^\s]+)  prefixlen (\d+)'
        last_interf = None
        for line in command_res.split('\n'):
            # print(line)
            match = re.match(iname_pattern, line)
            if match:
                if last_interf != None:
                    res.append(last_interf)
                last_interf = {'name': match.group(1)}
                continue
            match = re.match(ipv6_pattern, line)
            if match:
                last_interf['address'] = ip_interface(match.group(1)+'/'+match.group(2))
                last_interf['ipv6'] = last_interf['address'].ip
                last_interf['subnet_mask'] = last_interf['address'].netmask
                continue
            match = re.match(mac_pattern, line)
            if match:
                last_interf['mac'] = match.group(1)
        res.append(last_interf)
        return res
    def get_ipv6_routes(self):
        res = []
        command_res = self.run_command('netstat -nr -6')
        pattern = r'([^\s]+?)\s+([^\s]+?)\s+(?:[^\s]+?)\s+(?:[^\s]+?)\s+(?:[^\s]+?)\s+(?:[^\s]+?)\s+([^\s]+)'
        for idx, line in enumerate(command_res.splitlines()):
            if idx < 2:
                continue
            match = re.match(pattern, line)
            if match:
                ro = {
                    'dest': ip_interface(match.group(1)),
                    'gateway': match.group(2),
                    'interface': match.group(3)
                }
                res.append(ro)
        return res
    def get_listening_ports(self):
        res = []
        command_res = self.run_command('netstat -ln')
        pattern = r'([^\s]+?)\s+([^\s]+?)\s+([^\s]+?) ([^\s]+?)\s+([^\s]+?)\s+?([^\s]+)?\s+(?:\n|$)'
        for idx,line in enumerate(command_res.splitlines()):
            if idx < 2:
                continue
            if line == 'Active UNIX domain sockets (only servers)':
                break
            match = re.match(pattern, line)
            if match:
                d = {
                    'Proto': match.group(1),
                    'Recv-Q': match.group(2),
                    'Send-Q':match.group(3),
                    'Local Address': match.group(4),
                    'Foreign Address': match.group(5),
                }
                if match.group(6):
                    d['State'] = match.group(6)
            res.append(d)
        return res

def pretty_print(arr,headers,*args):
    t = []
    for dictio in arr:
        line = [dictio.get(prop,'') for prop in args]
        t.append(line)
    print(tabulate(t,headers=headers))

s = SystemUtils()

# pretty_print(s.get_ipv4_interfaces(), ['Interface Name', 'IPv4', 'Subnet Mask', 'MAC'], 'name','ipv4','subnet_mask','mac')
# pretty_print(s.get_ipv6_interfaces(), ['Interface Name', 'IPv6', 'Subnet Mask', 'MAC'], 'name','ipv6','subnet_mask','mac')
# pretty_print(s.get_ipv4_routes(),['Destination', 'Gateway', 'Interface'],'dest','gateway','interface')
# pretty_print(s.get_ipv6_routes(),['Destination', 'Gateway', 'Interface'],'dest','gateway','interface')
# pretty_print(s.get_listening_ports(), ['Proto','Recv-Q','Send-Q','Local Address', 'Foreign Address','State'],'Proto','Recv-Q','Send-Q','Local Address','Foreign Address', 'State')

