import os
from typing import List, Dict
import json
from tqdm import tqdm
from llm import LLM
import re

def split_text_into_chunks(text: str, chunk_size: int = 3000, window_size: int = 200) -> List[str]:
    """
    Split text into chunks with windows to avoid splitting questions in half.
    Each chunk includes a window of text from both the previous and next chunks.
    
    Args:
        text (str): The text to split
        chunk_size (int): Maximum size of each chunk
        window_size (int): Size of the window to look for question boundaries
    
    Returns:
        List[str]: List of text chunks with overlapping windows
    """
    chunks = []
    current_pos = 0
    text_length = len(text)
    
    while current_pos < text_length:
        # Calculate the end position for this chunk
        end_pos = min(current_pos + chunk_size, text_length)
        
        # Add the chunk with windows
        start_window = max(0, current_pos - window_size)
        end_window = min(text_length, end_pos + window_size)
        chunk = text[start_window:end_window]
        chunks.append(chunk)
        
        current_pos = end_pos
    
    return chunks

def parse_question_chunk(chunk: str, llm: LLM) -> Dict[str, Dict]:
    """
    Parse a chunk of text containing questions into a dictionary with question_id as key.
    
    Args:
        chunk (str): The text chunk containing questions
        llm (LLM): The LLM instance to use for parsing
    
    Returns:
        Dict[str, Dict]: Dictionary of questions with question_id as key
    """
    prompt = f"""Please format the following text into a structured format where each question has:
1. A question_id (number)
2. The question text
3. The choices (a, b, c, d)

Only inlcude the formatted question and choices if the text contains all the information.

Format should be:
question_id
question
choices

question_id
question
choices

Here's the text to format:
{chunk}"""

    print("prompt: ", prompt)
    # Call the LLM
    response = llm.query_llm(
        prompt=prompt,
        max_tokens=10000,
        temperature=0.0
    )
    
    print(response)
    # Split into questions by double newline
    questions = {}
    for question_text in response.split('\n\n'):
        lines = [line.strip() for line in question_text.split('\n') if line.strip('`., ')]
        if len(lines) >= 3:  # At least question_id, question, and one choice
            try:
                question_id = int(lines[0])
            except:
                print("question_id parsing error: ", lines[0])
                continue
            question = lines[1]
            # Get all remaining lines as choices
            choices = {}
            for choice in lines[2:]:
                if choice.startswith(('a)', 'b)', 'c)', 'd)')):
                    letter = choice[0]
                    text = choice[2:].strip()
                    choices[letter] = text
            
            if question and len(choices) == 4:
                questions[question_id] = {
                    'question': question,
                    'options': choices,
                    'correct_answer': None
                }
    
    return questions

def parse_answer(answers: str) -> Dict[str, str]:
    """
    Parse the answer line from the text into a dictionary mapping question IDs to correct answers.
    
    Args:
        answers (str): The text containing the answers in the format "question_id answer question_id answer ..."
    
    Returns:
        Dict[str, str]: Dictionary mapping question IDs to their correct answers (a, b, c, or d)
    """
    # Extract question-answer pairs using regex
    pairs_pattern = r"(\d+)\s+([a-dA-D])"
    pairs = re.findall(pairs_pattern, answers)
    
    # Create dictionary from pairs
    return {int(question_id): answer.lower() for question_id, answer in pairs}

def clean_text(input_file: str, output_file: str) -> None:
    """
    Cleans and formats text from an input file using an LLM and saves the result to an output file.
    
    Args:
        input_file (str): Path to the input text file
        output_file (str): Path where the cleaned text will be saved
    """
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    
    answers_line = text.split('\n')[-1]
    answers = parse_answer(answers_line)
    print("answers: ", answers)
    text = '\n'.join(text.split('\n')[:-1])


    # Initialize LLM client
    llm = LLM(provider="mistral", model_name="mistral-large-latest")
    
    # Split text into chunks
    chunks = split_text_into_chunks(text)
    
    # Parse each chunk
    all_questions = {}
    for chunk in tqdm(chunks):
        questions = parse_question_chunk(chunk, llm)
        questions = {question_id: questions[question_id] for question_id in questions if question_id not in all_questions}
        all_questions.update(questions)

    # add answers to all_questions
    for question_id in all_questions:
        try:
            correct_answer = answers[question_id]
            all_questions[question_id]['correct_answer'] = correct_answer
        except:
            print("question_id not found: ", question_id)
        
    
    # reformat all_questions to be a list of questions to be like {question_id, question, options, correct_answer}
    final_questions = []
    for question_id, question in all_questions.items():
        final_questions.append({
            "question_id": question_id,
            "question": question['question'],
            "options": question['options'],
            "correct_answer": question['correct_answer']
        })

    # Write the formatted questions to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_questions, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # Example usage
    years = [2023, 2024]
    for year in years: 
        input_file = f"data/parsing/{year}/text.txt"
        output_file = f"data/parsing/{year}/questions.json"
        clean_text(input_file, output_file) 