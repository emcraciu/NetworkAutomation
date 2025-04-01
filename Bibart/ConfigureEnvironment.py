from ConfigureUbuntuServer import configure_server_interfaces
from ConfigureRouter import configure_router

def configure_environment():
    print("Configuring server interfaces")
    configure_server_interfaces()
    print("Configuring router")
    configure_router()
