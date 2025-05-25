import time
from TelnetContext import TelnetContext

with TelnetContext(address="192.168.11.1",hostname="IOU1",port=23) as t:
    with open("../modul2/test.txt", "wb") as file:
        t.write(b"show running-config")
        while True:
            time.sleep(2)
            out = t.read_very_eager()
            file.write(b'\n'.join(filter(lambda line: b'--More--' not in line, out.split(b'\n'))))
            file.flush()
            if not b'--More--' in out:
                break
            t.write(b' ')


