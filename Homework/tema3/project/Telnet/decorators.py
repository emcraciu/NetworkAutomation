

def with_telnet(func):
    def wrapper(*args, **kwargs):
        with Telnet_Connection() as telnet:
            return func(ssh, *args, **kwargs)
    return wrapper