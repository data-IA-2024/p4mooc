import csv, os, time
from dotenv import load_dotenv
from mistralai import Mistral
import psycopg2 # must be psycopg 3

load_dotenv()  # take environment variables

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-embed"

conn = psycopg2.connect(os.environ["DATABASE_STRING"])
cur = conn.cursor()

client = Mistral(api_key=api_key)

with open('data/documents_embed - Feuille 1.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for id,txt in reader:
        if id=='ID': continue
        print('=>', txt)

        embeddings_batch_response = client.embeddings.create(
            model=model,
            inputs=[txt],
        )

        print(embeddings_batch_response.data[0].embedding)
        cur.execute("""INSERT INTO public.documents ("text", embedding) VALUES (%s, %s::vector)""",
                    (txt, embeddings_batch_response.data[0].embedding))
        time.sleep(1)

        conn.commit()
