import asyncio

from TelnetContext import TelnetContext
from time import sleep
import re
async def test_ping():
    '''
    Returns True or False depending on ping success
    Returns False if the regex match somehow failed
    '''
    print("Testing Guest Ping")
    with TelnetContext(address="92.83.42.103",hostname="root",port=5058) as t:
        t.write(b"ping 192.168.11.254 -c 4")
        sleep(6)
        out = t.read_very_eager().decode()
        pattern = r'(\d+)% packet loss'
        match = re.search(pattern, out)
        if match:
            loss = match.group(1)
            try:
                loss = int(loss)
                if loss != 100:
                    return True
                return False
            except ValueError:
                print('Match failed somehow')
                return False
        else:
            print('No match found ??')
            return False
        # print(out)

async def main():
    res = await asyncio.gather(test_ping())
    print(res)

if __name__ == '__main__':
    asyncio.run(main())