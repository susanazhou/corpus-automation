from sentence_transformers import SentenceTransformer, util
from transformers import pipeline

# Sample documents
documents = [
    "The capital of France is Paris.",
    "Paris is known for the Eiffel Tower.",
    "France is a country in Europe.",
    "The Eiffel Tower is a famous landmark.",
    "Berlin is the capital of Germany.",
    "Germany is known for its engineering and automotive industry."
]

# Load a pre-trained Sentence-BERT model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Step 1: Document Retrieval
def retrieve_documents(query, documents, model, top_k=3):
    doc_embeddings = model.encode(documents, convert_to_tensor=True)
    query_embedding = model.encode(query, convert_to_tensor=True)
    cos_scores = util.cos_sim(query_embedding, doc_embeddings)[0]
    top_results = zip(range(len(cos_scores)), cos_scores)
    top_results = sorted(top_results, key=lambda x: x[1], reverse=True)
    top_doc_indices = [documents[i] for i, _ in top_results[:top_k]]
    return top_doc_indices

# Step 2: Document Ranking (already done in retrieve_documents)

# Step 3: Response Generation
def generate_response(query, top_docs):
    generator = pipeline('text2text-generation', model='facebook/bart-large-cnn')
    context = " ".join(top_docs)  # Use top documents as context
    response = generator(f"answer: {query} context: {context}", max_length=50, num_return_sequences=1)
    return response[0]['generated_text']

# Example usage
query = "What is the capital of France?"
top_docs = retrieve_documents(query, documents, model)
response = generate_response(query, top_docs)
print(response)
