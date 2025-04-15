import json
import os
import sys
from llm import LLM

def load_questions(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def evaluate_questions(file_path, llm):
    questions = load_questions(file_path)
    total_questions = len(questions)
    correct_answers = 0
    
    for question in questions:
        print("Pregunta:")
        print(f"{question['question']}\n")
        
        # Print options
        options_text = ""
        for option, text in question['options'].items():
            if text:  # Only include non-empty options
                options_text += f"{option}) {text}\n"
        
        # Create prompt for LLM
        prompt = f"""Por favor responda la siguiente pregunta de opción múltiple. Primero proporcione su razonamiento, luego escribe la respuesta final (a, b, c, o d).
Proporcione su razonamiento y respuesta en el siguiente formato:
Razonamiento: [su razonamiento aquí]
Respuesta: [a, b, c, o d]

Ejemplo:
Pregunta: Según la Constitución Española, ¿cuál de las siguientes afirmaciones es correcta respecto a la jerarquía de las fuentes del Derecho?

Opciones:
a) La Constitución establece que las leyes orgánicas tienen mayor jerarquía que las leyes ordinarias.
b) La Constitución no menciona explícitamente la jerarquía entre las leyes orgánicas y las leyes ordinarias.
c) La Constitución determina que las leyes ordinarias pueden modificar las leyes orgánicas en ciertos casos.
d) La Constitución especifica que las leyes orgánicas y las leyes ordinarias tienen la misma jerarquía

Razonamiento: La Constitución Española establece explícitamente que las leyes orgánicas tienen una jerarquía superior a las leyes ordinarias, ya que regulan materias de especial importancia y requieren un procedimiento de aprobación más riguroso.
Respuesta: a


Pregunta: {question['question']}

Opciones:
{options_text}

"""

        # Get LLM response
        response = llm.query_llm(prompt)
        print("\nLLM Response:")
        print(response)
        
        # Extract answer from response
        answer = None
        for line in response.split('\n'):
            if line.lower().startswith('respuesta:'):
                answer = line.split(':')[1].strip().lower()
                break
        
        # Check if answer is correct
        if answer == question['correct_answer']:
            correct_answers += 1
            print("\n✅ Correct!")
        else:
            print(f"\n❌ Incorrect. The correct answer was {question['correct_answer']}")
        
        print("\n----------------------------------------")
    
    # Calculate and return accuracy
    accuracy = (correct_answers/total_questions)*100
    return accuracy

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python evaluate_questions.py <questions_file_path>")
        sys.exit(1)
    
    # Initialize LLM
    llm = LLM(provider="cohere", model_name="command-r-08-2024")
    
    file_path = sys.argv[1]
    accuracy = evaluate_questions(file_path, llm)
    print(f"\nAccuracy: {accuracy:.2f}%") 