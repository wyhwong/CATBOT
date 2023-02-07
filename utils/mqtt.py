import yaml
import paho.mqtt.client as mqtt
from abc import ABC, abstractmethod
from overrides import overrides

from .logger import get_logger


def load_broker_config() -> dict:
    with open("common_config/broker.yml", "r") as file:
        return yaml.load(file, Loader=yaml.SafeLoader)


class Broker:
    def __init__(self, config=load_broker_config()) -> None:
        self.host = config["host"]
        self.port = config["port"]
        self.username = config["username"]
        self.password = config["password"]


class MQTTMessage:
    def __init__(self, topic: str, payload: bytes) -> None:
        self.topic = topic
        self.payload = payload

    @staticmethod
    def from_str(topic: str, message: str):
        return MQTTMessage(topic=topic, payload=bytes(message, "utf8"))


class MQTTClient(ABC):
    def __init__(self, client_id: str, broker: Broker) -> None:
        self.logger = get_logger(logger_name="MQTT")
        self.client_id = client_id
        self.broker = broker

        self.client = mqtt.Client(client_id=client_id)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.username_pw_set(broker.username, broker.password)
        self.client.connect(broker.host, broker.port)

    def on_connect(self, client, userdata, flags, rc) -> None:
        if rc == 0:
            self.logger.info("Connected to MQTT Broker.")
        else:
            self.logger.error("Failed to connect, return code %d\n", rc)

    def on_disconnect(self, client, userdata, rc) -> None:
        self.logger.info(f"Disconnected MQTT Broker with result code {rc}.")

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass


class Subscriber(MQTTClient):
    def __init__(self, client_id: str, broker: Broker, topic) -> None:
        super().__init__(client_id, broker)
        self.topic = topic

    @overrides
    def start(self) -> None:
        self.client.subscribe(self.topic)
        self.client.on_message = self.on_message
        self.client.loop_forever()

    @overrides
    def stop(self) -> None:
        self.client.disconnect()
        self.client.loop_stop()

    def on_message(self, client, userdata, msg) -> None:
        mqtt_msg = MQTTMessage(topic=self.topic, payload=msg.payload)
        self.logger.debug(f"Received payload: {mqtt_msg.payload} from topic: {mqtt_msg.topic}")
        for handler in self.handlers:
            handler.on_MQTTMessage(mqtt_message=mqtt_msg)


class Publisher(MQTTClient):
    def __init__(self, client_id: str, broker: Broker) -> None:
        super().__init__(client_id, broker)
        self.client.loop_start()

    @overrides
    def start(self) -> None:
        self.client.loop_start()

    @overrides
    def stop(self) -> None:
        self.client.disconnect()
        self.client.loop_stop()

    def publish(self, message: MQTTMessage) -> None:
        result = self.client.publish(message.topic, message.payload)
        if result[0] == 0:
            self.logger.info(f"Successfully sent {message.payload} to topic {message.topic}.")
        else:
            self.logger.error(f"Failed to send message to topic {message.topic}.")
