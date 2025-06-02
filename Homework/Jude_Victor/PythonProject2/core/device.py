# core/device.py

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class NetworkDevice:
    """
    Reprezintă un dispozitiv de rețea și gestionează conexiunile și configurările acestuia.
    Contributors: Dusca Alexandru, Furmanek Carina, Jude Victor, Ivaschescu Gabriel

    """

    def __init__(self, name: str, device_info: dict):
        """
        Inițializează obiectul NetworkDevice.

        Args:
            name (str): Numele dispozitivului.
            device_info (dict): Dicționar cu detalii despre dispozitiv, inclusiv OS, tip, credențiale și conexiuni.
        """
        self.name: str = name
        self.os: Optional[str] = device_info.get('os')
        self.device_type: Optional[str] = device_info.get('type')
        self.credentials: dict = device_info.get('credentials', {})
        self.connection_params: dict = device_info.get('connections', {})
        self.connector: Optional[object] = None
        self.is_connected: bool = False

    def connect(self, protocol: str = 'cli') -> bool:
        """
        Creează o conexiune către dispozitiv folosind protocolul specificat.

        Args:
            protocol (str): Protocolul de conexiune (ex: 'telnet', 'ssh', 'cli').

        Returns:
            bool: True dacă conexiunea a fost realizată cu succes, altfel False.
        """
        if self.is_connected:
            logger.info(f"{self.name}: Already connected.")
            return True

        conn_params = self.connection_params.get(protocol)
        if not conn_params:
            logger.error(f"{self.name}: No connection parameters found for protocol '{protocol}'.")
            return False

        connector_class_str = conn_params.get('class')

        try:
            module_name, class_name = connector_class_str.rsplit('.', 1)
            ConnectorModule = __import__(module_name, fromlist=[class_name])
            ConnectorClass = getattr(ConnectorModule, class_name)

            self.connector = ConnectorClass(
                host=conn_params.get('ip'),
                port=conn_params.get('port'),
                username=self.credentials.get('default', {}).get('username') or conn_params.get('credentials', {}).get('login', {}).get('username'),
                password=self.credentials.get('default', {}).get('password') or conn_params.get('credentials', {}).get('login', {}).get('password'),
                enable_password=self.credentials.get('enable', {}).get('password')
            )
            logger.info(f"{self.name}: Attempting to connect via {protocol} using {connector_class_str}...")

            if self.connector.connect():
                self.is_connected = True
                logger.info(f"{self.name}: Connected successfully via {protocol}.")
                return True
            else:
                logger.error(f"{self.name}: Connection failed via {protocol}.")
                self.connector = None
                return False

        except Exception as e:
            logger.error(f"{self.name}: Error instantiating or using connector {connector_class_str}: {e}")
            self.connector = None
            return False

    def disconnect(self) -> None:
        """
        Deconectează dispozitivul curent dacă este conectat.
        """
        if self.connector and self.is_connected:
            logger.info(f"{self.name}: Disconnecting...")
            self.connector.disconnect()
            self.is_connected = False
            self.connector = None
            logger.info(f"{self.name}: Disconnected.")
        else:
            logger.info(f"{self.name}: Not connected or no active connector.")

    def send_command(self, command: str, expect_string: Optional[str] = None) -> str:
        """
        Trimite o comandă către dispozitivul conectat.

        Args:
            command (str): Comanda de trimis.
            expect_string (Optional[str]): String de așteptat în output (dacă este necesar).

        Returns:
            str: Răspunsul primit de la dispozitiv.
        """
        if not self.is_connected or not self.connector:
            logger.error(f"{self.name}: Not connected. Cannot send command.")
            return ""

        try:
            logger.debug(f"{self.name}: Sending command: {command}")
            output = self.connector.send_command(command, expect_string=expect_string)
            logger.debug(f"{self.name}: Received output:\n{output}")
            return output
        except Exception as e:
            logger.error(f"{self.name}: Error sending command '{command}': {e}")
            return ""

    def configure(self, config_commands: list[str]) -> str:
        """
        Trimite o listă de comenzi de configurare către dispozitiv.

        Args:
            config_commands (list[str]): Lista de comenzi de configurare.

        Returns:
            str: Output-ul rezultat al configurării.
        """
        if not self.is_connected or not self.connector:
            logger.error(f"{self.name}: Not connected. Cannot send configuration.")
            return ""

        if hasattr(self.connector, 'send_config_set'):
            try:
                logger.info(f"{self.name}: Sending configuration set...")
                output = self.connector.send_config_set(config_commands)
                logger.debug(f"{self.name}: Config output:\n{output}")
                return output
            except Exception as e:
                logger.error(f"{self.name}: Error sending config set: {e}")
                return ""
        else:
            all_output = []
            for cmd in config_commands:
                all_output.append(self.send_command(cmd))
            return "\n".join(all_output)

    def __del__(self):
        """
        Destructor: deconectează automat dispozitivul dacă este conectat.
        """
        self.disconnect()
