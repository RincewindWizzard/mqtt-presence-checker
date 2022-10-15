import json
from typing import Callable, Any

from asyncio_mqtt import Client
from loguru import logger
from typepy import Bool

import util


def publish_to_mqtt(mqtt: Client, topic: str):
    async def sink(is_present):
        logger.debug(f'Current state is: {is_present}')
        payload = json.dumps({
            'is_present': is_present
        }).encode('utf-8')
        await mqtt.publish(topic, payload)

    return sink


async def mqtt_source(mqtt: Client, topic: str, predicate: Callable[[Any], Bool]):
    async with mqtt.filtered_messages(topic) as messages:
        await mqtt.subscribe(topic)
        async for message in messages:
            payload = message.payload.decode('utf-8')
            logger.debug(f'{message.topic} {message.payload.decode()}')

            yield predicate(util.try_parse_json(payload))
