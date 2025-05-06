import strawberry, typing
import jwt
from fastapi import FastAPI, Depends
from strawberry.fastapi import GraphQLRouter
from pymongo import MongoClient
import dotenv, os
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated

dotenv.load_dotenv()  # take environment variables

SECRET_KEY = "09d25e094f5555a2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

scopes = {
    "read": "Read access to protected resources",
    "write": "Write access to protected resources"
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
class Message:
    _id: str
    id: str
    username: str='---'
    user_id: int=0
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
    children: str
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
    def protected_hello2(self, token: str = Depends(oauth2_scheme)) -> str:
        return f"OK {token=}"

@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_message(self, title: str, username: str) -> Message:
        print(f"Adding {title=} {username=}")

        return Message(title=title, username=username)

schema = strawberry.Schema(query=Query, mutation=Mutation)


graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

@app.get("/test")
async def test(token: Annotated[str, Depends(oauth2_scheme)]):
    '''
    Test du token identifié !
    :param token:
    :return:
    '''
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print(f"/test {payload=}")
    return {"token": token, "payload": payload}

@app.post("/token")
async def login_for_access_token(
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
    print(f"{access_token=}")
    return Token(access_token=access_token, token_type="bearer")
