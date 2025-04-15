import json
import re

def parse_markdown(input_file, output_file):
    # Read the markdown file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into sections using regex pattern for ## titles
    # The pattern looks for "## Title" followed by the content until the next title
    title_pattern = r'##\s+(.*?)\n(.*?)(?=##\s+|$)'
    sections = re.findall(title_pattern, content, re.DOTALL)
    
    # Create the data structure
    data = [
        {
            "data": {
                "text": f"## {title.strip()}\n{content.strip()}"
            }
        }
        for title, content in sections
    ]
    
    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    input_file = "data/codigo_derecho_constitiucional/codigo1/text.txt"  # Replace with your input file path
    output_file = "data/codigo_derecho_constitiucional/codigo1.json"  # Replace with your desired output file path
    parse_markdown(input_file, output_file) 