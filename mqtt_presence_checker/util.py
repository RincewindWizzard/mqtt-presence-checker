import asyncio
import json


def try_parse_json(o):
    try:
        return json.loads(o)
    except:
        return o



async def default_wakeup_source(sleep_intervall = 10):
    while True:
        yield False
        await asyncio.sleep(sleep_intervall)