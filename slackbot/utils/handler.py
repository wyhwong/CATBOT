from slack_sdk.web import WebClient
from threading import Thread

from common_utils.mqtt import Subscriber, Publisher
from common_utils.logger import get_logger
from .command_exector import SlackCommandExector

LOGGER = get_logger(logger_name="Utils | Handler")


class MQTTHandler:
    def on_MQTTMessage(self, mqtt_message) -> None:
        mqtt_message.decode_payload()
        command = mqtt_message.content.get("command", None)
        datatype = mqtt_message.content.get("datatype", None)
        if mqtt_message.content["command"] == "log":
            pass


class SlackMessageHandler:
    def __init__(self, web_client: WebClient, user_id: str, publisher: Publisher, subscriber: Subscriber) -> None:
        self.user_id = user_id
        self.commandExector = SlackCommandExector(web_client, publisher)
        self.subscriber = subscriber
        self.subscriber.handlers.append(MQTTHandler())
        Thread(target=self.subscriber.start, daemon=True).start()

    def _is_user(self, user_id: str) -> bool:
        if user_id == self.user_id:
            return True
        LOGGER.info(f"Received message from non user, ignored.")
        return False

    def _is_command(self, text: str) -> bool:
        if text.split(" ")[0].lower() in self.commandExector.commands:
            return True
        LOGGER.info(f"Received message is not a command: {text}, ignored.")
        return False

    def _is_vaild_message(self, message: dict) -> bool:
        if message["type"] != "message":
            LOGGER.info("Input event is not a message, ignored.")
            return False
        if message.get("bot_id"):
            LOGGER.info("Input event is from bot, ignored.")
            return False
        return True

    def handle_message(self, message: dict) -> None:
        if not self._is_vaild_message(message):
            return
        text, user, channel = message["text"], message["user"], message["channel"]
        if not self._is_user(user):
            return
        if self._is_command(text):
            getattr(self.commandExector, text.split(" ")[0].lower())(text.lower(), user, channel)
        else:
            LOGGER.info(
                f"Not responding to message: {message['text']}, user: {message['user']}, channel: {message['channel']}"
            )

    def start_analysis(self) -> None:
        self.commandExector.analyze(text="analyze", user=None, channel=None)
