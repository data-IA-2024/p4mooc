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
    name: typing.Optional[str]=None
    title: typing.Optional[str]=None
    organisation: typing.Optional[str]=None

@strawberry.type
class Course(CourseInput):
    __collection__:strawberry.Private[str]='courses'
    _id: str

@strawberry.input
class OrganisationInput:
    name: typing.Optional[str]=None

def get_courses_from_orga(root):
    return [Course(**doc) for doc in db['courses'].find({'organisation': root.name})]

@strawberry.type
class Organisation(OrganisationInput):
    __collection__:strawberry.Private[str]='organisations'
    _id: str
    courses : typing.List[Course] = strawberry.field(resolver=get_courses_from_orga)

@strawberry.input
class MessageInput:
    title: str = strawberry.field(description="The title of the message")
    username: typing.Optional[str]=None
    body: typing.Optional[str]=None

@strawberry.type
class Message(MessageInput):
    __collection__:strawberry.Private[str]='documents'
    _id: str
    id: str
    user_id: int=-1
    type: str = ''
    thread_type: str = ''
    comments_count: int = 0
    context: str = ''
    endorsed: int = ''
    thread_id: str = ''
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
    user_id: typing.Optional[int]=None
    username: typing.Optional[str]=None

@strawberry.type
class User(UserInput):
    __collection__:strawberry.Private[str]='users'
    _id: str=''
    messages : typing.List[Message] = strawberry.field(resolver=get_message_from_user)

def get_messages(course_id : str=None, username : str=None, id: str=None, limit:int=20):
    query={}
    if course_id: query['course_id']=course_id
    if username: query['username']=username
    if id: query['id']=id
    print(f"get_messages, {query=}")
    cursor=db['documents'].find(query).limit(limit)
    return [Message(**doc) for doc in cursor]

def create_add(clo, collection):
    print(f"create_add {clo} {clo.__bases__} {clo.__collection__}")
    cli=clo.__bases__[0] # class parent
    def add_obj(doc:cli)->clo:
        id = db[collection].insert_one(doc.__dict__).inserted_id
        return clo(**db[collection].find_one({'_id': id}))
    return add_obj

def create_get(clo):
    cli=clo.__bases__[0] # class parent
    print(f"create_get {clo} {clo.__bases__} {clo.__collection__=}")
    def get_list(filter:cli)->typing.List[clo]:
        query = {key: value for key, value in filter.__dict__.items() if value is not None}
        print(f"get_list, {clo.__collection__=} {query}")
        cursor=db[clo.__collection__].find(query)
        return [clo(**doc) for doc in cursor]
    return get_list

@strawberry.type
class Query:
    orgas: typing.List[Organisation] = strawberry.field(resolver=create_get(Organisation))
    messages: typing.List[Message] = strawberry.field(resolver=create_get(Message))
    users: typing.List[User] = strawberry.field(resolver=create_get(User))
    courses: typing.List[Course] = strawberry.field(resolver=create_get(Course))

@strawberry.type
class Mutation:
    add_message: Message = strawberry.field(resolver=create_add(Message, 'messages'))
    add_user: User = strawberry.field(resolver=create_add(User, 'users'))
    add_orga: Organisation = strawberry.field(resolver=create_add(Organisation, 'organisations'))
    add_course: Course = strawberry.field(resolver=create_add(Course, 'courses'))

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
