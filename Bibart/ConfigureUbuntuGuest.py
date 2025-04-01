import time
from TelnetContext import TelnetContext
def configure_ubuntu_guest(hostname):
    with TelnetContext(address='92.83.42.103', port=5027, hostname=hostname) as te:
        te.write(b'cd /etc/network/interfaces.d/')
        te.write(b'echo "auto eth0\niface eth0 inet dhcp" > eth0')
        time.sleep(1)
        te.write(b'service networking restart')
        time.sleep(3)
        te.write(b'ip link set eth0 up')
        time.sleep(1)
        out = te.read_very_eager().decode()
        print(out)

if __name__ == '__main__':
    configure_ubuntu_guest('root')

# NU mere

