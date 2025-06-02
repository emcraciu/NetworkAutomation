import subprocess
import telnetlib
import time
import telnetlib3
import asyncio

address = '192.168.0.100'
port = 5032

def set_ip_on_ubuntu():
    interface='ens4'
    ubuntu_ip='192.168.11.21/24'
    gateway_ip='192.168.11.1'
    dict_of_destionations={"cloud":'192.168.12.0/24',"client":'192.168.101.0/24',"csr":'192.168.102.0/24'}
    subprocess.Popen(['sudo','ip','address',"add",ubuntu_ip,"dev",interface],stdout=subprocess.PIPE)
    subprocess.Popen(["sudo","ip","link","set",interface,"up"],stdout=subprocess.PIPE)
    for value in dict_of_destionations.values():
        subprocess.Popen(['sudo',"ip","route","add",value,"via",gateway_ip],stdout=subprocess.PIPE)


def set_ip_on_guest():
    interface = 'eth0'
    guest_ip = '192.168.101.100/24' #nu ia cu dhcp ip :(
    destination_ip = '192.168.101.1/24'

    new_te = telnetlib.Telnet("92.83.42.103", 5045)
    new_te.write(f"ip addr add {guest_ip} dev {interface}".encode())
    new_te.write(f"ip link set dev {interface} up".encode())
    new_te.write(f"ip route add default via {destination_ip}".encode())

def ip_setting_function(te,i):
    te.write(f'int eth0/{str(i)}\n'.encode())
    te.expect([b"IOU1\(config-if\)#"])
    te.write(f'ip add 192.168.10{str(i)}.1 255.255.255.0\n'.encode())
    te.expect([b"IOU1\(config-if\)#"])
    te.write(b'no shutdown\n')
    te.expect([b"IOU1\(config-if\)#"])
    te.write(b'exit\n')
    te.expect([b"IOU1\(config\)#"])

def dhcp_exclude_interval(te,start,finish):
    te.write(f'ip dhcp excluded-address 192.168.101.{start} 192.168.101.{finish}\n'.encode())
    te.expect([b"IOU1\(config\)#"])

def dhcp_function(te):
    te.write(b'ip dhcp pool UbuntuDocker\n')
    te.expect([b"IOU1\(dhcp-config\)#"])
    te.write(b'network 192.168.101.0 255.255.255.0\n')
    te.expect([b"IOU1\(dhcp-config\)#"])
    te.write(b'default-router 192.168.101.1\n')
    te.expect([b"IOU1\(dhcp-config\)#"])
    te.write(b'dns-server 192.168.102.1\n')
    te.expect([b"IOU1\(dhcp-config\)#"])

def ssh_function(te):
    te.write(b'ip domain name local\n')
    te.expect([b"IOU1\(config\)#"])
    te.write(b'username admin secret cisco\n')
    te.expect([b"IOU1\(config\)#"])
    te.write(b'crypto key generate rsa\n')
    time.sleep(3)
    te.write(b' \n')
    time.sleep(3)
    te.write(b'yes\n')
    time.sleep(3)
    te.write(b'\n')
    te.expect([b"IOU1\(config\)#"])
    te.write(b'ip ssh version 2\n')
    te.expect([b"IOU1\(config\)#"])
    te.write(b'line vty 0 4\n')
    te.expect([b"IOU1\(config-line\)#"])
    te.write(b'login local\n')
    te.expect([b"IOU1\(config-line\)#"])
    te.write(b'transport input ssh\n')
    te.expect([b"IOU1\(config-line\)#"])
    te.write(b'exit\n')
    te.expect([b"IOU1\(config\)#"])
    te.write(b'exit\n')

def router():
    host='92.83.42.103'
    port=5044
    interface_number=4

    te=telnetlib.Telnet(host,port)

    print("m-am conectat")
    te.write(b'')

    te.write(b'conf t\n')
    te.expect([b"IOU1\(config\)#"])

    te.write(b'int eth0/0\n')
    te.expect([b"IOU1\(config-if\)#"])
    te.write(b'ip add 192.168.11.1 255.255.255.0\n')
    te.expect([b"IOU1\(config-if\)#"])
    te.write(b'no shutdown\n')

    for i in range(1,interface_number):
       ip_setting_function(te,i)

    te.write(b'int eth1/0\n')
    te.expect([b"IOU1\(config-if\)#"])
    te.write(b'ip add 192.168.104.1 255.255.255.0\n')
    te.expect([b"IOU1\(config-if\)#"])
    te.write(b'no shutdown\n')
    te.expect([b"IOU1\(config-if\)#"])
    te.write(b'exit\n')
    te.expect([b"IOU1\(config\)#"])
    te.write(b'ip route 0.0.0.0 0.0.0.0 192.168.11.21\n')
    te.expect([b"IOU1\(config\)#"])

    dhcp_exclude_interval(te,1,99)
    dhcp_exclude_interval(te,200,254)

    dhcp_function(te)

    te.write(b'exit\n')
    te.expect([b"IOU1\(config\)#"])
    ssh_function(te)
    te.write(b'exit\n')


def test_ping():

    try:
        output=subprocess.check_output(
                ['ping', '-c', '1', '192.168.101.100'],
                stderr=subprocess.STDOUT,
                text=True)

        if 'bytes from' in output:
            print("Ping is working")
        else:
            print("Ping failed")

    except subprocess.CalledProcessError as e:
        print("Ping failed")

async def configure_csr_device(address, port, user, password,hostname):
    connection = await telnetlib3.open_connection(address, port)
    t_reader, t_writer = connection
    t_writer.write("\n")
    try:
        response = await asyncio.wait_for(t_reader.readuntil(b"[yes/no]:"),timeout=5)

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
            time.sleep(25)
            t_writer.write(' \n')
            time.sleep(25)
            t_writer.write(' \n')
            await t_reader.readuntil(b"Router>")
            t_writer.write(f'en\n')
            await t_reader.readuntil(b"Password:")
            t_writer.write(f'{password}\n')
            await t_reader.readuntil(b"Router#")
            t_writer.write(f'conf t\n')
            await t_reader.readuntil(b"Router(config)#")
            t_writer.write(f'ip route 192.168.11.0 255.255.255.0 192.168.102.1\n')
            await t_reader.readuntil(b"Router(config)#")
            t_writer.write(f'ip route 192.168.101.0 255.255.255.0 192.168.102.1\n')
            await t_reader.readuntil(b"Router(config)#")

        elif b'Router>' in response:
            print('Router is configured')

    except asyncio.TimeoutError:
        print("Router is configured")


while True:
    print("1.Set IP on Ubuntu Server and Configure")
    print("2.Set IP on Guest and Configure")
    print("3.Configure Router")
    print("4.Check IP from Ubuntu Server to Guest")
    print("5.Configure CSR Router")
    print("6.Exit")
    option=input("Choose an option:")

    match option:
        case "1":
            set_ip_on_ubuntu()
            print("Command executed successfully!")
        case "2":
            set_ip_on_guest()
            print("Command executed successfully!")
        case "3":
            router()
            print("Command executed successfully!")
        case "4":
            test_ping()
            print("Command executed successfully!")
        case "5":
            asyncio.run(configure_csr_device(address, port, user='admin', password='Cisco!12', hostname="Router"))
            print("Command executed successfully!")
        case "6":
            break

    time.sleep(2)




