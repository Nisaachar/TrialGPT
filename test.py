

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
    dic = {}
    total_score = 0
    # Read the test file to extract relevant documents for the given query ID
    with open(test_file, "r") as file:
        for line in file:
            parts = line.strip().split(",")
     
            if parts[0] == query_id and int(parts[2]) > 0:
                score = int(parts[2])
                relevant_docs.add(parts[1])
                dic[parts[1]] = score
                total_score += score
    print(total_score)
    if not relevant_docs:
        print(f"No relevant documents found for query ID: {query_id}")
        return 0.0

    # Calculate recall
    # retrieved_relevant_docs = [doc_id for doc_id in retrieved_doc_ids if doc_id in relevant_docs]
    score = 0
    retrieved_relevant_docs = []
    #cal
    for id in retrieved_doc_ids:
        if id in relevant_docs:
            retrieved_relevant_docs.append(id)
            score += dic[id]

    recall = score/total_score
    return recall


test_file = 'storage/test.csv'
query_id = '1'
retrieved_doc_ids = [
        "NCT00292955",
        "NCT06598631",
        "NCT01890967",
        "NCT02652871",
        "NCT01139775",
        "NCT01524705",
        "NCT00617734",
        "NCT01936373",
        "NCT05305924",
        "NCT01936372"
    ]

res = calculate_recall(test_file, query_id, retrieved_doc_ids)

print(res)

