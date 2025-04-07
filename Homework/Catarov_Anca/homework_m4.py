from modul3.part2.telnet_context import TelnetContext
from subprocess import PIPE, Popen
from ipaddress import ip_address
import time
import telnetlib3
import asyncio

address = '192.168.0.100'
port = 5027

async def configure_csr_device(address: str, port: int, user: str, password: str, hostname: str):
    print("a intrat in functia de conf csr")
    connection = await telnetlib3.open_connection(address, port)
    t_reader, t_writer = connection
    t_writer.write("\n")
    response = await t_reader.readuntil(b'Router>')
    # response = await t_reader.readuntil(b'Router#')


    print(type(connection))
    print(connection)
    print(response)

    if b'initial configuration dialog? [yes/no]' in response:
        t_writer.write('yes\n')
        await t_reader.readuntil(b"management setup? [yes/no]:")
        t_writer.write('yes\n')
        await t_reader.readuntil(b"host name [Router]:")
        t_writer.write(f'{hostname}\n')
        await t_reader.readuntil(b"Enter enable secret:")
        t_writer.write(f'{password}\n')
        await t_reader.readuntil(b"Enter enable password:")
        t_writer.write(f'{password}\n')
        await t_reader.readuntil(b"Enter virtual terminal password:")
        t_writer.write(f'{password}\n')
        await t_reader.readuntil(b"SNMP Network Management? [yes]:")
        t_writer.write('no\n')
        await t_reader.readuntil(b"interface summary:")
        t_writer.write('GigabitEthernet1\n')
        await t_reader.readuntil(b"IP on this interface? [yes]:")
        t_writer.write('yes\n')
        await t_reader.readuntil(b"IP address for this interface:")
        t_writer.write('192.168.102.2\n')
        await t_reader.readuntil(b"mask for this interface [255.255.255.0] :")
        t_writer.write('255.255.255.0\n')
        await t_reader.readuntil(b"Enter your selection [2]:")
        t_writer.write('2\n')

        for _ in range(10):
            time.sleep(60)
            t_writer.write('\n')
            try:
                await asyncio.wait_for(t_reader.readuntil(hostname), timeout=10)
            except asyncio.TimeoutError:
                continue
    elif b'Router>' in response:
        print('Router is configured')
        t_writer.write('en\n')
        await t_reader.readuntil(b"Password:")
        t_writer.write(f'{password}\n')
        await t_reader.readuntil(b"Router#")
        t_writer.write('conf t\n')
        await t_reader.readuntil(b"Router(config)#")
        t_writer.write('ip route 192.168.11.0 255.255.255.0 192.168.102.1\n')
        await t_reader.readuntil(b"Router(config)#")
        t_writer.write('ip route 192.168.101.0 255.255.255.0 192.168.102.1\n')
        await t_reader.readuntil(b"Router(config)#")
        t_writer.write('exit\n')
        await t_reader.readuntil(b"Router#")
    elif b'Router#' in response:
        print('Router is configured')
        t_writer.write('conf t\n')
        await t_reader.readuntil(b"Router(config)#")
        t_writer.write('ip route 192.168.11.0 255.255.255.0 192.168.102.1\n')
        await t_reader.readuntil(b"Router(config)#")
        t_writer.write('ip route 192.168.101.0 255.255.255.0 192.168.102.1\n')
        await t_reader.readuntil(b"Router(config)#")
        t_writer.write('exit\n')
        await t_reader.readuntil(b"Router#")



def set_ubuntu_config():
    subnet_mask = '24'
    pc_address = ip_address('192.168.11.254')

    set_ip_command = f'sudo ip address add {pc_address}/{subnet_mask} dev ens4'.split(' ')
    set_int_on_command = 'ip link set dev ens4 up'.split(' ')

    set_ip_route_csr = f'ip route add 192.168.102.0/24 via 192.168.11.1'.split(' ')  ##for CSR
    set_ip_route_docker = f'ip route add 192.168.101.0/24 via 192.168.11.1'.split(' ')  ##for U-Doker

    set_ip = Popen(set_ip_command, stdout=PIPE, stderr=PIPE)
    print(set_ip.communicate())

    set_interf_on = Popen(set_int_on_command, stdout=PIPE, stderr=PIPE)
    print(set_interf_on.communicate())

    set_route = Popen(set_int_on_command, stdout=PIPE, stderr=PIPE)
    print(set_route.communicate())

    set_ip_route_response = Popen(set_ip_route_csr, stdout=PIPE, stderr=PIPE)
    print(set_ip_route_response.communicate())

    set_ip_route_response_docker = Popen(set_ip_route_docker, stdout=PIPE, stderr=PIPE)
    print(set_ip_route_response_docker.communicate())

def set_ip_address_router(ipAddress,interfaceName,dhcp):
    remote_address = ('192.168.0.100')
    port = 5015
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

        #add static route
        te.write(b"ip route 0.0.0.0 0.0.0.0 192.168.11.254\n")
        te.write(b"ip route 0.0.0.0 0.0.0.0 192.168.101.2\n")
        #add static route

        te.expect([b"\(config\)#"])
        te.write(b"exit")
        te.expect([b"#"])
        te.write(b"wr")
        te.expect([b"\[confirm\]|#"])
        # te.__exit__(None, None, None)


def test_ping(ipAddress):
    print('ai intrat in functie')
    remote_address = ('192.168.0.100')
    port = 5015
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


try:
    set_ubuntu_config()
except Exception as e:
    print(e)
print("Config router")
for conf in config_router:
    set_ip_address_router(conf['ip'],conf['interfaceName'],conf['dhcp'])
print("config csr")
asyncio.run(configure_csr_device(address, port, user='admin', password='Cisco!12', hostname='Router'))
print("finish configuration")
