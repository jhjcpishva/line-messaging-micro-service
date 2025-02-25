import logging
import time
import io
from uuid import uuid4

import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response

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
    secure=False,
    logger=logger,
    public_url=config.S3_STORAGE_PUBLIC_URL,
)


@app.get(f"{config.CONTEXT_PATH}speech")
async def speech():
    timestamp = int(time.time())
    filename = f"{timestamp}_aivisspeech-synthesis_{uuid4()}.mp3"
    logger.info(f"filename: {filename}")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{config.AIVIS_SPEECH_FAST_API_URL}/synthesis?text=Hello%20World!", timeout=None)
        media_type = response.headers.get('Content-Type')
        audio_data = response.content
    result = storage.put_file(config.S3_STORAGE_BUCKET_NAME, filename, io.BytesIO(audio_data), len(audio_data), media_type)

    return JSONResponse({"upload": storage.get_public_url(result), "media_type": media_type})


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
