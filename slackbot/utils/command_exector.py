from slack_sdk.web import WebClient

from common_utils.mqtt import Publisher, MQTTMessage
from common_utils.common import read_content_from_yml
from common_utils.logger import get_logger

LOGGER = get_logger(logger_name="Utils | Command Exector")


def _load_supported_cryptocurrencies() -> list:
        return read_content_from_yml(path="./configs/supported_cryptocurrencies.yml")


def _load_command_list() -> dict:
    return read_content_from_yml(path="./configs/commands.yml")


class SlackCommandExector:
    def __init__(self, web_client: WebClient, publisher: Publisher) -> None:
        self.publisher = publisher
        self.topic = "slackbot-pub"
        self.web_client = web_client
        self.log_channel = None
        self.targets = []
        self.supported_targets = _load_supported_cryptocurrencies()
        self.commands = _load_command_list()

    def _prepare_help_message(self) -> str:
        message = "Available commands are the following:\n"
        for command, content in self.commands.items():
            message += f"\t - {command}: {content} \n"
        message += "Supported list of cryptocurrencies are the following:\n"
        for supported_target in self.supported_targets:
            message += f"\t - {supported_target} \n"
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

    def set_log(self, text: str, user: str, channel: str) -> None:
        LOGGER.info(f"Set channel for logging: from {self.log_channel} to {channel}...")
        self.log_channel = channel

    def target(self, text: str, user: str, channel: str) -> None:
        targets = text.upper().split(" ")[1:]
        if len(targets) == 0:
            message = "Target is not specified, ignored the target command."
            self._post_message(text=message, channel=channel)
            return
        LOGGER.info("Updating targeted cryptocurrencies...")
        for target in targets:
            if target not in self.supported_targets:
                message = "The target is not supported, skipped."
                self._post_message(text=message, channel=channel)
            else:
                self.targets.append(target)
                LOGGER.info(f"Added {target} to targets.")

        message = f"Targets updated, {self.targets}."
        self._post_message(text=message, channel=channel)

    def analyze(self, text: str, user: str, channel: str) -> None:
        if text == "analyze" and self.targets:
            LOGGER.info(f"Starting analysis...")
            target_scores = {}
            for target in self.targets:
                target_scores[target] = {}
            message = str(target_scores)
            mqtt_message = MQTTMessage.from_str(topic="slackbot-pub", message=str(message))
            self.publisher.publish(message=mqtt_message)
        elif text == "analyze":
            LOGGER.info("No target set. Ignored.")
        else:
            LOGGER.info(f"Invalid command, send ask message, channel: {channel}")
            self._post_message(text='Invalid command, do you mean "analyze"?', channel=channel)

    def show_last_visuals(self, text: str, user: str, channel: str) -> None:
        for target in self.targets:
            self._post_image(self,
                             title=f"{target}_last_visuals",
                             file=f"/data/{target}_last_vis.png",
                             channel=channel)

    def log_scores(self, scores: dict) -> None:
        LOGGER.info(f"Logging scores to Slack channel: {scores}...")
        for target in self.targets:
            message = f"Logging ({target}): "
            for analyzer, score in scores[target].items():
                message += f"\t {analyzer}: {score}"
            LOGGER.info(message)
            if self.log_channel:
                self._post_message(text=message, channel=self.log_channel)
