import os
import pandas as pd
from time import sleep
from slack_sdk.web import WebClient

from common_utils.mqtt import Publisher, MQTTMessage
from common_utils.common import load_yml
from common_utils.logger import get_logger

LOGGER = get_logger("slackbot/utils/command_exector")


def _load_supported_cryptocurrencies() -> list:
    """
    Load supported cryptocurrencies from yml file.

    Args:
        None.
    Returns:
        Supported cryptocurrencies (list).
    """
    return load_yml("./configs/slackbot/supported_cryptocurrencies.yml")


def _load_command_list() -> dict:
    """
    Load command list from yml file.

    Args:
        None.
    Returns:
        Command list (dict).
    """
    return load_yml("./configs/slackbot/commands.yml")


class SlackCommandExector:
    """
    Slackbot Command Exector.
    """

    def __init__(self, web_client: WebClient, publisher: Publisher) -> None:
        """
        Initialize Slackbot Command Exector.

        Args:
            web_client (WebClient): WebClient of Slack.
            publisher (Publisher): Publisher for publishing messages to MQTT.
        Returns:
            None.
        """
        LOGGER.debug("Initializing Slackbot Command Exector...")
        self.publisher = publisher
        self.topic = "slackbot-pub"
        self.web_client = web_client
        self.log_channel = None
        self.targets = []
        self.last_analysis_time = None
        analysis_waittime = float(os.getenv("ANALYSIS_WAITTIME", 0.0))
        self.analysis_waittime = pd.Timedelta(seconds=analysis_waittime)
        self.supported_targets = _load_supported_cryptocurrencies()
        self.commands = _load_command_list()
        LOGGER.debug("Initialized Slackbot Command Exector.")

    def wait_if_after_analysis(self) -> None:
        """
        Wait if the analysis is just after.

        Args:
            None.
        Returns:
            None.
        """
        if self.last_analysis_time:
            analysis_aftertime = pd.Timestamp.now() - self.last_analysis_time
            if analysis_aftertime < self.analysis_waittime:
                timediff_in_secs = (
                    self.analysis_waittime - analysis_aftertime
                ).total_seconds()
                LOGGER.info(
                    f"Just after analysis, sleep for {timediff_in_secs} secs..."
                )
                sleep(timediff_in_secs)

    def _prepare_help_message(self) -> str:
        """
        Prepare help message.

        Args:
            None.
        Returns:
            Help message (str).
        """
        message = "Available commands are the following:\n"
        for command, content in self.commands.items():
            message += f"\t {command}: {content['description']}\n"
            message += f"\t \t - format: {content['format']}\n"
            if content.get("example", None):
                message += f"\t \t - example: {content['example']}\n"
            message += f"\t \t - require privilege: {content['require_privilege']}\n"
        message += "\nSupported list of cryptocurrencies are the following:\n"
        for supported_target in self.supported_targets:
            message += f"\t - {supported_target} \n"
        return message

    def _post_message(self, text: str, channel: str) -> None:
        """
        Post message to Slack.

        Args:
            text (str): Text of the message.
            channel (str): Channel of the message.
        Returns:
            None.
        """
        LOGGER.debug(f"Sending message to Slack, channel: {channel}, text: {text}")
        sent_message = self.web_client.chat_postMessage(channel=channel, text=text)[
            "ok"
        ]
        LOGGER.info(f"Successfully sent message: {sent_message}")

    def _post_attachment(self, title: str, file: str, channel: str) -> None:
        """
        Post attachment to Slack.

        Args:
            title (str): Title of the attachment.
            file (str): File of the attachment.
            channel (str): Channel of the attachment.
        Returns:
            None.
        """
        LOGGER.debug(f"Sending attachment to Slack, channel: {channel}, file: {file}")
        sent_attachment = self.web_client.files_upload_v2(
            title=title, file=file, channel=channel
        )
        LOGGER.info(f"Successfully sent attachment: {sent_attachment}")

    def help(self, text: str, user: str, channel: str) -> None:
        """
        Help command.

        Args:
            text (str): Text of the message.
            user (str): User of the message.
            channel (str): Channel of the message.
        Returns:
            None.
        """
        if text == "help":
            LOGGER.info(f"Sending help message, channel: {channel}")
            self._post_message(self._prepare_help_message(), channel)
        else:
            LOGGER.info(f"Invalid command, send ask message, channel: {channel}")
            self._post_message('Invalid command, do you mean "help"?', channel)

    def set_log(self, text: str, user: str, channel: str) -> None:
        """
        Set log command.

        Args:
            text (str): Text of the message.
            user (str): User of the message.
            channel (str): Channel of the message.
        Returns:
            None.
        """
        LOGGER.info(f"Set channel for logging: from {self.log_channel} to {channel}...")
        self.log_channel = channel
        self._post_message("Set this channel for logging.", channel)

    def unset_log(self, text: str, user: str, channel: str) -> None:
        """
        Unset log command.

        Args:
            text (str): Text of the message.
            user (str): User of the message.
            channel (str): Channel of the message.
        Returns:
            None.
        """
        LOGGER.info(f"Unset channel for logging: {self.log_channel=}...")
        if text == "unset" and channel == self.log_channel:
            self.log_channel = None
            self._post_message("Unset this channel for logging.", channel)

    def target(self, text: str, user: str, channel: str) -> None:
        """
        Target command.

        Args:
            text (str): Text of the message.
            user (str): User of the message.
            channel (str): Channel of the message.
        Returns:
            None.
        """
        targets = text.upper().split(" ")[1:]
        if len(targets) == 0:
            message = "Target is not specified, ignored the target command."
            self._post_message(message, channel)
            return
        LOGGER.info("Updating targeted cryptocurrencies...")
        for target in targets:
            if target not in self.supported_targets:
                message = f"The target ({target}) is not supported, skipped."
                self._post_message(message, channel)
            elif target in self.targets:
                message = f"The target ({target}) is already in targets, skipped."
            else:
                self.targets.append(target)
                LOGGER.info(f"Added {target} to targets.")
        message = f"Targets updated, {self.targets}."
        self._post_message(message, channel)

    def list_targets(self, text: str, user: str, channel: str) -> None:
        """
        List targets command.

        Args:
            text (str): Text of the message.
            user (str): User of the message.
            channel (str): Channel of the message.
        Returns:
            None.
        """
        if text == "list_targets" and self.targets:
            message = f"Current targets: {self.targets}."
            self._post_message(message, channel)
        elif text == "list_targets":
            message = "Currently there are no targets."
            self._post_message(message, channel)
        else:
            LOGGER.info(f"Invalid command, send ask message, channel: {channel}")
            self._post_message('Invalid command, do you mean "list_targets"?', channel)

    def untarget(self, text: str, user: str, channel: str) -> None:
        """
        Untarget command.

        Args:
            text (str): Text of the message.
            user (str): User of the message.
            channel (str): Channel of the message.
        Returns:
            None.
        """
        untargets = text.upper().split(" ")[1:]
        for untarget in untargets:
            if untarget in self.targets:
                self.targets.remove(untarget)
            else:
                message = f"The untarget ({untarget}) is not in self.targets, skipped."
                self._post_message(message, channel)

        message = f"Targets updated, {self.targets}."
        self._post_message(message, channel)

    def analyze(self, text: str, user: str, channel: str) -> None:
        """
        Analyze command.

        Args:
            text (str): Text of the message.
            user (str): User of the message.
            channel (str): Channel of the message.
        Returns:
            None.
        """
        if text == "analyze":
            LOGGER.info(f"Starting analysis...")
            target_scores = {}
            for target in self.targets:
                target_scores[target] = {}
            message = str({"scores": target_scores})
            mqtt_message = MQTTMessage.from_str("slackbot-pub", message)
            self.publisher.publish(mqtt_message)
            self.last_analysis_time = pd.Timestamp.now()
        else:
            LOGGER.info(f"Invalid command, send ask message, channel: {channel}")
            self._post_message('Invalid command, do you mean "analyze"?', channel)

    def t_analyze(self, text: str, user: str, channel: str) -> None:
        """
        T-Analyze command.

        Args:
            text (str): Text of the message.
            user (str): User of the message.
            channel (str): Channel of the message.
        Returns:
            None.
        """
        if not self.log_channel:
            LOGGER.info(
                f"Log channel not set, set channel for logging: from {self.log_channel} to {channel}..."
            )
            self.log_channel = channel
            self._post_message(
                "Log channel not set, set this channel for logging.", channel
            )
        keywords = text.split(" ")[1:]
        LOGGER.info(f"Starting text analysis for {keywords=}")
        message = str({"tcommand": "keywords_analysis", "args": {"keywords": keywords}})
        mqtt_message = MQTTMessage.from_str("slackbot-pub", message)
        self.publisher.publish(mqtt_message)

    def s_show_klines(self, text: str, user: str, channel: str) -> None:
        """
        S-Show-Klines command.

        Args:
            text (str): Text of the message.
            user (str): User of the message.
            channel (str): Channel of the message.
        Returns:
            None.
        """
        if not self.log_channel:
            LOGGER.info(
                f"Log channel not set, set channel for logging: from {self.log_channel} to {channel}..."
            )
            self.log_channel = channel
            self._post_message(
                "Log channel not set, set this channel for logging.", channel
            )
        args = text.split(" ")[1:]
        if len(args) != 3:
            message = "Wrong command format, please check help."
        target, duration, interval = args
        message = None
        if interval[-1] not in ["s", "m", "d"]:
            message = 'Unit of interval should be in ["s", "m", "d"].'
        try:
            int(interval[:-1])
            float(duration)
        except ValueError:
            message = "Type of duration should be float / Value in interval should be integer."
        finally:
            if message:
                self._post_message(message, channel)
            else:
                message = str(
                    {
                        "scommand": "show_klines",
                        "args": {
                            "target": target,
                            "duration": duration,
                            "interval": interval,
                        },
                    }
                )
                mqtt_message = MQTTMessage.from_str("slackbot-pub", message)
                self.publisher.publish(mqtt_message)

    def s_show_last_predict(self, text: str, user: str, channel: str) -> None:
        """
        S-Show-Last-Predict command.

        Args:
            text (str): Text of the message.
            user (str): User of the message.
            channel (str): Channel of the message.
        Returns:
            None.
        """
        if not self.log_channel:
            LOGGER.info(
                f"Log channel not set, set channel for logging: from {self.log_channel} to {channel}..."
            )
            self.log_channel = channel
            self._post_message(
                "Log channel not set, set this channel for logging.", channel
            )
        args = text.split(" ")[1:]
        message = None
        if len(args) != 1:
            message = "Wrong command format, please check help."
        if args[0].upper() not in self.targets:
            message = (
                f"Not able to show, target {args[0].upper()} is not in list of targets."
            )
        if message:
            self._post_message(message, channel)
        else:
            message = str(
                {"scommand": "show_last_predict", "args": {"target": args[0].upper()}}
            )
            mqtt_message = MQTTMessage.from_str("slackbot-pub", message)
            self.publisher.publish(mqtt_message)

    def post(self, command_args: dict) -> None:
        """
        Post command.

        Args:
            command_args (dict): Command arguments.
        Returns:
            None.
        """
        posttype = command_args.get("type", None)
        if posttype in ["csv", "png"]:
            self._post_attachment(
                "User requested analysis results",
                command_args.get("path", None),
                self.log_channel,
            )

    def log_scores(self, scores: dict) -> None:
        """
        Log scores to Slack channel.

        Args:
            scores (dict): Scores of the targets.
        Returns:
            None.
        """
        LOGGER.info(f"Logging scores to Slack channel: {scores}...")
        message = f"Logging:"
        for target in self.targets:
            message += f"\n\t- {target}:"
            for analyzer, score in scores[target].items():
                message += f" {analyzer}: {score:.3f} |"
        LOGGER.info(message)
        if self.log_channel:
            self._post_message(message, self.log_channel)
