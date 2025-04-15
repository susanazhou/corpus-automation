# Corpus Automation Pipeline

![SomosNLP](somosNLP.svg)

This project was developed as part of the [SomosNLP Hackathon 2025](https://somosnlp.org/hackathon), focused on advancing Spanish language AI and NLP.

This repository contains a pipeline for processing and analyzing legal exam questions. The pipeline consists of several components that work together to parse, categorize, and evaluate questions.

## Pipeline Components

### 1. PDF Parsing (`parse_pdf.py` and `parse_pdf_mistral.py`)
- **Purpose**: Extracts text and images from PDF files containing exam questions
- **Features**:
  - Extracts text with layout information
  - Handles tables and formatting
  - Can extract images from PDFs
  - Supports both synchronous and batch processing
  - Uses Mistral's OCR service for high-quality text extraction
- **Output**: Text files, markdown files, and extracted images

### 2. Text Formatting (`format_text.py`)
- **Purpose**: Processes raw text into structured question format
- **Features**:
  - Splits text into manageable chunks
  - Uses LLM to identify and structure questions
  - Extracts question IDs, question text, and options
  - Handles answer parsing
- **Output**: JSON file with structured questions

### 3. Category Addition (`add_categories.py`)
- **Purpose**: Adds legal categories to questions using LLM
- **Features**:
  - Uses predefined legal categories
  - Automatically categorizes questions based on content
  - Supports multiple LLM providers
- **Categories**:
  - Constitucional
  - Administrativo
  - Civil
  - Penal
  - Procesal
  - Internacional
  - Mercantil
  - Comunitario Europeo
  - Teoría del Derecho y Filosofía del Derecho
  - Otros

### 4. Merge and Filter (`merge_and_filter.py`)
- **Purpose**: Combines questions from multiple sources and filters by category
- **Features**:
  - Merges questions from different years/sources
  - Filters questions by legal category
  - Creates organized datasets for specific categories
- **Output**: Filtered JSON files containing questions by category

### 5. Evaluation (`evaluate.py`)
- **Purpose**: Evaluates LLM performance on answering questions
- **Features**:
  - Tests LLM accuracy on multiple-choice questions
  - Provides detailed reasoning for answers
  - Calculates accuracy metrics
- **Output**: Accuracy statistics and detailed evaluation results

### 6. RAG Evaluation (`evaluate_rag.py`)
- **Purpose**: Evaluates Retrieval-Augmented Generation (RAG) system performance
- **Features**:
  - Uses context from legal documents
  - Implements document retrieval and reranking
  - Evaluates answer quality with context
  - Provides detailed analysis of performance
- **Output**: Comprehensive evaluation results including accuracy and context usage

## Usage

1. **PDF Processing**:
   ```bash
   python parse_pdf.py <pdf_file> <output_dir>
   ```

2. **Text Formatting**:
   ```bash
   python format_text.py <input_file> <output_file>
   ```

3. **Category Addition**:
   ```bash
   python add_categories.py <input_file> <output_file>
   ```

4. **Merge and Filter**:
   ```bash
   python merge_and_filter.py --input_dir <input_dir> --category <category> --output_path <output_path>
   ```

5. **Evaluation**:
   ```bash
   python evaluate.py <questions_file>
   ```

6. **RAG Evaluation**:
   ```bash
   python evaluate_rag.py <questions_file> <context_file>
   ```

## Dependencies

- Python 3.x
- Required packages:
  - pdfplumber
  - PyMuPDF
  - mistralai
  - cohere
  - numpy
  - tqdm

## Configuration

- API keys for LLM services (Mistral, Cohere) should be set as environment variables
- Input files should be in the specified format
- Output directories will be created automatically if they don't exist

## Results

The pipeline produces:
- Structured question datasets
- Categorized questions by legal domain
- Evaluation metrics for LLM performance
- RAG system performance analysis

## Notes

- The pipeline is designed for Spanish legal exam questions
- LLM models can be configured based on requirements
- Processing large datasets may require significant computational resources