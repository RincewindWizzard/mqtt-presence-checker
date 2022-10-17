import asyncio
import inspect

from loguru import logger
from time import time
from typing import List, Callable, Any, AsyncGenerator, NewType, Union, Optional, Coroutine
from .util import as_awaitable

State = NewType('State', bool)


async def default_wakeup_source(sleep_intervall=10):
    """
    Yields False every sleep_intervall seconds.
    Ensures that the event loop of minuterie is woken up at regular intervals.
    :param sleep_intervall:
    :return:
    """
    while True:
        logger.debug(f'Wake up')
        yield False
        await asyncio.sleep(sleep_intervall)


async def if_changed(old_value: State, new_value: State, func: Callable) -> State:
    if not old_value == new_value:
        await func()
    return new_value


class Minuterie(object):
    """
    This class provides a timed relais like the light system in a stairwell.
    It listens for events from sources. If an event evaluates to True then the current state is set to "active" (True).
    After a cooldown period of self.cooldown seconds the state returns back to "incactive" (False).
    Every state change is propageted to all sinks.
    """

    def __init__(
            self,
            sources: List[AsyncGenerator[bool, Any]],
            sinks: List[Callable],
            cooldown: int = 10
    ):
        self._last_event_timestamp = time()
        self.sources = sources
        self.sources.append(default_wakeup_source(cooldown))
        self.sinks = [as_awaitable(sink) for sink in sinks]
        self.cooldown = cooldown

        self.tasks = []
        self._event = asyncio.Event()

    async def loop(self):
        old_state = None
        while True:
            await self._event.wait()
            self._event.clear()
            new_state = self.is_active
            logger.debug(f'loop')

            await self.on_event(old_state, new_state)
            old_state = new_state

    async def on_event(self, old_state: Optional[State], new_state: State):
        logger.debug(f'on_event({old_state} -> {new_state})')
        if old_state is None or not old_state == new_state:
            await self._propagate_presence_change(new_state)

    async def _propagate_presence_change(self, state: State):
        """
        Propagates the current state to all sinks.
        :return:
        """
        logger.debug(f'propagate_presence_change: {state}')

        await asyncio.gather(*[sink(state) for sink in self.sinks])

    async def _consume(self, source: AsyncGenerator[bool, Any]):
        """
        Consumes all events from source and updates the last_event_timestamp everytime the event was True.
        :param source:
        :return:
        """
        async for new_state in source:
            logger.debug(f'consumed {new_state}')
            if new_state:
                self.update_last_event_timestamp()

            self._event.set()

    def _schedule_task(self, coroutine):
        """
        Schedules a task and adds it to the task list for later canceling in self.__aexit__.
        :param coroutine:
        :return:
        """
        self.tasks.append(asyncio.ensure_future(coroutine))

    async def __aenter__(self, *args, **kwargs):
        self._event.set()
        for source in self.sources:
            self._schedule_task(self._consume(source))

        self._schedule_task(self.loop())
        return self

    async def __aexit__(self, *args, **kwargs):
        """
        Cancel all tasks
        :param args:
        :param kwargs:
        :return:
        """
        logger.debug(f'Exiting presence checker')
        for task in self.tasks:
            task.cancel()

    @property
    def last_event_timestamp(self):
        return self._last_event_timestamp

    def update_last_event_timestamp(self):
        """
        Updates timestamp of last event and wakes up the run loop.
        :return:
        """
        self._last_event_timestamp = time()
        logger.debug(f'Updating timestamp!')

    @property
    def is_active(self) -> State:
        """
        Returns the current state (True, False) of the minuterie.
        :return:
        """
        return (time() - self._last_event_timestamp) < self.cooldown
