import subprocess

setip = subprocess.Popen(['sudo', 'ip', 'address', 'add','192.168.11.200/24', 'dev', 'ens4'],  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
whatevz, _ = setip.communicate()
print(whatevz)



setip = subprocess.Popen(['ip', 'link', 'set', 'ens4', 'up'],  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
whatevz, _ = setip.communicate()
print(whatevz)

setip2 = subprocess.Popen(['ip', 'route', 'add', '192.168.12.0/24', 'via', '192.168.11.1'],  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
whatevz1, _ = setip2.communicate()
print(whatevz1)

