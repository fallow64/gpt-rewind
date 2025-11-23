from typing import Union
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sqlite3
from generate_audio import transcribe

app = FastAPI()


@app.post("/conversation")

@app.get("/data/{randomId}/insights")

@app.get("/data/{randomId}/sounds/{pageIndex}")
async def getSoundFile(randomId: str, pageIndex: int):
    file_path = os.path.join(os.getcwd(), "user", randomId, "sound", f"{pageIndex}.mp3")
    
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=file_path)
    else:
        raise HTTPException(status_code=404, detail="Item not found")









# GET /user/userId/insights -> JSON results
# GET /user/userId/sound/index -> Sound for slide index=
# POST /user/userId/conversation -> upload file to process
#
#
