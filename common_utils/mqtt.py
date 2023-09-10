import json
import paho.mqtt.client as mqtt
from abc import ABC, abstractmethod
from overrides import overrides

from .logger import get_logger
from .common import load_yml

LOGGER = get_logger("common_utils/mqtt")


def load_broker_config() -> dict:
    """
    Load MQTT broker config.

    Args:
        None.
    Returns:
        Broker config (dict)."""
    return load_yml("./configs/common/mqtt_broker.yml")


class Broker:
    """
    MQTT Broker.
    """

    def __init__(self, config=load_broker_config()) -> None:
        """
        Initialize MQTT Broker.

        Args:
            config (dict): Config of MQTT Broker.
        Returns:
            None.
        """
        self.host = config["host"]
        self.port = config["port"]
        self.username = config["username"]
        self.password = config["password"]


class MQTTMessage:
    """
    MQTT Message.
    """

    def __init__(self, topic: str, payload: bytes) -> None:
        """
        Initialize MQTT Message.

        Args:
            topic (str): Topic of the message.
            payload (bytes): Payload of the message.
        Returns:
            None.
        """
        self.topic = topic
        self.payload = payload

    @staticmethod
    def from_str(topic: str, message: str):
        """
        Create MQTTMessage from string.

        Args:
            topic (str): Topic of the message.
            message (str): Message.
        Returns:
            MQTTMessage.
        """
        return MQTTMessage(topic=topic, payload=bytes(message, "utf8"))

    def decode_payload(self) -> None:
        """
        Decode payload.

        Args:
            None.
        Returns:
            None.
        """
        if type(self.payload) != bytes:
            LOGGER.error("The type of input payload is not bytes. Ignored decode.")
            return
        content = self.payload.decode("utf-8").replace("'", '"')
        self.content = json.loads(content)
        LOGGER.info(f"Decoded payloads, {content=}")


class MQTTClient(ABC):
    """
    MQTT Client.
    """

    def __init__(self, client_id: str, broker: Broker) -> None:
        """
        Initialize MQTT Client.

        Args:
            client_id (str): Client ID.
            broker (Broker): MQTT Broker.
        Returns:
            None.
        """
        self.client_id = client_id
        self.client = mqtt.Client(client_id=client_id)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.username_pw_set(broker.username, broker.password)
        self.client.connect(host=broker.host, port=broker.port, keepalive=3600)

    def on_connect(self, client, userdata, flags, rc) -> None:
        """
        Callback function when connected to MQTT Broker.

        Args:
            client (mqtt.Client): MQTT Client.
            userdata (dict): User data.
            flags (dict): Flags.
            rc (int): Return code.
        Returns:
            None.
        """
        if rc == 0:
            LOGGER.info("Connected to MQTT Broker.")
        else:
            LOGGER.error("Failed to connect, return code %d\n", rc)

    def on_disconnect(self, client, userdata, rc) -> None:
        """
        Callback function when disconnected from MQTT Broker.

        Args:
            client (mqtt.Client): MQTT Client.
            userdata (dict): User data.
            rc (int): Return code.
        Returns:
            None.
        """
        LOGGER.info(f"Disconnected MQTT Broker with result code {rc}.")

    @abstractmethod
    def start(self) -> None:
        """
        (abstract method) Start MQTT Client.
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        (abstract method) Stop MQTT Client.
        """
        pass


class Subscriber(MQTTClient):
    """
    MQTT Subscriber.
    """

    def __init__(
        self, client_id: str, broker: Broker, topic: str, handlers: list
    ) -> None:
        """
        Initialize MQTT Subscriber.

        Args:
            client_id (str): Client ID.
            broker (Broker): MQTT Broker.
            topic (str): Topic of the subscriber.
            handlers (list): Handlers of the subscriber.
        Returns:
            None.
        """
        super().__init__(client_id, broker)
        self.topic = topic
        self.handlers = handlers

    @overrides
    def start(self) -> None:
        """
        Start MQTT Subscriber.

        Args:
            None.
        Returns:
            None.
        """
        self.client.subscribe(self.topic)
        self.client.on_message = self.on_message
        self.client.loop_forever()

    @overrides
    def stop(self) -> None:
        """
        Stop MQTT Subscriber.

        Args:
            None.
        Returns:
            None.
        """
        self.client.disconnect()
        self.client.loop_stop()

    def on_message(self, client, userdata, msg) -> None:
        """
        Callback function when received message from MQTT Broker.

        Args:
            client (mqtt.Client): MQTT Client.
            userdata (dict): User data.
            msg (mqtt.MQTTMessage): MQTT Message.
        Returns:
            None.
        """
        mqtt_msg = MQTTMessage(topic=self.topic, payload=msg.payload)
        LOGGER.debug(
            f"Received payload: {mqtt_msg.payload} from topic: {mqtt_msg.topic}"
        )
        for handler in self.handlers:
            handler.on_MQTTMessage(mqtt_message=mqtt_msg)


class Publisher(MQTTClient):
    """
    MQTT Publisher.
    """

    def __init__(self, client_id: str, broker: Broker) -> None:
        """
        Initialize MQTT Publisher.

        Args:
            client_id (str): Client ID.
            broker (Broker): MQTT Broker.
        Returns:
            None.
        """
        super().__init__(client_id, broker)
        self.client.loop_start()

    @overrides
    def start(self) -> None:
        """
        Start MQTT Publisher.

        Args:
            None.
        Returns:
            None.
        """
        self.client.loop_start()

    @overrides
    def stop(self) -> None:
        """
        Stop MQTT Publisher.

        Args:
            None.
        Returns:
            None.
        """
        self.client.disconnect()
        self.client.loop_stop()

    def publish(self, message: MQTTMessage) -> None:
        """
        Publish message to MQTT Broker.

        Args:
            message (MQTTMessage): Message to be published.
        Returns:
            None.
        """
        result = self.client.publish(message.topic, message.payload)
        if result[0] == 0:
            LOGGER.info(
                f"Successfully sent {message.payload} to topic {message.topic}."
            )
        else:
            LOGGER.error(f"Failed to send message to topic {message.topic}.")
