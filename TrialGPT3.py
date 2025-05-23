import json
from nltk.tokenize import sent_tokenize
import time
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from ollama import Client
import boto3

load_dotenv()


client = boto3.client(service_name="bedrock-runtime")

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
	print(output)
	return output


def print_trial(
	trial_info: dict,
	inc_exc: str,
) -> str:
	"""Given a dict of trial information, returns a string of trial."""
	
	trial = f"Title: {trial_info['brief_title']}\n"
	trial += f"Target diseases: {', '.join(trial_info['diseases_list'])}\n"
	trial += f"Interventions: {', '.join(trial_info['drugs_list'])}\n"
	trial += f"Summary: {trial_info['brief_summary']}\n"
	
	if inc_exc == "inclusion":
		trial += "Inclusion criteria:\n %s\n" % parse_criteria(trial_info['inclusion_criteria'])
	elif inc_exc == "exclusion":
		trial += "Exclusion criteria:\n %s\n" % parse_criteria(trial_info['exclusion_criteria']) 
	
	return trial


def get_matching_prompt(
	trial_info: dict,
	inc_exc: str,
	patient: str,
) -> str:
	"""Output the prompt."""
	prompt = f"You are a helpful assistant for clinical trial recruitment. Your task is to compare a given patient note and the {inc_exc} criteria of a clinical trial to determine the patient's eligibility at the criterion level.\n"

	if inc_exc == "inclusion":
		prompt += "The factors that allow someone to participate in a clinical study are called inclusion criteria. They are based on characteristics such as age, gender, the type and stage of a disease, previous treatment history, and other medical conditions.\n"
	
	elif inc_exc == "exclusion":
		prompt += "The factors that disqualify someone from participating are called exclusion criteria. They are based on characteristics such as age, gender, the type and stage of a disease, previous treatment history, and other medical conditions.\n"

	prompt += f"You should check the {inc_exc} criteria one-by-one, and output the following three elements for each criterion:\n"
	prompt += f"\tElement 1. For each {inc_exc} criterion, briefly generate your reasoning process: First, judge whether the criterion is not applicable (not very common), where the patient does not meet the premise of the criterion. Then, check if the patient note contains direct evidence. If so, judge whether the patient meets or does not meet the criterion. If there is no direct evidence, try to infer from existing evidence, and answer one question: If the criterion is true, is it possible that a good patient note will miss such information? If impossible, then you can assume that the criterion is not true. Otherwise, there is not enough information.\n"
	prompt += f"\tElement 2. If there is relevant information, you must generate a list of relevant sentence IDs in the patient note. If there is no relevant information, you must annotate an empty list.\n" 
	prompt += f"\tElement 3. Classify the patient eligibility for this specific {inc_exc} criterion: "
	
	if inc_exc == "inclusion":
		prompt += 'the label must be chosen from {"not applicable", "not enough information", "included", "not included"}. "not applicable" should only be used for criteria that are not applicable to the patient. "not enough information" should be used where the patient note does not contain sufficient information for making the classification. Try to use as less "not enough information" as possible because if the note does not mention a medically important fact, you can assume that the fact is not true for the patient. "included" denotes that the patient meets the inclusion criterion, while "not included" means the reverse.\n'
	elif inc_exc == "exclusion":
		prompt += 'the label must be chosen from {"not applicable", "not enough information", "excluded", "not excluded"}. "not applicable" should only be used for criteria that are not applicable to the patient. "not enough information" should be used where the patient note does not contain sufficient information for making the classification. Try to use as less "not enough information" as possible because if the note does not mention a medically important fact, you can assume that the fact is not true for the patient. "excluded" denotes that the patient meets the exclusion criterion and should be excluded in the trial, while "not excluded" means the reverse.\n'
	
	prompt += "You should output only a JSON dict exactly formatted as: dict{str(criterion_number): list[str(element_1_brief_reasoning), list[int(element_2_sentence_id)], str(element_3_eligibility_label)]}."

	sample_output = '''
		"NCT02359643": {
        "inclusion": {
            "0": [
                "The patient is a 2-year-old boy who has been diagnosed with Kawasaki Disease, which matches the first inclusion criterion.",
                [
                    0
                ],
                "included"
            ],
            "1": [
                "The patient has had a fever for 5 days, which meets the criterion. However, the note does not specify the number of symptoms the patient has, so there is not enough information to determine if the patient meets this criterion.",
                [
                    0
                ],
                "not enough information"
            ],
            "2": [
                "The patient has a strawberry tongue, which is a sign of diffuse mucosal inflammation. Therefore, the patient meets this criterion.",
                [
                    1
                ],
                "included"
            ]
	'''
	# prompt += f"This is a sample output: {sample_output}"
	
	user_prompt = f"Here is the patient note, each sentence is led by a sentence_id:\n{patient}\n\n" 
	user_prompt += f"Here is the clinical trial:\n{print_trial(trial_info, inc_exc)}\n\n"
	user_prompt += f"Only output a Plain JSON output and nothing else:\n\n\n"

	return prompt, user_prompt


def trialgpt_matching(trial: dict, patient: str, model: str):
	results = {}

	# doing inclusions and exclusions in separate prompts

	combined_prompt = ''

	for inc_exc in ["inclusion", "exclusion"]:
		system_prompt, user_prompt = get_matching_prompt(trial, inc_exc, patient)

		combined_prompt += system_prompt + user_prompt

	# print(combined_prompt)

	



	messages = [
		{"role": "user", "content": [{"text": combined_prompt}]}
	]

	response = client.converse(
		modelId="us.amazon.nova-micro-v1:0",
		messages=messages,
		inferenceConfig={
			"temperature": 0.0
		}
	)

	output = response["output"]["message"]["content"][0]["text"] 



	# message = message.strip("`").strip("json")

	# # try:
	# # 	results[inc_exc] = json.loads(message)
	# # except:
	# # 	results[inc_exc] = message

	# print(message)

	# return results
