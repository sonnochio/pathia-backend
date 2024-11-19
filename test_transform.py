# test_transform.py
import asyncio
import os
from dotenv import load_dotenv
from pdf_transform import transform_text, process_pdf

load_dotenv()

def print_section_text(text: str, title: str = "Text"):
    """Print section text with clear formatting."""
    print(f"\n{title}:")
    print("=" * 80)
    print(text)
    print("=" * 80)

async def test_interface():
    """Test interface for PDF processing with section selection."""
    pdf_path = "test_paper.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Error: Test PDF file not found at {pdf_path}")
        return
        
    print(f"Processing PDF: {pdf_path}")
    with open(pdf_path, "rb") as f:
        pdf_content = f.read()
        
    print("\nExtracting sections...")
    sections = process_pdf(pdf_content)
    
    # Display all extracted sections with full text
    print("\nExtracted Sections:")
    for i, section in enumerate(sections):
        print(f"\nSection {i + 1}:")
        print("-" * 80)
        print(f"Question: {section['question']}")
        print(f"Task: {section['task']}")
        print(f"Marks: {section['marks']}")
        print_section_text(section['text'], "Original Text")
    
    # Get user input for sections to transform
    while True:
        try:
            section_input = input("\nEnter section numbers to transform (comma-separated, e.g., '1,2,3' or 'all'): ").strip()
            
            if section_input.lower() == 'all':
                selected_sections = list(range(len(sections)))
            else:
                selected_sections = [int(x.strip()) - 1 for x in section_input.split(',')]
                
            # Validate section numbers
            if any(i < 0 or i >= len(sections) for i in selected_sections):
                print("Invalid section number(s). Please try again.")
                continue
                
            break
        except ValueError:
            print("Invalid input. Please enter numbers separated by commas or 'all'.")
    
    # Get transformation level
    while True:
        try:
            level = int(input("\nEnter transformation level (1-5): "))
            if 1 <= level <= 5:
                break
            print("Level must be between 1 and 5.")
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 5.")
    
    # Transform selected sections
    print("\nTransforming selected sections...")
    for idx in selected_sections:
        section = sections[idx]
        print(f"\nSection {idx + 1} - Question {section['question']}:")
        print("-" * 80)
        
        # Display original text
        print_section_text(section['text'], "Original Text")
        
        # Transform and display transformed text
        transformed = transform_text(section['text'], level)
        print_section_text(transformed, f"Transformed Text (Level {level})")
        
        if len(selected_sections) > 1:
            input("\nPress Enter to continue to next section...")

if __name__ == "__main__":
    asyncio.run(test_interface())