"""
Contains function to ping all other devices
"""


from subprocess import Popen, PIPE
from typing import Tuple, List

from pyats.topology import loader
from ping_helper import test_pings
tb = loader.load('testbeds/config.yaml')
_topology_addresses = [
    interf.ipv4.ip.compressed for dev in tb.devices.values()
    for interf in dev.interfaces.values() if interf.ipv4
]
output = "" # pylint: disable=invalid-name

def execute(command) -> str:
    """
    Executes the command and returns the output
    Returns
        The output of the command until the matched part(inclusive)
    """
    global output # pylint: disable=global-statement
    with Popen(command.split(' '), stdout=PIPE, stderr=PIPE) as proc:
        output = proc.communicate()[0].decode()
    return output

def read()->str:
    """
    Returns the output of the previous command
    """
    return output

def ping_all(topology_addresses: List[str]=None)-> Tuple[bool, dict[str, bool]]:
    """
    Pings all interfaces with addresses from the testbed
    Args:
         topology_addresses: If provided, will ping these addresses instead of fetching addresses from the testbed
    """
    if topology_addresses is None:
        topology_addresses = _topology_addresses
    all_worked, ping_results = test_pings(topology_addresses, execute, read, device_name="UbuntuServer", os='ubuntu')
    return all_worked, ping_results

if __name__ == '__main__':
    ping_all(topology_addresses=['127.0.0.1'])
