import json
from transformers import AutoTokenizer, AutoModel
import faiss


bm25_cache_file = 'storage/embeddings/bm25_cache.json'
corpus_file = 'corpus.jsonl'




