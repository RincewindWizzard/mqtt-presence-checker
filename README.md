# mqtt-presence-checker

config.toml:

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




