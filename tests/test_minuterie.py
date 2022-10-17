from typing import NamedTuple, Any, AsyncGenerator
from time import time
import pytest
import asyncio
from mqtt_presence_checker.minuterie import Minuterie
from loguru import logger


class Event(NamedTuple):
    timestamp: float
    value: bool


async def always_true(interval: float = 1) -> AsyncGenerator[bool, Any]:
    while True:
        yield True
        await asyncio.sleep(interval)


@pytest.mark.asyncio
async def test_timing():
    events = []
    cooldown = 1
    test_duration = 5
    precision = 1

    async with Minuterie(
            sources=[
                always_true(test_duration - cooldown * 2.1)
            ],
            sinks=[lambda x: events.append(Event(time(), x))],
            cooldown=cooldown
    ) as minuterie:
        await asyncio.sleep(test_duration)

    start_timestamp = events[0].timestamp

    events = [Event(event.timestamp - start_timestamp, event.value) for event in events]

    expected_events = [
        Event(0.0, True),
        Event(1.0, False),
        Event(2.9, True),
        Event(4.0, False),
    ]

    logger.error(events)

    assert len(events) == len(expected_events)

    for expected, actual in zip(expected_events, events):
        assert actual.value == expected.value
        assert int(actual.timestamp * 10 ** precision) == int(expected.timestamp * 10 ** precision)
