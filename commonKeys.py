import json

new_file = 'storage/trials_data.json'
original_file = '../TrialGPT-Demo-V2/trial_info.json'

with open(new_file, 'r') as file:
    new = json.load(file)

with open(original_file, 'r') as file:
    original = json.load(file)

newKeys = set()

for study in new.get("studies", []):
    key = study.get("protocolSection", {}).get("identificationModule", {}).get("nctId", {})
    newKeys.add(key)


orgKeys = set(original.keys())
print(orgKeys)


commonKeys = set()

for key in newKeys:
    if key in orgKeys:
        commonKeys.add(key)

print(commonKeys)
print(f"Total common keys between two datasets are: {len(commonKeys)}")


# import json

# def extract_nct_ids(json_file):
#     """
#     Extracts NCT IDs from a JSON file.
#     :param json_file: Path to the JSON file.
#     :return: List of NCT IDs.
#     """
#     try:
#         with open(json_file, 'r', encoding='utf-8') as file:
#             data = json.load(file)
#             nct_ids = list(data.keys())  # Extracting keys which are NCT IDs
#             return nct_ids
#     except Exception as e:
#         print(f"Error reading JSON file: {e}")
#         return []

# if __name__ == "__main__":
#     json_file_path = "clinical_trials.json"  # Change this to your actual file path
#     nct_ids = extract_nct_ids(json_file_path)
#     print("Extracted NCT IDs:", nct_ids)


