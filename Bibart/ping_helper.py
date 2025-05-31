"""
Contains function that tracks the result of a ping from a device to another
"""
import logging
import time
from typing import Tuple
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def test_pings(topology_addresses: list[str], execute, read, device_name: str, os: str) -> Tuple[bool, dict[str, bool]]:
    """
    Performs pings to all addresses in topology_addresses.(All interface ips in the testbed)
    Args:
        topology_addresses (list[str]): list of ip addresses
        execute (function(command:str, **kwargs)): function that executes a command and waits until one regex expr matches
        device_name (str): name of the device performing the ping
    Returns:
        (result: bool, dict):
            result: True if all pings succeeded, False otherwise
            dict: Target ip, Result of ping to said Ip
    """
    ping_results: dict[str, bool] = {}
    pattern = r'(?:Success rate is (\d{1,3}) percent)|(?:(\d{1,3})\% packet loss)'
    if os != 'ubuntu':
        execute('\r', prompt=[r'\w+#'])
    for addr in topology_addresses:
        ping_command = f'ping {addr}' if os != 'ubuntu' else f'ping -c 4 {addr}'
        out = execute(ping_command, prompt=[])
        matched_regex = False
        percentage = 0
        for _ in range(4):
            time.sleep(1)
            if _ == 0:
                out = out + read()
            else:
                out = read()
            match = re.search(pattern, out)
            if not match:
                continue
            matched_regex = True
            percentage = int(match.group(1)) if match.group(1) is not None \
                else 100 - int(match.group(2))
            break
        if not matched_regex:
            logger.error(out)
            percentage = 0
        if percentage == 0:
            ping_results[addr] = False
            logger.warning('Ping from %s to %s failed\n', device_name, addr)
        else:
            ping_results[addr] = True
            logger.warning('Ping from %s to %s succeeded\n', device_name, addr)
    return all(list(ping_results.values())), ping_results
