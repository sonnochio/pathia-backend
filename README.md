

# PDF Transform API

A FastAPI-based service that processes PDF exam papers and provides text transformation capabilities using Claude AI. The service can parse exam sections and modify text complexity levels while maintaining content integrity.

## Features

- PDF parsing and text extraction
- Intelligent exam section parsing using Claude AI
- Configurable text transformation levels (1-5)
- RESTful API endpoints for file upload and text transformation

## Prerequisites

- Python 3.7+
- Anthropic API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pdf-transform
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```env
ANTHROPIC_API_KEY="sk-ant-..."
```

## Requirements.txt
```txt
fastapi
uvicorn
python-multipart
anthropic
pypdf2
python-dotenv
pytest
pytest-asyncio
httpx
pycryptodome
```

## Usage

1. Start the server:
```bash
uvicorn pdf_transform:app --reload
```

2. API Endpoints:

- `POST /upload-pdf/`: Upload and process a PDF file
- `POST /transform-sections/`: Transform specific sections with desired complexity level

### Example Request

```python
# Transform sections
payload = {
    "section_indices": [0, 1],
    "level": 3
}
response = requests.post("http://localhost:8000/transform-sections/", json=payload)
```

## Transformation Levels

- Level 1: Original text (no modifications)
- Level 2: Simplified sentence structure, original vocabulary
- Level 3: Simpler language and shorter sentences
- Level 4: Basic vocabulary with clear paragraph breaks
- Level 5: Elementary vocabulary with simple patterns

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
```

Would you like me to expand on any particular section or add more details to the documentation?