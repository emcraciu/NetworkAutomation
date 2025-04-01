from modul3.part2.telnet_context import TelnetContext


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
            # te.write(b"ip route 192.168.11.0 255.255.255.0 192.168.101.2")
            # te.write(b"ip route 192.168.101.0 255.255.255.0 192.168.11.2")
            # te.expect([b"\(config\)#"])
        #add dhcp


        #TODO
        ##static route
        # te.write(b"ip route [ip_destinatie] [subnet_mask] [next_hop]")
        ##static route

        te.write(b"exit")
        te.expect([b"#"])
        te.write(b"wr")
        te.expect([b"\[confirm\]|#"])
        # te.__exit__(None, None, None)

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
            'interfaceName': 'eth0/4',
            'dhcp': {}
        }
    ]
for conf in config_router:
    set_ip_address(conf['ip'],conf['interfaceName'],conf['dhcp'])
