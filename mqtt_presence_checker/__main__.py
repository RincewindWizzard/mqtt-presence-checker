import asyncio
import aioping
from asyncio_mqtt import Client
from loguru import logger
from jsonargparse import CLI
from time import time
from typing import List, Callable, Any
from docstring_parser import DocstringStyle
from jsonargparse import set_docstring_parse_options
from typepy import Bool

from ping import is_available
import toml
import ping
from presence import Presence
import json

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


def publish_to_mqtt(mqtt: Client, topic: str):
    async def sink(is_present):
        logger.debug(f'Current state is: {is_present}')
        payload = json.dumps({
            'is_present': is_present
        }).encode('utf-8')
        await mqtt.publish(topic, payload)

    return sink



def try_parse_json(o):
    try:
        return json.loads(o)
    except:
        return o
async def mqtt_source(mqtt: Client, topic: str, predicate: Callable[[Any], Bool]):
    # zigbee2mqtt/door_sensor {"battery":100,"battery_low":false,"contact":false,"linkquality":81,"tamper":false,"voltage":3200}

    async with mqtt.filtered_messages(topic) as messages:
        await mqtt.subscribe(topic)
        async for message in messages:
            payload = message.payload.decode('utf-8')
            logger.debug(f'{message.topic} {message.payload.decode()}')


            yield predicate(try_parse_json(payload))


async def async_main(config):
    async with Client(
            config['mqtt']['host'],
            username=config['mqtt']['username'],
            password=config['mqtt']['password'],
            logger=logger) as mqtt:
        mqtt_sensors = [
            mqtt_source(mqtt, sensor['topic'], eval(sensor['predicate']))
            for name, sensor in config['mqtt']['sensor'].items() if 'sensor' in config['mqtt']
        ]
        logger.debug(mqtt_sensors)

        async with Presence(
                sources=[
                            ping.availability_loop(host)
                            for host in config['ping']['hosts']
                        ] + mqtt_sensors,
                sinks=[
                    publish_to_mqtt(mqtt, config['mqtt']['topic'])
                ]
        ) as presence:
            while True:
                await asyncio.sleep(1)


async def foo(config):
    async with Client(
            config['mqtt']['host'],
            username=config['mqtt']['username'],
            password=config['mqtt']['password'],
            logger=logger) as mqtt:
        async for x in mqtt_source(mqtt, 'zigbee2mqtt/door_sensor', lambda x: True):
            logger.debug(x)


def main(conf_path: str = './config.toml'):
    config = toml.load(conf_path)
    logger.debug(config)

    asyncio.run(async_main(config))

    # asyncio.run(foo(config))


if __name__ == '__main__':
    try:
        CLI(main)
    except KeyboardInterrupt:
        ...
