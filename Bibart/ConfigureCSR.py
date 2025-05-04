import telnetlib3
import asyncio
from asyncio import sleep

address = '92.83.42.103'
port = 5037

async def configure_csr_device(address: str, port: int, user: str, password: str, hostname: str):
    print("Configuring CSR device")
    connection = await telnetlib3.open_connection(address, port)
    t_reader, t_writer = connection
    t_writer.write("\n")
    can_config = True
    try:
        response = await asyncio.wait_for(t_reader.readuntil(b"[yes/no]:"),10)
    except asyncio.exceptions.TimeoutError:
        can_config = False

    if not can_config:
        try:
            response = await asyncio.wait_for(t_reader.readuntil(b">"),10)
            print("CSR already configured")
            return
        except asyncio.exceptions.TimeoutError:
            print("Configuration failed")
            return

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
            await sleep(60)
            for __ in range(3):
                t_writer.write('\n')
            try:
                await asyncio.wait_for(t_reader.readuntil(hostname.encode()), timeout=10)
                break
            except asyncio.TimeoutError:
                continue
    print("Finished configuring CSR device")

if __name__ == '__main__':
    asyncio.run(configure_csr_device(address, port, user='user', password='pass', hostname='CSR'))
