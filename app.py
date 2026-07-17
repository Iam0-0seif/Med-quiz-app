import streamlit as st
import pypdf
import google.generativeai as genai
import time
import random

# Page settings
st.set_page_config(page_title="Anki Oral Card Gen", page_icon="🧠", layout="centered")
st.title("🧠 Dynamic Anki Flashcard Generator")
st.write("Convert medical PDFs into brand-new, unique oral active-recall cards every single time.")

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
    
    system_instruction = (
        "You are an expert medical school professor. Your job is to extract high-yield facts "
        "from the provided medical text and format them as short-answer active recall flashcards.\n\n"
        "CRITICAL FORMATTING RULE:\n"
        "You must output every card on its own single line. "
        "Separate the Question (Front) from the Answer (Back) using exactly ONE Tab character (\\t).\n"
        "Do not include card numbers, bullet points, headers, or any empty lines.\n\n"
        "Rules for content:\n"
        "1. No multiple choice. Questions must be direct prompts for oral recitation.\n"
        "2. Answers must be atomic and short (1-5 words or a brief phrase) for rapid mental memory checks.\n"
        "3. Focus on a completely random mixture of pathophysiology, diagnosis, first-line treatments, and key mutations."
    )
    
    # We change the model name configuration to allow maximum creativity and randomness
    generation_config = {
        "temperature": 1.0,  # Maximizes variety so it doesn't pick the same facts
        "top_p": 0.95,
        "top_k": 40,
    }
    
    model = genai.GenerativeModel(
        model_name="gemini-3.5-flash", 
        system_instruction=system_instruction,
        generation_config=generation_config
    )
    
    truncated_text = text_content[:40000] 
    
    # Injected a completely random seed value and timestamp to break the AI's internal predictability pattern
    random_seed = random.randint(1, 100000)
    current_time = time.time()
    
    prompt = (
        f"Generate exactly {count} unique Tab-Separated flashcards from this medical text.\n"
        f"Randomization Code: {random_seed}-{current_time}.\n"
        f"Ensure you prioritize different high-yield facts, structures, or concepts than previous runs.\n\n"
        f"Text:\n{truncated_text}"
    )
    
    response = model.generate_content(prompt)
    return response.text

# Main interface
uploaded_file = st.file_uploader("📂 Choose a medical lecture PDF", type=["pdf"])

if uploaded_file and not api_key:
    st.info("💡 Please enter your Gemini API key in the sidebar to start generating.")

if uploaded_file and api_key:
    if st.button("🚀 Generate New Unique Cards", type="primary"):
        with st.spinner("Shuffling facts and converting into fresh Anki flashcards..."):
            try:
                raw_text = extract_pdf_text(uploaded_file)
                anki_output = generate_anki_cards(raw_text, api_key, num_cards)
                
                st.success(f"🎉 Created {num_cards} unique cards successfully!")
                
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
