__author__ = "qiao"

"""
Running the TrialGPT matching for three cohorts (sigir, TREC 2021, TREC 2022).
"""

import json
from nltk.tokenize import sent_tokenize
import os
import sys

from TrialGPT import trialgpt_matching

from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
	api_version="2023-09-01-preview",
	azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
	api_key=os.getenv("OPENAI_API_KEY"),
)


if __name__ == "__main__":
    # Model and file paths
    model = 'clin-inquiry-agent-gpt4'
    dataset = json.load(open("detailed_trials.json"))
    output_path = "matching_results.json"

    # Load or initialize output
    if os.path.exists(output_path):
        output = json.load(open(output_path))
    else:
        output = {}

    # Dummy patient note (replace with real data if available)
    patient_note = "A 2-year-old boy is brought to the emergency department by his parents for 5 days of high fever and irritability. The physical exam reveals conjunctivitis, strawberry tongue, inflammation of the hands and feet, desquamation of the skin of the fingers and toes, and cervical lymphadenopathy with the smallest node at 1.5 cm. The abdominal exam demonstrates tenderness and enlarged liver. Laboratory tests report elevated alanine aminotransferase, white blood cell count of 17,580/mm, albumin 2.1 g/dL, C-reactive protein 4.5 mg, erythrocyte sedimentation rate 60 mm/h, mild normochromic, normocytic anemia, and leukocytes in urine of 20/mL with no bacteria identified. The echocardiogram shows moderate dilation of the coronary arteries with possible coronary artery aneurysm."
    sents = sent_tokenize(patient_note)
    sents.append("The patient will provide informed consent, and will comply with the trial protocol without any practical issues.")
    sents = [f"{idx}. {sent}" for idx, sent in enumerate(sents)]
    patient_note = "\n".join(sents)

    # Iterate through trials in the dataset
    for trial in dataset:
        trial_id = trial["trial_id"]

        # Skip already processed trials
        if trial_id in output:
            continue

        try:
            # Match trial with patient
            results = trialgpt_matching(trial, patient_note, model)
            output[trial_id] = results

            # Save results incrementally
            with open(output_path, "w") as f:
                json.dump(output, f, indent=4)

        except Exception as e:
            print(f"Error processing trial {trial_id}: {e}")
            continue

    print(f"Matching results saved to {output_path}.")
