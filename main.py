import logging
import time

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


@app.get(f"{config.CONTEXT_PATH}debug")
async def debug():
    # result = lm.push_text_message("U123...", "message")
    result = storage.list_files("line-messaging-micro-service")
    # data = b"Hello World!"
    # result = storage.put_file("line-messaging-micro-service", "test.txt", io.BytesIO(data), len(data), "text/plain", metadata={"key1":"value1"})
    # return Response(storage.fetch_file("line-messaging-micro-service", "test.txt").read(), media_type="text/plain")
    return JSONResponse({"items": result})

@app.get(f"{config.CONTEXT_PATH}health")
async def health_check():
    return JSONResponse({ "unix": int(time.time()) })


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=True)
