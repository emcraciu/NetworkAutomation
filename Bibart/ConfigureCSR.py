import re
from Bibart.TelnetContext import TelnetContext
from time import sleep


def configure_csr(t: TelnetContext):
    # Tre sa testez asta
    t.write(b"yes")
    sleep(2)
    t.expect([b'Would you like to enter basic management setup? [yes/no]: '])
    t.write(b"yes")
    t.expect(b"[Router]:")
    t.write(b"CSR")
    sleep(2)
    t.expect(b"enable secret:")
    t.write(b"pass")
    sleep(2)
    t.expect(b"enable password:")
    t.write(b"pass")
    sleep(2)
    t.expect([b"Enter virtual terminal password:"])
    t.write(b"pass")
    t.expect([b"Configure SNMP Network Management? [yes]:"])
    t.write(b"no")
    t.expect([b"Configure LAT? [yes]:"])
    t.write(b"no")
    t.expect([b'Configure IP? [yes]:'])
    t.write(b"yes")
    t.expect([b'Configure RIP routing? [no]:'])
    t.write(b"no")
    t.expect([b'Configure bridging? [no]:'])
    t.write(b"no")
    t.expect([b'Configure DECnet? [no]:'])
    t.write(b"no")
    t.expect([b'Configure CLNS? [no]:'])
    t.write(b"no")
    t.expect([b'Configure AppleTalk? [no]:'])
    t.write(b'no')
    t.expect([b'Configure Apollo? [no]:'])
    t.write(b"no")
    t.expect([b'Configure Vines? [no]:'])
    t.write(b"no")
    t.expect([b'Configure XNS? [no]:'])
    t.write(b"no")

    t.expect(b'Any interface listed with OK? value "NO" does not have a valid configuration')

    sleep(1)
    interfaces_text = t.read_very_eager()
    pattern = rb'(\w+)\s+\w+\s+\w{2,3}  \w+  up'
    matches = re.search(pattern, interfaces_text)
    if not matches:
        print("No interface is on up")
        return
    interface_name = matches.group(1)
    t.write(interface_name)
    sleep(1)
    t.expect([b'Configure IP on this interface? [yes]:'])
    t.write([b''])
    t.expect([b'IP address for this interface:'])
    t.write([b'192.168.102.2'])
    t.expect([b'Subnet mask for this interface [\d+.\d+.\d+.\d+] :'])
    t.write([b'255.255.255.0'])
    sleep(1)
    t.expect([b'Enter your selection [\d]:'])
    t.write([b'2'])
    for _ in range(5):
        sleep(60)
        t.write(b'')
        t.expect([b'CSR>'])


with TelnetContext(address="92.83.42.103",hostname="",port=5002) as t:
    t.write(b"")
    for _ in range(10):
        output = t.read_very_eager()
        if b'configuration dialog? [yes/no]:' in output:
            configure_csr(t)
            break
        sleep(10)
    else:
        print("Device already configured")
