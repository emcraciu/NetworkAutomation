"""
Contains function to ping all other devices
"""
from pyats.topology import loader
tb = loader.load('testbeds/config.yaml')
topology_addresses = [
    interf.ipv4.ip.compressed for dev in tb.devices.values()
    for interf in dev.interfaces.values() if interf.ipv4
]