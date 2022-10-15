import asyncio
import json

from loguru import logger
from time import time
from typing import List, Callable, Any, Coroutine
from types import AsyncGeneratorType

from typepy import Bool

from ping import is_available
import asyncio_mqtt


class Presence(object):
    SLEEP_INTERVALL = 1
    ABSENCE_THRESHOLD_SECONDS = 10

    def __init__(
            self,
            sources: List[AsyncGeneratorType],
            sinks):
        self._last_event_timestamp = time()
        self.sources = sources
        self.sinks = sinks
        self.tasks = []
        self._active = False
        self._value_changed = asyncio.Event()

    async def run(self):
        for source in self.sources:
            self._schedule_task(self._consume(source))

        last_presence = None
        while self._active:
            # check if presence has changed
            current_presence = self.is_present

            if not current_presence == last_presence:
                await self.propagate_presence_change()

            last_presence = current_presence

            self._value_changed.clear()
            await self._value_changed.wait()

    async def propagate_presence_change(self):
        is_present = self.is_present
        logger.debug(f'propagate_presence_change: {is_present}')
        await asyncio.gather(*[sink(is_present) for sink in self.sinks])

    async def _consume(self, source: AsyncGeneratorType):
        async for is_present in source:
            if is_present:
                self.update_last_event_timestamp()
            self._value_changed.set()

    def _schedule_task(self, task):
        self.tasks.append(
            asyncio.get_event_loop().create_task(
                task
            ))

    async def __aenter__(self, *args, **kwargs):
        self._active = True
        self._schedule_task(self.run())
        return self

    async def __aexit__(self, *args, **kwargs):
        logger.debug(f'Exiting presence checker')
        self._active = False
        for task in self.tasks:
            await task

    @property
    def last_event_timestamp(self):
        return self._last_event_timestamp

    def update_last_event_timestamp(self):
        self._last_event_timestamp = time()
        self._value_changed.set()
        logger.debug(f'Presence detected, updating timestamp!')

    @property
    def is_present(self):
        return (time() - self._last_event_timestamp) < Presence.ABSENCE_THRESHOLD_SECONDS
