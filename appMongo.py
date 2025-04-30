import re
from pymongo import MongoClient

# Requires the PyMongo package.
# https://api.mongodb.com/python/current

client = MongoClient('mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false')
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

