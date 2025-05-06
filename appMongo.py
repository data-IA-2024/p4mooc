import re
from pymongo import MongoClient
import dotenv, os

dotenv.load_dotenv()  # take environment variables

# Requires the PyMongo package.
# https://api.mongodb.com/python/current

MONGO_URL=os.environ['MONGO_URL']
client = MongoClient(MONGO_URL)
db = client[os.environ["MONGO_DB"]]
collection = db[os.environ["MONGO_COLLEC"]]


filter={}
project={
    'content' : 1
}

result = collection.find(
    filter=filter,
    projection=project
)

def stevefunk(content):
    children = content.get("children", [])
    endorsed_responses = content.get('endorsed_reponses',[])
    non_endorsed_responses = content.get('non_endorsed_reponses',[])
    db['documents'].insert_one(content)
    #print(f"{content.get('depth')} {content.get('courseid'):30} {content.get('username')}")

    for doc in children+endorsed_responses+non_endorsed_responses:
        stevefunk(doc)

for doc in result:
    content = doc["content"]
    print("-" * 100)
    stevefunk(content)

quit()

filter={
    'Title': re.compile(r"futur(?i)")
}
project={
    'Title': 1,
    'Year': 1,
    '_id': 0
}
sort=list({
              'Year': -1,
              'Title': 1
          }.items())
limit=200

result = client['cinema']['movies'].find(
    filter=filter,
    projection=project,
    sort=sort,
    limit=limit
)
print(result)



# Requires the PyMongo package.
# https://api.mongodb.com/python/current

client = MongoClient('mongodb://localhost:27017/')
result = client['cinema']['computers'].aggregate([
    {
        '$group': {
            '_id': '$usage',
            'Nbre': {
                '$count': {}
            }
        }
    }
])

for res in result:
    print(res)

