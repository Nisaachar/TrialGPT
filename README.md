# TrialGPT: AI-Powered Clinical Trial Screening

## Overview
TrialGPT is an AI-driven system designed to streamline the clinical trial screening process in the pharmaceutical manufacturing industry. By leveraging advanced retrieval and ranking methodologies, TrialGPT significantly reduces screening time, improving efficiency and accuracy.

## Features
- **Multistage Retrieval Pipeline**: Utilizes patient summaries, keyword generation, BM25, and MedCPT indexing for enhanced trial retrieval.
- **Hybrid Search Mechanism**: Combines lexical (BM25) and semantic (MedCPT) search for improved recall.
- **Ranking System**: Aggregates retrieved results and ranks them based on relevance.
- **Multilingual Helpdesk Ticket Processing**: Detects ticket language, translates if necessary, categorizes, and assigns priority levels.
- **Autogen Framework Integration**: Enables agentic AI operations for processing helpdesk tickets.

## Project Structure
```
TrialGPT/
├── data/
│   ├── retrieved_trials.json   # Output of the retrieval stage
├── retrieval/
│   ├── retrieval.py            # Code for the retrieval process
├── ranking/
│   ├── aggregation.py          # Code for aggregation step
│   ├── ranking.py              # Code for ranking step
├── README.md                   # This document
```

## Setup Instructions
### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- Required Python dependencies from `requirements.txt`

### Installation
```sh
# Clone the repository
git clone https://github.com/your-repo/trialgpt.git
cd trialgpt

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

## Usage
### Running the Retrieval Pipeline
```sh
python retrieval/retrieval.py
```
### Running the Ranking Pipeline
```sh
python ranking/aggregation.py
python ranking/ranking.py
```


