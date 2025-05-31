import json
from typing import Optional

import requests
import urllib3
from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient
from pyats.datastructures import AttrDict
from pyats.topology import Device

"""
  Contributors: Dusca Alexandru, Carina Furmanek
  """
class SwaggerConnector:
    """
    Connector class for interacting with a network device via Swagger (REST API).
    """

    def __init__(self, device: Device, **kwargs) -> None:
        """
        Initializes the SwaggerConnector instance.

        Args:
            device (Device): The pyATS Device object representing the network device.
            **kwargs: Optional keyword arguments (not used).
        """
        self._session = None
        self._auth = None
        self._headers: dict[str, str] = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self._url: Optional[str] = None
        self._url_login: Optional[str] = None
        self.device = device
        self.connection: Optional[AttrDict] = None
        self.api_endpoints: list[str] = []
        self.client: Optional[SwaggerClient] = None
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def connect(self, **kwargs) -> None:
        """
        Establishes a connection to the device and initializes the Swagger client.

        Args:
            **kwargs: Should contain 'connection' details (IP, port, credentials).
        """
        self.connection = kwargs['connection']
        endpoint = '/apispec/ngfw.json'
        self._url = f'https://{self.connection.ip.compressed}:{self.connection.port}'
        self.__login(
            self.connection.credentials.login.username,
            self.connection.credentials.login.password.plaintext
        )
        self._headers.update({'Authorization': f'{self.token_type} {self.access_token}'})
        https_client = RequestsClient()
        https_client.session.verify = False
        https_client.ssl_verify = False
        https_client.session.headers = self._headers
        swagger_client = SwaggerClient.from_url(
            self._url + endpoint,
            http_client=https_client,
            request_headers=self._headers,
            config={'validate_certificate': False, 'validate_responses': False},
        )
        self.client = swagger_client

    def __login(self, username: Optional[str] = None, password: Optional[str] = None) -> None:
        """
        Authenticates to the device and retrieves tokens for API usage.

        Args:
            username (Optional[str]): Username for login.
            password (Optional[str]): Password for login.
        """
        endspoint = '/api/fdm/latest/fdm/token'
        response = requests.post(
            self._url + endspoint,
            verify=False,
            data=json.dumps({'username': username, 'password': password, 'grant_type': 'password'}),
            headers=self._headers
        )
        self.access_token: str = response.json()['access_token']
        self.token_type: str = response.json()['token_type']
        self.refresh_token: str = response.json()['refresh_token']

    def disconnect(self) -> None:
        """
        Disconnects the session (placeholder method).
        """
        pass

    def execute(self, command, **kwargs):
        """
        Executes a command on the device (placeholder method).

        Args:
            command: The command to execute.
            **kwargs: Additional parameters for execution.
        """
        pass

    def configure(self, command, **kwargs):
        """
        Sends configuration data to the device (placeholder method).

        Args:
            command: The configuration command or payload.
            **kwargs: Additional configuration parameters.
        """
        pass

    def is_connected(self) -> bool:
        """
        Checks if the connector is considered connected (placeholder method).

        Returns:
            bool: True if connected, False otherwise.
        """
        pass
