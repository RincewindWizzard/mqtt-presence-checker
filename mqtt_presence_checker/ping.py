import asyncio
import re
import pingparsing
from loguru import logger
from typing import List

ping_parser = pingparsing.PingParsing()

ping_result = re.compile(r'^\d* packets transmitted, \d* received,.* (?P<packet_loss>\d*)% packet loss, time \d*ms$')

PACKET_LOSS_THRESHOLD = 90


async def ping(host, count=5):
    """
    Calls the ping program and parses the result asynchronously.
    :param host: Host to be pinged
    :param count: How many packets to send
    :return: A percentage between 0 and 100 how many pakets are dropped
    """
    proc = await asyncio.create_subprocess_exec(
        'ping', host, '-c', str(count), '-W', '1',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    if len(stderr) > 0:
        logger.error(stderr)
    result = ping_parser.parse(stdout.decode('utf-8')).as_dict()
    return result


async def is_available(host):
    """
    CHecks if a given host is available.
    :param host: hostname of the host to be checked
    :return: True if packet loss rate ist below PACKET_LOSS_THRESHOLD
    """
    result = await ping(host)
    result = result['packet_loss_rate'] < PACKET_LOSS_THRESHOLD

    if result:
        logger.debug(f'{host} is available.')
    else:
        logger.debug(f'{host} is unreachable.')
    return result


async def availability_loop(host: str):
    """
    Continuosly yields if any of the hosts is available.
    :param hosts: Which hosts should be pinged?
    :return:
    """
    while True:
        yield await is_available(host)
