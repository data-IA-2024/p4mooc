import requests, os, json
from dotenv import load_dotenv

load_dotenv()  # take environment variables

url="https://mooc-forums.inria.fr/moocsl/t/11162/159.json"

params = {
    'track_visit': 'true',
    'forceLoad': 'true'
}

# En-têtes
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    #'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    #'Accept-Encoding': 'gzip, deflate, br, zstd',
    #'Referer': 'https://mooc-forums.inria.fr/moocsl/',
    'X-CSRF-Token': os.environ["CSRF"],
    #'Discourse-Logged-In': 'true',
    #'Discourse-Track-View': 'true',
    #'Discourse-Present': 'true',
    #'X-Requested-With': 'XMLHttpRequest',
    #'Connection': 'keep-alive',
    'Cookie': os.environ["Cookie"],
    #'Sec-Fetch-Dest': 'empty',
    #'Sec-Fetch-Mode': 'cors',
    #'Sec-Fetch-Site': 'same-origin',
    #'Priority': 'u=0',
    #'TE': 'trailers'
}

# Effectuer la requête
response = requests.get(url, headers=headers, params=params)

# Afficher la réponse
print(f"STATUS: {response.status_code}")
print(json.dumps(response.json(), indent=2))