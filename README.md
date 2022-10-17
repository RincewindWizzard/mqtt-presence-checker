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

## Install

Install from [pypi](https://pypi.org/project/mqtt-presence-checker/) with:

    pip install mqtt-presence-checker

Configure to start at boot with systemd.
Copy [mqtt-presence-checker.service](./sample_conf/mqtt-presence-checker.service) 
to _/lib/systemd/system/mqtt-presence-checker.service_.

Enable your service:

    sudo systemctl enable mqtt-presence-checker.service

And start it:

    sudo systemctl start mqtt-presence-checker.service

Check its status:

    systemctl status application.service
