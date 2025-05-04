from netmiko import ConnectHandler

conn_data = {
    'device_type': 'cisco_ios',
    'host': '192.168.102.2',
    'username': 'user',
    'password': 'pass',
    'secret': 'pass'
}

conn = ConnectHandler(**conn_data)
conn.enable()
out = conn.send_command('show version')
print(out)