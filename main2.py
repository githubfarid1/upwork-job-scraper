import requests
from pathlib import Path
headers = {
    'sec-ch-ua-platform': '"Windows"',
    'Referer': 'https://search.libraryofleaks.org/',
    'Accept-Language': 'en',
    'sec-ch-ua': '"Not(A:Brand";v="99", "Microsoft Edge";v="133", "Chromium";v="133"',
    'sec-ch-ua-mobile': '?0',
    'X-Aleph-Session': '997db3e4-fa09-4263-b95c-9d55dcb1670a',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0',
    'Accept': 'application/json, text/plain, */*',
}

params = {
    'filter:collection_id': '61',
    'filter:schema': 'Pages',
    'filter:schemata': 'Thing',
    'highlight': 'true',
    'limit': '30',
}

response = requests.get('https://search.libraryofleaks.org/api/2/entities', params=params, headers=headers)
results = response.json()
for res in results['results']:
    filename = Path("results/" + res['properties']['fileName'][0])
    print("Download file", filename)
    url = res['links']['file']
    response = requests.get(url)
    filename.write_bytes(response.content)
