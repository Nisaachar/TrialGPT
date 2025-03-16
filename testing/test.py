import json



corpus_file = "queries.jsonl"


with open(corpus_file, "r") as f:
    for line in f:
        entry = json.loads(line)
        print(entry["_id"])
        # doc_titles.append(entry["title"])