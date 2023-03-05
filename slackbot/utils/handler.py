from overrides import overrides
from slack_sdk.web import WebClient

from common_utils.mqtt import Subscriber, Publisher
from common_utils.common import MessageHandler
from common_utils.logger import get_logger
from .command_exector import SlackCommandExector

LOGGER = get_logger(logger_name="Utils | Handler")


class SlackMessageHandler(MessageHandler):
    def __init__(self, web_client: WebClient, publisher: Publisher, subscriber: Subscriber) -> None:
        self.subscriber = subscriber
        self.commandExector = SlackCommandExector(self.status, web_client, publisher)

    def _is_command(self, text: str) -> bool:
        if text.split(" ")[0].lower() in self.commandExector.commands:
            return True
        return False

    @overrides
    def _is_vaild_message(self, message: dict) -> bool:
        if message["type"] != "message":
            LOGGER.info("Input event is not a message, ignored")
            return False
        if message.get("bot_id"):
            LOGGER.info("Input event is from bot, ignored")
            return False
        return True

    @overrides
    def handle_message(self, message: dict) -> None:
        if not self._is_vaild_message(message):
            return
        text, user, channel = message["text"], message["user"], message["channel"]
        if self._is_command(text):
            getattr(self.commandExector, text.split(" ")[0].lower())(text.lower(), user, channel)
        if self.status.in_chat:
            self._handle_message_when_in_chat(text, user, channel)
        else:
            LOGGER.info(
                f"Not responding to message: {message['text']}, user: {message['user']}, channel: {message['channel']}"
            )
