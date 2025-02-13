import json
import re

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




    # Extract Inclusion Criteria
    inclusion_match = re.search(r"(?<=Inclusion Criteria:\n\n)(.*?)(?=\n\nExclusion Criteria:)", eligible_criteria, re.DOTALL)
    inclusion_criteria = inclusion_match.group(1).strip() if inclusion_match else None

    #formatting
    if inclusion_criteria:
        inclusion_criteria = 'inclusion criteria: \n\n' + inclusion_criteria  
        inclusion_criteria = re.sub(r"\*\s*", " ", inclusion_criteria)


    # Extract Exclusion Criteria
    exclusion_match = re.search(r"(?<=Exclusion Criteria:\n\n)(.*)", eligible_criteria, re.DOTALL)
    exclusion_criteria = exclusion_match.group(1).strip() if exclusion_match else None

    if exclusion_criteria:
        exclusion_criteria = 'exclusion criteria: \n\n' + exclusion_criteria
        exclusion_criteria = re.sub(r"\*\s*", "", exclusion_criteria)



    #disease List
    diseases_list = study.get("protocolSection", {}).get("conditionsModule", {}).get("conditions", [])

    #Drug list
    interventions = study.get("protocolSection", {}).get("armsInterventionsModule", {}).get("interventions", [])
    drug_list = []
    for x in interventions:
        drug_name = x.get("name", [])
        drug_list.append(drug_name)


    #enrollment
    enrollment = study.get("protocolSection", {}).get("designModule", {}).get("enrollmentInfo", {}).get("count", [])


    #keywords
    keywords = study.get("protocolSection", {}).get("conditionsModule", {}).get("keywords", [])



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
            "enrollment": enrollment,
            "inclusion_criteria" : inclusion_criteria,
            "exclusion_criteria" : exclusion_criteria,
            "keywords" : keywords,
        }


with open(filtered_data, "w") as file:
    json.dump(result, file, indent=4)

print(f'Dataset has been successfully filtered out and is saved at {filtered_data}')
