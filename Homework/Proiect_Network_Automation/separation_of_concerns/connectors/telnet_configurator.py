"""
Handles Telnet-based device configuration.
"""
import ipaddress
import logging
import re
import time

from pyats.topology import Device
from connectors.telnet_connector import TelnetConnector  # Assuming connector is in the same directory

logger = logging.getLogger(__name__)


class TelnetConfigurator:
    """
    Manages device configuration over a Telnet connection.
    """

    def __init__(self, device: Device, connector: TelnetConnector):
        self.device = device
        self.connector = connector
        if not self.connector.is_connected():
            raise ConnectionError(f"Telnet connector for {device.name} is not connected.")

    def execute_command(self, command: str, prompt: list[str], timeout= None,
                        read_timeout= None) -> str:
        """
        Sends a command and waits for one of the prompt patterns.
        'timeout' is for the expect operation.
        'read_timeout' is an optional sleep after writing the command.
        """
        logger.info(f"Executing on {self.device.name}: {command}")
        self.connector.write(command)
        if read_timeout:
            time.sleep(read_timeout)

        index, _, output = self.connector.expect(prompt, timeout=timeout)
        if index == -1:  # No prompt matched
            raise TimeoutError(
                f"Expected prompt {prompt} not found for command '{command}' on {self.device.name}. Output: {output}")
        logger.debug(f"Output from {self.device.name} for '{command}':\n{output}")
        return output

    def contains(self, patterns: list[str]) -> bool:
        """
        Checks if any of the given patterns appear in immediate output.
        """
        out = self.connector.read()
        return any(p in out for p in patterns)

    def configure_initial_interface(self):
        """Configures the initial interface with IP address and brings it up"""
        configured_one = False
        for iface_name, interface in self.device.interfaces.items():
            if interface.type != 'ethernet' or not interface.ipv4:
                continue

            ip = interface.ipv4.ip.compressed
            mask = interface.ipv4.network.netmask.exploded

            logger.info(f"Configuring interface {iface_name} with IP {ip} {mask} on {self.device.name}")
            self.execute_command(f'interface {iface_name}', prompt=[r'\(config-if\)#'])
            self.execute_command(f'ip address {ip} {mask}', prompt=[r'\(config-if\)#'])
            self.execute_command('no shutdown', prompt=[r'\(config-if\)#'])
            self.execute_command('exit', prompt=[r'\(config\)#'])
            configured_one = True

        if not configured_one:
            logger.warning(f"No suitable Ethernet interface found for initial IP configuration on {self.device.name}.")

    def configure_ssh(self):
        """Enables SSH access with local login"""
        if not hasattr(self.device.connections, 'ssh') or \
                not hasattr(self.device.connections.ssh, 'credentials') or \
                not hasattr(self.device.connections.ssh.credentials, 'login'):
            logger.error(f"SSH credentials not found for {self.device.name}. Skipping SSH configuration.")
            return

        username = self.device.connections.ssh.credentials.login.username
        password = self.device.connections.ssh.credentials.login.password.plaintext

        logger.info(f"Configuring SSH on {self.device.name} for user {username}")
        self.execute_command('ip ssh version 2', prompt=[r'\(config\)#'])
        self.execute_command(f'username {username} privilege 15 secret {password}', prompt=[r'\(config\)#'])
        self.execute_command('ip domain name cisco.com', prompt=[r'\(config\)#'])  # Consider making domain configurable
        self.execute_command('crypto key generate rsa modulus 2048', prompt=[r'\(config\)#'],
                             read_timeout=15)  # Keys can take time
        self.execute_command('line vty 0 4', prompt=[r'\(config-line\)#'])
        self.execute_command('transport input ssh', prompt=[r'\(config-line\)#'])
        self.execute_command('login local', prompt=[r'\(config-line\)#'])
        self.execute_command('exit', prompt=[r'\(config\)#'])

    def configure_ftd(self):
        """Goes through the initial FTD setup wizard."""
        creds = self.device.credentials
        # Ensure Management0/0 and its ipv4 attribute exist
        if 'Management0/0' not in self.device.interfaces or not self.device.interfaces['Management0/0'].ipv4:
            logger.error(
                f"Management0/0 interface or its IPv4 configuration is missing for FTD device {self.device.name}. Skipping FTD setup.")
            return

        mgmt_interface = self.device.interfaces['Management0/0'].ipv4
        mgmt_ip, mask = mgmt_interface.ip.compressed, mgmt_interface.network.netmask.exploded

        # Ensure custom attributes exist
        if 'management_gateway' not in self.device.custom or \
                'dns' not in self.device.custom or \
                'domain' not in self.device.custom:
            logger.error(
                f"Custom attributes (management_gateway, dns, domain) missing for FTD device {self.device.name}. Skipping FTD setup.")
            return

        gateway = ipaddress.ip_address(self.device.custom['management_gateway']).compressed
        dns = ipaddress.ip_address(self.device.custom['dns']).compressed
        domain = self.device.custom['domain']

        logger.info(f"Starting FTD initial setup for {self.device.name}")
        self.connector.write('\n\r')
        time.sleep(2)
        out = self.connector.read()

        if re.search(r'(FTD|firepower) login:|Password:', out, re.IGNORECASE):
            logger.info("Attempting FTD login")
            if 'Password:' in out:  # Already at password prompt
                # Try sending newline to see if it asks for username, or directly enter password
                self.connector.write('\n')
                time.sleep(0.5)
                out_after_enter = self.connector.read()
                if re.search(r'(FTD|firepower) login:', out_after_enter, re.IGNORECASE):
                    self.connector.write(creds.default.username)
                else:  # Assume it's still asking for password from a previous attempt
                    self.connector.write(creds.default.password.plaintext)  # Use default password first
            else:  # At username prompt
                self.connector.write(creds.default.username)

            time.sleep(1)  # Wait for password prompt
            self.connector.read()  # Clear buffer
            self.connector.write(creds.default.password.plaintext)
            time.sleep(3)  # Wait for login result or next prompt
            out = self.connector.read()

            if 'Login incorrect' in out:
                logger.error(f"FTD default credentials failed for {self.device.name}.")
                return

            # Check if password change is required
            if 'You must change your password' in out or 'Enter new password:' in out:
                logger.info(f"FTD requires password change for {self.device.name}.")
                new_password = creds.login.password.plaintext
                self.connector.write(new_password)  # New password
                time.sleep(0.5);
                self.connector.read()
                self.connector.write(new_password)  # Confirm new password
                time.sleep(5)
                out = self.connector.read()  # Read output after password change attempt

        if any(k in out for k in ['Press <ENTER>', 'AGREE to EULA', '--More--']):
            logger.info(f"Proceeding through FTD setup wizard for {self.device.name}")
            # Handle EULA / --More--
            max_eula_scrolls = 20
            eula_agreed = False
            for _ in range(max_eula_scrolls):
                if 'AGREE to EULA' in out:
                    self.execute_command('YES', prompt=[
                        r'Enter new password:|configure manager locally\?'])  # May go to password or other prompts
                    eula_agreed = True
                    break
                self.connector.write_raw(' ')  # Send space for --More--
                time.sleep(0.3)
                out += self.connector.read()  # Accumulate output

            if not eula_agreed and 'AGREE to EULA' in out:  # Final check if loop ended before YES
                self.execute_command('YES', prompt=[r'Enter new password:|configure manager locally\?'])

            # If it asks for password again (after EULA or if initial default didn't lead to change)
            # This part can be tricky as the prompt order varies.
            current_output = self.connector.read()  # Get fresh output
            if 'Enter new password:' in current_output:
                self.execute_command(creds.login.password.plaintext, prompt=[r'Confirm new password:'])
                self.execute_command(creds.login.password.plaintext, prompt=[r'IPv4\? \(y/n\) \[y\]:'])

            cmds = [
                ('y', r'IPv6\? \(y/n\) \[n\]:'),
                ('n', r'\(dhcp\/manual\) \[manual\]:'),
                ('manual', r'management interface \[.*?\]:'),
                (mgmt_ip, r'netmask for the management interface \[.*?\]:'),
                (mask, r'gateway for the management interface \[.*?\]:'),
                (gateway, r'fully qualified hostname for this system \[.*?\]:'),
                (self.device.custom.get('hostname', 'firepower'),
                 r'comma-separated list of DNS servers or \'none\' \[.*?\]:'),
                (dns, r'comma-separated list of search domains or \'none\' \[.*?\]:'),
                (domain, r'Manage the device locally\? \(yes\/no\) \[yes\]:')
            ]
            for cmd_to_send, expected_prompt in cmds:
                self.execute_command(cmd_to_send, prompt=[expected_prompt])

            self.connector.write('yes')  # For "Manage the device locally?"

            # Wait for setup to finish and prompt to appear (e.g., 'firepower>')
            logger.info(f"Waiting for FTD ({self.device.name}) setup to complete...")
            for _ in range(20):  # Increased timeout/retries
                time.sleep(3)
                output_after_setup = self.connector.read()
                if '>' in output_after_setup or '#' in output_after_setup:  # Common FTD/ASA prompts
                    logger.info(f"FTD setup completed for {self.device.name}.")
                    return
                logger.debug(f"FTD setup still in progress... Read: {output_after_setup[:100]}")

            logger.error(f"FTD setup timed out for {self.device.name}.")
        elif 'Login incorrect' in out and not (
                'You must change your password' in out or 'Enter new password:' in out):  # Ensure it's not a password change prompt
            logger.error(f"FTD default credentials failed for {self.device.name}.")
        else:
            logger.info(
                f"FTD {self.device.name} does not seem to be in initial setup wizard state or login failed. Current output snippet: {out[:200]}")

    def configure_scp_server(self):
        """Enables the SCP server"""
        logger.info(f"Enabling SCP server on {self.device.name}")
        self.execute_command('ip scp server enable', prompt=[r'\(config\)#'])

    def enable_secret(self):
        """Sets the enable secret password"""
        if not hasattr(self.device.credentials, 'default') or \
                not hasattr(self.device.credentials.default, 'password') or \
                not self.device.credentials.default.password:
            logger.warning(f"Enable secret password not defined for {self.device.name}. Skipping.")
            return

        enable_pass = self.device.credentials.default.password.plaintext
        logger.info(f"Setting enable secret on {self.device.name}")
        self.execute_command(f'enable secret {enable_pass}', prompt=[r'\(config\)#'])

    def save_config(self):
        """Saves the running configuration"""
        logger.info(f"Saving configuration on {self.device.name}")
        self.execute_command('end', prompt=[r'\w+#'])
        self.connector.write('write memory')  # write memory might not have a prompt always
        time.sleep(1)  # Give it a moment
        output = self.connector.read()

        # Cisco devices might ask for confirmation, especially if no changes.
        # Some devices just return to prompt. Others might show "Building configuration..."
        # This needs to be robust.
        confirm_patterns = [r'\[confirm\]', r'Continue\? \[no\]:', r'\w+#']  # Add device prompt as a success case

        if any(re.search(p, output, re.IGNORECASE) for p in [r'\[confirm\]', r'Continue\? \[no\]:']):
            logger.info(f"Confirmation required for save on {self.device.name}. Sending 'yes'.")
            # Using execute_command here might be problematic if the prompt isn't standard config
            self.connector.write('yes\n')
            time.sleep(3)  # Wait for save to complete
            self.connector.read()  # Clear any output from save
        elif r'\w+#' not in output:  # If no confirm prompt and no standard prompt, wait a bit
            time.sleep(5)  # Wait longer if building configuration
            self.connector.read()  # Clear "Building configuration..." etc.

        # Ensure we are back at the privileged exec prompt
        self.execute_command('', prompt=[r'\w+#'])  # Send a blank line to confirm prompt
        logger.info(f"Configuration saved on {self.device.name}")

    def configure_routes(self):
        """Configures static routes"""
        if not self.device.custom.get('routes'):
            logger.info(f"No static routes to configure for {self.device.name}")
            return

        logger.info(f"Configuring static routes on {self.device.name}")
        for route_name, route_details in self.device.custom['routes'].items():
            try:
                net = ipaddress.IPv4Network(route_details['network'])
                via = route_details['via']
                # Metric is optional, default to 1 if not specified, or handle device-specific defaults
                metric = route_details.get('metric', 150 if self.device.os in ('ios', 'iosxe') else 1)
                command = f"ip route {net.network_address} {net.netmask} {via}"
                if metric:  # Some OS might not use metric or have it as optional part of command
                    command += f" {metric}"
                logger.info(f"Adding route: {command} on {self.device.name} ({route_name})")
                self.execute_command(command, prompt=[r'\(config\)#'])
            except KeyError as e:
                logger.error(f"Route '{route_name}' for {self.device.name} is missing key: {e}")
            except ValueError as e:
                logger.error(f"Invalid network or IP for route '{route_name}' on {self.device.name}: {e}")

    def do_initial_config(self):
        """Performs initial setup for IOS/IOS-XE devices"""
        if self.device.os not in ('ios', 'iosxe'):
            logger.info(f"Device {self.device.name} is os '{self.device.os}', skipping IOS/IOSXE initial config.")
            return

        logger.info(f"Performing initial IOS/IOSXE configuration for {self.device.name}")

        # Wake up the console, ensure at user exec mode >
        self.connector.write('\r\n')
        time.sleep(1)
        initial_output = self.connector.read()

        # Check if already in enable mode or config mode
        if r'\w+#' in initial_output:  # Already in enable mode
            logger.info(f"{self.device.name} already in enable mode.")
        elif r'\(config\)' in initial_output:  # Already in config mode
            logger.info(f"{self.device.name} already in config mode.")
            self.execute_command('end', prompt=[r'\w+#'])  # Go to enable mode to be consistent
        else:  # Attempt to enter enable mode
            self.connector.write('en\r\n')
            time.sleep(0.5)
            out = self.connector.read()
            if 'Password:' in out:
                if not hasattr(self.device.credentials, 'default') or \
                        not hasattr(self.device.credentials.default, 'password') or \
                        not self.device.credentials.default.password:
                    logger.error(
                        f"Enable password requested for {self.device.name} but not defined. Cannot proceed with initial config.")
                    raise ValueError(f"Enable password for {self.device.name} not defined.")
                enable_pass = self.device.credentials.default.password.plaintext
                self.execute_command(enable_pass, prompt=[r'\w+#'])
            elif not re.search(r'\w+#', out):  # if 'en' didn't result in '#' and no password prompt
                # Try sending another newline, sometimes initial 'en' is missed
                self.execute_command('\r\n', prompt=[r'\w+#'], timeout=5)

        # Enter global configuration mode
        self.execute_command('configure terminal', prompt=[r'\(config\)#'])

        # Set hostname
        if self.device.custom.get('hostname'):
            self.execute_command(f'hostname {self.device.custom.hostname}',
                                 prompt=[fr'{self.device.custom.hostname}\(config\)#|config'])  # Prompt might change
        else:
            logger.warning(f"No custom hostname defined for {self.device.name}.")

        self.configure_initial_interface()
        self.configure_routes()  # If any static routes are needed early
        self.configure_ssh()

        # self.configure_scp_server() # Uncomment if needed by default

        # IOU devices (often Cisco IOL) might require 'enable secret' if not set by default image
        if self.device.platform == 'iou' or 'iou' in self.device.name.lower() or \
                (hasattr(self.device, 'type') and 'iou' in self.device.type.lower()):
            self.enable_secret()

        self.save_config()
        logger.info(f"Initial IOS/IOSXE configuration completed for {self.device.name}")