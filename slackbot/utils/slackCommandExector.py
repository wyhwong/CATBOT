import yaml
import logging
from slack_sdk.web import WebClient

from common_utils.mqtt import Publisher


class SlackCommandExector:
    def __init__(self, status, web_client: WebClient, publisher: Publisher, logger: logging.Logger) -> None:
        self.logger = logger
        self.publisher = publisher
        self.topic = "slackbot-pub"
        self.web_client = web_client
        self.status = status
        self.commands = self._load_command_list().keys()

    def _load_command_list(self) -> list:
        with open("config/commands.yml", "r") as file:
            return yaml.load(file, Loader=yaml.SafeLoader)

    def _prepare_help_message(self) -> str:
        commands = self._load_command_list()
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
            self._post_message(text=self._prepare_help_message(), channel=channel)
        else:
            self.logger.info(f"Invalid command, send ask message, channel: {channel}")
            self._post_message(text='Invalid command, do you mean "help"?', channel=channel)

    def send(self, text: str, user: str, channel: str, dialogue: bool = None) -> None:
        if dialogue:
            text = self._load_dialogue(dialogue)
        self._post_message(text, channel)
