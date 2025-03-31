from model1.cv9 import TelnetContext

password = 'pass'
# def get_running_config(tn: Telnet):
#     while True:
#         sleep(1)
#         text = tn.read_very_eager().decode('ascii')
#         print(text)
#         if '--More--' in text:
#             tn.write(b' ')
#         if '#' in text:
#             break
remote_address = '92.83.42.103'
port = 5907
with TelnetContext(remote_address, port, b"IOU1") as te:
    te.write(b'conf t')
    te.write(b"int eth0/0")
    te.expect([b"\(config-if\)#"])
    te.write(b"ip add 192.168.11.1 255.255.255.0")
    te.expect([b"\(config-if\)#"])
    te.write(b"no sh")
    te.expect([b"\(config-if\)#"])
    te.write(b"line vty 0 4")
    te.expect([b"\(config-line\)#"])
    te.write(b"transport input telnet")
    te.expect([b"\(config-line\)#"])
    te.write(b"password password")
    te.expect([b"\(config-line\)#"])
    te.write(b"privilege level 15")
    te.expect([b"\(config-line\)#"])
    te.write(b"exit")
    te.expect([b"\(config\)#"])
    te.write(b"exit")
    te.expect([b"#"])
    te.write(b"wr")
    te.expect([b"\[confirm\]|#"])
print("afara")


