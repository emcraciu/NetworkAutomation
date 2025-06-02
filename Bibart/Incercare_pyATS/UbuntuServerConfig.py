import logging
from subprocess import Popen, PIPE
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, encoding='utf-8')

def configure():
    commands = [
        'sudo ip address add 192.168.11.254/24 dev ens4',
        'sudo ip link set dev ens4 up',
        'sudo ip route add 192.168.101.0/24 via 192.168.11.1',
        'sudo ip route add 192.168.101.0/24 via 192.168.11.1',
        'sudo ip route add 192.168.102.0/24 via 192.168.11.1',
        'sudo ip route add 192.168.103.0/24 via 192.168.11.1',
        'sudo ip route add 192.168.104.0/24 via 192.168.11.1',
        'sudo ip route add 10.10.10.0/24 via 192.168.11.1',
        'sudo ip route add 20.20.20.0/24 via 192.168.11.1',
        'sudo ip route add 30.30.30.0/24 via 192.168.11.1',
        'sudo ip route add 40.30.30.0/24 via 192.168.11.1',
        'sudo ip route add 50.50.50.0/24 via 192.168.11.1',
    ]
    for c in commands:
        logger.info(f'executing: {c.split(' ')}')
        out = Popen(c.split(' '), stdout=PIPE, stderr=PIPE).communicate()
        logger.warn(out)

