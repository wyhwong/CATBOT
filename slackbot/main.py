#!/usr/bin/env python3
import os
from time import sleep
from threading import Thread
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.web import WebClient

from common_utils.mqtt import Broker, Subscriber, Publisher
from common_utils.common import get_logger
from utils.handler import SlackMessageHandler

LOGGER = get_logger("Slackbot")
MODE = os.getenv("MODE")


def main():
    app = App(token=os.getenv("SLACK_TOKEN"))
    slack_user_id = os.getenv("SLACK_USER_ID")
    web_client = WebClient(token=os.getenv("SLACK_TOKEN"), logger=LOGGER)
    subscriber = Subscriber("slackbot-sub", Broker(), "stats-analyzer-pub", [])
    publisher = Publisher("slackbot-pub", Broker())
    handler = SlackMessageHandler(web_client, slack_user_id, publisher, subscriber)
    LOGGER.info("Initialized slack components.")

    @app.event("message")
    def on_message(body):
        handler.handle_message(body["event"])

    socket_mode_handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    Thread(target=socket_mode_handler.start, daemon=True).start()

    analysis_interval = int(os.getenv("ANALYSIS_INTERVAL_IN_SECOND"))
    while True:
        sleep(analysis_interval)
        handler.start_analysis()
        LOGGER.info("Initializing new analysis...")


if __name__ == "__main__":
    if MODE != "prod":
        LOGGER.info(f"Running in non-prod mode {MODE}, Sleep forever...")
        while True:
            sleep(60)
    main()
