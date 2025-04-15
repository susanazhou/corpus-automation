import json
import os
from pathlib import Path
from typing import List, Dict, Any

def merge_and_filter_questions(
    input_dir: str,
    category: str,
    output_path: str
) -> None:
    """
    Merge questions from categorized_questions.json files in subfolders and filter by category.
    
    Args:
        input_dir (str): Path to the directory containing subfolders with categorized_questions.json files
        category (str): Category to filter questions by
        output_path (str): Path where to save the filtered questions
    """
    all_questions: List[Dict[str, Any]] = []
    
    # Walk through all subdirectories
    for root, _, files in os.walk(input_dir):
        if 'categorized_questions.json' in files:
            file_path = os.path.join(root, 'categorized_questions.json')
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    questions = json.load(f)
                    all_questions.extend(questions)
            except json.JSONDecodeError as e:
                print(f"Error reading {file_path}: {e}")
            except Exception as e:
                print(f"Unexpected error reading {file_path}: {e}")
    
    # Filter questions by category
    filtered_questions = [
        q for q in all_questions
        if q.get('category', '').lower() == category.lower()
    ]
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Save filtered questions
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(filtered_questions, f, indent=2, ensure_ascii=False)
    
    print(f"Found {len(all_questions)} total questions")
    print(f"Filtered to {len(filtered_questions)} questions in category '{category}'")
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Merge and filter questions from multiple JSON files')
    parser.add_argument('--input_dir', help='Directory containing subfolders with categorized_questions.json files')
    parser.add_argument('--category', help='Category to filter questions by')
    parser.add_argument('--output_path', help='Path where to save the filtered questions')
    
    args = parser.parse_args()
    merge_and_filter_questions(args.input_dir, args.category, args.output_path) 