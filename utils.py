import os
import requests
from dotenv import load_dotenv
import pdfplumber
import re

# Load environment variable from .env
load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

def extract_text(uploaded_file):
    """Extract text from uploaded PDF or TXT file."""
    if uploaded_file.name.endswith('.pdf'):
        text = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    else:
        text = uploaded_file.read().decode('utf-8')
    return text.strip()


def generate_questions(text, num_questions):
    """Generate meaningful, higher-order questions using Together AI."""
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    # Prompt tuned for application & reasoning
    prompt = (
        f"You are a creative educational assistant. Based on the following text, generate exactly {num_questions} diverse, higher-order thinking questions. "
        f"Questions should cover real-world applications, conceptual understanding, problem-solving, and comparisons of composite solids. "
        f"Use a mix of question types: why, how, what-if, compare, and applied math. "
        f"Only return the questions as a numbered list (e.g., 1. ..., 2. ...). Do not include explanations or headings.\n\n"
        f"CONTENT:\n{text.strip()}\n\nQUESTIONS:"
    )

    payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.1",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a strict question generator. Only return the questions. "
                    "Do not include statements like 'Sure!', 'Understood', or any explanation."
                )
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 900
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        output = response.json()
        generated_text = output["choices"][0]["message"]["content"]

        # Debug: print the raw output from the model
        print("\n\n--- RAW MODEL OUTPUT ---\n")
        print(generated_text)
        print("\n-------------------------\n")

        # Try to extract numbered questions
        questions = re.findall(r'\d+[.)]\s*(.+?\?)', generated_text)

        # Fallback: use lines with question marks
        if not questions:
            lines = generated_text.strip().split("\n")
            questions = [line.strip("0123456789. )").strip() for line in lines if "?" in line]

        # Final fallback
        if not questions:
            return ["No questions were detected in the response. Try again with a longer or clearer concept file."]

        return questions[:num_questions]

    except Exception as e:
        return [f"Error: {e}"]
