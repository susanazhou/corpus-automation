import json
from llm import LLM
from typing import Dict, List
import argparse
from tqdm import tqdm

CATEGORIES = [
    "Constitucional",
    "Administrativo",
    "Civil",
    "Penal",
    "Procesal",
    "Internacional",
    "Mercantil",
    "Comunitario Europeo",
    "Teoría del Derecho y Filosofía del Derecho",
    "Otros"
]

def add_category_to_json(input_file: str, output_file: str, provider: str = "mistral", model_name: str = "mistral-medium") -> None:
    """
    Adds a category to each question in a JSON file using an LLM.
    
    Args:
        input_file (str): Path to the input JSON file
        output_file (str): Path to save the output JSON file
        provider (str): LLM provider to use (default: "mistral")
        model_name (str): Model name to use (default: "mistral-medium")
    """
    # Initialize LLM
    llm = LLM(provider=provider, model_name=model_name)
    
    # Read input JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Process each question
    for item in tqdm(data):
        if 'question' in item and 'category' not in item:
            # Create prompt for the LLM
            prompt = f"""Dada la siguiente pregunta, asígnala a una de estas categorías:
            {', '.join(CATEGORIES)}
            
            Pregunta: {item['question']}
            
            Devuelve únicamente el nombre de la categoría, nada más."""
            
            # Get category from LLM
            category = llm.query_llm(prompt, max_tokens=50, temperature=0.0)
            
            # Clean up the response and ensure it's a valid category
            category = category.strip()
            if category not in CATEGORIES:
                category = "Otros"  # Default to "Otros" if category is not recognized
            
            # Add category to the item
            item['category'] = category.strip(',. ').lower()
    
    # Write output JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    print("Adding categories to questions...")
    years = [2004, 2005, 2006, 2023, 2024]
    for year in years:
        input_file = f"data/parsing/{year}/questions.json"
        output_file = f"data/parsing/{year}/categorized_questions.json"
        add_category_to_json(
            input_file=input_file,
            output_file=output_file,
            provider="mistral",
            model_name="mistral-small-latest"
        )

if __name__ == '__main__':
    main()
