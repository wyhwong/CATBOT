import yaml
import logging
from slack_sdk.web import WebClient

from common_utils.common import Message
from common_utils.mqtt import MQTTMessage, Publisher


class SlackCommandExector:
    def __init__(self, status, web_client: WebClient, publisher: Publisher, logger: logging.Logger) -> None:
        self.logger = logger
        self.publisher = publisher
        self.topic = "slackbot-pub"
        self.web_client = web_client
        self.status = status
        self.commands = self._load_command_list()

    def _load_image(self, image: str) -> str:
        with open("config/image.yml", "r") as file:
            image = yaml.load(file, Loader=yaml.SafeLoader)[image]
        return image["title"], image["file"]

    def _load_dialogue(self, dialogue: str) -> str:
        with open("config/dialogue.yml", "r") as file:
            return yaml.load(file, Loader=yaml.SafeLoader)[dialogue]

    def _load_command_list(self) -> list:
        with open("config/commands.yml", "r") as file:
            commands = yaml.load(file, Loader=yaml.SafeLoader)
        return commands.keys()

    def _prepare_help_message(self) -> str:
        with open("config/commands.yml", "r") as file:
            commands = yaml.load(file, Loader=yaml.SafeLoader)
        message = "Available commands are the following:\n"
        for command, content in commands.items():
            message += f"\t - {command}: {content} \n"
        return message

    def _post_message(self, text: str, channel: str) -> None:
        self.logger.info(f"Sending message to Slack, channel: {channel}, text: {text}")
        sent_message = self.web_client.chat_postMessage(channel=channel, text=text)["ok"]
        self.logger.info(f"Successfully sent message: {sent_message}")

    def _post_image(self, title: str, file: str, channel: str) -> None:
        self.logger.info(f"Sending image to Slack, channel: {channel}, file: {file}")
        sent_image = self.web_client.files_upload_v2(title=title, file=file, channel=channel)
        self.logger.info(f"Successfully sent image: {sent_image}")

    def help(self, text: str, user: str, channel: str) -> None:
        if text == "help":
            self.logger.info(f"Sending help message, channel: {channel}")
            message = Message(self._prepare_help_message())
            mq_msg = MQTTMessage(self.topic, message.to_payload())
            self.publisher.publish(mq_msg)
            self._post_message(self._prepare_help_message(), channel)
        else:
            self.logger.info(f"Invalid command, send ask message, channel: {channel}")
            self._post_message('Invalid command, do you mean "help"?', channel)

    def send(self, text: str, user: str, channel: str, dialogue: bool = None) -> None:
        if dialogue:
            text = self._load_dialogue(dialogue)
        self._post_message(text, channel)
