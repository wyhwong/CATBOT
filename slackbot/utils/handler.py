from slack_sdk.web import WebClient
from threading import Thread

from common_utils.mqtt import Subscriber, Publisher
from common_utils.logger import get_logger
from .command_exector import SlackCommandExector

LOGGER = get_logger("slackbot/utils/handler")


class MQTTHandler:
    def __init__(self, command_exector: SlackCommandExector) -> None:
        self.command_exector = command_exector

    def on_MQTTMessage(self, mqtt_message) -> None:
        mqtt_message.decode_payload()
        command = mqtt_message.content.get("command", None)
        if command == "log":
            scores = mqtt_message.content.get("scores", None)
            if scores:
                self.command_exector.log_scores(scores)
        if command == "post":
            self.command_exector.post(command_args=mqtt_message.content["args"])


class SlackMessageHandler:
    def __init__(
        self, web_client: WebClient, privilege_user_id: str, publisher: Publisher, subscriber: Subscriber
    ) -> None:
        LOGGER.debug("Initializing Slackbot Message Handler...")
        self.privilege_user_id = privilege_user_id
        self.commandExector = SlackCommandExector(web_client, publisher)
        self.subscriber = subscriber
        self.subscriber.handlers.append(MQTTHandler(self.commandExector))
        Thread(target=self.subscriber.start, daemon=True).start()
        LOGGER.debug("Initialized Slackbot Command Exector.")

    def _is_permission_enough(self, command: str, user_id: str) -> bool:
        require_privilege = self.commandExector.commands[command]["require_privilege"]
        if require_privilege and user_id != self.privilege_user_id:
            LOGGER.info("Received command message from non privileged user, ignored.")
            return False
        LOGGER.info("Received command message from user, processing...")
        return True

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
        if self._is_command(text):
            command = text.split(" ")[0].lower()
            if not self._is_permission_enough(command=command, user_id=user):
                return
            self.commandExector.wait_if_after_analysis()
            getattr(self.commandExector, command)(text.lower(), user, channel)
        else:
            LOGGER.info(
                f"Not responding to message: {message['text']}, user: {message['user']}, channel: {message['channel']}"
            )

    def start_analysis(self) -> None:
        self.commandExector.analyze("analyze", None, None)
