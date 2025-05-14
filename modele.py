from pymongo import MongoClient
import dotenv, os

dotenv.load_dotenv()  # take environment variables

client = MongoClient(os.environ["MONGO_URL"])
db = client[os.environ["MONGO_DB"]]

def get_courses():
    return db['threads'].distinct('content.course_id')