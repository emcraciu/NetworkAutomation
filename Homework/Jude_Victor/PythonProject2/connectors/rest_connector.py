import re
import requests
from requests.auth import HTTPBasicAuth
import json
import urllib3
from typing import Optional, Any

from pyats.datastructures import AttrDict
from pyats.topology import Device

"""
   Contributors: Dusca Alexandru, Furmanek Carina, Jude Victor, Ivaschescu Gabriel
"""

class RESTConnector:
    """
    Connector class for managing RESTCONF communication with a network device.
    """

    def __init__(self, device: Device, **kwargs):
        """
        Initialize the RESTConnector instance.

        Args:
            device (Device): pyATS device object.
            **kwargs: Additional keyword arguments (not used explicitly here).
        """
        self._session: Optional[Any] = None
        self._auth: Optional[HTTPBasicAuth] = None
        self._headers: Optional[dict[str, str]] = None
        self._url: Optional[str] = None
        self.device: Device = device
        self.connection: Optional[AttrDict] = None
        self.api_endpoints: Optional[list[str]] = None
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def connect(self, **kwargs) -> None:
        """
        Establish a REST connection to the device using Basic Auth.

        Expected kwargs:
            - connection: AttrDict with IP and port.
            - username: Username for authentication.
            - password: Password for authentication.
        """
        self.connection = kwargs['connection']
        self._auth = HTTPBasicAuth(kwargs['username'], kwargs['password'])
        self._headers = {
            'Content-Type': 'application/yang-data+json',
            'Accept': 'application/yang-data+json',
        }
        self._url = f'https://{self.connection.ip.compressed}:{self.connection.port}'

    def get_interface(self, interface_name: str) -> Optional[AttrDict]:
        """
        Retrieve information about a specific interface using RESTCONF.

        Args:
            interface_name (str): Name of the interface to query.

        Returns:
            Optional[AttrDict]: Parsed JSON response from the device.
        """
        endpoint = f'/restconf/data/ietf-interfaces:interfaces/interface={interface_name}'
        url = self._url + endpoint
        response = requests.get(url, auth=self._auth, headers=self._headers, verify=False)
        return response.json()

    def get_netconf_capabilities(self) -> None:
        """
        Retrieve the NETCONF capabilities advertised by the device.
        """
        netconf = '/restconf/data/netconf-state/capabilities'
        url = self._url + netconf
        response = requests.get(url, auth=self._auth, headers=self._headers, verify=False)
        self.netconf_capabilities = response.json().get(
            'ietf-netconf-monitoring:capabilities', {}
        ).get('capability', [])

    def get_restconf_capabilities(self) -> None:
        """
        Retrieve the RESTCONF capabilities advertised by the device.
        """
        restconf = '/restconf/data/ietf-yang-library:modules-state'
        url = self._url + restconf
        response = requests.get(url, auth=self._auth, headers=self._headers, verify=False)
        self.resconf_capabilities = self.__extract_endpoints(response.json())

    def get_api_endpoint(self, url: str) -> None:
        """
        Download and extract container names from a YANG schema available at the given URL.

        Args:
            url (str): The full URL of the YANG schema.
        """
        response = requests.get(url, auth=self._auth, headers=self._headers, verify=False)
        with open(f"{url.split('/')[-2]}.yang", 'w') as file:
            file.write(response.text)
        text = response.text
        pattern = r'container\s(\w+) \{'
        for line in text.splitlines():
            match = re.search(pattern, line)
            if match:
                name = match.group(1)
                try:
                    self.api_endpoints.remove(url)
                except ValueError:
                    pass
                self.api_endpoints.append(f'{url.rsplit("/", 1)[0]}:{name}')
                print(self.api_endpoints[-1])

    def __extract_endpoints(self, response: dict) -> None:
        """
        Internal helper method to extract YANG module schemas from response JSON.

        Args:
            response (dict): JSON response from the RESTCONF server.
        """
        self.api_endpoints = []
        for key, value in response.get('ietf-yang-library:modules-state', {}).items():
            if key != 'module':
                continue
            for endpoint in value:
                self.api_endpoints.append(endpoint.get('schema'))

    def disconnect(self) -> None:
        """
        Stub for disconnecting the REST session.
        """
        pass

    def execute(self, command: Any, **kwargs) -> None:
        """
        Stub method for executing a REST command.

        Args:
            command: The command or endpoint to execute.
            **kwargs: Additional options for execution.
        """
        pass

    def configure(self, command: Any, **kwargs) -> None:
        """
        Stub method for sending configuration via REST.

        Args:
            command: The configuration data or endpoint.
            **kwargs: Additional options.
        """
        pass

    def is_connected(self) -> None:
        """
        Stub method for checking if the session is still active.
        """
        pass
