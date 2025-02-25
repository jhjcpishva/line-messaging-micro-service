import logging
import time
import io
from uuid import uuid4

import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from mutagen.mp3 import MP3

import config
from line_messaging import LineMessaging
from s3_storage import S3Storage

logger = logging.getLogger('uvicorn.app')

app = FastAPI()

lm = LineMessaging(access_token=config.LINE_CHANNEL_ACCESS_TOKEN, logger=logger)
storage = S3Storage(
    host=config.S3_STORAGE_HOST,
    access_key=config.S3_STORAGE_ACCESS_KEY,
    secret_key=config.S3_STORAGE_SECRET_KEY,
    secure=config.S3_STORAGE_SECURE,
    logger=logger,
    public_url=config.S3_STORAGE_PUBLIC_URL,
)


@app.get(f"{config.CONTEXT_PATH}speech")
async def speech():
    timestamp = int(time.time())
    filename = f"{timestamp}_aivisspeech-synthesis_{uuid4()}.mp3"
    logger.info(f"filename: {filename}")
    
    # Generate speech mp3 using AIVIS Speech API
    async with httpx.AsyncClient() as client:
        params = {
            "text": "Hello World!",
            "volume": 0.3,
            "pitch": 0,
            "speed": 1,
            "format": "mp3",
        }
        audio_response = await client.get(f"{config.AIVIS_SPEECH_FAST_API_URL}/synthesis",params=params, timeout=None)
        media_type = audio_response.headers.get('Content-Type')
        audio_data = audio_response.content

    # Get audio length
    # Note: LINE AudioMessage still works even `audio_length = 0`, following documentation for now but might able to skip dependency
    audio_length = MP3(io.BytesIO(audio_data)).info.length  # seconds in float
    audio_length = int(audio_length * 1000)
        
    # Upload to S3 bucket
    s3_result = storage.put_file(config.S3_STORAGE_BUCKET_NAME, filename, io.BytesIO(audio_data), len(audio_data), media_type)

    # Send to LINE Messaging API
    lm_result = lm.push_audio_message("U123...", audio_url=storage.get_public_url(s3_result), audio_length=audio_length)

    return JSONResponse({
        "upload": storage.get_public_url(s3_result), 
        "media_type": media_type, 
        "duration": audio_length,
        "lm_result": lm_result.to_dict(),
        })


@app.get(f"{config.CONTEXT_PATH}debug")
async def debug():
    # result = lm.push_text_message("U123...", "message")
    result = storage.list_files(config.S3_STORAGE_BUCKET_NAME)
    # data = b"Hello World!"
    # result = storage.put_file(config.S3_STORAGE_BUCKET_NAME, "test.txt", io.BytesIO(data), len(data), "text/plain", metadata={"key1":"value1"})
    # return Response(storage.fetch_file(config.S3_STORAGE_BUCKET_NAME, "test.txt").read(), media_type="text/plain")
    return JSONResponse({"items": [r.__dict__ for r in result]})

@app.get(f"{config.CONTEXT_PATH}health")
async def health_check():
    return JSONResponse({ "timestamp": int(time.time()) })


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=True)
