import strawberry, typing
import jwt
from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from strawberry.fastapi import GraphQLRouter, BaseContext
from pymongo import MongoClient
import dotenv, os
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from functools import cached_property

dotenv.load_dotenv()  # take environment variables

MONGO_URL=os.environ['MONGO_URL']
client = MongoClient(MONGO_URL)
db = client[os.environ["MONGO_DB"]]

@strawberry.input
class CourseInput:
    name: str=''
    title: str=''
    organisation: str=''

@strawberry.type
class Course(CourseInput):
    _id: str

@strawberry.input
class OrganisationInput:
    name: str='---'

def get_courses_from_orga(root):
    return [Course(**doc) for doc in db['courses'].find({'organisation': root.name})]

@strawberry.type
class Organisation(OrganisationInput):
    _id: str
    courses : typing.List[Course] = strawberry.field(resolver=get_courses_from_orga)

@strawberry.input
class MessageInput:
    title: str = strawberry.field(description="The title of the message")
    username: str
    body: str

@strawberry.type
class Message:
    _id: str
    id: str
    username: str='---'
    user_id: int=-1
    body: str = ''
    type: str = ''
    thread_type: str = ''
    comments_count: int = 0
    context: str = ''
    endorsed: int = ''
    thread_id: str = ''
    title: str = ''
    unread_comments_count: int = 0
    votes: str = ''
    anonymous: bool = ''
    created_at: str = ''
    updated_at: str = ''
    resp_skip: int = 0
    course_id: str = ''
    courseware_url: str = ''
    courseware_title: str = ''
    anonymous_to_peers: str = ''
    children: str=''
    pinned: bool = False
    commentable_id: str = ''
    abuse_flaggers: str = ''
    closed: bool = ''
    resp_total: int = 0
    resp_limit: int = 0
    at_position_list: int = ''
    read: str = ''
    depth: int = -1
    parent_id: str = ''

def get_message_from_user(root):
    print(f"get_message_from_user {root} : ")
    cursor=db['documents'].find({'user_id':str(root.user_id)}) #.limit(limit)
    return [Message(**doc) for doc in cursor]

@strawberry.input
class UserInput:
    user_id: int
    username: str

@strawberry.type
class User(UserInput):
    _id: str=''
    messages : typing.List[Message] = strawberry.field(resolver=get_message_from_user)

def get_orgas():
    query={}
    cursor=db['organisations'].find(query)
    print(f"get_orgas, {query=}")
    return [Organisation(**doc) for doc in cursor]

def get_messages(course_id : str=None, username : str=None, id: str=None, limit:int=20):
    query={}
    if course_id: query['course_id']=course_id
    if username: query['username']=username
    if id: query['id']=id
    print(f"get_messages, {query=}")
    cursor=db['documents'].find(query).limit(limit)
    return [Message(**doc) for doc in cursor]

def get_users(limit:int=20):
    query={}
    print(f"get_users, {query=}")
    cursor=db['users'].find(query).limit(limit)
    return [User(**doc) for doc in cursor]

def add_message(msg: MessageInput)->Message:
    print(f"Adding {msg}")
    return Message(id=0, _id='', title=msg.title, username=msg.username, body=msg.body)

def add_orga(orga: OrganisationInput)->Organisation:
    id = db['organisations'].insert_one({'name': orga.name}).inserted_id
    return Organisation(**db['organisations'].find_one({'_id': id}))

def add_course(course: CourseInput)->Course:
    id = db['courses'].insert_one({'name': course.name, 'organisation': course.organisation}).inserted_id
    return Course(**db['courses'].find_one({'_id': id}))

def add_user(user: UserInput) -> User:
    print(f"add_user {user}")
    user2=User(user_id=user.user_id, username=user.username)
    db['users'].insert_one({'user_id': user.user_id, 'username': user.username})
    return user2

@strawberry.type
class Query:
    orgas: typing.List[Organisation] = strawberry.field(resolver=get_orgas)
    messages: typing.List[Message] = strawberry.field(resolver=get_messages)
    users: typing.List[User] = strawberry.field(resolver=get_users)

@strawberry.type
class Mutation:
    add_message: Message = strawberry.field(resolver=add_message)
    add_user: User = strawberry.field(resolver=add_user)
    add_orga: Organisation = strawberry.field(resolver=add_orga)
    add_course: Course = strawberry.field(resolver=add_course)

schema = strawberry.Schema(query=Query,
                           mutation=Mutation
                           )
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(graphql_app, prefix="/graphql")

@app.get('/')
def get_root():
    return RedirectResponse('/static/index.html')
