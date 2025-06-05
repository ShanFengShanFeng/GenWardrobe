import os
import re
import json
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core import VectorStoreIndex, Settings, Document
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.core import StorageContext, load_index_from_storage
from config import GEMINI_API_KEY, raw_dict, index, embed_model, llm_model, merged_dict

# Fix keys: remove "b'" prefix and "'" suffix if present
merged_dict = {}
for raw_key, value in raw_dict.items():
    normalized_key = raw_key.strip().strip("b'").strip("'").strip('"')
    merged_dict[normalized_key] = value


def find_json_data(source):
    if source.endswith(".json"):
        source = source[:-5]
    return merged_dict.get(source)

def load_query_from_txt(query_path):
    with open(query_path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def query_index(index, query, k=6):
    print("[query_index] Using query:", query)
    llm = GoogleGenAI(model=llm_model, api_key=GEMINI_API_KEY)
    # increase similarity_top_k to return more json
    query_engine = index.as_query_engine(llm=llm, similarity_top_k=20)

    response = query_engine.query(query)
    results = []

    for node_with_score in response.source_nodes[:k]:
        source = node_with_score.node.metadata.get("source", None)
        score = node_with_score.score
        print(f"[Match] Score: {score:.4f} | Source: {source}")

        results.append({
            'text': node_with_score.node.text,
            'score': score,
            'source': source
        })
    return results

# Index builder
def load_and_split_by_marker(file_path, marker="###"):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    chunks = [chunk.strip() for chunk in content.split(marker) if chunk.strip()]
    documents = []
    for chunk in chunks:
        lines = chunk.splitlines()
        if not lines:
            continue
        file_id = lines[0].strip()
        content_text = "\n".join(lines[1:]).strip()
        documents.append(Document(text=content_text, metadata={"source": file_id}))
    return documents

def load_all_txt_documents(folder_path, marker="###"):
    all_documents = []
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(".txt"):
            full_path = os.path.join(folder_path, filename)
            chunks = load_and_split_by_marker(full_path, marker)
            all_documents.extend(chunks)
    return all_documents

# pipeline.py call
def run_retrieval(req_id, k=3):
    query_path = f"data_embedding/query_{req_id}.txt"
    if not os.path.exists(query_path):
        raise FileNotFoundError(f"Query file not found: {query_path}")

    print(f"\n📥 Running retrieval for req_id: {req_id}")
    query = load_query_from_txt(query_path)

    # Run query
    results = query_index(index, query, k=k)

    matched_jsons = []
    for i, res in enumerate(results):
        source = res.get("source")

        # 🧹 Normalize: remove ".json" suffix and surrounding quotes if any
        if source:
            source = source.strip().replace(".json", "").strip("'").strip('"')
        else:
            # Try fallback from text using regex
            match = re.search(r"b'([0-9a-f]{32})'", res["text"])
            if match:
                source = match.group(1)
            else:
                print(f"[Result {i+1}] ❌ Cannot extract JSON key")
                continue
        json_data = merged_dict.get(source)
        if json_data:
            matched_jsons.append(json_data)
            print(f"[Result {i+1}] ✅ Matched source: {source} (Score: {res['score']:.4f})")
        else:
            print(f"[Result {i+1}] ⚠️ No JSON found for source: {source}")

    return matched_jsons








