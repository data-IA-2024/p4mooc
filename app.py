from typing import Union
from fastapi import FastAPI
import json, dotenv, modele

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/courses")
def get_courses():
    return modele.get_courses()
