#!/usr/bin/env python3
import os
from time import sleep
from threading import Thread
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.web import WebClient

from common_utils.mqtt import Broker, Subscriber, Publisher
from common_utils.common import get_logger
from slackbot.utils.handler import SlackMessageHandler

LOGGER = get_logger(logger_name="Main | Slackbot")


def main():
    LOGGER.info("Initializing slackbot components...")
    app = App(token=os.getenv("SLACK_TOKEN"))
    slack_user_id = os.getenv("SLACK_USER_ID")
    web_client = WebClient(token=os.getenv("SLACK_TOKEN"), logger=LOGGER)
    subscriber = Subscriber(client_id="slackbot-sub", broker=Broker(), topic="stats-analyzer-pub", handlers=[])
    publisher = Publisher(client_id="slackbot-pub", broker=Broker())
    handler = SlackMessageHandler(web_client=web_client, user_id=slack_user_id, publisher=publisher, subscriber=subscriber)
    LOGGER.info("Initialized slack components.")

    @app.event("message")
    def on_message(body):
        handler.handle_message(body["event"])

    socket_mode_handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    Thread(socket_mode_handler.start, daemon=True).start()

    analysis_interval = int(os.getenv("ANALYSIS_INTERVAL_IN_SECOND"))
    while True:
        LOGGER.info("Initializing new analysis...")
        handler.start_analysis()
        sleep(analysis_interval)


if __name__ == "__main__":
    main()
