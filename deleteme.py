import multiprocessing
import telnetlib
import time

import paramiko
import telnetlib3


def connect_to(args):
    host, port, type_ = args
    if(type_ == "ssh"):
        client = paramiko.SSHClient()
        conn = client.connect(hostname=host, port=port)
        in_,out, err = conn.exec_command("ping 192.168.11.1 -c 4")
        return (in_,out,err)
    elif(type_ == "telnet"):
        conn = telnetlib.Telnet(host, port)
        conn.write("ping 192.168.102.2 -c 4")
        time.sleep(2)
        out = conn.read_very_eager().decode()
        return out


if __name__ == '__main__':
    with multiprocessing.Pool(2) as pool:
        res = pool.map(connect_to, [('192.168.11.1', 22, 'ssh'),('192.168.0.100',5037,'telnet' )])

    for r in res:
        print(r)
