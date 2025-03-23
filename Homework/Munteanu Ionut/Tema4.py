# Create class named SystemUtils that will have methods for getting the following info
#
# get_ipv4_interfaces() - returns list of dict with interface name/IP/subnet/MAC
# get_ipv4_routes() - returns list of dict with routeing information destination/gateway/interface/
# get_ipv6_interfaces() - returns list of dict with interface name/IP/subnet/MAC
# get_ipv6_routes() - returns list of dict with routeing information destination/gateway/interface/
# get_listening_ports() - create table like format that can be later printed with tabulate and should
# contain all the columns (and data) in the output of command netstat -ln

import ipaddress
import subprocess
import re
from tabulate import tabulate

port_data = subprocess.run("netstat -ln", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
port_data = port_data.stdout
ip_addr_show=subprocess.run("ip addr show", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
ip_addr_show = ip_addr_show.stdout
route_show=subprocess.run("ip route show", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
route_show=route_show.stdout
route_show_ipv6=subprocess.run("ip -6 route show", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
route_show_ipv6=route_show_ipv6.stdout


class SystemUtils:
    def __init__(self,data,route_show,route_show_ipv6,port_data):
        self.data=data.splitlines()
        self.route_show=route_show.splitlines()
        self.route_show_ipv6=route_show_ipv6.splitlines()
        self.port_data=port_data.splitlines()

    def get_ipv4(self,string="inet "):
        dict_of_elements={}
        interfaces=""
        for element in self.data:
            result=re.match("(\d)",element)
            if result:
                interfaces=result.string.split(" ")[1].replace(":","")
                dict_of_elements[interfaces]={}

            if string in element:
                ip_addr,subnet=element.split()[1].split("/")
                ip_addr=ipaddress.ip_address(ip_addr)
                dict_of_elements[interfaces]["ip"]=ip_addr
                dict_of_elements[interfaces]["subnet"]=subnet

            if "link/ether " in element:
                mac_addr=element.split()[1]
                dict_of_elements[interfaces]["mac"]=mac_addr

        return dict_of_elements

    def get_ipv6(self):
        return self.get_ipv4("inet6")

    def ipv4_route(self):
        route_dict={}
        for element in self.route_show:


            destination=element.split()[0].split("/")[0]
            if destination == "default":
                destination=ipaddress.ip_address("0.0.0.0")
            destination=ipaddress.ip_address(destination)
            route_dict[destination]={}

            if " via " in element:
                gateway=element.split("via ")[1].split(" ")[0]
                route_dict[destination]["gateway"]=ipaddress.ip_address(gateway)

            if " dev " in element:
                interface=element.split(" dev ")[1].split(" ")[0]
                route_dict[destination]["interface"]=interface

        for key in route_dict:
            try:
                if route_dict[key]["gateway"]==" ":
                    pass
            except KeyError:
                route_dict[key]["gateway"]=ipaddress.ip_address("0.0.0.0")

        return route_dict

    def ipv6_route(self):
        route_dict={}
        for element in self.route_show_ipv6:

            destination = element.split()[0].split("/")[0]
            destination = ipaddress.ip_address(destination)
            route_dict[destination] = {}

            if " via " in element:
                gateway = element.split("via ")[1].split(" ")[0]
                route_dict[destination]["gateway"] = ipaddress.ip_address(gateway)

            if " dev " in element:
                interface = element.split(" dev ")[1].split(" ")[0]
                route_dict[destination]["interface"] = interface

        for key in route_dict:
            try:
                if route_dict[key]["gateway"] == " ":
                    pass
            except KeyError:
                route_dict[key]["gateway"] = ipaddress.ip_address("::")

        return route_dict

    def get_listening_ports(self):
        list_of_ports=[]
        for element in self.port_data[2:]:
            protocol=element.split(" ")[0]
            if protocol=="Active":
                break

            local_address=element.split()[3].split(":")[0]
            foreign_address=element.split()[4].split(":")[0]
            items=[protocol,local_address,foreign_address]
            list_of_ports.append(items)

        print(tabulate(list_of_ports, headers=['Proto', 'Local Address', 'Foreign Address']))


obj1 = SystemUtils(ip_addr_show,route_show,route_show_ipv6,port_data)
# print(obj1.get_ipv4())
# print(obj1.get_ipv6())
# print(obj1.ipv4_route())
# print(obj1.ipv6_route())
# obj1.get_listening_ports()

