import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import requests
import os
from datetime import datetime

# Load raw_text from JSON
with open("data/raw_text.json", "r") as f:
    raw_text = json.load(f)

# Encode documents for retrieval
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode([str(entry) for entry in raw_text])

# Build FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# Path to corrections
corrections_path = os.path.join(os.path.dirname(__file__), "data", "corrections.json")

def load_corrections():
    """Load previously corrected answers"""
    try:
        with open(corrections_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_correction(question, original_answer, corrected_answer):
    """Save a human-corrected answer"""
    corrections = load_corrections()
    corrections.append({
        "question": question.strip(),
        "original_answer": original_answer,
        "corrected_answer": corrected_answer,
        #"reviewer": reviewer.strip(),
        "timestamp": datetime.now().isoformat()
    })
    with open(corrections_path, "w") as f:
        json.dump(corrections, f, indent=2)
    print("✅ Correction saved:", question)

def retrieve_and_answer(query):
    """Retrieve most relevant document and generate answer"""

    # First check if correction exists
    corrections = load_corrections()
    for entry in corrections:
        if entry["question"].strip().lower() == query.strip().lower():
            return entry["corrected_answer"]

    # Otherwise, use RAG
    query_emb = model.encode([query])
    D, I = index.search(np.array(query_emb), k=1)
    context = str(raw_text[I[0][0]])

    answer_prompt = f"""
Answer the following question using the provided context:
Question: {query}
Context:
{context}
Answer:
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": answer_prompt, "stream": False}
        )
        ans = response.json()["response"].strip()
    except Exception as e:
        ans = f"Error generating answer: {e}"

    return ans