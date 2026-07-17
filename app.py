import streamlit as st
import pypdf
import google.generativeai as genai

# Page settings optimized for flashcard viewing
st.set_page_config(page_title="Oral Exam Flashcard Gen", page_icon="🪞", layout="centered")
st.title("🪞 Oral Exam Active Recall Generator")
st.write("Convert medical PDFs into high-yield, short-answer flashcards specifically tailored for oral examination drills.")

# Sidebar setup for security
st.sidebar.header("🔑 API Setup")
st.sidebar.markdown("[Get a free Gemini API key here](https://aistudio.google.com/)")
api_key = st.sidebar.text_input("Enter your Gemini API Key:", type="password")
num_cards = st.sidebar.slider("Number of flashcards to generate", min_value=5, max_value=25, value=10)

def extract_pdf_text(uploaded_file):
    reader = pypdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def generate_oral_flashcards(text_content, key, count):
    genai.configure(api_key=key)
    
    # System prompt explicitly engineered for fast oral-recall answers
    system_instruction = (
        "You are an expert medical school professor testing students via an oral examination viva. "
        "Your task is to extract high-yield medical facts from the text and format them into brief, "
        "direct question-and-answer flashcards optimized for fast mental recall.\n\n"
        "Rules for the Flashcards:\n"
        "1. The Front (Question) must be a direct prompt or brief clinical sign. Never include choices like A, B, C, D.\n"
        "2. The Back (Answer) must be clear, concise, and answerable aloud in 5-10 seconds. Focus on the single gold-standard diagnostic tool, first-line medication, specific pathway mutation, or absolute pathognomonic sign.\n\n"
        "Format every single card exactly like this example:\n"
        "### CARD X\n"
        "**FRONT (Question):** [Insert direct query here, e.g., What is the first-line medication for acute status epilepticus?]\n"
        "**BACK (Answer):** [Insert short answer here, e.g., IV Lorazepam (Ativan).]\n"
        "--------------------------------------------------\n"
    )
    
    model = genai.GenerativeModel(model_name="gemini-3.5-flash", system_instruction=system_instruction)
    truncated_text = text_content[:40000] 
    prompt = f"Generate exactly {count} direct Q&A oral exam flashcards based on this medical text:\n\n{truncated_text}"
    response = model.generate_content(prompt)
    return response.text

# Main interface
uploaded_file = st.file_uploader("📂 Choose a medical lecture PDF", type=["pdf"])

if uploaded_file and not api_key:
    st.info("💡 Please enter your Gemini API key in the sidebar to start generating.")

if uploaded_file and api_key:
    if st.button("🧠 Create Flashcards", type="primary"):
        with st.spinner("Analyzing text and creating rapid-fire oral flashcards..."):
            try:
                raw_text = extract_pdf_text(uploaded_file)
                flashcards_output = generate_oral_flashcards(raw_text, api_key, num_cards)
                st.success(f"🎉 Created {num_cards} flashcards successfully!")
                
                # Download button for printing or archiving
                st.download_button(
                    label="📥 Download Flashcards (.txt)",
                    data=flashcards_output,
                    file_name="Medical_Oral_Flashcards.txt",
                    mime="text/plain"
                )
                st.markdown("---")
                st.markdown(flashcards_output)
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")

