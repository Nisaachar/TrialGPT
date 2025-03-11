import json

matching_results_path = "storage/matching_results.json"
agg_results_path = "storage/aggregation_results.json"
trial_info_path = "storage/dataset.json"

# Load results
matching_results = json.load(open(matching_results_path))

#details of retirived)trials

retrieved_trials_path = "storage/retrieved_trials.json"

retrieved_trials = json.load(open(retrieved_trials_path))

trials_to_consider = set(retrieved_trials['retrieved_trials'])
print(trials_to_consider)

print(matching_results)


for trial_id, results in matching_results.items():
    print(trial_id)