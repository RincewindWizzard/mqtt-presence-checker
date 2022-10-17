import asyncio
import pytest
from loguru import logger
from mqtt_presence_checker.ping import is_available

# def test_sum():
#     assert sum([1, 2, 3]) == 6, "Should be 6"
#
#
# async def sample_generator():
#     for i in range(10):
#         yield i
#         await asyncio.sleep(1)
#
# @pytest.mark.asyncio
# async def test_async_generator():
#     async for i in sample_generator():
#         logger.debug(i)
#
#
# @pytest.mark.asyncio
# async def test_ping():
#     hosts = [
#         'dfl-desktop.fritz.box',
#         'dfl-oneplus.fritz.box',
#         'neb-oneplus.fritz.box',
#         '192.168.178.250'
#     ]
#
#     result = await asyncio.gather(*[is_available(host) for host in hosts])
#     logger.debug(f'{result}')
