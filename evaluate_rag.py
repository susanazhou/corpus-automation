import json
import os
import sys
import argparse
from llm import LLM
import numpy as np
from typing import List, Dict, Any
from tqdm import tqdm
class RAGEvaluator:
    def __init__(self, llm: LLM):
        self.llm = llm
        self.context_embeddings = None
        self.context_documents = None
        self.embed_model = "embed-english-v3.0"
        self.rerank_model = "rerank-v3.5"

    def load_context(self, context_file: str):
        """Load and embed the context documents"""
        with open(context_file, 'r', encoding='utf-8') as f:
            self.context_documents = json.load(f)
        
        # Embed the documents
        if self.llm.provider == "cohere":
            # For Cohere, we can use their embed endpoint
            texts = [doc["data"]["text"] for doc in self.context_documents]
            
            # Process in batches of 96 (Cohere's limit)
            batch_size = 96
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                response = self.llm.client.embed(
                    model=self.embed_model,
                    input_type="search_document",
                    texts=batch_texts,
                    embedding_types=["float"]
                )
                all_embeddings.extend(response.embeddings.float)
            
            self.context_embeddings = all_embeddings
        else:
            # For other providers, we'll need to implement embedding
            raise NotImplementedError("Embedding not implemented for this provider")

    def retrieve_relevant_documents(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve the most relevant documents for a query"""
        if self.llm.provider == "cohere":
            # Embed the query
            query_embedding = self.llm.client.embed(
                model=self.embed_model,
                input_type="search_query",
                texts=[query],
                embedding_types=["float"]
            ).embeddings.float[0]

            # Compute similarity scores
            scores = np.dot(query_embedding, np.transpose(self.context_embeddings))[0]
            top_indices = np.argsort(-scores)[:top_k]
            
            # Rerank the documents
            rerank_response = self.llm.client.rerank(
                model=self.rerank_model,
                query=query,
                documents=[self.context_documents[idx]["data"]["text"] for idx in top_indices],
                top_n=top_k
            )
            
            # Return reranked documents
            return [self.context_documents[top_indices[result.index]] for result in rerank_response.results]
        else:
            raise NotImplementedError("Retrieval not implemented for this provider")

    def evaluate_question(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single question using RAG"""
        # Retrieve relevant documents
        relevant_docs = self.retrieve_relevant_documents(question["question"])
        
        # Create prompt with context
        context = "\n".join([doc["data"]["text"] for doc in relevant_docs])
        prompt = f"""Responda la siguiente pregunta de opción múltiple. Primero proporcione su razonamiento, luego escriba la respuesta final (a, b, c o d).
Proporcione su razonamiento y respuesta en el siguiente formato:
Razonamiento: [su razonamiento aquí]
Respuesta: [a, b, c o d]

Ejemplo:
Contexto: 
El context irá aquí.

Pregunta: Según la Constitución Española, ¿cuál de las siguientes afirmaciones es correcta respecto a la jerarquía de las fuentes del Derecho?

Opciones:
a) La Constitución establece que las leyes orgánicas tienen mayor jerarquía que las leyes ordinarias.
b) La Constitución no menciona explícitamente la jerarquía entre las leyes orgánicas y las leyes ordinarias.
c) La Constitución determina que las leyes ordinarias pueden modificar las leyes orgánicas en ciertos casos.
d) La Constitución especifica que las leyes orgánicas y las leyes ordinarias tienen la misma jerarquía

Razonamiento: La Constitución Española establece explícitamente que las leyes orgánicas tienen una jerarquía superior a las leyes ordinarias, ya que regulan materias de especial importancia y requieren un procedimiento de aprobación más riguroso.
Respuesta: a



Contexto:
{context}

Pregunta: {question['question']}

Opciones:
{chr(10).join([f"{k}) {v}" for k, v in question['options'].items() if v])}

"""
        
        # Get LLM response
        response = self.llm.query_llm(prompt)
        
        # Extract answer
        answer = None
        for line in response.split('\n'):
            if line.lower().startswith('respuesta:'):
                answer = line.split(':')[1].strip().lower()
                break
        
        return {
            "question": question["question"],
            "correct_answer": question["correct_answer"],
            "predicted_answer": answer,
            "context_used": [doc["data"]["text"] for doc in relevant_docs],
            "llm_response": response
        }

    def evaluate_questions(self, questions_file: str, context_file: str) -> Dict[str, Any]:
        """Evaluate all questions using RAG"""
        # Load questions
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        
        # Load and embed context
        self.load_context(context_file)
        
        # Evaluate each question
        results = []
        total_questions = len(questions)
        correct_answers = 0
        
        for question in tqdm(questions):
            result = self.evaluate_question(question)
            results.append(result)
            if result["predicted_answer"] == result["correct_answer"]:
                correct_answers += 1
        
        # Calculate accuracy
        accuracy = (correct_answers / total_questions) * 100
        
        return {
            "accuracy": accuracy,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "results": results
        }

def main():
    parser = argparse.ArgumentParser(description='Evaluate RAG system performance')
    parser.add_argument('questions_file', help='Path to the questions JSON file')
    parser.add_argument('context_file', help='Path to the context JSON file')
    parser.add_argument('--model', default='command-r-08-2024', 
                       help='Main model to use for generation (default: command-r-plus)')
    parser.add_argument('--embed-model', default='embed-multilingual-v3.0',
                       help='Model to use for embeddings (default: embed-multilingual-v3.0)')
    parser.add_argument('--rerank-model', default='rerank-multilingual-v3.0',
                       help='Model to use for reranking (default: rerank-multilingual-v3.0)')
    
    args = parser.parse_args()
    
    # Initialize LLM with specified models
    llm = LLM(provider="cohere", model_name=args.model)
    
    # Initialize evaluator
    evaluator = RAGEvaluator(llm)
    
    # Set model parameters
    evaluator.embed_model = args.embed_model
    evaluator.rerank_model = args.rerank_model
    
    # Evaluate questions
    results = evaluator.evaluate_questions(args.questions_file, args.context_file)
    
    # Print results
    print(f"\nAccuracy: {results['accuracy']:.2f}%")
    print(f"Total Questions: {results['total_questions']}")
    print(f"Correct Answers: {results['correct_answers']}")
    
    # Save detailed results
    output_file = "rag_evaluation_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nDetailed results saved to {output_file}")

if __name__ == "__main__":
    main() 