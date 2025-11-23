from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel



app = FastAPI()


@app.get("/user/{userID}/insights")



@app.get("/user/{userID}/sound/{index}")


@app.post("/user/{userID}/conversation")









# GET /user/userId/insights -> JSON results
# GET /user/userId/sound/index -> Sound for slide index=
# POST /user/userId/conversation -> upload file to process
#
#
