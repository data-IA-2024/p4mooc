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

## Docker
Création de VM sur Azure
```bash
 # création de network
 docker network create -d bridge my-net
 # Ollama
 docker run -d -v ollama:/root/.ollama --network=my-net -p 11434:11434 --name ollama ollama/ollama
 # PGvector
 docker run --name pgvector -p 5432:5432 -e POSTGRES_PASSWORD=P4SECRET -d pgvector/pgvector:pg17
 # Ajout des services -> my-network & redémarrage auto
 docker network connect my-net pgvector
 docker network connect my-net mongop4
 docker update --restart always pgvector
 docker update --restart always mongop4
 docker update --restart always ollama
```

Déployer manuellement :
```bash
 # En local sur ma machine
 docker login p4acr.azurecr.io # A faire 1 seule fois
 docker build -t p4acr.azurecr.io/mooc_ego .
 docker push p4acr.azurecr.io/mooc_ego
 # sur la VM Azure (connection SSH)
 docker pull p4acr.azurecr.io/mooc_ego
 docker run --name appli --network=my-net -p 8080:80 --env-file .env.ego -d p4acr.azurecr.io/mooc_ego 
```

Déployer automatiquement (build dans ACR)  
Utilisation de workflow : https://github.com/Azure/acr-build  
Voir .github/workflows/buildACR.yml  
3 secrets ont été mis dans github
## BDD PG vector
```bash
 docker run --name pgvector -p 5432:5432 -e POSTGRES_PASSWORD=P4SECRET -d pgvector/pgvector:pg17
```

## API
```bash
 fastapi dev graph.py --port 8888
```
```mermaid
%% Example of sequence diagram
  sequenceDiagram
      actor User

    User->>API : requète initiale<br>GET /
    API->>User : redirection vers /static/index.html
    User->>API : requète /static/index.html<br>GET /static/index.html
    API->>User : page index.html
    API->>User : page index.html, lecture HTML & affichage
    User->>google : requète lib jquery<br>GET jquery.min.js
    google->>User : requète lib jquery<br>GET jquery.min.js
    User->>API : requète données avec jquery<br>POST /graphql "messages {id body}"
    API->>MongoDB : requère messages, champs id, body
    MongoDB->>API : liste des messages
    API->>User : données JSON messsages
```

```bash
 source venv/bin/activate
 fastapi dev app.py --port 8888
```

```bash
 python3 graph.py
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
    User->>API : Charge le fil de discussion (id)<br>GET /thread?id=***?course_id=***
    API->>+Modele : Extrait les messages du fil (id)<br>extract(id, course_id)
    Modele->>MongoDB : récupère le document <br>db.threads.find({id:id})
    MongoDB->>Modele: document<br>JSON du fil
    loop chaque message du fil
    Modele->>MongoDB : Sauve message<br>db.messages.update_one({'id':id}, {'$set': content}, upsert=True)
    MongoDB->>Modele : status
    Modele->>Embedding : embedding (messages)<br>Ollama POST http://localhost:11434/api/embed
    Embedding->>Modele : result<br>Vector dans JSON
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

    User->>API : fil similaire (question, course_id) <br>GET /question?q=ma question&course=course
    API->>+Modele : Appel modèle <br>question(question, course)
    Modele->>Embedding : embedding (question)<br>Ollama POST http://localhost:11434/api/embed
    Embedding->>Modele : result<br>Vector dans JSON
    Modele->>PGvector : liste des messages du cours les plus proches<br>SELECT * FROM public.documents ...
    PGvector->>Modele : liste d'ID proches
    Modele->>MongoDB : contenu des messages
    MongoDB->>Modele : messages
    Modele->>-API : Réponses
    API->>User : Liste des fils 
```
