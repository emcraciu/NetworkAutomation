import logging
from subprocess import Popen, PIPE

from pyats.topology.device import Device

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, encoding='utf-8')

def configure(device: Device):
    eth1 = device.interfaces['eth1']
    print(eth1)
    commands = [
        f'sudo ip address add {eth1.ipv4.compressed} dev ens4',
        'sudo ip link set dev ens4 up',
    ]
    routes = device.custom['routes']
    for _,route in routes.items():
        commands.append(f'sudo ip route add {route['to_ip']} via {route['via']}')
    for c in commands:
#        logger.info(f'executing: {c.split(' ')}')
       out = Popen(c.split(' '), stdout=PIPE, stderr=PIPE).communicate()
       # logger.warn(out)

