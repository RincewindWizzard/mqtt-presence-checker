"""
Sources and sinks for mqtt.
"""

import json
from typing import Callable, Any, NamedTuple

import asyncio_mqtt
from loguru import logger
from typepy import Bool

from . import util


class MQTTTopic(NamedTuple):
    """
    Specifies a topic on broker where you are already connected to.
    """
    client: asyncio_mqtt.Client
    topic: str


def mqtt_sink(mqtt_client: asyncio_mqtt.Client, topic: str):
    """
    Returns a sink that publishes every event to a given mqtt topic.
    :param mqtt:
    :param topic:
    :return:
    """

    async def sink(is_present: bool):
        logger.debug(f'Current state is: {is_present}')
        payload = json.dumps({
            'is_present': is_present
        }).encode('utf-8')
        await mqtt_client.publish(topic, payload)

    return sink


async def mqtt_source(
        mqtt_client: asyncio_mqtt.Client,
        topic: str,
        map_func: Callable[[Any], Bool] = lambda x: bool(x)):
    """
    Returns a source which emits every map_func(payload) from a given topic
    :param src:
    :param map_func:
    :return:
    """
    async with mqtt_client.filtered_messages(topic) as messages:
        await mqtt_client.subscribe(topic)
        async for message in messages:
            payload = message.payload.decode('utf-8')
            logger.debug(f'{message.topic} {message.payload.decode()}')

            yield map_func(util.try_parse_json(payload))
