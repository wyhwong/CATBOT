#!/usr/bin/env python3
from common_utils.mqtt import Publisher, Broker, MQTTMessage
from time import sleep

if __name__ == "__main__":
    publisher = Publisher(client_id="test-pub", broker=Broker())
    while True:
        message = {"Command": "test", "content": "Hello World"}
        message = MQTTMessage.from_str(topic="testing", message=str(message))
        publisher.publish(message=message)
        sleep(3)
