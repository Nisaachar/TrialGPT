import json


dataset = "storage/trials_data.json"
filtered_data = "storage/dataset.json"

with open(dataset, 'r') as file:
    data = json.load(file)


result = {}

for study in data.get("studies", []): # [] returns null object if key not found.

    identification = study.get("protocolSection", {}).get("identificationModule", {})

    nct_id = identification.get("nctId")
    brief_title = identification.get("briefTitle") 
    official_title = identification.get("officialTitle")

    #lilly alias
    secondary_ids = identification.get("secondaryIdInfos", [])
    lilly_alias = [entry["id"] for entry in secondary_ids if "id" in entry]

    #brief summary
    briefSummary = study.get("protocolSection", {}).get("descriptionModule", {}).get("briefSummary", {})

    #Trial Status
    overallStatus = study.get("protocolSection", {}).get("statusModule", {}).get("overallStatus", {})

    #Trial Phase
    phase = study.get("protocolSection", {}).get("designModule", {}).get("phases", {})

    #Eligibility Criteria
    eligible_criteria = study.get("protocolSection", {}).get("eligibilityModule", {}).get("eligibilityCriteria", {})


    #disease List
    diseases_list = study.get("protocolSection", {}).get("conditionsModule", {}).get("conditions", {})

    #Drug list
    interventions = study.get("protocolSection", {}).get("armsInterventionsModule", {}).get("interventions", [])
    drug_list = []
    for x in interventions:
        drug_name = x.get("name", [])
        drug_list.append(drug_name)


    #enrollment
    enrollment = study.get("protocolSection", {}).get("designModule", {}).get("enrollmentInfo", {}).get("count", [])







#Fetch keywords.

    if nct_id:
        result[nct_id] = {
            "brief_title" : brief_title,
            "official_title" : official_title,
            "lillyAlias": lilly_alias,
            "brief_summary": briefSummary,
            "trial_status": overallStatus,
            "phase": phase,
            "diseases_list": diseases_list,
            "drugs_list" : drug_list,
            "enrollment": enrollment
        }


with open(filtered_data, "w") as file:
    json.dump(result, file, indent=4)

print(f'Dataset has been successfully filtered out and is saved at {filtered_data}')
