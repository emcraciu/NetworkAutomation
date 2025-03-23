import subprocess
import re
from subprocess import Popen, PIPE
res = subprocess.Popen(['ip', 'address', 'show'], stdout=PIPE, stderr=PIPE)
res = res.communicate()[0].decode('utf-8').split('\n')
pattern1 = r'\d: (.+):'
pattern2 = r'inet (?P<joe>\d+\.\d+\.\d+\.\d+/\d+)'
interfaces = {}
last_int = ''
for line in res:
    try:
        match1 = re.search(pattern1, line).group(1)
        last_int = match1
        print(last_int)
    except AttributeError:
        pass
    try:
        match2 = re.search(pattern2, line).group('joe')
        interfaces[last_int] = match2
    except AttributeError:
        continue

print(interfaces)

# REZOLVATA
# import subprocess
# import re
# result = subprocess.Popen(['ifconfig'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# output, _ = result.communicate()
# pattern = r'(?m)^(\S+):.*?\n\s+inet\s+(\d+\.\d+\.\d+\.\d+)'
# output = output.decode("utf-8")
# print(type(str(output)))
# print(str(output))
# found = re.findall(pattern, output)
# print(type(found))
# dict1 = {}
# for item in found:
#      dict1[item[0]] = item[1]
# print(dict1)