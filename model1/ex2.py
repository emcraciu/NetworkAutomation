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

def configure_interface(tn: telnetlib.Telnet, config:dict, interface):


    tn.write(b'\n')
    tn.expect([b'IOU1#'])
    tn.write(b'conf t')
    tn.expect([b'config'])
    tn.write(b'interface' + interface.encode('ascii'))
    tn.expect([b'config-if'])





if __name__ == '__main__':
    HOST = "192.168.11.1"
    #user = input("Enter your remote account: ")
    password = getpass.getpass()
    tn = telnetlib.Telnet(HOST)
    #tn.read_until(b"Username: ")
   # tn.write(user.encode('ascii') + b"\n")
    if password:
        tn.read_until(b"Password: ")
        tn.write(password.encode('ascii') + b"\n")
        # tn.read_until(b"IOU1>")
        # tn.write(b"en\n")
        # tn.read_until(b"Password:")
        # tn.write(b"pass\n")
        # tn.read_until(b"IOU1#")
        tn.write(b'show running-config\n')
        #get_running_config(tn)
        configure_interface(tn, {}, 'eth0/1')
        # for _ in range(5):
        #     sleep(1)
        #     print(tn.read_very_eager().decode('ascii'))

tn.write(b"exit\n")
print(tn.read_all().decode('ascii'))