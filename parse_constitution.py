import json
import re

def parse_constitution(input_file, output_file):
    # Read the constitution file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into articles using regex pattern
    # The pattern looks for "Artículo X." followed by the content until the next article
    article_pattern = r'Artículo (\d+)\.\s*(.*?)(?=Artículo \d+\.|$)'
    articles = re.findall(article_pattern, content, re.DOTALL)
    
    # Create the data structure
    data = [
            {
                "data":{
                    "text": f"Artículo {num}. {text.strip()}"
                }
                
            }
            for num, text in articles
    ]
    
    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    input_file = "data/constitucion/constitucion_espanola/text.txt"
    output_file = "data/constitucion/constitucion_espanola/articles.json"
    parse_constitution(input_file, output_file)
