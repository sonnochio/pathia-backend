# pdf_transform.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import anthropic
import PyPDF2
from io import BytesIO
import os
from dotenv import load_dotenv
import json
import re

# Load environment variables
load_dotenv()

app = FastAPI()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

class Section(BaseModel):
    question: str
    text: str
    task: str
    marks: int

class TransformRequest(BaseModel):
    section_indices: List[int]
    level: int

class TransformedSection(BaseModel):
    index: int
    question: str
    original: str
    transformed: str

class TransformationResponse(BaseModel):
    transformed_sections: List[TransformedSection]

def extract_sections_with_claude(text: str) -> List[Dict[str, str]]:
    """Use Claude to intelligently parse the exam paper into sections."""
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=3000,
            system="Return only the JSON array without any additional text or explanations. Each object in the array should have exactly these keys: question, text, task, marks.",
            messages=[
                {
                    "role": "user",
                    "content": f"""Parse this GCSE English comprehension exam into a JSON array where each object has these exact keys:
                    - question (the question number)
                    - text (the passage or text if present)
                    - task (the actual question or task)
                    - marks (the number of marks available)
                    
                    Exam content:
                    {text}"""
                }
            ]
        )
        
        # Extract JSON from response
        response_text = message.content[0].text.strip()
        
        # Remove any potential markdown code block syntax
        response_text = re.sub(r'^```json\s*', '', response_text)
        response_text = re.sub(r'\s*```$', '', response_text)
        
        # Parse the JSON
        sections = json.loads(response_text)
        
        # Validate the structure
        for section in sections:
            required_keys = {'question', 'text', 'task', 'marks'}
            if not all(key in section for key in required_keys):
                raise ValueError(f"Missing required keys. Section must contain: {required_keys}")
        
        return sections

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing sections: {str(e)}")

def process_pdf(pdf_file: bytes) -> List[Dict[str, str]]:
    """Process PDF and extract sections using Claude."""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file))
        full_text = ""
        
        for page in pdf_reader.pages:
            full_text += page.extract_text() + "\n"
        
        sections = extract_sections_with_claude(full_text)
        return sections
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

def transform_text(text: str, level: int) -> str:
    """Transform text using Claude API based on specified level."""
    try:
        # Define transformation instructions for each level
        instructions = {
            1: "Maintain the original text exactly as provided, without any modifications.",
            2: "Rewrite using simpler sentence structures while keeping original vocabulary. Maintain academic tone.",
            3: "Rewrite using simpler language and shorter sentences. Break complex ideas into digestible parts.",
            4: "Rewrite using basic vocabulary and very short sentences. Create clear paragraph breaks.",
            5: "Rewrite using elementary vocabulary and simple repetitive patterns. Break into small chunks."
        }
        
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            system="Return only the transformed text without any explanations, introductions, or metadata.",
            messages=[
                {
                    "role": "user",
                    "content": f"{instructions[level]}\n\nText to transform:\n{text}"
                }
            ]
        )
        
        # Extract and clean the transformed text
        transformed_text = message.content[0].text.strip()
        
        # Remove any potential markdown syntax
        transformed_text = re.sub(r'^```.*\n', '', transformed_text)
        transformed_text = re.sub(r'\n```$', '', transformed_text)
        
        return transformed_text
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-pdf/", response_model=List[Section])
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process PDF file."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    contents = await file.read()
    sections = process_pdf(contents)
    return sections

@app.post("/transform-sections/", response_model=TransformationResponse)
async def transform_sections(transform_request: TransformRequest, sections: List[Section]):
    """Transform multiple sections based on specified indices and level."""
    transformed_sections = []
    
    for idx in transform_request.section_indices:
        if 0 <= idx < len(sections):
            original_text = sections[idx].text
            transformed_text = transform_text(original_text, transform_request.level)
            
            transformed_sections.append(TransformedSection(
                index=idx,
                question=sections[idx].question,
                original=original_text,
                transformed=transformed_text
            ))
            
    return TransformationResponse(transformed_sections=transformed_sections)