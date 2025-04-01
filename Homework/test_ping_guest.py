from Bibart.TelnetContext import TelnetContext

with TelnetContext(hostname='root', port=5002, address='92.83.42.103') as te:
    te.write(b'ip addr show')
    te.expect([b'root'])