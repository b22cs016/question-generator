import re
import pdfplumber
import streamlit as st
import requests

# Read Together AI API key securely
TOGETHER_API_KEY = st.secrets["TOGETHER_API_KEY"]

def extract_text(uploaded_file):
    """Extract text from a PDF or TXT file."""
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
    """Generate diverse, meaningful questions using Together AI."""
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    # STRONG prompt for better diversity + formatting
    prompt = (
        f"Generate exactly {num_questions} diverse and meaningful questions based on the content below. "
        f"Include a mix of factual (what/how), conceptual (why), comparative, and real-world application questions. "
        f"Only return the questions, in a numbered list format (1., 2., etc.), with each ending in a question mark.\n\n"
        f"Content:\n{text.strip()}\n\nQuestions:"
    )

    payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.1",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a strict educational question generator. Do not provide explanations or headings. "
                    "Only output a numbered list of diverse questions ending in question marks."
                )
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        output = response.json()
        generated_text = output["choices"][0]["message"]["content"]

        # Print debug output (Streamlit UI option)
        if st.session_state.get("debug_mode", False):
            st.markdown("### 🔍 Raw model output")
            st.code(generated_text)

        # Extract using regex
        questions = re.findall(r'\d+[.)]?\s*(.+?\?)', generated_text)

        # Fallback: use any lines with question marks
        if not questions:
            lines = generated_text.strip().split("\n")
            questions = [line.strip("0123456789. )").strip() for line in lines if "?" in line]

        # Final fallback
        if not questions:
            return ["No questions were detected in the response. Try again with a longer or clearer concept file."]

        return questions[:num_questions]

    except Exception as e:
        return [f"Error: {e}"]
