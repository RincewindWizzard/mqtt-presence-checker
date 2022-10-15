import asyncio
import aioping
from asyncio_mqtt import Client
from loguru import logger
from jsonargparse import CLI
from time import time
from typing import List
from docstring_parser import DocstringStyle
from jsonargparse import set_docstring_parse_options
from ping import is_available
import toml
from presence import Presence

set_docstring_parse_options(style=DocstringStyle.REST)


async def run(config):
    async with Client(
            config['mqtt']['host'],
            username=config['mqtt']['username'],
            password=config['mqtt']['password'],
            logger=logger) as client:
        async with client.filtered_messages("#") as messages:
            await client.subscribe("#")
            async for message in messages:
                logger.debug(f'{message.topic} {message.payload.decode()}')


async def async_main(config):
    async with Client(
            config['mqtt']['host'],
            username=config['mqtt']['username'],
            password=config['mqtt']['password'],
            logger=logger) as client:
        async with Presence(
                ping_probes=config['ping']['hosts'],
                mqtt=client
        ) as presence:
            while True:
                await asyncio.sleep(1)


def main(conf_path: str = './config.toml'):
    config = toml.load(conf_path)
    logger.debug(config)

    asyncio.run(async_main(config))

    # asyncio.run(run(config))


if __name__ == '__main__':
    try:
        CLI(main)
    except KeyboardInterrupt:
        ...
