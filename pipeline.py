import subprocess


scripts_to_run = [
    "retrieval.py",
    "matching.py",
    "aggregation.py",
    "ranking.py",
]



for script in scripts_to_run:
    result = subprocess.run(["python", script], check=True, capture_output=True, text=True)
    print(result.stdout)  # Print standard output