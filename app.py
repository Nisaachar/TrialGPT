import streamlit as st
import json
import subprocess

# Function to load the JSON file
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to update the patient_note in the JSON file
def update_patient_note(file_path, new_note):
    with open(file_path, 'r+') as file:
        data = json.load(file)
        data['patient_note'] = new_note
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()

# Streamlit UI
st.title("TrialGPT Demo")

# Input fields
json_file_path = 'input.json'
retrieved_results_path = 'retrieved_trials.json'
detailed_results = 'detailed_trials.json'
new_note = st.text_area("Enter the patient info:")

# Update button
if st.button("Fetch Trials"):
    if json_file_path and new_note:
        try:
            update_patient_note(json_file_path, new_note)
            
            try:
                result = subprocess.run(
                    ["python", "retrieval.py"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                st.success("Trials fetched successfully!")
                # st.text("Output from retrieval.py:")
                st.text(result.stdout)
            
            except FileNotFoundError:
                st.error("retrieval.py not found. Please ensure the file is in the correct location.")
            
            # try:
            #     retrieved_data = load_json(retrieved_results_path)
            #     st.subheader("Retrieved Results:")
            #     st.json(retrieved_data)
            # except FileNotFoundError:
            #     st.error("retrieved_results.json not found. Ensure the retrieval script generates this file.")
            
            try:
                result = subprocess.run(
                    ["python", "prepare_metadata.py"],
                    capture_output=True,
                    text=True,
                    check=True
                )

                detailed_trials = load_json(detailed_results)

                if isinstance(detailed_trials, list):
                    detailed_trials = detailed_trials[:3]

                st.subheader("Fetched Trials: ")
                st.text("(Fetched only the first three trials for saving up space.)")
                st.json(detailed_trials)            
            
            except FileNotFoundError:
                st.error("detailed_trials.py not found. Please ensure the file is in the correct location.")
            
            try:
                result = subprocess.run(
                    ["python", "run_matching.py"],
                    capture_output=True,
                    text=True,
                    check=True
                )

                matched_trials = load_json('matching_results.json')

                if isinstance(detailed_trials, list):
                    detailed_trials = detailed_trials[:3]

                st.subheader("Matching Trials: ")
                st.text("(This stage introduces tranparency.)")
                st.json(matched_trials)            
            
            except FileNotFoundError:
                st.error("run_matching.json not found. Please ensure the file is in the correct location.")




#end results
            try:
                result = subprocess.run(
                    ["python", "results.py"],
                    capture_output=True,
                    text=True,
                    check=True
                )
               
                st.text("Final Trials:")
                st.text(result.stdout)
            
            except FileNotFoundError:
                st.error("retrieval.py not found. Please ensure the file is in the correct location.")



        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please provide both the file path and the new note.")
