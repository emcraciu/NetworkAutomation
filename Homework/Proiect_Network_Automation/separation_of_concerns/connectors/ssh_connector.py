"""
Manages an SSH connection using Paramiko.
"""
import logging
import re
import socket
import time
from typing import Optional

import paramiko
from paramiko import SSHClient, AutoAddPolicy, SSHException, ChannelException, \
    Transport  # Added ChannelException & Transport
from pyats.topology import Device

logger = logging.getLogger(__name__)


class SSHConnector:
    """
    Manages an SSH connection to a device.
    Handles basic command sending and output reading.
    """

    def __init__(self, device: Device):
        self.device = device
        self._ssh = SSHClient()
        self._ssh.set_missing_host_key_policy(AutoAddPolicy())
        self._shell: Optional[paramiko.Channel] = None  # Type hint for shell
        self.connection_details = None

    def connect(self, **kwargs):
        """
        Connects to the device using SSH.
        Expects 'connection' in kwargs.
        """
        self.connection_details = kwargs['connection']
        conn_params = self.connection_details

        hostname = conn_params.ip.compressed
        port = conn_params.get('port', 22)  # Use .get for port with default
        username = conn_params.credentials.login.username
        password = conn_params.credentials.login.password.plaintext

        # Standard Cisco KEX algorithms (older devices might need some of these)
        # Order can matter. Start with more secure/modern ones.
        preferred_kex = [
            'diffie-hellman-group-exchange-sha256',  # Common and secure
            'diffie-hellman-group14-sha256',  # RFC 5656
            'diffie-hellman-group16-sha512',  # Stronger
            'diffie-hellman-group14-sha1',  # Older but widely supported
            # 'diffie-hellman-group1-sha1',          # Very old, use as last resort
        ]

        # Disabled algorithms from your original code (modern ones)
        # This is unusual; typically, you disable *weak* algorithms.
        # If you are connecting to very old devices, they might *not* support these.
        # For modern devices, you'd want these *enabled*.
        # For now, retaining your list but this might need adjustment based on target devices.
        disabled_kex_by_user = [
            "curve25519-sha256",
            "curve25519-sha256@libssh.org",
            "ecdh-sha2-nistp256",
            "ecdh-sha2-nistp384",
            "ecdh-sha2-nistp521",
        ]

        logger.info(f"Attempting SSH connection to {hostname}:{port} as {username}")

        try:
            self._ssh.connect(
                hostname=hostname,
                port=port,
                username=username,
                password=password,
                look_for_keys=False,
                allow_agent=False,
                timeout=kwargs.get('timeout', 20),  # Connection timeout
                # Kex negotiation can be tricky. Paramiko tries to auto-negotiate.
                # If issues persist, you might need to explicitly set kex, ciphers, etc.
                # disabled_algorithms={'kex': disabled_kex_by_user} # Your original setting
                # Try connecting without disabling first, or provide a specific KEX list.
            )

            # If connect worked, try to set a specific KEX if required for older devices
            # This needs to be done *before* invoke_shell typically, via Transport
            # Forcing KEX after connection is not standard for client.
            # transport = self._ssh.get_transport()
            # if transport:
            #     # transport.get_security_options().kex = preferred_kex # Example
            #     pass

            self._shell = self._ssh.invoke_shell()
            self._shell.settimeout(kwargs.get('shell_timeout', 10))  # Timeout for shell operations

            # Clear initial banner/output
            time.sleep(1)  # Give shell time to send banner
            self.read(max_wait_time=2)  # Read with a timeout
            logger.info(f"Successfully connected to {self.device.name} via SSH and shell invoked.")

        except SSHException as e:
            logger.error(f"SSH connection to {self.device.name} ({hostname}) failed: {e}")
            # Attempt to get more KEX negotiation details if possible (advanced)
            if "Unable to agree on key exchange algorithm" in str(e) and self.device.os in ('ios', 'iosxe'):
                logger.warning(f"KEX algorithm mismatch for {self.device.name}. "
                               f"Consider enabling 'ip ssh server algorithm kex diffie-hellman-group-exchange-sha1 diffie-hellman-group14-sha1' on the Cisco device "
                               f"or adjust client-side KEX preferences.")
            self._ssh.close()  # Ensure client is closed on failure
            raise ConnectionError(f"Failed to connect to {self.device.name} via SSH: {e}") from e
        except Exception as e:  # Catch other potential errors like socket errors
            logger.error(f"An unexpected error occurred during SSH connection to {self.device.name} ({hostname}): {e}")
            if self._ssh: self._ssh.close()
            raise ConnectionError(f"Unexpected error connecting to {self.device.name}: {e}") from e

    def send_command(self, cmd: str, add_newline: bool = True, encoding: str = 'utf-8'):
        """Sends a command string to the shell."""
        if not self._shell or self._shell.closed:
            raise ConnectionError(f"SSH shell for {self.device.name} is not active.")
        logger.debug(f"Sending to {self.device.name}: {cmd.strip()}")
        payload = cmd.encode(encoding)
        if add_newline:
            payload += b'\n'
        try:
            self._shell.sendall(payload)
        except Exception as e:
            logger.error(f"Error sending command '{cmd}' to {self.device.name}: {e}")
            raise IOError(f"Failed to send command to {self.device.name}") from e

    def read(self, buffer_size: int = 65535, encoding: str = 'utf-8', errors: str = 'ignore',
             max_wait_time: float = 1.0, min_bytes: int = 1) -> str:
        """
        Reads available data from the shell with non-blocking checks and a timeout.
        """
        if not self._shell or self._shell.closed:
            # logger.warning(f"Attempted to read from a closed or non-existent shell for {self.device.name}.")
            return ""

        output_buffer = b""
        start_time = time.monotonic()

        # Initial read attempt
        if self._shell.recv_ready():
            try:
                data = self._shell.recv(buffer_size)
                if data:
                    output_buffer += data
            except (socket.timeout, ChannelException) as e:  # Paramiko raises ChannelException on timeout for recv
                logger.debug(f"Socket/Channel timeout during initial read on {self.device.name}: {e}")
                # This is okay, it means no data was immediately ready within shell's own timeout
            except Exception as e:
                logger.error(f"Error during initial read from {self.device.name}: {e}")
                return output_buffer.decode(encoding, errors=errors)  # Return what we have

        # Wait for more data if needed, up to max_wait_time
        while time.monotonic() - start_time < max_wait_time:
            if self._shell.recv_ready():
                try:
                    data = self._shell.recv(buffer_size)
                    if not data and output_buffer:  # Connection closed by peer while data was present
                        logger.warning(f"SSH connection to {self.device.name} closed by peer during read.")
                        break
                    output_buffer += data
                except (socket.timeout, ChannelException) as e:
                    logger.debug(f"Socket/Channel timeout during polling read on {self.device.name}: {e}")
                    break  # No more data within this poll cycle's timeout
                except Exception as e:
                    logger.error(f"Error during polling read from {self.device.name}: {e}")
                    break  # Stop on error
            elif len(output_buffer) >= min_bytes and not self._shell.recv_ready():
                # If we have some data and nothing more is immediately available, break
                break
            time.sleep(0.1)  # Short pause before checking recv_ready again

        decoded_output = output_buffer.decode(encoding, errors=errors)
        # logger.debug(f"Read from {self.device.name}: {decoded_output[:200]}") # Log snippet
        return decoded_output

    def execute_command_and_wait_for_prompt(self, command: str, prompt_regex: str, timeout: float = 10.0,
                                            initial_delay: float = 0.5, attempt_interval: float = 0.5) -> str:
        """
        Sends a command and reads output until a specific prompt regex is matched or timeout.
        """
        if not self._shell or self._shell.closed:
            raise ConnectionError(f"SSH shell for {self.device.name} is not active.")

        logger.info(f"Executing on {self.device.name} (waiting for '{prompt_regex}'): {command}")
        self.send_command(command)

        # Optional delay after sending command, before starting to read
        if initial_delay > 0:
            time.sleep(initial_delay)

        output = ""
        start_time = time.monotonic()

        while time.monotonic() - start_time < timeout:
            output += self.read(max_wait_time=0.2)  # Read small chunks frequently
            if re.search(prompt_regex, output, re.MULTILINE):  # re.MULTILINE for prompts at start of new lines
                logger.debug(f"Prompt '{prompt_regex}' found on {self.device.name}.")
                # Remove command from output if it was echoed and prompt is at end
                # This is a common behavior.
                command_echo_pattern = re.escape(command.strip()) + r'.*?\n'
                output_cleaned = re.sub(command_echo_pattern, '', output, count=1)
                return output_cleaned

            # Check for common error indicators
            if "% Incomplete command" in output or "% Ambiguous command" in output or "% Invalid input detected" in output:
                logger.error(f"Command error detected for '{command}' on {self.device.name}:\n{output}")
                raise ValueError(f"Command error on {self.device.name}: {output}")

            time.sleep(attempt_interval)  # Wait before next read attempt

        logger.error(
            f"Timeout waiting for prompt '{prompt_regex}' after command '{command}' on {self.device.name}. Full output:\n{output}")
        raise TimeoutError(f"Timeout waiting for prompt '{prompt_regex}' on {self.device.name}. Output: {output}")

    def is_connected(self) -> bool:
        """
        Checks if the SSH transport is active and shell is not closed.
        """
        if not self._ssh or not self._ssh.get_transport():
            return False
        transport_active = self._ssh.get_transport().is_active()
        shell_open = self._shell and not self._shell.closed
        return transport_active and shell_open

    def disconnect(self):
        """Closes the SSH connection and shell."""
        logger.info(f"Disconnecting SSH from {self.device.name}")
        if self._shell and not self._shell.closed:
            try:
                self._shell.close()
            except Exception as e:
                logger.warning(f"Error closing SSH shell for {self.device.name}: {e}")
        if self._ssh:
            try:
                self._ssh.close()
            except Exception as e:
                logger.warning(f"Error closing SSH client for {self.device.name}: {e}")
        self._shell = None
        self.connection_details = None