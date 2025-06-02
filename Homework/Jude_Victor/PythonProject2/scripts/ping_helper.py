# ping_helper.py

import logging
import time
from typing import Callable, Tuple
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
"""
Contributors: Dusca Alexandru, Furmanek Carina, Jude Victor, Ivaschescu Gabriel
"""
def test_pings(
    topology_addresses: list[str],
    execute: Callable[..., str],
    read: Callable[[], str],
    device_name: str,
    os: str
) -> Tuple[bool, dict[str, bool]]:
    """
    Testează conectivitatea prin ping de la un dispozitiv către o listă de adrese IP.

    Args:
        topology_addresses (list[str]): Lista de adrese IP către care se vor trimite ping-uri.
        execute (Callable[..., str]): Funcție care execută comenzi pe dispozitiv.
        read (Callable[[], str]): Funcție care citește output adițional, dacă este necesar.
        device_name (str): Numele dispozitivului care trimite ping-urile.
        os (str): Sistemul de operare al dispozitivului ("ios", "ubuntu" etc.).

    Returns:
        Tuple[bool, dict[str, bool]]:
            - Un boolean care indică dacă toate ping-urile au fost cu succes.
            - Un dicționar care mapează fiecare IP la rezultatul ping-ului (True/False).
    """
    ping_results: dict[str, bool] = {}
    pattern = r'(?:Success rate is (\d{1,3}) percent)|(?:(\d{1,3})\% packet loss)'

    if os != 'ubuntu':
        execute('\r', prompt=[r'\w+#'])

    for addr in topology_addresses:
        ping_command = f'ping {addr}' if os != 'ubuntu' else f'ping -c 4 {addr}'
        print(f"\n--- Running ping command: {ping_command} ---")
        out = execute(ping_command, prompt=[])
        matched_regex = False
        percentage = 0

        for i in range(4):
            time.sleep(1)
            out += read() if i != 0 else ""
            print(f"\n--- Ping Output Round {i + 1} ---\n{out}\n")

            match = re.search(pattern, out)
            if match:
                matched_regex = True
                percentage = int(match.group(1)) if match.group(1) is not None else 100 - int(match.group(2))
                break

        if not matched_regex:
            logger.error(out)
            percentage = 0

        if percentage == 0:
            ping_results[addr] = False
            logger.warning('Ping from %s to %s failed\n', device_name, addr)
        else:
            ping_results[addr] = True
            logger.info('Ping from %s to %s succeeded\n', device_name, addr)

    return all(ping_results.values()), ping_results
