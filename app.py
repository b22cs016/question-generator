import streamlit as st
from utils import extract_text, generate_questions

st.set_page_config(page_title="Question Generator", layout="centered")

st.title("📘 Question Generator")
st.write("Upload a concept file and generate up to 10 relevant questions.")

uploaded_file = st.file_uploader("Upload your concept file (.pdf or .txt)", type=['pdf', 'txt'])

num_questions = st.slider("Number of Questions", min_value=1, max_value=10, value=5)

if st.button("Generate"):
    if uploaded_file is not None:
        with st.spinner("Extracting content..."):
            text = extract_text(uploaded_file)
        with st.spinner("Generating questions..."):
            questions = generate_questions(text, num_questions)
        st.success("Here are your questions:")
        for i, q in enumerate(questions, 1):
            st.markdown(f"**Q{i}.** {q}")
    else:
        st.warning("Please upload a valid file.")
