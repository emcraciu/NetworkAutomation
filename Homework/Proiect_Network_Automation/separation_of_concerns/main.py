# main_test_script.py (Rewritten "initial" structure with "actual" methods)

import logging
from typing import Dict

from pyats import aetest
from pyats.aetest.steps import Steps
from pyats.topology import loader, Device  # Ensure Device is imported if used for type hinting

# Import from the "actual code" (refactored connectors and new configurators)
from connectors.telnet_connector import TelnetConnector
from connectors.telnet_configurator import TelnetConfigurator
from connectors.ssh_connector import SSHConnector
from connectors.ssh_configurator import SSHConfigurator

# Assuming ubuntu_config.py exists and has a configure function.
# You might need to adapt its call if it relies on a specific connector.
# from ubuntu_config import configure as configure_ubuntu_server

# --- Testbed Loading ---
# This should be at the module level for 'aetest.main(testbed=testbed)' to work as expected.
try:
    testbed = loader.load('testbed_config.yaml')
except Exception as e:
    # Log critical error if testbed loading fails, as the script cannot proceed.
    logging.critical(f"CRITICAL: Failed to load testbed 'testbed_config.yaml': {e}", exc_info=True)
    raise  # Re-raise to stop execution.

# --- Logging Setup ---
# Get a logger for this script.
log = logging.getLogger(__name__)


# Note: pyATS test execution (e.g., via `pyats run job`) typically configures its own logging.
# BasicConfig is useful for direct `python your_script.py` runs.
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')


# ---------------------------------------------------------------------
# Common Setup: Initialize objects and establish Telnet connections
# ---------------------------------------------------------------------
class GlobalDeviceSetup(aetest.CommonSetup):
    """
    Global Setup:
    1. Initializes runtime_data storage.
    2. Instantiates Telnet/SSH Connectors and Configurators.
    3. Attempts to connect via TELNET ONLY. SSH connections are deferred.
    """

    @aetest.subsection
    def initialize_and_prepare_device_objects(self, steps: Steps):  # Combined for one setup subsection
        """Create storage and instantiate all connector/configurator objects. Connect Telnet."""
        # Initialize runtime_data in parent parameters for sharing across sections
        if 'runtime_data' not in self.parent.parameters:
            self.parent.parameters['runtime_data'] = {}
        runtime_data_dict = self.parent.parameters['runtime_data']

        # Ensure all expected keys exist in runtime_data from the start
        runtime_data_dict.setdefault('telnet_connectors', {})
        runtime_data_dict.setdefault('telnet_configurators', {})
        runtime_data_dict.setdefault('ssh_connectors', {})
        runtime_data_dict.setdefault('ssh_configurators', {})
        log.info("Initialized runtime_data storage structure.")

        # Fetch the testbed object (should be passed to aetest.main)
        active_testbed = self.parameters.get('testbed')
        if not active_testbed:
            # If testbed is not found, abort as no devices can be processed.
            self.aborted("Testbed object not found in script parameters. Critical setup failure.",
                         goto=['common_cleanup'])  # common_cleanup might not run if aborted this early
            return

        log.info(f"Processing devices from testbed: {active_testbed.name}")
        for dev_name, device_obj in active_testbed.devices.items():
            with steps.start(f"Preparing device: {dev_name}", continue_=True) as device_preparation_step:

                # --- Telnet Object Instantiation & Connection Attempt ---
                if 'telnet' in device_obj.connections:
                    log.debug(f"Setting up Telnet resources for {dev_name}.")
                    telnet_conn_details = device_obj.connections.telnet
                    telnet_connector = TelnetConnector(device=device_obj)  # Instantiate connector

                    try:
                        log.info(f"Attempting Telnet connection to '{dev_name}'...")
                        telnet_connector.connect(connection=telnet_conn_details,
                                                 timeout=telnet_conn_details.get('timeout', 20))
                        runtime_data_dict['telnet_connectors'][dev_name] = telnet_connector
                        log.info(f"Telnet successfully connected to '{dev_name}'.")

                        # Instantiate configurator only if Telnet connection was successful
                        telnet_configurator = TelnetConfigurator(device=device_obj, connector=telnet_connector)
                        runtime_data_dict['telnet_configurators'][dev_name] = telnet_configurator
                        log.info(f"TelnetConfigurator initialized for '{dev_name}'.")

                    except Exception as e:
                        log.error(f"Telnet setup for '{dev_name}' failed: {e}", exc_info=True)
                        # Store the connector instance even if connection failed for debugging.
                        runtime_data_dict['telnet_connectors'][dev_name] = telnet_connector
                        # Configurator might not be creatable or useful if connector failed badly
                        # and TelnetConfigurator checks connection in __init__ (it shouldn't ideally for consistency)
                        if dev_name not in runtime_data_dict.get('telnet_configurators', {}):
                            try:
                                # Assuming TelnetConfigurator might also need a live connection
                                # If TelnetConfigurator is tolerant, this is fine.
                                runtime_data_dict['telnet_configurators'][dev_name] = TelnetConfigurator(
                                    device=device_obj, connector=telnet_connector)
                                log.warning(
                                    f"TelnetConfigurator for {dev_name} instantiated with a non-connected Telnet connector.")
                            except Exception as e_cfg_tel:
                                log.warning(
                                    f"Could not instantiate TelnetConfigurator for {dev_name} after Telnet connect failure: {e_cfg_tel}")
                else:
                    log.debug(f"No Telnet connection defined for '{dev_name}'.")

                # --- SSH Object Instantiation (NO connection attempt in GlobalSetup) ---
                if 'ssh' in device_obj.connections:
                    log.debug(f"Instantiating SSH objects for {dev_name} (connection will be deferred).")
                    ssh_connector = SSHConnector(device=device_obj)  # Does NOT connect
                    runtime_data_dict['ssh_connectors'][dev_name] = ssh_connector

                    # SSHConfigurator's __init__ MUST be tolerant of a non-connected SSHConnector
                    ssh_configurator = SSHConfigurator(device=device_obj, connector=ssh_connector)
                    runtime_data_dict['ssh_configurators'][dev_name] = ssh_configurator
                    log.info(
                        f"SSHConnector & SSHConfigurator instances created for '{dev_name}'. Actual SSH connection is deferred.")
                else:
                    log.debug(f"No SSH connection defined for '{dev_name}'.")

                device_preparation_step.passed()  # Mark step as passed for processing the device entry


# ---------------------------------------------------------------------
# Testcase: Telnet Device Bootstrap (Initial Configuration)
# ---------------------------------------------------------------------
class TelnetDeviceBootstrap(aetest.Testcase):
    """
    BOOTSTRAP PHASE: Uses Telnet to perform initial device setup, including enabling SSH.
    This structure is similar to your initial `TelnetDeviceConfiguration`.
    """
    uid = "tc_telnet_bootstrap_phase"

    @aetest.setup
    def check_telnet_resources(self, runtime_data: dict):
        if not runtime_data or not runtime_data.get('telnet_configurators'):
            self.skipped("No Telnet configurators available for bootstrapping phase.",
                         goto=['next_tc'])  # Skip to next testcase if no Telnet work

    # @aetest.test # Placeholder for Ubuntu configuration
    # def configure_ubuntu_server_if_present(self, steps: Steps, runtime_data: dict, testbed):
    #     ubuntu_device_name = 'UbuntuServer' # Example name
    #     if ubuntu_device_name in testbed.devices:
    #         # This section needs to be adapted based on how configure_ubuntu_server works
    #         # Does it use Telnet? SSH? Does it need a connector from runtime_data?
    #         log.info(f"Placeholder for configuring {ubuntu_device_name}. Adapt as necessary.")
    #         # Example:
    #         # if ubuntu_device_name in runtime_data.get('telnet_configurators', {}):
    #         #     ubuntu_telnet_cfg = runtime_data['telnet_configurators'][ubuntu_device_name]
    #         #     # configure_ubuntu_server(testbed.devices[ubuntu_device_name], telnet_configurator=ubuntu_telnet_cfg)
    #         # else:
    #         #     # configure_ubuntu_server(testbed.devices[ubuntu_device_name]) # Original call
    #     else:
    #         log.info(f"Device '{ubuntu_device_name}' not in testbed, skipping its specific configuration.")
    #     pass

    @aetest.test
    def bootstrap_network_devices_via_telnet(self, steps: Steps, runtime_data: dict):
        """Performs initial setup on network devices using Telnet."""
        log.info("--- Starting Telnet Bootstrap Phase for Network Devices ---")
        telnet_configurators: Dict[str, TelnetConfigurator] = runtime_data.get('telnet_configurators', {})

        for dev_name, configurator in telnet_configurators.items():
            device_obj = configurator.device

            # Check if Telnet connector for this device is actually connected
            if not configurator.connector.is_connected():
                log.warning(f"Telnet for '{dev_name}' is not connected. Skipping bootstrap for this device.")
                continue

            # Target specific OS types for network device bootstrapping
            if device_obj.os not in ('ios', 'iosxe', 'ftd'):  # Add other OS if they have Telnet bootstrap
                log.debug(
                    f"Skipping Telnet bootstrap for '{dev_name}' (OS: {device_obj.os}) - not a targeted network OS for this action.")
                continue

            with steps.start(f"Telnet Bootstrap Action: {dev_name} (OS: {device_obj.os})",
                             continue_=True) as bootstrap_step:
                try:
                    log.info(f"Performing Telnet bootstrap actions for '{dev_name}'...")
                    if device_obj.os == 'ftd':
                        configurator.configure_ftd()
                    elif device_obj.os in ('ios', 'iosxe'):
                        configurator.do_initial_config()  # This method is responsible for enabling SSH
                    # Add other OS-specific bootstrap calls here if needed

                    log.info(f"Telnet bootstrap actions completed for '{dev_name}'.")
                    bootstrap_step.passed()
                except Exception as e:
                    log.error(f"Telnet bootstrap actions for '{dev_name}' failed: {e}", exc_info=True)
                    bootstrap_step.failed(f"Telnet bootstrap error: {e}")


# ---------------------------------------------------------------------
# Testcase: SSH Device Configuration (Main Configuration)
# ---------------------------------------------------------------------
class SshDeviceConfiguration(aetest.Testcase):
    """
    MAIN CONFIGURATION PHASE: Uses SSH for further device configuration.
    SSHConfigurator methods will handle ensuring connection internally.
    This structure is similar to your initial `SSHDeviceConfiguration`.
    """
    uid = "tc_ssh_main_configuration_phase"

    @aetest.setup
    def check_ssh_resources(self, runtime_data: dict):
        if not runtime_data or not runtime_data.get('ssh_configurators'):
            self.skipped("No SSH configurators available for SSH configuration phase.",
                         goto=['common_cleanup'])  # Skip to cleanup if no SSH work

    @aetest.test
    def configure_network_devices_via_ssh(self, steps: Steps, runtime_data: dict):
        """Performs main configuration on network devices using SSH."""
        log.info("--- Starting SSH Configuration Phase for Network Devices ---")
        ssh_configurators: Dict[str, SSHConfigurator] = runtime_data.get('ssh_configurators', {})

        for dev_name, configurator in ssh_configurators.items():
            device_obj = configurator.device

            # Example: Target only specific OS for this full configuration pass
            # Add other OS types if they have an apply_full_configuration method or similar
            if device_obj.os not in ('ios', 'iosxe'):
                log.debug(
                    f"Skipping SSH configuration for '{dev_name}' (OS: {device_obj.os}) - not targeted for this detailed SSH configuration pass.")
                continue

            with steps.start(f"SSH Configuration Action: {dev_name}", continue_=True) as config_step:
                try:
                    log.info(f"Performing SSH configuration for '{dev_name}'...")
                    # The apply_full_configuration method (or any other method in SSHConfigurator
                    # that sends commands) MUST internally call its 'ensure_connection()' method
                    # to establish the SSH connection if it's not already active.
                    if hasattr(configurator, 'apply_full_configuration'):
                        configurator.apply_full_configuration()
                    else:
                        log.warning(
                            f"SSHConfigurator for {dev_name} does not have 'apply_full_configuration' method. Skipping detailed config.")
                        config_step.skipped("No 'apply_full_configuration' method.")
                        continue

                    log.info(f"SSH configuration completed for '{dev_name}'.")
                    config_step.passed()
                except ConnectionError as conn_err:
                    log.error(f"SSH connection failed for '{dev_name}' during configuration attempt: {conn_err}",
                              exc_info=True)
                    config_step.failed(f"SSH connection error for {dev_name}: {conn_err}")
                except Exception as e:
                    log.error(f"SSH configuration for '{dev_name}' failed: {e}", exc_info=True)
                    config_step.failed(f"SSH configuration error for {dev_name}: {e}")


# ---------------------------------------------------------------------
# Common Cleanup
# ---------------------------------------------------------------------
class DeviceCleanup(aetest.CommonCleanup):
    """Cleanup Phase: Disconnect all active Telnet and SSH connections."""

    @aetest.subsection
    def disconnect_all_active_connections(self, runtime_data: dict):  # Renamed method for clarity
        log.info("--- Starting Device Disconnection Phase ---")
        if not runtime_data:
            log.warning("Runtime data not found in cleanup phase, cannot perform disconnections.")
            return

        # Disconnect Telnet Connectors
        telnet_connectors = runtime_data.get('telnet_connectors', {})
        for name, conn in telnet_connectors.items():
            try:
                if conn and conn.is_connected():  # Defensive check
                    log.info(f"Disconnecting Telnet from '{name}'...")
                    conn.disconnect()
            except Exception as e:
                log.error(f"Error during Telnet disconnection from '{name}': {e}", exc_info=True)

        # Disconnect SSH Connectors
        ssh_connectors = runtime_data.get('ssh_connectors', {})
        for name, conn in ssh_connectors.items():
            try:
                if conn and conn.is_connected():  # Defensive check
                    log.info(f"Disconnecting SSH from '{name}'...")
                    conn.disconnect()
            except Exception as e:
                log.error(f"Error during SSH disconnection from '{name}': {e}", exc_info=True)
        log.info("Device disconnection attempts completed.")


# --- Main Execution Entry Point ---
if __name__ == '__main__':
    import sys

    # Configure basic logging when the script is run directly.
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,  # Adjust to logging.DEBUG for more verbosity
        format='%(asctime)s [%(levelname)s] (%(module)s:%(lineno)d) %(message)s'  # More detailed format
    )
    # You can set specific logger levels for your modules if needed during development:
    # logging.getLogger('connectors.telnet_connector').setLevel(logging.DEBUG)
    # logging.getLogger('connectors.ssh_connector').setLevel(logging.DEBUG)
    # logging.getLogger('connectors.telnet_configurator').setLevel(logging.DEBUG)
    # logging.getLogger('connectors.ssh_configurator').setLevel(logging.DEBUG)
    # logging.getLogger(__name__).setLevel(logging.DEBUG) # For this main script's own log messages

    log.info("Starting PyATS Test Execution from __main__ block.")
    # The 'testbed' variable should be loaded at the module level (top of the file)
    # for aetest.main() to pick it up seamlessly when passed as an argument.
    aetest.main(testbed=testbed)