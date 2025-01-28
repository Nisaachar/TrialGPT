import json


# Open the JSON file and load it into a Python dictionary
with open('input.json', 'r') as file:
    data = json.load(file)

id = data['patient_note']

print(f'Patien ID: {id}')