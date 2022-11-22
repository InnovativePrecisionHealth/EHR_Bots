'''
Minimal example using fastAPI.
'''
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel




app = FastAPI()


@app.get("/")
def hello():
    return {"Sury did it": "suck a dick world"}
