import logging
import time
import io
import json
import tomllib
from uuid import uuid4
from typing import Union

import httpx
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from mutagen.mp3 import MP3

import config
from line_messaging import LineMessaging
from s3_storage import S3Storage

logger = logging.getLogger('uvicorn.app')

config.verify()

app = FastAPI(debug=True)

lm = LineMessaging(
    access_token=config.LINE_CHANNEL_ACCESS_TOKEN, logger=logger)
storage = S3Storage(
    host=config.S3_STORAGE_HOST,
    access_key=config.S3_STORAGE_ACCESS_KEY,
    secret_key=config.S3_STORAGE_SECRET_KEY,
    secure=config.S3_STORAGE_SECURE,
    logger=logger,
    public_url=config.S3_STORAGE_PUBLIC_URL,
)

# collect version
with open('pyproject.toml', 'rb') as f:
    running_version = tomllib.load(f).get('project', {}).get('version', {})


class PushMessageTextRequest(BaseModel):
    text: str


class PushMessageTTSRequest(BaseModel):
    tts: str
    text: Union[str, None] = None
    volume: Union[float, None] = None
    pitch: Union[float, None] = None
    speed: Union[float, None] = None
    speaker: Union[int, None] = None


@app.post(f"{config.CONTEXT_PATH}v1/push_message/{{user_id}}/text")
async def push_simple_text(user_id: str, body: PushMessageTextRequest):
    logger.info(f"push_message user_id: {user_id}")
    result = lm.push_text_message(user_id, text=body.text)
    return JSONResponse(result.to_dict())


@app.post(f"{config.CONTEXT_PATH}v1/push_message/{{user_id}}/tts")
async def push_message_tts(user_id: str, body: PushMessageTTSRequest):
    logger.info(f"push_message user_id: {user_id}")

    timestamp = int(time.time())
    filename = f"{config.S3_STORAGE_TTS_UPLOAD_PATH}/{timestamp}_aivisspeech-synthesis_{uuid4()}"
    logger.info(f"filename: {filename}")

    # Generate speech mp3 using AIVIS Speech API
    async with httpx.AsyncClient() as client:
        params = {
            "text": body.tts,
            "format": "mp3",
        }
        if body.volume:
            params["volume"] = body.volume
        if body.pitch:
            params["pitch"] = body.pitch
        if body.speed:
            params["speed"] = body.speed
        if body.speaker:
            params["speaker"] = body.speaker

        audio_response = await client.get(f"{config.AIVIS_SPEECH_FAST_API_URL}/synthesis", params=params, timeout=None)
        media_type = audio_response.headers.get('Content-Type')
        audio_data = audio_response.content

    # Get audio length
    # Note: LINE AudioMessage still works even `audio_length` is fake value. Probably used for audio length preview before loading
    audio_length = MP3(io.BytesIO(audio_data)).info.length  # seconds in float
    audio_length = int(audio_length * 1000)

    # Upload to S3 bucket
    s3_result = storage.put_file(config.S3_STORAGE_BUCKET_NAME, f"{filename}.mp3", io.BytesIO(
        audio_data), len(audio_data), media_type)

    # Upload meta data to S3 bucket
    meta_json = json.dumps({
        "tts": body.tts,
        "audio_length": audio_length
    })
    s3_result_meta = storage.put_file(config.S3_STORAGE_BUCKET_NAME, f"{filename}.meta.json", io.BytesIO(
        meta_json.encode()), len(meta_json), "application/json")

    # Send to LINE Messaging API
    lm_result = lm.push_audio_message(
        user_id,
        text=body.text,
        audio_url=storage.get_public_url(s3_result),
        audio_length=audio_length,
    )

    return JSONResponse({
        "sentMessages": lm_result.to_dict()["sentMessages"],
        "tts_audio_url": storage.get_public_url(s3_result),
        "tts_audio_duration": audio_length,
    })


@app.post(f"{config.CONTEXT_PATH}v1/push_message/{{user_id}}/image")
async def push_message_image(user_id: str, image: UploadFile = File(), text: Union[str | None] = Form(None)):
    logger.info(f"push_message user_id: {user_id}")
    timestamp = int(time.time())
    filename = f"{config.S3_STORAGE_IMAGE_UPLOAD_PATH}/{timestamp}_image_{uuid4()}"
    [_img, ext] = image.content_type.split("/")

    if _img != "image":
        return JSONResponse({
            "error": f"'{image.content_type}' is not image type",
        }, status_code=400)

    image_content = await image.read()
    s3_result = storage.put_file(config.S3_STORAGE_BUCKET_NAME, f"{filename}.{ext}", io.BytesIO(
        image_content), len(image_content), image.content_type)

    meta_json = json.dumps({
        "filename": image.filename,
    })
    s3_result_meta = storage.put_file(config.S3_STORAGE_BUCKET_NAME, f"{filename}.meta.json", io.BytesIO(
        meta_json.encode()), len(meta_json), "application/json")

    # Send to LINE Messaging API
    lm_result = lm.push_image_message(
        user_id,
        text=text if text is not None and len(text) else None,
        image_url=storage.get_public_url(s3_result),
    )

    return JSONResponse({
        "sentMessages": lm_result.to_dict()["sentMessages"],
        "image_url": storage.get_public_url(s3_result),
    })


@app.get(f"{config.CONTEXT_PATH}health")
async def health_check():
    return JSONResponse({"timestamp": int(time.time())})


@app.get(f"{config.CONTEXT_PATH}version")
async def version():
    return JSONResponse({"version": running_version})


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=True)
