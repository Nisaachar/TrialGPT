__author__ = "qiao"

"""
TrialGPT-Matching main functions and execution for a specific patient ID.
"""

import json
from nltk.tokenize import sent_tokenize
import os
from openai import AzureOpenAI

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_version="2023-09-01-preview",
    azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Function to parse inclusion/exclusion criteria
def parse_criteria(criteria):
    output = ""
    criteria = criteria.split("\n\n")

    idx = 0
    for criterion in criteria:
        criterion = criterion.strip()
        if "inclusion criteria" in criterion.lower() or "exclusion criteria" in criterion.lower():
            continue
        if len(criterion) < 5:
            continue
        output += f"{idx}. {criterion}\n"
        idx += 1
    return output

# Function to format trial information
def print_trial(trial_info: dict, inc_exc: str) -> str:
    trial = f"Title: {trial_info['brief_title']}\n"
    trial += f"Target diseases: {', '.join(trial_info['diseases_list'])}\n"
    trial += f"Interventions: {', '.join(trial_info['drugs_list'])}\n"
    trial += f"Summary: {trial_info['brief_summary']}\n"

    if inc_exc == "inclusion":
        trial += "Inclusion criteria:\n %s\n" % parse_criteria(trial_info['inclusion_criteria'])
    elif inc_exc == "exclusion":
        trial += "Exclusion criteria:\n %s\n" % parse_criteria(trial_info['exclusion_criteria'])

    return trial

# Function to generate the matching prompt
def get_matching_prompt(trial_info: dict, inc_exc: str, patient: str) -> str:
    prompt = f"You are a helpful assistant for clinical trial recruitment. Your task is to compare a given patient note and the {inc_exc} criteria of a clinical trial to determine the patient's eligibility at the criterion level.\n"

    if inc_exc == "inclusion":
        prompt += "The factors that allow someone to participate in a clinical study are called inclusion criteria.\n"
    elif inc_exc == "exclusion":
        prompt += "The factors that disqualify someone from participating are called exclusion criteria.\n"

    prompt += "Output should be a JSON dict.\n"
    user_prompt = f"Here is the patient note:\n{patient}\n\nHere is the clinical trial:\n{print_trial(trial_info, inc_exc)}\n\nPlain JSON output:"
    return prompt, user_prompt

# Function for TrialGPT matching
def trialgpt_matching(trial: dict, patient: str, model: str):
    results = {}
    for inc_exc in ["inclusion", "exclusion"]:
        system_prompt, user_prompt = get_matching_prompt(trial, inc_exc, patient)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
        )
        message = response.choices[0].message.content.strip()
        try:
            results[inc_exc] = json.loads(message)
        except:
            results[inc_exc] = message
    return results

# Main execution
if __name__ == "__main__":
    # Hardcoded patient ID
    patient_id = "sigir-20144"

    retrieved_trials_file = "detailed_trials.json"
    trial_info_file = "trial_info.json"
    model = "clin-inquiry-agent-gpt4"  # Change as needed
    output_path = f"matching_results.json"

    # Load retrieved trials and trial information
    with open(retrieved_trials_file, "r") as f:
        retrieved_trials = json.load(f)["retrieved_trials"]
    with open(trial_info_file, "r") as f:
        trial_info = json.load(f)

    if os.path.exists(output_path):
        output = json.load(open(output_path))
    else:
        output = {}

    # Dummy patient note (replace with real data if available)
    patient_note = "A 2-year-old boy presents with high fever, irritability, conjunctivitis, strawberry tongue, skin inflammation and desquamation, cervical lymphadenopathy, abdominal tenderness, enlarged liver, and possible coronary artery aneurysm. Lab results indicate elevated alanine aminotransferase, high white blood cell count, low albumin, high C-reactive protein, high erythrocyte sedimentation rate, mild normochromic normocytic anemia, and leukocytes in urine."
    sents = sent_tokenize(patient_note)
    sents.append("The patient will comply with the trial protocol.")
    sents = [f"{idx}. {sent}" for idx, sent in enumerate(sents)]
    patient_note = "\n".join(sents)

    # Match each trial
    for trial_id in retrieved_trials:
        if trial_id in output:
            continue  # Skip already processed trials

        trial = trial_info.get(trial_id)
        if not trial:
            print(f"Trial ID {trial_id} not found in trial_info.json.")
            continue

        try:
            results = trialgpt_matching(trial, patient_note, model)
            output[trial_id] = results
            with open(output_path, "w") as f:
                json.dump(output, f, indent=4)
        except Exception as e:
            print(f"Error processing trial {trial_id}: {e}")
            continue

    print(f"Matching results saved to {output_path}.")

    