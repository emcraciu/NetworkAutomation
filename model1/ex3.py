import configparser
import getpass
import telnetlib
from time import sleep



def get_running_config(tn: telnetlib.Telnet):
    while True:
        sleep(1)
        text = tn.read_very_eager().decode('ascii')
        print(text)
        if '--More--' in text:
            tn.write(b' ')
            if 'IOU1#' in text:
                break

if __name__ == '__main__':
    HOST = "192.168.11.1"
    password = getpass.getpass()
    tn = telnetlib.Telnet(HOST)
    if password:
        tn.read_until(b"Password: ")
        tn.write(password.encode('ascii') + b"\n")
        tn.write(b'show running-config\n')
        get_running_config(tn)
