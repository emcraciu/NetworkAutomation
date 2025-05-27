"""
Manages REST connection via Swagger
"""
import json
from typing import Optional

import requests
import urllib3
from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient
from pyats.datastructures import AttrDict
from pyats.topology import Device



class SwaggerConnector:
    """
    Manages Swagger REST connection
    """
    def __init__(self, device: Device):
        self._session = None
        self._auth = None
        self._headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        self._url = None
        self._url_login = None
        self.device = device
        self.connection: Optional[AttrDict] = None
        self.api_endpoints: list[str] = []
        self.client: Optional[SwaggerClient] = None
        self.refresh_token: Optional[str] = None
        self.access_token: Optional[str] = None
        self.token_type: Optional[str] = None

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def connect(self, **kwargs):
        """
        Establish connection to Swagger API.
        Args:
            connection(pyats.Connection): The rest connection
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

    def __login(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Login to Swagger API by sending POST on token endpoint. Stores token in self.access_token.
        """
        endpoint = '/api/fdm/latest/fdm/token'
        response = requests.post(
            self._url + endpoint,
            verify=False,
            data=json.dumps({'username': username, 'password': password, 'grant_type': 'password'}),
            headers=self._headers,
            timeout=60
        )
        self.access_token = response.json()['access_token']
        self.token_type = response.json()['token_type']
        self.refresh_token = response.json()['refresh_token']


    def disconnect(self):
        """
        Terminate connection.
        """

    def execute(self, command, **kwargs):
        """
        Executes a command
        """

    def configure(self, command, **kwargs):
        """
        Configures the device
        """

    def is_connected(self):
        """
        Returns connection status.
        """
