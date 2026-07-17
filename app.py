import streamlit as st
import pypdf
import google.generativeai as genai

# Page settings
st.set_page_config(page_title="MedExam Generator", page_icon="🏥")
st.title("🏥 High-Yield Med School Question Generator")
st.write("Upload a lecture PDF to generate USMLE-style questions.")

# Sidebar setup for security
st.sidebar.header("🔑 API Setup")
st.sidebar.markdown("[Get a free Gemini API key here](https://google.com)")
api_key = st.sidebar.text_input("Enter your Gemini API Key:", type="password")
num_questions = st.sidebar.slider("Number of questions to generate", min_value=3, max_value=15, value=5)

def extract_pdf_text(uploaded_file):
    reader = pypdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def generate_medical_questions(text_content, key, count):
    genai.configure(api_key=key)
    system_instruction = (
        "You are an expert medical school professor and USMLE board examiner. "
        "Your task is to generate high-yield, 4-option multiple-choice questions based on the provided text.\n\n"
        "Format every single question exactly like this example:\n"
        "### Question X\n"
        "[Insert clinical vignette here]\n"
        "A) Option A\n"
        "B) Option B\n"
        "C) Option C\n"
        "D) Option D\n\n"
        "**Correct Answer:** [Letter]\n"
        "**Explanation:** [Detailed paragraph breaking down why the choice is right and others are wrong.]\n"
        "--------------------------------------------------\n"
    )
    model = genai.GenerativeModel(model_name="gemini-3.5-flash", system_instruction=system_instruction)
    truncated_text = text_content[:40000] 
    prompt = f"Generate exactly {count} high-yield multiple-choice questions based on this medical text:\n\n{truncated_text}"
    response = model.generate_content(prompt)
    return response.text

# Main website area
uploaded_file = st.file_uploader("📂 Choose a medical PDF file", type=["pdf"])

if uploaded_file and not api_key:
    st.info("💡 Please enter your Gemini API key in the sidebar to start generating.")

if uploaded_file and api_key:
    if st.button("🧠 Generate Questions", type="primary"):
        with st.spinner("Analyzing PDF and drafting clinical vignettes..."):
            try:
                raw_text = extract_pdf_text(uploaded_file)
                questions_output = generate_medical_questions(raw_text, api_key, num_questions)
                st.success(f"🎉 Generated {num_questions} questions successfully!")
                
                st.download_button(
                    label="📥 Download Questions (.txt)",
                    data=questions_output,
                    file_name="Medical_Exam_Questions.txt",
                    mime="text/plain"
                )
                st.markdown("---")
                st.markdown(questions_output)
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
