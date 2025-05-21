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

SECRET_KEY = os.environ['SECRET_KEY']
ALGORITHM = os.environ['ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])

scopes = {
    "read": "Read access to protected resources",
    "write": "Write access to protected resources",
    "fail": "Scope qui n'existe pas !"
}
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scopes=scopes)

class Token(BaseModel):
    access_token: str
    token_type: str

MONGO_URL=os.environ['MONGO_URL']
client = MongoClient(MONGO_URL)
db = client[os.environ["MONGO_DB"]]
#collection = db[os.environ["MONGO_COLLEC"]]

@strawberry.type
class User:
    _id: str
    username: str='---'
    user_id: int=0

@strawberry.type
class Message:
    _id: str
    id: str
    username: str='---'
    user_id: int=-1
    body: str
    type: str
    thread_type: str = ''
    comments_count: int = 0
    context: str = ''
    endorsed: int
    thread_id: str = ''
    title: str = ''
    unread_comments_count: int = 0
    votes: str
    anonymous: bool
    created_at: str
    updated_at: str
    resp_skip: int = 0
    course_id: str
    courseware_url: str = ''
    courseware_title: str = ''
    anonymous_to_peers: str = ''
    children: str=''
    pinned: bool = False
    commentable_id: str
    abuse_flaggers: str
    closed: bool
    resp_total: int = 0
    resp_limit: int = 0
    at_position_list: int
    read: str = ''
    depth: int = -1
    parent_id: str = ''

def get_data(token:str=Depends(oauth2_scheme)) -> str:
    print(f"get_data {token=}")
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return str(payload)


def get_messages(course_id : str=None, username : str=None, id: str=None, limit:int=20):
    query={}
    if course_id: query['course_id']=course_id
    if username: query['username']=username
    if id: query['id']=id
    print(f"get_messages, {query=}")
    cursor=db['documents'].find(query).limit(limit)
    return [Message(**doc) for doc in cursor]

@strawberry.type
class Query:
    messages: typing.List[Message] = strawberry.field(resolver=get_messages)

    @strawberry.field
    def protected_hello2(self, data:str = Depends(get_data)) -> str:
        return f"OK {data=}"

@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_message(self, title: str, username: str) -> Message:
        print(f"Adding {title=} {username=}")

        return Message(title=title, username=username)

class Context(BaseContext):
    @cached_property
    def user(self) -> str:
        if not self.request:
            return None

        authorization = self.request.headers.get("Authorization", None)
        return authorization
        #return authorization_service.authorize(authorization)




def get_context() -> Context:
    context = Context()
    print(f'CONTEXT {context=} {context.user}')
    return context

schema = strawberry.Schema(query=Query,
                           mutation=Mutation
                           )


graphql_app = GraphQLRouter(schema, context_getter=get_context)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(graphql_app, prefix="/graphql")

@app.get('/')
def get_root():
    return RedirectResponse('/static/index.html')

@app.get("/test")
def test(data=Depends(get_data)):
    '''
    Test du token identifié !
    :param token:
    :return:
    '''
    return data

@app.post("/token")
def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    '''
    Valide l'authentification !
    :param form_data:
    :return:
    '''
    print(f"/token {form_data.username=} {form_data.password=} {form_data.scopes=}")
    data = {'username': form_data.username, "scope": form_data.scopes}
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return Token(access_token=access_token, token_type="bearer")
