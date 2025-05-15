from pymongo import MongoClient
import psycopg2
import dotenv, os, re, requests

dotenv.load_dotenv()  # take environment variables

# Mongo
client = MongoClient(os.environ["MONGO_URL"])
db = client[os.environ["MONGO_DB"]]

#PG
conn = psycopg2.connect(os.environ["DATABASE_STRING"])
cur = conn.cursor()

# Ollama
OLLAMA_URL=os.environ["OLLAMA_URL"]
OLLAMA_MODEL=os.environ["OLLAMA_MODEL"]

def get_courses():
    courses=db['threads'].distinct('content.course_id')
    print(f"get_courses: {len(courses)}")
    return courses

def get_threads_id(course_id):
    return db['threads'].distinct('_id', {'content.course_id': re.compile(course_id)})


def stevefunk(content, txts, ids, cids):
    id = content.get("id")
    body=content.get('body')
    children = content.get("children", [])
    endorsed_responses = content.get('endorsed_reponses',[])
    non_endorsed_responses = content.get('non_endorsed_reponses',[])
    N=1

    for doc in children+endorsed_responses+non_endorsed_responses:
        N+=stevefunk(doc, txts, ids, cids)

    content.pop('children', None)
    content.pop('endorsed_reponses', None)
    content.pop('non_endorsed_reponses', None)

    db['documents'].update_one({'id':id}, {'$set': content}, upsert=True)

    txts.append(body)
    ids.append(id)
    cids.append(content.get('course_id'))

    return N

def extract(id:str = None, course_id:str=None):
    query={'_extracted':{'$exists':False}}
    if id: query['_id'] = id
    if course_id: query['content.course_id'] = re.compile(course_id)
    #query={'_id':id} if id else ({'content.course_id': re.compile(course_id)} if course_id else {'id':'XXX'})
    print(f"extract, {query=}")
    Nthread=0
    Nmsg=0

    for thread in db['threads'].find(query):
        Nthread+=1
        txts=[]
        ids=[]
        cids=[]
        print(f"  thread {thread['_id']}")
        content = thread["content"]
        Nmsg+=stevefunk(content, txts, ids, cids)

        data={"model":OLLAMA_MODEL, "keep_alive": -1, "input": txts}
        #print(data)
        resp = requests.post(OLLAMA_URL, json=data)
        data = resp.json()['embeddings']

        print(f"[{resp.status_code}] {len(data)} {ids=}")

        for id,txt,vec,cid in zip(ids, txts, data, cids):
            cur.execute("""INSERT INTO public.documents (id, course_id, embedding) VALUES (%s, %s, %s::vector) ON CONFLICT (id) DO NOTHING""",
                        (id, cid, vec))
        conn.commit()

        db['threads'].update_one({'_id':thread["_id"]}, {'$set':{'_extracted':True}})

    return f"OK, {Nthread=} {Nmsg=} {course_id=}"

def question(course_id:str, question:str):
    print(f"question, {course_id=} {question}")

    data={"model":OLLAMA_MODEL, "keep_alive": -1, "input": question}
    resp = requests.post(OLLAMA_URL, json=data)
    data = resp.json()['embeddings'][0]

    cur.execute("""SELECT id, course_id, embedding<=>%s::vector AS dist 
    FROM public.documents
    WHERE (%s='toutes' or course_id=%s) 
    ORDER BY dist  ASC
    LIMIT 10""", (data, course_id, course_id, ))
    res=""
    res=[]
    for (id,cid,d) in cur:
        doc=db['documents'].find_one({'id':id}, {'body':1})
        print(id,d)
        res.append({'id':id, 'd':round(d,3), 'cid':cid, 'body':doc['body']})

    return res
