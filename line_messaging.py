import logging
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    PushMessageRequest,
    PushMessageResponse,
    TextMessage,
)


class LineMessaging:
    logger: logging.Logger
    config: Configuration
    def __init__(self, access_token: str, logger: logging.Logger):
        self.config = Configuration(access_token=access_token)
        self.logger = logger
        
    def push_text_message(self, to: str, text: str) -> PushMessageResponse:
        with ApiClient(self.config) as api_client:
            line_bot_api = MessagingApi(api_client)
            result = line_bot_api.push_message(PushMessageRequest(
                to=to,
                messages=[TextMessage(text=text.strip())]
            ))
            return result
