from requests.sessions import Request
from fastapi import BackgroundTasks, FastAPI, Header, Response, Form, Depends, Request, File
from fastapi import UploadFile
from typing import Optional
import re
from pydantic import BaseModel
import os
from fastapi.responses import JSONResponse as JsonResponse
from fastapi.encoders import jsonable_encoder as create_json
from typing import Any, Dict
import time
from bots import add_file_TIND, add_file_frontier, add_file_piedmont, add_file_INI
#import bots
from pydantic.types import JsonMeta
import logging
import sys
from Utils import *
from pydantic import BaseModel
import json
import requests




app: FastAPI = FastAPI(title="Innovative Precision Health Bot Processing",
                       description="This is the documentation for the IPH Bot Automation. Latest Updates: support for new data models, gait post support, PRO post support.",
                       version="1.0.0")

VERIFICATION_TOKEN="splice_test"
 
@app.get("/")
def hello():
    return {"result": "Sury did it, suck a dick world -Main2"}



@app.post('/TIND_Process')
async def ecw_upload(body: dict):
    try:
        print("Recieved file, uploading now")
        mrn=body['mrn']
        filename=body['filename']
        response=add_file_TIND(mrn, filename)
        return("Processing Upload"+", "+str(response))
    except Exception as e:
        print(e)
        return("Not working: "+str(e))


@app.post('/Frontier_Process')
async def athena_upload(body:dict):
    try: 
        print("Recieved file, uploading now")
        mrn=body['mrn']
        filename=body['filename']
        response=add_file_frontier(mrn, filename)
        return("Processing Upload"+", "+str(response))
    except Exception as e:
        print(e)
        return("Not working: "+str(e))


@app.post('/Piedmont_Process')
async def athena_upload(body:dict):
    try:
        print("Recieved file, uploading now")
        mrn=body['mrn']
        filename=body['filename']
        response=add_file_piedmont(mrn, filename, 0)
        return("Processing Upload"+", "+str(response))
    except Exception as e:
        print(e)
        return("Not working: "+str(e))



@app.post("/INI_Process")
async def INI_upload(body:dict):
    try:
        print("Recieved file, uploading now")
        mrn=body['mrn']
        filename=body['filename']
        response=add_file_INI(mrn, filename)
        return("Processing Upload"+", "+str(response))
    except Exception as e:
        print(e)
        return("Not working: "+str(e))



@app.post("/uploadfile/")
async def download_file(file: UploadFile = File(...)):
    print("downloading file")
    file_location = file.filename
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    return("Processing upload to Bot")


@app.post('/billing')
def billing_request(body:dict):
    print("Recieved Billing Request")
    if body['securityKey']!=f'{VERIFICATION_TOKEN}':
        return "security key is not valid"
    
    clinicID = body['clinic_ID']
    url = f"https://aiq.burstiq.com/api/iq/PROD_BILLING_TABLE/query"
    query=f"where CLINIC_ID = '{clinicID}'"
    payload = json.dumps({
        f"queryTql": f"SELECT * FROM PROD_BILLING_TABLE {query} ORDER BY DATE_OF_REPORT DESC"
    })
    headers = {
    'Authorization': 'Basic aW5mb0BpcGguYWk6MlBlbm5zd2F5ISEh',
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return(response.json())