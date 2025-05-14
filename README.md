# Projet Embedding

Fichier source : Docs: https://docs.google.com/spreadsheets/d/1MqFjyMphIG1xh1exAus5fP0B6S6GGlHLKOF_S9ZlDNI/edit?usp=sharing
export en CSV

## Install
```bash
 python3.9 -m venv venv
 source venv/bin/activate
 pip install -r requirements.txt
```

```bash
 clear; python3 importCSV.py
```

## BDD PG vector
```bash
 docker run --name pgvector -p 5432:5432 -e POSTGRES_PASSWORD=P4SECRET -d pgvector/pgvector:pg17
```

## API
```bash
 fastapi dev main.py --port 8888
```

```bash
 source venv/bin/activate
 fastapi dev app.py --port 8888
```

```bash
 python3 main.py
```

```bash
 python appMongo.py
```

```bash
 clear; python scrap.py
```

## Mongo Users
Sur Datalab:
`docker run --name mongop4 -d -e MONGO_INITDB_ROOT_USERNAME=p4user -e MONGO_INITDB_ROOT_PASSWORD=P4SECRET -p 27017:27017 mongo`

```text
# user root
use admin
db.createUser({user:"G1", pwd:"qsfdqsdqsdqsdqa", roles:[{role:"dbAdmin", db:"G1"}]})
db.grantRolesToUser( "G1", [ { role: "readWrite", db: "G1" } ])
db.createUser({user:"G2", pwd:"qsfdwcwxqsdqsdqsdqa", roles:[{role:"dbAdmin", db:"G2"}]})
db.grantRolesToUser( "G2", [ { role: "readWrite", db: "G2" } ])
db.createUser({user:"G3", pwd:"qsfdqsdqwxcwxsdqsdqa", roles:[{role:"dbAdmin", db:"G3"}]})
db.grantRolesToUser( "G3", [ { role: "readWrite", db: "G3" } ])
db.createUser({user:"G4", pwd:"qsfdqsdqsdqsdwxcwqa", roles:[{role:"dbAdmin", db:"G4"}]})
db.grantRolesToUser( "G4", [ { role: "readWrite", db: "G4" } ])

mongosh mongodb://G1:qsfdqsdqsdqsdqa@localhost:27018/
```

## Postgres Vector
Sur Datalab (port 5432 déjà pris) -> port 5442:
`docker run --name pgvectorp4 -p 5442:5432 -e POSTGRES_PASSWORD=P4SECRET -d pgvector/pgvector:pg17`
tunnel 5445->5442
```sql
create database g0;
CREATE USER g0 WITH PASSWORD 'qsfdqsdqsdqsdqa';
grant all privileges on database g0 to g0;
--GRANT USAGE ON SCHEMA public TO g0;
\c g0
GRANT CREATE ON SCHEMA public TO g0;
```


## Schéma

Schéma des fils de discussion :
```text
Thread
├─ _id
├─ content
   ├─ id
   ├─ title
   ├─ body
   ├─ updated_at
   ├─ created_at (2014-2022)
   ├─ username (68k avec, 8k sans)
   ├─ user_id
   ├─ anonymous (true/false)
   ├─ course_id
   ├─ courseware_title
   ├─ resp_count
   ├─ comment_count
   ├─ votes
      ├─ count (& autres)
   ├─ children / endorsed_response / non_endorsed_response (*)
      ├─ id
      ├─ => même champs que dans content sauf title,
      ├─ depth (pas dans content)
      ├─ children / endorsed_response / non_endorsed_response (*)
```

```mermaid
%% Example of sequence diagram
  sequenceDiagram
      actor User
    User->>API : Charge le fil de discussion (id)<br>GET /thread?id=***
    API->>+Modele : Extrait les messages du fil (id)<br>extract(id)
    Modele->>MongoDB : récupère le document <br>db.threads.find({id:id})
    MongoDB->>Modele: document<br>JSON du fil
    loop chaque message du fil
    Modele->>MongoDB : Sauve message<br>db.messages.update_one({'id':id}, {'$set': content}, upsert=True)
    MongoDB->>Modele : status
    Modele->>Ollama : embedding (messages)<br>POST http://localhost:11434/api/embed
    Ollama->>Modele : result<br>Vector dans JSON
    Modele->>PGvector : ajout (id,course_id,embedding) dans table<br>INSERT INTO public.documents ...
    PGvector->>Modele : status
    end
    Modele->>-API : Nbre de messages
    API->>User : Nbre de messages (status 200)
```

```mermaid
%% Example of sequence diagram
  sequenceDiagram

    box lightyellow Récupération des cours disponibles
        actor User
        participant API
        participant Modele
        participant MongoDB
        participant PGvector
        participant Ollama
    end

    User->>API : Donne la liste des cours <br/>GET /courses
    API->>+Modele : liste des cours<br>get_courses()
    Modele->>MongoDB : liste des valeurs<br>db.threads.distinct('content.course_id')
    MongoDB->>Modele : liste <br>JSON list
    Modele->>-API : liste<br>JSON list
    API->>User : liste cours (JSON)
```

```mermaid
%% Example of sequence diagram
  sequenceDiagram

    box lightyellow Je pose une question
        actor User
        participant API
        participant Modele
        participant MongoDB
        participant PGvector
        participant Ollama
    end

    User->>API : fil similaire (question, course_id) 
    API->>User : Liste des fils 
```
