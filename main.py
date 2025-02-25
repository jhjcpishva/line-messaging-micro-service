import logging
import time

from fastapi import FastAPI
from fastapi.responses import JSONResponse

import config
from line_messaging import LineMessaging


logger = logging.getLogger('uvicorn.app')

app = FastAPI()

lm = LineMessaging(access_token=config.LINE_CHANNEL_ACCESS_TOKEN, logger=logger)


@app.post(f"{config.CONTEXT_PATH}synthesis")
async def speech():

    return 

@app.get(f"{config.CONTEXT_PATH}debug")
async def debug():
    result = lm.push_text_message("U123...", "message")
    return result

@app.get(f"{config.CONTEXT_PATH}health")
async def health_check():
    return JSONResponse({ "unix": int(time.time()) })


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=True)
