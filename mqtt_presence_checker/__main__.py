from pathlib import Path
import daemon
import toml
import asyncio
from asyncio_mqtt import Client
from daemon import pidfile
from loguru import logger
from jsonargparse import CLI, set_docstring_parse_options
from docstring_parser import DocstringStyle
from dotwiz import DotWiz

from . import ping
from .minuterie import Minuterie
from .mqtt import mqtt_source, mqtt_sink, MQTTTopic

set_docstring_parse_options(style=DocstringStyle.REST)

POSSIBLE_CONFIG_PATHS = [Path(path) for path in [
    './config.toml',
    '/etc/mqtt-presence-checker/mqtt-presence-checker.conf'
]]


def parse_mqtt_sensors(config, mqtt):
    try:
        return [
            mqtt_source(mqtt, sensor.topic, eval(sensor.predicate))
            for name, sensor in config.mqtt.sensor.items() if 'sensor' in config.mqtt
        ]
    except SyntaxError as e:
        logger.error(f'There is an error in your sensor configuration! {config.mqtt.sensor}')
        raise e


async def async_main(config):
    """
    Creates a minuterie from config and runs it forever.
    :param config:
    :return:
    """
    async with Client(
            config.mqtt.host,
            username=config.mqtt.username,
            password=config.mqtt.password,
            logger=logger) as mqtt:
        mqtt_sensors = parse_mqtt_sensors(config, mqtt)
        logger.debug(mqtt_sensors)

        async with Minuterie(
                sources=[
                            ping.availability_loop(host, config.ping.interval)
                            for host in config.ping.hosts
                        ] + mqtt_sensors,
                sinks=[
                    mqtt_sink(mqtt, config.mqtt.topic)
                ],
                cooldown=config.main.cooldown
        ) as _:
            while True:
                # Run forever
                await asyncio.sleep(1000)


def load_config(conf_path: Path = None):
    if conf_path is not None:
        return toml.load(conf_path.open('r'))
    else:
        for path in POSSIBLE_CONFIG_PATHS:
            try:
                if path.is_file():
                    return toml.load(path.open('r'))
            except:
                logger.warning(f'Could not load config from {path}')


# def run_daemon(config):
#     with open(config.main.log, 'w+') as log_out:
#         with daemon.DaemonContext(
#                 detach_process=False,
#                 stdout=log_out,
#                 stderr=log_out,
#                 pidfile=pidfile.TimeoutPIDLockFile(config.main.pidfile)
#         ):
#             ...


def main(conf_path: Path = None):
    config = load_config(conf_path)
    if config is None:
        logger.error('Could not find any configuration!')
        exit(1)

    logger.debug(config)
    config = DotWiz(config)

    logger.debug('daemon context entered')
    asyncio.run(async_main(config))


if __name__ == '__main__':
    try:
        CLI(main)
    except KeyboardInterrupt:
        ...
