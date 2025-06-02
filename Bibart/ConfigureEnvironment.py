import asyncio

from ConfigureUbuntuServer import configure_server_interfaces
from ConfigureRouter import configure_router
from ConfigureCSR import configure_csr_device

async def configure_environment():
    task = await asyncio.gather(configure_server_interfaces(), configure_router(), configure_csr_device(address='92.83.42.103',port=5002,hostname='CSR',password='pass',user='user'))

if __name__ == '__main__':
    asyncio.run(configure_environment())