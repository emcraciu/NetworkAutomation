"""
Manages REST connections
"""
import re
from typing import Optional
import urllib3
import requests
from requests.auth import HTTPBasicAuth
from pyats.datastructures import AttrDict
from pyats.topology import Device


class RESTConnector:
    """
    Manages REST connections
    """
    def __init__(self, device: Device):
        self._session = None
        self._auth = None
        self._headers = None
        self._url = None
        self.device = device
        self.connection: Optional[AttrDict] = None
        self.api_endpoints: list[str] = []
        self.resconf_capabilities = None
        self.netconf_capabilities = None
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def connect(self, **kwargs):
        """
        Connects to device
        Args:
            kwargs:
                connection(testbed.Connection): The REST connection object used to connect
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
        Returns the interfaces data
        """
        endpoint = f'/restconf/data/ietf-interfaces:interfaces/interface={interface_name}'
        url = self._url + endpoint
        response = requests.get(url, auth=self._auth, headers=self._headers, verify=False, timeout=60)
        return response.json()

    def get_netconf_capabilities(self):
        """
        Returns the netconf capabilities from the netconf-state endpoint
        """
        netconf = '/restconf/data/netconf-state/capabilities'
        url = self._url + netconf
        response = requests.get(url, auth=self._auth, headers=self._headers, verify=False, timeout=60)
        self.netconf_capabilities = response.json().get(
            'ietf-netconf-monitoring:capabilities', {}
        ).get('capability', [])

    def get_restconf_capabilities(self):
        """
        Returns the restconf capabilities from the restconf-state endpoint
        """
        restconf = '/restconf/data/ietf-yang-library:modules-state'
        url = self._url + restconf
        response = requests.get(url, auth=self._auth, headers=self._headers, verify=False, timeout=60)
        self.__extract_endpoints(response.json())

    def get_api_endpoint(self, url):
        """
        Returns the api endpoint from the url
        """
        response = requests.get(url, auth=self._auth, headers=self._headers, verify=False, timeout=60)
        with open(f"{url.split('/')[-2]}.yang", 'w', encoding='utf-8') as file:
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
                self.api_endpoints.append(f'{url.rsplit('/', 1)[0]}:{name}')
                print(self.api_endpoints[-1])

    def __extract_endpoints(self, response):
        """
        Fetches all api endpoints from the yang schema
        """
        self.api_endpoints = []
        for key, value in response.get('ietf-yang-library:modules-state', []).items():
            if key != 'module':
                continue
            for endpoint in value:
                self.api_endpoints.append(endpoint.get('schema'))

    def disconnect(self):
        """
        Terminates REST connection
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
