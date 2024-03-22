import asyncio
import asyncvnc


async def run_client():
    async with asyncvnc.connect('localhost') as client:
        print(client)

asyncio.run(run_client())
