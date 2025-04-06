import re
from ipaddress import ip_address, IPv4Address, IPv4Network
from TelnetContext import TelnetContext
import asyncio
from asyncio import sleep

class IPv4AddrRange():
    def __init__(self, start: IPv4Address, end: IPv4Address):
        self.start = start
        self.end = end

async def configure_interfaces(te: TelnetContext):
    te.write(b'conf t')
    te.write(b'')
    te.expect([b'\(config\)#'])
    te.write(b"int eth0/0")
    te.expect([b'\(config-if\)'])
    te.write(b"ip add 192.168.11.1 255.255.255.0")
    te.expect([b'\(config-if\)'])
    te.write(b'no sh')
    te.expect([b'\(config-if\)', b'console by console', b'changed state to up'])

    for i in range(1,5):
        if i != 4:
            interf_name = f"eth0/{i}"
        else:
            interf_name = "eth1/0"
        te.write(f"int {interf_name}".encode())
        te.expect([b'\(config-if\)'])
        te.write(f"ip add 192.168.10{i}.1 255.255.255.0".encode())
        te.expect([b'\(config-if\)'])
        te.write(b'no sh')
        await sleep(1)
        te.write(b'')
        te.expect([b'\(config-if\)', b'console by console', b'changed state to up'])
    te.expect([b'\(config-if\)',b'console by console', b'changed state to up'])
    te.write(b'end')

async def configure_dhcp(te: TelnetContext, pool_name: str,network_addr: IPv4Address,subnet_mask: str, excluded_addr_intervals: list[IPv4AddrRange], gateway: IPv4Address, dns: IPv4Address):
    te.write(b'conf t')
    te.write(f'ip dhcp pool {pool_name}'.encode())
    te.expect([b'\(dhcp-config\)'])
    te.write(f'network {network_addr} {subnet_mask}'.encode())
    te.expect([b'\(dhcp-config\)'])
    te.write(f'async default-router {gateway}'.encode())
    te.expect([b'\(dhcp-config\)'])
    te.write(f'dns-server {dns}'.encode())
    te.expect([b'\(dhcp-config\)'])
    te.write(b'exit')
    te.expect([b'\(config\)#'])
    te.write(b'service dhcp')
    te.expect([b'\(config\)#'])
    for interval in excluded_addr_intervals:
        te.write(f'ip dhcp excluded-address {interval.start} {interval.end}'.encode())
        te.expect([b'\(config\)#'])
    await sleep(3)
    te.write(b'exit')

async def save_run_conf(te: TelnetContext):
    te.write(b"wr")
    out = te.read_very_eager()
    if b'Continue' in out:
        te.write(b"")
    await sleep(3)
    te.expect([b"#", b'[confirm]'])
    te.write(b'')


async def compress_run_conf(te: TelnetContext):
    te.write(b"conf t")
    te.expect([b'\(config\)#'])
    te.write(b"service compress-config")
    await sleep(3)
    te.expect([b'\(config\)#'])
    te.write(b"")
    await sleep(1)
    te.write(b"exit")

async def configure_telnet(te: TelnetContext):
    te.write(b'conf t')
    te.write(b"int eth0/0")
    te.expect([b"\(config-if\)#"])
    te.write(b"ip add 192.168.11.1 255.255.255.0")
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
    te.write(b"exit")
    te.expect([b"#"])

async def skip_initial_config_and_rename(te: TelnetContext):
    for _ in range(2):
        te.write(b'')
    await sleep(3)
    output = te.read_very_eager()
    if b'Autoinstall trying' in output:
        te.write(b'')
        await sleep(3)
        output = te.read_very_eager()
    if b'IOU1' in output:
        print("Device already has IOU1 hostname")
        te.write(b'en')
        await sleep(2)
        return
    pattern = rb'(\w+)(?:>|#)'
    match = re.search(pattern, output)
    curr_hostname = b''
    if not match:
        if b'initial configuration dialog? [yes/no]:' in output:
            te.write(b'no')
            te.expect([b'terminate autoinstall\? \[yes\]\:'])
            te.write(b'yes')
            for _ in range(3):
                await sleep(60)
                output = te.read_very_eager()
                if b'saved successfully' in output:
                    print('Saved successfully')
                    break
            # Nu vrea sa dea endline aici ? DE CE??? TODO:
            for _ in range(5):
                te.write(b'')
            await sleep(5)
            output = te.read_very_eager()
            match = re.search(pattern, output)
            if match:
                curr_hostname = match.group(1).decode()
            else:
                print("Failed to rename")
                exit(1)
    else:
        curr_hostname = match.group(1).decode()

    print(f'Curr hostname: {curr_hostname}')
    te.write(b'')
    te.expect([f'{curr_hostname}(?:\>|#)'.encode()])
    te.write(b'en')
    te.expect([f'{curr_hostname}#'.encode()])
    te.write(b'conf t')
    te.expect([b'\(config\)#'])
    te.write(b'hostname IOU1')
    te.expect([b'IOU1\(config\)#'])
    te.write(b'end')
    print(f"Successfully renamed from {curr_hostname} to IOU1")

async def configure_ssh(te: TelnetContext, domain_name: str, modulus: int):
    te.write(b'conf t')
    te.expect([b"\(config\)#"])
    te.write(f'ip domain name {domain_name}'.encode())
    te.expect([b"\(config\)#"])
    te.write(f'crypto key generate rsa modulus {modulus}'.encode())
    await sleep(2)
    te.expect([b"\(config\)#"])
    te.write(b'line vty 0 4')
    te.expect([b"\(config-line\)#"])
    te.write(b"transport input ssh")
    te.expect([b"\(config-line\)#"])
    te.write(b"login local")
    te.expect([b"\(config-line\)#"])
    te.write(b"privilege level 15")
    te.expect([b"\(config-line\)#"])
    te.write(b"exit")
    te.expect([b"\(config\)#"])
    te.write(b'username user secret pass privilege 15')
    te.expect([b"\(config\)#"])
    # de ce nu intra in exit???
    await sleep(1)
    te.write(b'')
    await sleep(1)
    te.write(b'exit')

async def add_static_route(te: TelnetContext, remote_network: IPv4Network, remote_sub_mask: str, via_address: IPv4Address):
    te.write(b'conf t')
    te.expect([b"\(config\)#"])
    te.write(f'ip route {remote_network} {remote_sub_mask} {via_address}'.encode())
    await sleep(1)
    te.expect([b"\(config\)#"])
    te.write(b'exit')

async def configure_router():
    print("Configuring Router")
    remote_address = '92.83.42.103'
    port=5006

    with TelnetContext(remote_address, port, b'') as te:
        await skip_initial_config_and_rename(te)

    with TelnetContext(remote_address, port, b"IOU1") as te:
        await configure_interfaces(te)
        await configure_dhcp(te = te,
                   pool_name="Joe",
                   network_addr=("192.168.101.0"),
                   subnet_mask="255.255.255.0",
                   excluded_addr_intervals=[
                       IPv4AddrRange(
                           ip_address("192.168.101.1"),
                           ip_address("192.168.101.99")
                       ),
                       IPv4AddrRange(
                           ip_address("192.168.101.201"),
                           ip_address("192.168.101.254")
                       )
                   ],
                   gateway=("192.168.101.1"),
                   dns=("192.168.10.10"),
                   )
        await add_static_route(te,
             remote_network=ip_address('192.168.10.0'),
             remote_sub_mask='255.255.255.0',
             via_address='192.168.10.254')
        await configure_ssh(te, 'cisco.com', 2048)
        await compress_run_conf(te)
        await save_run_conf(te)
        print("Router configuration complete")
if __name__ == "__main__":
    asyncio.run(configure_router())