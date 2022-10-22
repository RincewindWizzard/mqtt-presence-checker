# mqtt-presence-checker

Check if you (or your phone) is at home and notify your smarthome via mqtt.
You can configure this daemon via a toml file in _/etc/mqtt-presence-checker/mqtt-presence-checker.conf_.

/etc/mqtt-presence-checker/mqtt-presence-checker.conf:

    [main]
    cooldown = 10
    log = "/var/log/mqtt-presence-checker.log"

    [mqtt]
    host = "mqtt.example.org"
    username = "<username>"
    password = "<password>"
    topic = "presence-checker/presence"
    
    [mqtt.sensor.door-sensor]
    topic = "zigbee2mqtt/door_sensor"
    predicate = "lambda x: not x['contact']"

    [ping]
    hosts = [
        'alice.example.org',
        'bob.example.org'
    ]

This is rather rudimentary and might crash or behave strange. Feel free to [fork me on github](https://github.com/RincewindWizzard/mqtt-presence-checker) and send a PR if you find any bug!

## Install with docker

Run with docker:

    docker run --cap-add net_raw --cap-add net_admin --name mqtt-presence-checker  --restart unless-stopped -v /etc/mqtt-presence-checker/:/etc/mqtt-presence-checker/ -d docker.io/rincewindwizzard/mqtt-presence-checker:latest
