from modul3.part2.telnet_context import TelnetContext
from subprocess import PIPE, Popen
from ipaddress import ip_address

from modul4.part1.async_module import sleep


def set_ubuntu_config():
    subnet_mask = '24'
    network_address = ip_address('192.168.11.0')
    pc_address = ip_address('192.168.11.254')
    router_address = ip_address('192.168.11.1')

    set_ip_command = f'sudo ip address add {pc_address}/{subnet_mask} dev ens4'.split(' ')
    remove_ip_command = f'sudo ip remove address {pc_address}/{subnet_mask} dev ens4'.split(' ')
    add_route_command = f'ip route add {network_address}/{subnet_mask} via {router_address}'.split(' ')
    set_int_on_command = 'ip link set dev ens4 up'.split(' ')
    set_ip_route = f'ip route add 192.168.102.0/24 via 192.168.11.1'.split(' ')  ##for CSR
    set_ip_route = f'ip route add 192.168.101.0/24 via 192.168.11.1'.split(' ')  ##for U-Doker

    set_ip = Popen(set_ip_command, stdout=PIPE, stderr=PIPE)
    print(set_ip.communicate())

    set_interf_on = Popen(set_int_on_command, stdout=PIPE, stderr=PIPE)
    print(set_interf_on.communicate())

    set_route = Popen(set_int_on_command, stdout=PIPE, stderr=PIPE)
    print(set_route.communicate())

    set_ip_route_response = Popen(set_ip_route, stdout=PIPE, stderr=PIPE)
    print(set_ip_route_response.communicate())

def set_ip_address(ipAddress,interfaceName,dhcp):
    remote_address = ('192.168.0.100')
    port = 5007
    addIpCommand = "ip add " + ipAddress + " 255.255.255.0"
    interfaceCommand = "int " + interfaceName
    with TelnetContext(remote_address, port, b"IOU1") as te:
        te.write(b'conf t')
        te.write(interfaceCommand.encode())
        te.expect([b"\(config-if\)#"])
        te.write(addIpCommand.encode())
        te.expect([b"\(config-if\)#"])
        te.write(b"no sh")
        te.expect([b"\(config-if\)#"])
        te.write(b"line vty 0 4")
        te.expect([b"\(config-line\)#"])
        te.write(b"transport input telnet")
        te.expect([b"\(config-line\)#"])
        te.write(b"password password")
        te.expect([b"\(config-line\)#"])
        te.write(b"privilege level 15")
        te.expect([b"\(config-line\)#"])
        te.write(b"exit")
        te.expect([b"\(config\)#"])
        # add dhcp
        if dhcp:
            te.write(interfaceCommand.encode())
            te.expect([b"\(config-if\)#"])
            dhcpNameCommand = "ip dhcp pool "+dhcp['name']
            te.write(dhcpNameCommand.encode())
            # te.write(b"ip dhcp pool MyPool")

            te.expect([b"\(dhcp-config\)#"])
            dhcpNetworkCommand = "network " + dhcp['network']
            te.write(dhcpNetworkCommand.encode())
            # te.write(b"network 192.168.101.0 255.255.255.0")

            te.expect([b"\(dhcp-config\)#"])
            dhcpGatewayCommand = "default-router " + dhcp['gateway']
            te.write(dhcpGatewayCommand.encode())
            #te.write(b"default-router 192.168.101.1")

            te.expect([b"\(dhcp-config\)#"])
            dhcpDnsCommand = "dns-server " + dhcp['dns']
            te.write(dhcpDnsCommand.encode())
            # te.write(b"dns-server 192.168.11.254")

            te.expect([b"\(dhcp-config\)#"])
            te.write(b"exit")
            te.expect([b"\(config\)#"])

        #add dhcp

        te.write(b"ip route 0.0.0.0 0.0.0.0 192.168.11.254\n")
        te.write(b"ip route 0.0.0.0 0.0.0.0 192.168.101.2\n")
        te.expect([b"\(config\)#"])
        #TODO
        ##static route
        # te.write(b"ip route [ip_destinatie] [subnet_mask] [next_hop]")
        ##static route

        te.write(b"exit")
        te.expect([b"#"])
        te.write(b"wr")
        te.expect([b"\[confirm\]|#"])
        # te.__exit__(None, None, None)


def test_ping(ipAddress):
    print('ai intrat in functie')
    remote_address = ('192.168.0.100')
    port = 5004
    addIpCommand = "ping -c 5 " + ipAddress
    with TelnetContext(remote_address, port, b"UbuntuDockerGuest-1") as te:
        te.write(addIpCommand.encode())



config_router = [
        {
            'ip': '192.168.101.1',
            'interfaceName': 'eth0/1',
            'dhcp': {
                "name": "MyPool",
                "network": "192.168.101.0 255.255.255.0",
                "gateway" : "192.168.101.1",
                "dns" : "192.168.11.254"
            }
        },
        {
            'ip': '192.168.102.1',
            'interfaceName': 'eth0/2',
            'dhcp': {}
        },
        {
            'ip': '192.168.103.1',
            'interfaceName': 'eth0/3',
            'dhcp': {}
        },
        {
            'ip': '192.168.104.1',
            'interfaceName': 'eth1/0',
            'dhcp': {}
        }
    ]

# set_ubuntu_config()
# for conf in config_router:
#     set_ip_address(conf['ip'],conf['interfaceName'],conf['dhcp'])

test_ping('192.168.11.254')
