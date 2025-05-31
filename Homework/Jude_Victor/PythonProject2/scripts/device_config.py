"""
Module for configuring network devices (routers, switches, firewalls).
Contributors: Furmanek Carina, Jude Victor
"""
from typing import Any  # For now, using Any for device type


# from pyats.topology import Device # Later, you can use the specific pyATS Device type

def set_device_hostname(device: Any, hostname: str) -> bool:
    """
    Sets the hostname on the given device.

    Args:
        device: A pyATS-like device object that has a 'configure' method
                and a 'name' attribute.
        hostname: The desired hostname string.

    Returns:
        True if the configuration command was attempted successfully (does not check device state),
        False if an exception occurred during the attempt.
    """
    if not hostname or not isinstance(hostname, str):
        print("Error: Hostname must be a non-empty string.")
        return False

    print(f"Attempting to set hostname to '{hostname}' on device '{device.name}'...")
    try:
        device.configure(f"hostname {hostname}")
        print(f"Hostname configuration command sent for {device.name}.")
        return True
    except Exception as e:
        print(f"Error sending hostname configuration to {device.name}: {e}")
        return False


def get_device_prompt(device: Any) -> str | None:
    """
    Retrieves the current prompt of the device.

    Args:
        device: A pyATS-like device object with an 'execute' method and a 'prompt' attribute.

    Returns:
        The device prompt string, or None if an error occurs.
    """
    try:
        return device.prompt
    except Exception as e:
        print(f"Error retrieving prompt for {device.name}: {e}")
        return None