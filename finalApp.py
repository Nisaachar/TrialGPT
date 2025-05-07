import streamlit as st
import json
import subprocess
import re
import time

from retrieval_module import hybrid_retriever
from matching_module import matching
from ranking_module import ranking
import torch

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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

torch.classes.__path__ = []




# Apply CSS
load_css("style.css")

# Full-width Header
st.markdown("""
    <div class="header-container">
        <h1 class="header-text">Lilly</h1>
    </div>
""", unsafe_allow_html=True)


# Add space to prevent content from being hidden under the fixed header
st.write("<br><br><br>", unsafe_allow_html=True)

st.title("TrialGPT Demo")

json_file_path = 'storage/input.json'
retrieved_trials = 'storage/retrieved_trials.json'
detailed_results = 'storage/detailed_trials.json'
new_note = st.text_area("Enter the patient info:")



if st.button("Extract Trials"):
    start_time = time.time()
    if new_note:
        try:
            update_patient_note(json_file_path, new_note)
            st.divider()
            st.subheader("Extracting Trials")
            with st.spinner(text="Analyzing Patient Information to extract meaningful trials..."):
                
                result = hybrid_retriever()

                output_data = ""

                try:
                    output_data = json.loads(result)
                except:
                    match = re.search(r'\{.*\}', result, re.DOTALL)
                    if match:
                        json_str = match.group(0)
                        try:
                            output_data = json.loads(json_str)
                            
                            summary = output_data.get("summary", "No summary found")
                            # st.markdown(f"The patient summary is: **{summary}**")

                            keywords = output_data.get("conditions", "No keyword found")
                            # st.markdown(f"The keywrods generated for this patient are: {keywords}")
                        except json.JSONDecodeError:
                            st.error("Failed to parse retrieval output as JSON")
                    else:
                        st.error("Could not find JSON data in output")

                if output_data:
                    summary = output_data.get("summary", "No summary found")
                    st.markdown(f"Patient information is analyzed and here's a summary of it: **{summary}**")

                    # keywords = output_data.get("conditions", "No keyword found")
                    # st.markdown(f"The keywrods generated for this patient are: **{keywords}**")




#*****stage 2******

            #Running Matching Stage
            # st.divider()
            # st.header("Stage 2: Matching")
            with st.spinner(text="Performing in-depth analysis of patient information with the inclusion and exclusion criterias of trials..."):
                result = matching()




#****stage 3*******

            # st.divider()
            # st.header("Stage 3: Ranking")

            try:
  
                st.subheader("Ranked Trials:")

                result = ranking()
                st.text(result)


            except Exception as e:
                st.error(f"An error occurred: {e}")


        except Exception as e:
            st.error(f"An error occurred: {e}")
    
    end_time = time.time()
    time_elapsed = end_time - start_time
    st.markdown(f"**The total run time = {time_elapsed : .2f} seconds.**")







