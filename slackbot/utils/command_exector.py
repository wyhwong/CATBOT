import yaml
import logging
from slack_sdk.web import WebClient

from common_utils.mqtt import Publisher, MQTTMessage
from common_utils.common import read_content_from_yml
from common_utils.logger import get_logger

LOGGER = get_logger(logger_name="Utils | Command Exector")


class SlackCommandExector:
    def __init__(self, status, web_client: WebClient, publisher: Publisher) -> None:
        self.publisher = publisher
        self.topic = "slackbot-pub"
        self.web_client = web_client
        self.status = status
        self.targets = []
        self.supported_targets = self._load_supported_cryptocurrencies()
        self.commands = self._load_command_list().keys()

    def _load_supported_cryptocurrencies(self) -> list:
        return read_content_from_yml(path="./configs/supported_cryptocurrencies.yml")

    def _load_command_list(self) -> list:
        return read_content_from_yml(path="./configs/commands.yml")

    def _prepare_help_message(self) -> str:
        commands = self._load_command_list()
        message = "Available commands are the following:\n"
        for command, content in commands.items():
            message += f"\t - {command}: {content} \n"
        return message

    def _post_message(self, text: str, channel: str) -> None:
        LOGGER.info(f"Sending message to Slack, channel: {channel}, text: {text}")
        sent_message = self.web_client.chat_postMessage(channel=channel, text=text)["ok"]
        LOGGER.info(f"Successfully sent message: {sent_message}")

    def _post_image(self, title: str, file: str, channel: str) -> None:
        LOGGER.info(f"Sending image to Slack, channel: {channel}, file: {file}")
        sent_image = self.web_client.files_upload_v2(title=title, file=file, channel=channel)
        LOGGER.info(f"Successfully sent image: {sent_image}")

    def help(self, text: str, user: str, channel: str) -> None:
        if text == "help":
            LOGGER.info(f"Sending help message, channel: {channel}")
            self._post_message(text=self._prepare_help_message(), channel=channel)
        else:
            LOGGER.info(f"Invalid command, send ask message, channel: {channel}")
            self._post_message(text='Invalid command, do you mean "help"?', channel=channel)

    def send(self, text: str, user: str, channel: str) -> None:
        self._post_message(text, channel)

    def target(self, text: str, user: str, channel: str) -> None:
        targets = text.split(" ")[1:]
        if len(targets) == 0:
            message = "Target is not specified, ignored the target command."
            LOGGER.info(message)
            self._post_message(text=message, channel=channel)
            return
        LOGGER.info("Updating targeted cryptocurrencies...")
        for target in targets:
            if target not in self.supported_targets:
                message = "The target is not supported, skipped."
                LOGGER.warning(message)
                self._post_message(text=message, channel=channel)
            else:
                self.targets.append(target)
                LOGGER.info(f"Added {target} to targets.")

        message = f"Targets updated, {self.targets}."
        LOGGER.info(message)
        self._post_message(text=message, channel=channel)

    def analyze(self, text: str, user: str, channel: str):
        if text == "analyze" and self.taregts:
            LOGGER.info(f"Starting analysis...")
            for idx, target in enumerate(self.targets):
                if idx == 0:
                    targets_str = target
                else:
                    targets_str += f"|{target}"
            message = {"targets": targets_str}
            mqtt_message = MQTTMessage.from_str(topic="slackbot-pub", message=str(message))
            self.publisher.publish(message=mqtt_message)
        elif text == "analyze":
            LOGGER.info("No target set. Ignored.")
        else:
            LOGGER.info(f"Invalid command, send ask message, channel: {channel}")
            self._post_message(text='Invalid command, do you mean "analyze"?', channel=channel)

    def visualize(self, text: str, user: str, channel: str):
        args = text.split(" ")
