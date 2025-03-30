import subprocess
import ipaddress
import tabulate

class SystemUtils:

    def __init__(self):
        pass

    def get_ipv4_interfaces(self):
        # stdout = returneaza output-ul comenzii ifconfig -v -> afiseaza doar interfetele
        ifconfigResults = subprocess.run(['ifconfig', '-v'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        nameInterface = ''
        ipv4 = ''
        subnetMask = ''
        macAddress = ''

        ipv4Interfaces = {}
        for line in ifconfigResults.stdout.splitlines():
            lineDecode = line.decode('utf-8')
            # daca variabila de numele interfetei este goala sau linia este un rand gol
            if not nameInterface or not line:
                #verificam daca linia este un rand gol si reinitializam variabila de nume cu valoare goala
                if not lineDecode.strip():
                    ipv4Interfaces.update({nameInterface: {"ip": ipv4, "subnet mask": subnetMask, "macAddress":macAddress}})
                    nameInterface = ''
                    ipv4 = ''
                    subnetMask = ''
                    macAddress = ''
                    #daca nu este linia goala extragi numele de interfata si il salvezi in variabila
                else:
                    nameInterface = lineDecode.split(':')[0]
            print(lineDecode)
            if 'inet' in lineDecode and 'inet6' not in lineDecode:
                #extrag din linie ip ,subnet
                ipv4 = lineDecode.split()[1]
                subnetMask = lineDecode.split()[3]

            if 'ether' in lineDecode:
                macAddress = lineDecode.split()[1]
                # daca am gasit ip si subnetmask verificam daca linia contine 'ether', daca contine extragem din acea linie mac

        return ipv4Interfaces


    def get_ipv6_interfaces(self):
        ifconfigResults = subprocess.run(['ifconfig', '-a'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        nameInterface = ''
        ipv6 = ''
        subnetMask = ''
        macAddress = ''

        ipv6Interfaces = {}
        for line in ifconfigResults.stdout.splitlines():
            lineDecode = line.decode('utf-8')
            # daca variabila de numele interfetei este goala sau linia este un rand gol
            if not nameInterface or not line:
                #verificam daca linia este un rand gol si reinitializam variabila de nume cu valoare goala
                if not lineDecode.strip():
                    ipv6Interfaces.update({nameInterface: {"ip": ipv6, "subnet mask": subnetMask, "macAddress":macAddress}})
                    nameInterface = ''
                    ipv6 = ''
                    subnetMask = ''
                    macAddress = ''
                    #daca nu este linia goala extragi numele de interfata si il salvezi in variabila
                else:
                    nameInterface = lineDecode.split(':')[0]
            print(lineDecode)
            if 'inet6' in lineDecode:
                #extrag din linie ip ,subnet
                ipv6 = lineDecode.split()[1]
                subnetMask = lineDecode.split()[3]

            if 'ether' in lineDecode:
                macAddress = lineDecode.split()[1]
                # daca am gasit ip si subnetmask verificam daca linia contine 'ether', daca contine extragem din acea linie mac

        return ipv6Interfaces

    def get_ipv4_routes(self):
        routeResults = subprocess.run(['route'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        destination = ''
        gateway = ''
        interface = ''
        routing_information = {}

        startRoutes = False
        indexRoutes = 0
        for line in routeResults.stdout.splitlines():
            lineDecode = line.decode('utf-8') #decodeaza din bytes in str
            print(lineDecode)
            if startRoutes:
                # if True
                # if False
                print(lineDecode)
                destination = lineDecode.split()[0]
                gateway = lineDecode.split()[1]
                interface = lineDecode.split()[7]
                routing_information.update({indexRoutes: {'destination': destination, 'gateway': gateway, 'interface': interface}})
                indexRoutes += 1
            if 'Destination' in lineDecode and 'Gateway' in lineDecode:
                startRoutes = True

        return routing_information

    def get_ipv6_routes(self):
        routeResults = subprocess.run(['route', '-6'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        destination = ''
        gateway = ''
        interface = ''
        routing_information = {}

        startRoutes = False
        indexRoutes = 0
        for line in routeResults.stdout.splitlines():
            lineDecode = line.decode('utf-8')  # decodeaza din bytes in str
            print(lineDecode)
            if startRoutes:
                # if True
                # if False
                print(lineDecode)
                destination = lineDecode.split()[0]
                gateway = lineDecode.split()[1]
                interface = lineDecode.split()[6]
                routing_information.update(
                    {indexRoutes: {'destination': destination, 'gateway': gateway, 'interface': interface}})
                indexRoutes += 1
            if 'Destination' in lineDecode and 'Next Hop' in lineDecode:
                startRoutes = True

        return routing_information

##TODO
    # nu merge sa instalez tabulate
    def get_listening_ports(self):
        portsResults = subprocess.run(['netstat', '-ln'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

clasa = SystemUtils()
# print(clasa.get_ipv4_interfaces())
# print(clasa.get_ipv6_interfaces())
# print(clasa.get_ipv4_routes())
# print(clasa.get_ipv6_routes())

