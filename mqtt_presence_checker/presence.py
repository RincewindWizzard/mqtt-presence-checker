import asyncio
import json

from loguru import logger
from time import time
from typing import List
from ping import is_available
import asyncio_mqtt


class Presence(object):
    SLEEP_INTERVALL = 10
    ABSENCE_THRESHOLD_SECONDS = 1
    PRESENCE_TOPIC = 'presence-checker/presence'

    def __init__(self, ping_probes: List[str] = None, mqtt: asyncio_mqtt.Client = None):
        self._last_event_timestamp = time()
        self.ping_probes = ping_probes if ping_probes else []
        self.mqtt = mqtt
        self.tasks = []
        self._active = False

    async def run(self):
        last_presence = None
        while self._active:
            logger.debug(f'Tick')
            if await self.any_ping_probe_available():
                self.update_last_event_timestamp()

            # check if presence has changed
            current_presence = self.is_present
            if not current_presence == last_presence:
                self._schedule_task(self.propagate_presence_change())
            last_presence = current_presence
            await asyncio.sleep(Presence.SLEEP_INTERVALL)




    def _schedule_task(self, task):
        self.tasks.append(
            asyncio.get_event_loop().create_task(
                task
            ))

    async def propagate_presence_change(self):
        is_present = self.is_present
        logger.debug(f'Presence is now {is_present}')

        if self.mqtt:
            payload = json.dumps({
                'is_present': is_present
            }).encode('utf-8')
            await self.mqtt.publish(Presence.PRESENCE_TOPIC, payload)



    async def __aenter__(self, *args, **kwargs):
        self._active = True
        loop = asyncio.get_event_loop()
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
        logger.debug(f'Presence detected, updating timestamp!')

    @property
    def is_present(self):
        return (time() - self._last_event_timestamp) < Presence.ABSENCE_THRESHOLD_SECONDS
