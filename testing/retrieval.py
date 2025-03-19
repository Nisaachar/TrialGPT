from embeddings import create_bm25_index, create_medcpt_index
from openai import AzureOpenAI
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModel
import os
import json
import numpy as np
import torch
from ollama import Client
from nltk import word_tokenize
import re


load_dotenv()

# Initialize the Azure OpenAI client
# client = AzureOpenAI(
#     api_version="2023-09-01-preview",
#     azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
#     api_key=os.getenv("OPENAI_API_KEY"),
# )

client = Client(
  host='http://localhost:11434'
)

def get_keyword_generation_messages(note, max_keywords):
    """
    Prepare the messages for keyword generation.
    """
    system = (
        f'You are a helpful assistant and your task is to help search relevant clinical trials for a given patient description. Do not explain your reasoning. Just output the result directly.'
        f'Please first summarize the main medical problems of the patient. Then generate up to {max_keywords} key conditions for searching relevant clinical trials for this patient. '
        'The key condition list should be ranked by priority. Please output only a JSON dict formatted as Dict{{"summary": Str(summary), "conditions": List[Str(condition)]}}.'
    )

    prompt = f"Here is the patient description: \n{note}\n\nJSON output:"

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt}
    ]

    return messages


def generate_summary_and_keywords(patient_note, max_keywords=32, model="clin-inquiry-agent-gpt4"):
    """
    Generate a patient summary and search keywords from the given note.
    """
    messages = get_keyword_generation_messages(patient_note, max_keywords)

    # response = client.chat.completions.create(
    #     model=model,
    #     messages=messages,
    #     temperature=0,
    # )

    # output = response.choices[0].message.content

    response = client.chat(
        model='deepseek-r1',
        messages=messages,
        options= {
            "num_ctx": 2048,
            "temperature": 0,
        }
    )

    output = response['message']['content'] 
    # output = re.sub(r"<think>.*?</think>\n?", "", output, flags=re.DOTALL)

    match = re.search(r'\{.*\}', output, re.DOTALL)
    data = ''
    if match:
        json_str = match.group(0)  # Extract matched JSON content
        try:
            data = json.loads(json_str)  # Parse JSON
            return data
        except json.JSONDecodeError as e:
            print("Error parsing JSON:", e)
            return None
            
    else:
        print("No valid JSON found.")
        return None
        

    # output = output.strip("`").strip("json")
  
  
    # try:
    #     result = json.loads(data)
    #     return result
    # except json.JSONDecodeError as e:
    #     print("Error decoding JSON:", e)
    #     return None


def hybrid_retrieval_and_fusion(queries, bm25, bm25_doc_ids, bm25_doc_titles, medcpt_index, medcpt_doc_ids, bm25_wt=1, medcpt_wt=1, top_n=100, k=20):
    """
    Perform hybrid retrieval and fusion using multiple queries (keywords).

    Parameters:
    queries (list): List of query strings (keywords).
    bm25 (BM25Okapi): The BM25 index.
    bm25_doc_ids (list): Document IDs for BM25.
    bm25_doc_titles (list): Document titles for BM25.
    medcpt_index (faiss.IndexFlatIP): The FAISS index for MedCPT embeddings.
    medcpt_doc_ids (list): Document IDs for MedCPT.
    bm25_wt (int): Weight for BM25 scores.
    medcpt_wt (int): Weight for MedCPT scores.
    top_n (int): Number of top documents to return.
    k (int): Smoothing factor for rank-based scoring.

    Returns:
    list: Top N documents with their IDs and titles ranked by combined score.
    """

    combined_scores = {}
    doc_id_to_title = {doc_id: title for doc_id, title in zip(bm25_doc_ids, bm25_doc_titles)}

    tokenizer = AutoTokenizer.from_pretrained("ncbi/MedCPT-Query-Encoder")
    model = AutoModel.from_pretrained("ncbi/MedCPT-Query-Encoder").to("mps")

    for query_idx, query in enumerate(queries):
        # BM25 retrieval
        bm25_tokens = word_tokenize(query.lower()) #individual keywords just word tokenzied in case multiple words in a single keyword or for summary
        bm25_scores = bm25.get_scores(bm25_tokens)
        bm25_top_indices = np.argsort(bm25_scores)[-top_n:][::-1]
        
        for rank, idx in enumerate(bm25_top_indices):
            doc_id = bm25_doc_ids[idx]
            score = (1 / (rank + k)) * (1 / (query_idx + 1))  # Fusion rank-based score
            combined_scores[doc_id] = combined_scores.get(doc_id, 0) + bm25_wt * score #accumulates the score overtime: {'NCT02896868': 0.00390625, 'NCT05516758': 0.003472222222222222, 'NCT06023095': 0.005208333333333333}}

        # MedCPT retrieval
        with torch.no_grad():
            encoded_query = tokenizer(
                query,
                truncation=True,
                padding=True,
                return_tensors='pt',
                max_length=512
            ).to("mps")
            query_embed = model(**encoded_query).last_hidden_state[:, 0, :].cpu().numpy()  #a 768-d vector formed from the query.

        medcpt_scores, medcpt_indices = medcpt_index.search(query_embed, top_n)
        
        for rank, idx in enumerate(medcpt_indices[0]):
            doc_id = medcpt_doc_ids[idx]
            #--------------
            # score = (1 / (rank + k)) * (1 / (query_idx + 1))  # Fusion rank-based score
            
            score = medcpt_scores[0][rank] * (1 / (rank + k)) * (1 / (query_idx + 1))   #new scoring method utilizing medcpt_scores

            #--------------
            combined_scores[doc_id] = combined_scores.get(doc_id, 0) + medcpt_wt * score

    # Rank documents by combined scores
    ranked_docs = sorted(combined_scores.items(), key=lambda x: -x[1])[:top_n]

    return [(doc_id, doc_id_to_title.get(doc_id, "Unknown Title")) for doc_id, _ in ranked_docs]



def calculate_recall(test_file, query_id, retrieved_doc_ids):
    """
    Calculate the recall for a specific query ID.

    Parameters:
    test_file (str): Path to the test file (TSV format).
    query_id (str): Query ID for which recall needs to be calculated.
    retrieved_doc_ids (list): List of document IDs retrieved for the query.

    Returns:
    float: Recall value for the query.
    """
    relevant_docs = set()
    
    # Read the test file to extract relevant documents for the given query ID
    with open(test_file, "r") as file:
        for line in file:
            parts = line.strip().split("\t")
            if parts[0] == query_id and int(parts[2]) > 0:
                relevant_docs.add(parts[1])
    
    if not relevant_docs:
        print(f"No relevant documents found for query ID: {query_id}")
        return 0.0

    # Calculate recall
    retrieved_relevant_docs = [doc_id for doc_id in retrieved_doc_ids if doc_id in relevant_docs]
    recall = len(retrieved_relevant_docs) / len(relevant_docs)
    return recall

if __name__ == "__main__":
    # Example patient record

    # Open the JSON file and load it into a Python dictionary
    scores = []
    with open('queries.jsonl', 'r') as file:
    
        avg_score = 0
        for line in file:
            data = json.loads(line)


            patient_note = data['text']

            print(patient_note)
   
            max_keywords = 32  # Define the maximum number of keywords
            # print(patient_note)

            result = generate_summary_and_keywords(patient_note, max_keywords=max_keywords)

            if result:
                print("\nPatient Summary and Keywords:\n")
                print(json.dumps(result, indent=4))
            else:
                print("Failed to generate summary and keywords.")

            # Example usage of BM25 index creation
            corpus_file = "corpus.jsonl"  # Path to the corpus file
            bm25_cache_file = "bm25_cache.json"  # Path to the BM25 cache file

            bm25_index, bm25_document_ids, bm25_document_titles = create_bm25_index(corpus_file, bm25_cache_file)
            # print("BM25 index created. Document count:", len(bm25_document_ids))

            # Example usage of MedCPT index creation
            medcpt_embed_cache = "/medcpt_embeds.npy"  # Path to the embedding cache
            medcpt_id_cache = "medcpt_doc_ids.json"  # Path to the document ID cache

            medcpt_index, medcpt_document_ids = create_medcpt_index(corpus_file, medcpt_embed_cache, medcpt_id_cache)
            # print("MedCPT index created. Document count:", len(medcpt_document_ids))

            # Example hybrid retrieval

            #--------------
            queries = [result["summary"]] + result["conditions"]  # Combine summary and keywords

            # queries = result["conditions"]
            #--------------


            top_docs = hybrid_retrieval_and_fusion(
                queries,
                bm25_index,
                bm25_document_ids,
                bm25_document_titles,
                medcpt_index,
                medcpt_document_ids,
                bm25_wt=1,
                medcpt_wt=1,
                top_n=10
            )

            # print("\nTop documents from hybrid retrieval:")
            # for doc_id, title in top_docs
            #     print(f"ID: {doc_id}, Title: {title}")

            # Save retrieved trial IDs to a JSON file
            retrieved_trial_ids = [doc_id for doc_id, _ in top_docs]
            with open("retrieved_trials.json", "w") as f:
                json.dump({"retrieved_trials": retrieved_trial_ids}, f, indent=4)
            # print("\nRetrieved Clinical Trial IDs saved to 'retrieved_trials.json'.")

            # Evaluate recall
            test_file = "test.tsv"
            query_id = data['_id']
            recall = calculate_recall(test_file, query_id, retrieved_trial_ids) * 100
            # print(f"\nRecall for query ID {query_id}: {recall:.4f}")
            print(f"\n\nValidation Score for this Patient Note is: {recall:.2f}%")

            avg_score += recall

        print("The final scores are: ")
        for i, s in enumerate(scores):
            print(f"{i + 1}. {s}")
        print(f"\n\n********************\nThe avergae validation score is: {avg_score/len(scores):.2f}%\n********************")


