import asyncio

from ConfigureEnvironment import configure_environment
from TestGuestPing import test_ping

async def main():
    await configure_environment()
    res = await test_ping()
    if res == True:
        print("Ping from Guest to Server succeeded")
    else:
        print("Ping from Guest to Server failed")

if __name__ == '__main__':
    asyncio.run(main())