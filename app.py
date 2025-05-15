from typing import Union, Annotated
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json, dotenv, modele

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
def read_root():
    return {"Hello": "World !"}

@app.get("/question", response_class=HTMLResponse)
@app.post("/question", response_class=HTMLResponse)
def get_question(request: Request, question: Annotated[str, Form()] = None, course: Annotated[str, Form()] = None):
    print(f"get_question {question=} {course}")

    answer=modele.question(course, question) if question else None

    return templates.TemplateResponse(
        request=request, name="question.html", context={
            "question": question,
            "course": course,
            "courses": modele.get_courses(),
            "answer": answer
        }
    )


@app.get("/courses")
def get_courses():
    # Liste les cours
    return modele.get_courses()

@app.get("/threads_id")
def get_threads_id(course_id:str=None):
    # Liste les _id des fils d'un cours (RE)
    print(f"get_threads_id {course_id=}")
    return modele.get_threads_id(course_id)

@app.get("/extract")
def get_extract(id:str=None, course_id:str=None):
    # Extraction de thread
    print(f"get_extract {id=} {course_id=}")
    return modele.extract(id, course_id)

