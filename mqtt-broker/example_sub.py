#!/usr/bin/env python3
from common_utils.mqtt import Subscriber, Broker


class Handler:
    def on_MQTTMessage(self, mqtt_message) -> None:
        mqtt_message.decode_payload()
        print(mqtt_message.content)


if __name__ == "__main__":
    handler = Handler()
    subscriber = Subscriber(
        client_id="test-sub", broker=Broker(), topic="testing", handlers=[handler]
    )
    subscriber.start()
