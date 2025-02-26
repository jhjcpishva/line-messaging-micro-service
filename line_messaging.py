import logging
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    PushMessageRequest,
    PushMessageResponse,
    TextMessage,
    AudioMessage,
    ImageMessage,
    Message,
)


class LineMessaging:
    logger: logging.Logger
    config: Configuration
    def __init__(self, access_token: str, logger: logging.Logger):
        self.config = Configuration(access_token=access_token)
        self.logger = logger
        
    def push_message(self, to: str, messages: list[Message]) -> PushMessageResponse:
        with ApiClient(self.config) as api_client:
            line_bot_api = MessagingApi(api_client)
            result = line_bot_api.push_message(PushMessageRequest(
                to=to,
                messages=messages
            ))
            return result
        
    def push_text_message(self, to: str, text: str) -> PushMessageResponse:
        return self.push_message(to, [TextMessage(text=text.strip())])

    def push_audio_message(self, to: str, text: str=None, audio_url: str=None, audio_length=None) -> PushMessageResponse:
        messages: list[Message] = []
        if text is not None:
            messages.append(TextMessage(text=text.strip()))
        if audio_url is not None:
            if audio_length is None:
                raise ValueError("Audio length must be provided when audio URL is given")
            messages.append(AudioMessage(originalContentUrl=audio_url, duration=audio_length))
            
        if len(messages) == 0:
            raise ValueError("No message to send")
            
        return self.push_message(to, messages)

    def push_image_message(self, to: str, text: str=None, image_url: str=None) -> PushMessageResponse:
        messages: list[Message] = []
        if text is not None:
            messages.append(TextMessage(text=text.strip()))
        if image_url is not None:
            messages.append(ImageMessage(originalContentUrl=image_url, previewImageUrl=image_url))
            
        if len(messages) == 0:
            raise ValueError("No message to send")
            
        return self.push_message(to, messages)
