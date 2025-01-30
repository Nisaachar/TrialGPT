import json

ncts = ['NCT02359643', 'NCT02317913', 'NCT01917721', 'NCT02390596', 'NCT00486863']


with open('filtered_studies.json', 'r') as file:
    data = json.load(file)

aliases = {}

for nct_id in ncts:
    if nct_id in data:
        aliases[nct_id] = data[nct_id].get('lillyAlias', [])
    else:
        aliases[nct_id] = 'Couldn\'t find Lilly alias'

print(json.dumps(aliases, indent=4))
