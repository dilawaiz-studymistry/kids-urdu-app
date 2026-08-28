import streamlit as st
import google.generativeai as genai
import json
import re

# --- Page Configuration ---
st.set_page_config(page_title="Kids Urdu Vocab & Quran App", page_icon="📖", layout="centered")

st.title("📖 Kids English-Urdu Learning App")
st.write("Type an English word to learn its Urdu meaning, audio pronunciation, and connection to the Quran & Hadith!")

# --- API Key Setup ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Gemini API Key not found. Please add it to your Streamlit Secrets.")
    st.stop()

# --- Search Input ---
word = st.text_input("Enter an English Word:", placeholder="e.g., Patience, Truth, Justice").strip()

if st.button("Search Word", type="primary"):
    if not word:
        st.warning("Please enter a word first!")
    else:
        with st.spinner(f"Finding meanings and Quranic verses for '{word}'..."):
            try:
                # Using Gemini 3.5 Flash
                model = genai.GenerativeModel("gemini-3.5-flash")
                
                prompt = f"""
                You are an educational assistant for Muslim children. 
                Analyze the word: '{word}'.
                Return ONLY a valid JSON object matching this exact structure:
                {{
                    "word": "{word}",
                    "urdu_meaning": "Urdu translation of the word",
                    "english_example": "A simple child-friendly English sentence using the word",
                    "urdu_example": "Urdu translation of the example sentence",
                    "quran": {{
                        "surah_name": "Surah name with reference (e.g., Surah Al-Baqarah 2:153)",
                        "surah_num": 2,
                        "ayah_num": 153,
                        "arabic": "Arabic text of the verse",
                        "transliteration": "English transliteration",
                        "translation_urdu": "Urdu translation of the Ayah"
                    }},
                    "hadith": {{
                        "reference": "Book reference (e.g., Sahih al-Bukhari 6470)",
                        "text_english": "English translation of the Hadith",
                        "text_urdu": "Urdu translation of the Hadith"
                    }}
                }}
                """

                # Enforce JSON output format
                response = model.generate_content(
                    prompt, 
                    generation_config={"response_mime_type": "application/json"}
                )
                
                # Extract JSON cleanly using regular expressions
                raw_text = response.text.strip()
                json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                
                if json_match:
                    clean_json = json_match.group(0)
                    data = json.loads(clean_json)
                else:
                    data = json.loads(raw_text)

                st.divider()

                # --- Section 1: Vocabulary & Pronunciation ---
                st.header(f"🔤 Word: {data['word'].capitalize()}")
                st.subheader(f"Urdu Meaning: {data['urdu_meaning']}")

                st.markdown("**Listen to Pronunciation:**")
                col1, col2 = st.columns(2)
                with col1:
                    uk_audio_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={word}&tl=en-GB&client=tw-ob"
                    st.write("🇬🇧 UK English:")
                    st.audio(uk_audio_url, format="audio/mp3")
                with col2:
                    us_audio_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={word}&tl=en-US&client=tw-ob"
                    st.write("🇺🇸 US English:")
                    st.audio(us_audio_url, format="audio/mp3")

                st.info(f"**Example:** {data['english_example']}\n\n**Urdu:** {data['urdu_example']}")

                # --- Section 2: Quran Connection ---
                st.divider()
                st.header("🌙 Quran Connection")
                st.caption(f"Reference: {data['quran']['surah_name']}")
                
                st.markdown(f"<h2 style='text-align: right; color: #1E3A8A;'>{data['quran']['arabic']}</h2>", unsafe_allow_html=True)
                st.write(f"**Transliteration:** *{data['quran']['transliteration']}*")
                st.write(f"**Urdu Translation:** {data['quran']['translation_urdu']}")

                # Recitation Audio
                s_num = str(data['quran']['surah_num']).zfill(3)
                a_num = str(data['quran']['ayah_num']).zfill(3)
                quran_audio_url = f"https://www.everyayah.com/data/Abdul_Basit_Murattal_192kbps/{s_num}{a_num}.mp3"
                st.markdown("**Listen to Verse Recitation (Reciter: Abdul Basit):**")
                st.audio(quran_audio_url, format="audio/mp3")

                # --- Section 3: Hadith Connection ---
                st.divider()
                st.header("📚 Hadith Connection")
                st.caption(f"Reference: {data['hadith']['reference']}")
                st.write(f"**English:** {data['hadith']['text_english']}")
                st.write(f"**Urdu:** {data['hadith']['text_urdu']}")

            except Exception as e:
                # Displays exact error to make troubleshooting easy
                st.error(f"Search Error: {e}")
