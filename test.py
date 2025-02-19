

import json

with open('storage/dataset.json', 'r') as file:
    data = json.load(file)


lilly_alias = data['NCT03151551'].get('lillyAlias', [])
print(lilly_alias)