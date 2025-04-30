# Projet Embedding

Fichier source : Docs: https://docs.google.com/spreadsheets/d/1MqFjyMphIG1xh1exAus5fP0B6S6GGlHLKOF_S9ZlDNI/edit?usp=sharing
export en CSV

## Install
```bash
 python3 -m venv venv
 source venv/bin/activate
 pip install -r requirements.txt
```

```bash
 clear; python3 importCSV.py
```

## BDD PG vector
```bash
 docker run --name pgvector -p 5432:5432 -e POSTGRES_PASSWORD=goudot -d pgvector/pgvector:pg17
```

## API
```bash
 fastapi dev main.py --port 8888
```

```bash
 python appMongo.py
```

```bash
 clear; python scrap.py
```