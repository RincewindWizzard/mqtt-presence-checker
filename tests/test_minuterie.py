from typing import NamedTuple
from time import time
import pytest
import asyncio
from mqtt_presence_checker.minuterie import Minuterie
from loguru import logger


class Event(NamedTuple):
    timestamp: float
    value: bool


@pytest.mark.asyncio
async def test_timing():
    events = []
    cooldown = 1
    margin = 0.5

    async with Minuterie(
            sources=[],
            sinks=[lambda x: events.append(Event(time(), x))],
            cooldown=cooldown
    ) as minuterie:
        await asyncio.sleep(cooldown + margin)
        assert len(events) == 2
        assert time() - events[-1].timestamp < cooldown
        logger.error(events)




