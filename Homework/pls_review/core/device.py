from genie.conf import Genie
from genie.testbed import load
from genie.libs.ops.interface.iosxe.interface import Interface
from jinja2 import Template

from unicon.core.errors import ConnectionError
from utils.logger import setup_logger
from core import templates
from core.renderables import InterfaceConfig, StaticRoute
from utils.utils import get_interfaces_without_ip

logger = setup_logger("renderer")

class NetworkDevice:
    def __init__(self, genie_device):
        """
        Wrapper around a pyATS/Genie device object.
        """
        self.device = genie_device
        self.name = genie_device.name
        self.connected = False

    def connect(self):
        """
        Try to SSH first; if that fails, fall back to Telnet console.
        """
        # Attempt SSH
        try:
            logger.info(f"{self.name}: trying SSH...")
            self.device.connect(alias="cli", log_stdout=False)
            self.connected_via = "cli"
            logger.info(f"{self.name}: connected via SSH")
            return
        except ConnectionError as e:
            logger.warning(f"{self.name}: SSH failed ({e}), falling back to console…")

        # Fallback to console (Telnet)
        try:
            self.device.connect(alias="console", log_stdout=False)
            self.connected_via = "console"
            logger.info(f"{self.name}: connected via Telnet console")
        except ConnectionError as e:
            logger.error(f"{self.name}: console connect also failed: {e}")
            raise

    def configure_interface_ip(self, interface_obj, cidr, shutdown=False):

        intf_config = InterfaceConfig(interface_obj, shutdown)
        config_lines = intf_config.render()
        logger.info(f"Configuring interface {intf_config.name} on {self.name}")
        return self.device.configure(config_lines)

    def add_static_route(self, static_route_obj: StaticRoute):
        logger.info(f"{self.name}: Adding static route {static_route_obj.destination} via {static_route_obj.next_hop}")
        return self.device.configure(static_route_obj.render())

    def get_unconfigured_interfaces(self):
        return get_interfaces_without_ip(self.device)