import streamlit as st
import pypdf
import google.generativeai as genai

# Page settings
st.set_page_config(page_title="Anki Oral Card Gen", page_icon="🧠", layout="centered")
st.title("🧠 Anki Oral Flashcard Generator")
st.write("Convert medical PDFs into a text file that imports directly into Anki as direct, short-answer oral cards.")

# Sidebar setup
st.sidebar.header("🔑 API Setup")
st.sidebar.markdown("[Get a free Gemini API key here](https://google.com)")
api_key = st.sidebar.text_input("Enter your Gemini API Key:", type="password")
num_cards = st.sidebar.slider("Number of flashcards to generate", min_value=5, max_value=30, value=15)

def extract_pdf_text(uploaded_file):
    reader = pypdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def generate_anki_cards(text_content, key, count):
    genai.configure(api_key=key)
    
    # System prompt formatted specifically for Anki tab-separated import
    system_instruction = (
        "You are an expert medical school professor. Your job is to extract high-yield facts "
        "from the provided medical text and format them as short-answer active recall flashcards.\n\n"
        "CRITICAL FORMATTING RULE:\n"
        "You must output every card on its own single line. "
        "Separate the Question (Front) from the Answer (Back) using exactly ONE Tab character (\\t).\n"
        "Do not include card numbers, bullet points, headers, or any empty lines.\n\n"
        "Example structural layout (where -> represents a single Tab press):\n"
        "What is the first-line medication for acute status epilepticus?->IV Lorazepam.\n"
        "What is the pathognomonic finding for Acute Myeloid Leukemia?->Auer rods.\n\n"
        "Rules for content:\n"
        "1. No multiple choice. Questions must be direct prompts for oral recitation.\n"
        "2. Answers must be atomic and short (1-5 words or a brief phrase) for rapid mental memory checks."
    )
    
    model = genai.GenerativeModel(model_name="gemini-3.5-flash", system_instruction=system_instruction)
    truncated_text = text_content[:40000] 
    prompt = f"Generate exactly {count} Tab-Separated flashcards from this medical text:\n\n{truncated_text}"
    response = model.generate_content(prompt)
    return response.text

# Main interface
uploaded_file = st.file_uploader("📂 Choose a medical lecture PDF", type=["pdf"])

if uploaded_file and not api_key:
    st.info("💡 Please enter your Gemini API key in the sidebar to start generating.")

if uploaded_file and api_key:
    if st.button("🚀 Generate Anki File", type="primary"):
        with st.spinner("Processing PDF and converting into Anki flashcards..."):
            try:
                raw_text = extract_pdf_text(uploaded_file)
                anki_output = generate_anki_cards(raw_text, api_key, num_cards)
                
                st.success(f"🎉 Created {num_cards} cards successfully!")
                
                # Download button for Anki TXT file
                st.download_button(
                    label="📥 Download Anki Import File (.txt)",
                    data=anki_output,
                    file_name="Anki_Oral_Cards.txt",
                    mime="text/plain"
                )
                
                # Visual preview layout for user verification
                st.markdown("### 👀 Card Preview (Question vs Answer)")
                lines = [line for line in anki_output.split('\n') if line.strip()]
                for index, line in enumerate(lines):
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        st.markdown(f"**Card {index+1}**")
                        st.info(f"❓ **Front:** {parts[0]}")
                        st.success(f"💡 **Back:** {parts[1]}")
                    else:
                        st.text(f"Raw line layout error: {line}")
                        
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
