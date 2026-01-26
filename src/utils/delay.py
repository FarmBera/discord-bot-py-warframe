import asyncio


async def delay(seconds: int = 5.0) -> None:
    await asyncio.sleep(seconds)
