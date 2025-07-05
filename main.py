from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from utils.exceptions import *
from application.api.v1 import v1
import datetime


# from middleware import Middle

app = FastAPI()



@app.exception_handler(Error)
async def exceptionHandler(request: Request, exc:Error):
    error = {"responseData": {"message": "FAILURE", "reason": exc.details}}
    return JSONResponse(status_code=exc.status_code,content=error)


app.include_router(v1, prefix="/v1")