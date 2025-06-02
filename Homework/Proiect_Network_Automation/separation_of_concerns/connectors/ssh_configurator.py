"""
Handles SSH-based device configuration.
"""
import ipaddress
import logging
import re
import time
from ipaddress import IPv4Interface

from pyats.topology import Device
from connectors.ssh_connector import SSHConnector  # Assuming connector is in the same directory

# from netutils.ip import wildcardmask_to_netmask, netmask_to_wildcardmask # Not used here, but good for reference

logger = logging.getLogger(__name__)


class SSHConfigurator:
    """
    Manages device configuration over an SSH connection.
    """

    def __init__(self, device: Device, connector: SSHConnector):
        self.device = device
        self.connector = connector
        # if not self.connector.is_connected():
        #     raise ConnectionError(f"SSH connector for {device.name} is not connected.")

        # Define common prompts based on device OS or type.
        # These are regex patterns.
        self.prompt_map = {
            'default_enabled': r'\S+#\s*$',  # e.g., Router# or firepower#
            'default_config': r'\S+\(config\)#\s*$',  # e.g., Router(config)#
            'config_if': r'\S+\(config-if\)#\s*$',
            'config_router': r'\S+\(config-router\)#\s*$',
            'config_line': r'\S+\(config-line\)#\s*$',
            'dhcp_config': r'\S+\(dhcp-config\)#\s*$',
        }
        self.current_hostname_prompt_base = self.device.custom.get('hostname', self.device.name)

    def _get_prompt(self, mode: str = 'enabled') -> str:
        """Returns the expected prompt regex for the current device context."""
        base_prompt = self.current_hostname_prompt_base
        if mode == 'enabled':
            return fr"{re.escape(base_prompt)}#\s*$"
        elif mode == 'config':
            return fr"{re.escape(base_prompt)}\(config\)#\s*$"
        elif mode == 'config-if':
            return fr"{re.escape(base_prompt)}\(config-if\)#\s*$"
        elif mode == 'config-router':
            return fr"{re.escape(base_prompt)}\(config-router\)#\s*$"
        elif mode == 'config-line':
            return fr"{re.escape(base_prompt)}\(config-line\)#\s*$"
        elif mode == 'dhcp-config':
            return fr"{re.escape(base_prompt)}\(dhcp-config\)#\s*$"
        # Add more modes as needed (e.g., specific to FTD, ASA)

        # Fallback to a generic prompt if mode is unknown for safety, but log it.
        logger.warning(f"Unknown prompt mode '{mode}' for {self.device.name}. Using generic enabled prompt.")
        return fr"\S+#\s*$"

    def _execute_cfg_command(self, command: str, expected_prompt_mode: str = 'config',
                             current_prompt_mode: str = 'config', timeout: float = 10.0,
                             delay_after_send: float = 0.5) -> str:
        """Helper to send a configuration command and verify the prompt."""
        # current_prompt = self._get_prompt(current_prompt_mode) # Not directly used if execute_command_and_wait_for_prompt handles it
        expected_prompt_regex = self._get_prompt(expected_prompt_mode)

        logger.info(f"Sending to {self.device.name}: {command} (expecting mode: {expected_prompt_mode})")

        output = self.connector.execute_command_and_wait_for_prompt(
            command,
            prompt_regex=expected_prompt_regex,
            timeout=timeout,
            initial_delay=delay_after_send
        )

        # Basic error check (can be expanded)
        if "% Invalid input" in output or "% Ambiguous command" in output:
            logger.error(f"Command error on {self.device.name} for '{command}': {output}")
            raise ValueError(f"Configuration command failed on {self.device.name}: {command} - {output}")
        logger.debug(f"Output from {self.device.name} for '{command}':\n{output}")
        return output

    def enter_enable_mode(self, enable_password:[str]= None):
        """Enters enable mode if not already there."""
        # Send a newline to get current prompt
        self.connector.send_command("\n", add_newline=False)  # Just wake it up
        time.sleep(0.5)
        current_output = self.connector.read(max_wait_time=1)

        if re.search(self._get_prompt('enabled'), current_output):
            logger.info(f"{self.device.name} is already in enable mode.")
            return

        # If not in enable mode, try sending 'enable'
        logger.info(f"Entering enable mode on {self.device.name}")
        self.connector.send_command('enable')
        time.sleep(0.5)
        output = self.connector.read(max_wait_time=2)

        if "Password:" in output:
            pw = enable_password
            if not pw and hasattr(self.device.credentials, 'enable') and self.device.credentials.enable:
                pw = self.device.credentials.enable.password.plaintext
            elif not pw and hasattr(self.device.credentials, 'default') and \
                    hasattr(self.device.credentials.default, 'enable_password') and \
                    self.device.credentials.default.enable_password:
                pw = self.device.credentials.default.enable_password.plaintext

            if not pw:
                raise ValueError(
                    f"Enable password required for {self.device.name} but not provided or found in testbed.")
            self.connector.send_command(pw)
            time.sleep(0.5)
            final_output = self.connector.read(max_wait_time=2)
            if not re.search(self._get_prompt('enabled'), final_output):
                raise ConnectionError(
                    f"Failed to enter enable mode on {self.device.name} after sending password. Output: {final_output}")
        elif not re.search(self._get_prompt('enabled'), output):
            # If no password prompt and not in enable mode, something is wrong
            raise ConnectionError(
                f"Failed to enter enable mode on {self.device.name}. No password prompt. Output: {output}")
        logger.info(f"{self.device.name} is now in enable mode.")

    def enter_config_mode(self):
        """Enters global configuration mode from enable mode."""
        self.enter_enable_mode()  # Ensure we are in enable mode first
        logger.info(f"Entering configuration mode on {self.device.name}")
        self._execute_cfg_command('configure terminal', expected_prompt_mode='config', current_prompt_mode='enabled')
        logger.info(f"{self.device.name} is now in configuration mode.")

    def exit_config_mode(self):
        """Exits from global configuration mode to enable mode."""
        logger.info(f"Exiting configuration mode on {self.device.name}")
        self._execute_cfg_command('end', expected_prompt_mode='enabled', current_prompt_mode='config')
        logger.info(f"{self.device.name} is now in enable mode.")

    def configure_hostname(self):
        """Configures the device hostname."""
        hostname = self.device.custom.get('hostname')
        if not hostname:
            logger.info(f"No custom hostname specified for {self.device.name}, skipping hostname configuration.")
            return

        logger.info(f"Configuring hostname to '{hostname}' on {self.device.name}")
        self._execute_cfg_command(f'hostname {hostname}', expected_prompt_mode='config')
        self.current_hostname_prompt_base = hostname  # Update base for future prompt checks
        logger.info(f"Hostname set to '{hostname}' on {self.device.name}. Prompts will now expect this hostname.")

    def configure_interfaces(self):
        """Configures interfaces based on testbed definition."""
        if not self.device.interfaces:
            logger.info(f"No interfaces defined for {self.device.name} in testbed, skipping interface configuration.")
            return

        logger.info(f"Configuring interfaces on {self.device.name}")
        for intf_name, intf_details in self.device.interfaces.items():
            # Skip if interface type is not suitable for IP config (e.g. 'loopback' handled differently)
            # Or if no IP configuration is provided
            if intf_details.type not in ('ethernet', 'gigabitethernet', 'fastethernet'):  # Add other relevant types
                logger.debug(
                    f"Skipping interface {intf_name} (type: {intf_details.type}) for IP configuration on {self.device.name}.")
                continue

            self._execute_cfg_command(f"interface {intf_name}", expected_prompt_mode='config-if')

            if intf_details.ipv4:
                ip_interface = IPv4Interface(f"{intf_details.ipv4.ip}/{intf_details.ipv4.prefixlen}")
                ip_addr = ip_interface.ip.compressed
                mask = ip_interface.netmask.exploded
                logger.info(f"Configuring {intf_name} with IP {ip_addr}/{mask} on {self.device.name}")
                self._execute_cfg_command(f"ip address {ip_addr} {mask}", expected_prompt_mode='config-if')
            elif intf_details.custom.get('dhcp_client', False) or \
                    (hasattr(intf_details,
                             'ip_address_type') and intf_details.ip_address_type == 'dhcp'):  # Check for DHCP client
                logger.info(f"Configuring {intf_name} for DHCP client on {self.device.name}")
                self._execute_cfg_command("ip address dhcp", expected_prompt_mode='config-if')
            else:
                logger.info(
                    f"No static IPv4 or DHCP client configuration for interface {intf_name} on {self.device.name}.")

            if intf_details.custom.get('description'):
                self._execute_cfg_command(f"description {intf_details.custom.description}",
                                          expected_prompt_mode='config-if')

            # Default to 'no shutdown' unless explicitly stated otherwise
            if not intf_details.custom.get('shutdown', False):
                self._execute_cfg_command("no shutdown", expected_prompt_mode='config-if')
            else:
                self._execute_cfg_command("shutdown", expected_prompt_mode='config-if')

            self._execute_cfg_command("exit", expected_prompt_mode='config')  # Exit from interface config
        logger.info(f"Interface configuration finished for {self.device.name}")

    def configure_rip(self):
        """Configures RIP routing protocol."""
        rip_cfg = self.device.custom.get('rip')
        if self.device.type != 'router' or not rip_cfg:
            logger.info(f"RIP configuration skipped for {self.device.name} (not a router or no RIP config).")
            return

        logger.info(f"Configuring RIP on {self.device.name}")
        self._execute_cfg_command("router rip", expected_prompt_mode='config-router')

        if rip_cfg.get('version', 2) == 2:  # Default to version 2 if not specified
            self._execute_cfg_command("version 2", expected_prompt_mode='config-router')

        if rip_cfg.get('no_auto_summary', True):  # Default to 'no auto-summary'
            self._execute_cfg_command("no auto-summary", expected_prompt_mode='config-router')

        for net_str in rip_cfg.get('networks', []):
            try:
                # For RIP, typically network command uses the classful network address if auto-summary is off,
                # or the specific network being advertised.
                # ipaddress.IPv4Network will give the network address directly.
                net = ipaddress.IPv4Network(net_str, strict=False)  # strict=False allows host bits
                self._execute_cfg_command(f"network {net.network_address}", expected_prompt_mode='config-router')
            except ValueError as e:
                logger.error(f"Invalid network string '{net_str}' for RIP on {self.device.name}: {e}")

        for iface in rip_cfg.get('passive-interfaces', []):
            self._execute_cfg_command(f"passive-interface {iface}", expected_prompt_mode='config-router')

        self._execute_cfg_command("exit", expected_prompt_mode='config')  # Exit from router rip config
        logger.info(f"RIP configuration finished for {self.device.name}")

    def configure_ospf(self):
        """Configures OSPF routing protocol."""
        if self.device.type != 'router' or not self.device.custom.get('ospf_enabled'):
            logger.info(f"OSPF configuration skipped for {self.device.name} (not a router or OSPF not enabled).")
            return

        ospf_process_id = self.device.custom.get('ospf_process_id', 1)
        ospf_area = self.device.custom.get('ospf_area', 0)
        router_id = self.device.custom.get('ospf_router_id')  # Optional: usually set from an IP

        logger.info(f"Configuring OSPF process {ospf_process_id} area {ospf_area} on {self.device.name}")
        self._execute_cfg_command(f"router ospf {ospf_process_id}", expected_prompt_mode='config-router')

        if router_id:
            self._execute_cfg_command(f"router-id {router_id}", expected_prompt_mode='config-router')

        # Advertise networks from interfaces configured for OSPF
        ospf_networks = self.device.custom.get('ospf_networks', [])  # Explicit networks to advertise
        if ospf_networks:
            for net_info in ospf_networks:  # Expecting list of dicts: {'address': 'x.x.x.x', 'wildcard': 'y.y.y.y', 'area': Z}
                try:
                    self._execute_cfg_command(
                        f"network {net_info['address']} {net_info['wildcard']} area {net_info.get('area', ospf_area)}",
                        expected_prompt_mode='config-router'
                    )
                except KeyError as e:
                    logger.error(f"Missing key in ospf_networks entry for {self.device.name}: {net_info} - {e}")
        else:  # Fallback: advertise networks of IP-configured interfaces if no explicit list
            logger.info(f"No explicit OSPF networks defined for {self.device.name}, attempting to use interface IPs.")
            for intf in self.device.interfaces.values():
                if hasattr(intf, 'ipv4') and intf.ipv4 and intf.type in ('ethernet', 'gigabitethernet', 'fastethernet',
                                                                         'loopback'):
                    ip_obj: IPv4Interface = IPv4Interface(f"{intf.ipv4.ip}/{intf.ipv4.prefixlen}")
                    network_addr = ip_obj.network.network_address.compressed
                    wildcard_mask = ip_obj.hostmask.exploded  # hostmask is the wildcard mask
                    self._execute_cfg_command(
                        f'network {network_addr} {wildcard_mask} area {ospf_area}',
                        expected_prompt_mode='config-router'
                    )

        passive_interfaces = self.device.custom.get('ospf_passive_interfaces', [])
        for iface_name in passive_interfaces:
            self._execute_cfg_command(f'passive-interface {iface_name}', expected_prompt_mode='config-router')

        self._execute_cfg_command('exit', expected_prompt_mode='config')  # Exit from router ospf config

        # Optional: Show running config for OSPF to verify (can be verbose)
        # self._execute_cfg_command('do show run | section router ospf', expected_prompt_mode='config', delay_after_send=1)
        logger.info(f"OSPF configuration finished for {self.device.name}")

    def configure_dhcp_pools(self):
        """Configures DHCP pools."""
        pools = self.device.custom.get('dhcp_pools', {})
        if not pools:
            logger.info(f"No DHCP pools to configure for {self.device.name}.")
            return

        logger.info(f"Configuring DHCP pools on {self.device.name}")
        for name, pool_data in pools.items():
            try:
                self._execute_cfg_command(f"ip dhcp pool {name}", expected_prompt_mode='dhcp-config')
                net = ipaddress.IPv4Network(pool_data['network'], strict=False)
                self._execute_cfg_command(f"network {net.network_address} {net.netmask}",
                                          expected_prompt_mode='dhcp-config')
                self._execute_cfg_command(f"default-router {pool_data['default_router']}",
                                          expected_prompt_mode='dhcp-config')

                if pool_data.get('domain_name'):
                    self._execute_cfg_command(f"domain-name {pool_data['domain_name']}",
                                              expected_prompt_mode='dhcp-config')
                if pool_data.get('dns_server'):  # Can be multiple, comma or space separated depending on IOS
                    dns_servers = pool_data['dns_server']
                    if isinstance(dns_servers, list):  # If multiple DNS servers are provided as a list
                        for dns_server in dns_servers:
                            self._execute_cfg_command(f"dns-server {dns_server}", expected_prompt_mode='dhcp-config')
                    else:  # Single DNS server
                        self._execute_cfg_command(f"dns-server {dns_servers}", expected_prompt_mode='dhcp-config')

                # Lease time (optional)
                if pool_data.get('lease'):  # e.g., "days hours minutes" or just seconds
                    self._execute_cfg_command(f"lease {pool_data['lease']}", expected_prompt_mode='dhcp-config')

                self._execute_cfg_command("exit", expected_prompt_mode='config')  # Exit from dhcp-config mode

                # Excluded addresses must be configured from global config mode
                for rng in pool_data.get('excluded_address_ranges', []):
                    start_ip = rng.get('start')
                    end_ip = rng.get('end', start_ip)  # If 'end' is not present, exclude single IP
                    if start_ip:
                        self._execute_cfg_command(f"ip dhcp excluded-address {start_ip} {end_ip}",
                                                  expected_prompt_mode='config')
                    else:
                        logger.warning(
                            f"Excluded address range for pool {name} on {self.device.name} missing 'start' IP: {rng}")

            except KeyError as e:
                logger.error(f"DHCP pool '{name}' for {self.device.name} is missing key: {e}")
            except ValueError as e:
                logger.error(f"Invalid network or IP for DHCP pool '{name}' on {self.device.name}: {e}")
        logger.info(f"DHCP pool configuration finished for {self.device.name}")

    def save_config(self):
        """Saves the running configuration to startup-config."""
        logger.info(f"Saving configuration on {self.device.name}")
        # Ensure we are in enable mode, not config mode.
        # self.exit_config_mode() # If called from within a config session.
        # However, 'do write memory' or 'do copy run start' can work from config mode.
        # For simplicity, let's assume it's called after all config is done and we are in enable mode.

        # Standard command is 'write memory' or 'copy running-config startup-config'
        # 'write' is a common alias.
        # Some devices (especially non-Cisco or older Cisco) might just be 'save'

        # Using 'write memory' as it's common and usually works.
        # The prompt after 'write memory' can be just the enable prompt if no changes,
        # or a confirmation prompt.
        self.connector.send_command('write memory')
        time.sleep(1)  # Give it a moment for the command to be processed and output to start

        # Read output, wait for confirmation or prompt.
        # This needs to be robust to different outputs.
        output = ""
        timeout = 20  # seconds for save to complete (e.g., NVRAM write)
        start_time = time.monotonic()
        confirmation_regex = r"\[confirm\]|Continue\? \[no\]:|Building configuration\.\.\.\s*\[OK\]|NVRAM configuration"

        while time.monotonic() - start_time < timeout:
            output += self.connector.read(max_wait_time=0.5)
            if re.search(self._get_prompt('enabled'), output):  # Back to prompt, save likely done
                logger.info(f"Configuration saved (returned to enable prompt) on {self.device.name}.")
                return
            if re.search(confirmation_regex, output, re.IGNORECASE):
                if "confirm" in output.lower() or "continue? [no]:" in output.lower():
                    logger.info(f"Confirmation needed for save on {self.device.name}. Sending 'yes'.")
                    # Send 'yes' or just '\n' if it's the default. '\n' is safer for [confirm]
                    self.connector.send_command('\n')
                    # Wait for it to return to prompt after [OK] or similar messages
                # Continue loop to wait for enable prompt
            time.sleep(0.5)

        # Final check for prompt if loop times out
        if re.search(self._get_prompt('enabled'), output):
            logger.info(f"Configuration saved (found enable prompt after timeout loop) on {self.device.name}.")
        else:
            logger.warning(
                f"Save config on {self.device.name} timed out or did not return to a recognized prompt. Output: {output}")
            # Send a newline to ensure we are at a prompt for next operations
            self.connector.execute_command_and_wait_for_prompt('', self._get_prompt('enabled'), timeout=5)

    def apply_full_configuration(self):
        """Applies a full baseline configuration to an IOS/IOSXE device."""
        if self.device.os not in ('ios', 'iosxe'):
            logger.warning(
                f"Full configuration skipped for {self.device.name} (OS: {self.device.os}) via SSH. Supported: IOS/IOSXE.")
            return

        logger.info(f"Starting full SSH configuration for {self.device.name}")
        try:
            self.enter_config_mode()  # Enters enable, then config mode

            self.configure_hostname()  # Sets hostname, updates internal prompt base
            self.configure_interfaces()

            # Routing protocols
            if self.device.custom.get('rip'):
                self.configure_rip()
            if self.device.custom.get('ospf_enabled'):
                self.configure_ospf()

            # DHCP Services
            if self.device.custom.get('dhcp_pools'):
                self.configure_dhcp_pools()

            # Other common settings can be added here:
            # e.g., banner, AAA, NTP, logging, VTY line config, SSH specific hardening
            # Example: self.configure_vty_lines()
            # Example: self.configure_logging()

            self.exit_config_mode()  # Back to enable mode
            self.save_config()

            logger.info(f"Full SSH configuration completed successfully for {self.device.name}")

        except ConnectionError as e:
            logger.error(f"Connection error during configuration of {self.device.name}: {e}")
            # No re-raise, allow script to continue with other devices if applicable
        except (ValueError, TimeoutError) as e:  # Errors from command execution or validation
            logger.error(f"Configuration error on {self.device.name}: {e}")
            # Attempt to gracefully exit config mode if possible, then re-raise or handle
            try:
                # Try to get back to a known state (enable prompt)
                self.connector.send_command('end\n')  # Send 'end'
                time.sleep(1)
                self.connector.read()  # Clear buffer
                self.connector.execute_command_and_wait_for_prompt('', self._get_prompt('enabled'), timeout=5)
            except Exception as cleanup_err:
                logger.error(f"Failed to return to enable prompt on {self.device.name} after error: {cleanup_err}")
            # self.failed() or let aetest handle it based on where this is called
        except Exception as e:
            logger.error(f"An unexpected error occurred during SSH configuration of {self.device.name}: {e}",
                         exc_info=True)
            # Similar cleanup attempt
            try:
                self.connector.send_command('end\n')
                time.sleep(1)
                self.connector.read()
                self.connector.execute_command_and_wait_for_prompt('', self._get_prompt('enabled'), timeout=5)
            except Exception as cleanup_err:
                logger.error(
                    f"Failed to return to enable prompt on {self.device.name} after unexpected error: {cleanup_err}")