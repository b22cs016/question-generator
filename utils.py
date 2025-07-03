import openai
import os
from dotenv import load_dotenv
import pdfplumber

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_text(uploaded_file):
    if uploaded_file.name.endswith('.pdf'):
        text = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    else:
        text = uploaded_file.read().decode('utf-8')
    return text

def generate_questions(text, num_questions):
    prompt = f"Generate {num_questions} thought-provoking questions based on the following content:\n\n{text}\n\nQuestions:"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant who generates educational questions."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7
    )
    questions_raw = response['choices'][0]['message']['content']
    return [q.strip("0123456789. ").strip() for q in questions_raw.strip().split('\n') if q.strip()]
