import logging
from overrides import overrides
from slack_sdk.web import WebClient

from common_utils.mqtt import Subscriber, Publisher
from common_utils.common import MessageHandler
from .command_exector import SlackCommandExector


class SlackMessageHandler(MessageHandler):
    def __init__(
        self, web_client: WebClient, publisher: Publisher, subscriber: Subscriber, logger: logging.Logger
    ) -> None:
        self.subscriber = subscriber
        self.logger = logger
        self.commandExector = SlackCommandExector(self.status, web_client, publisher, logger)

    def _is_command(self, text: str) -> bool:
        if text.split(" ")[0].lower() in self.commandExector.commands:
            return True
        return False

    @overrides
    def _is_vaild_message(self, message: dict) -> bool:
        if message["type"] != "message":
            self.logger.info("Input event is not a message, ignored")
            return False
        if message.get("bot_id"):
            self.logger.info("Input event is from bot, ignored")
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
            self.logger.info(
                f"Not responding to message: {message['text']}, user: {message['user']}, channel: {message['channel']}"
            )
