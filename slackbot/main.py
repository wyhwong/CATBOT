#!/usr/bin/env python3
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.web import WebClient

from common_utils.mqtt import Broker, Subscriber, Publisher
from common_utils.common import get_logger
from slackbot.utils.handler import SlackMessageHandler


def main():
    logger = get_logger("Slackbot")
    app = App(token=os.getenv("SLACK_TOKEN"))
    web_client = WebClient(token=os.getenv("SLACK_TOKEN"), logger=logger)
    subscriber = Subscriber(client_id="slackbot-sub", broker=Broker(), topic="chatgpt-pub")
    publisher = Publisher(client_id="slackbot-pub", broker=Broker())
    handler = SlackMessageHandler(web_client, publisher, subscriber, logger)

    @app.event("message")
    def on_message(body):
        handler.handle_message(body["event"])

    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()


if __name__ == "__main__":
    main()
