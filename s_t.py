import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Traductor de Voz", page_icon="🌐", layout="wide")

# --- CSS MODERNO ---
modern_style = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #6a11cb 100%);
    color: white;
    font-family: 'Poppins', sans-serif;
}

[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(12px);
    color: white;
}

h1, h2, h3 {
    color: #ffffff !important;
    text-shadow: 1px 1px 6px rgba(0,0,0,0.4);
    font-weight: 600;
}

.stButton>button {
    background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%);
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 17px;
    padding: 10px 28px;
    font-weight: 600;
    transition: 0.3s ease-in-out;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.2);
}

.stButton>button:hover {
    transform: scale(1.05);
    background: linear-gradient(90deg, #0072ff 0%, #00c6ff 100%);
}

div[data-testid="stMarkdownContainer"] {
    color: #e3e3e3;
}

.stAudio {
    background-color: rgba(255, 255, 255, 0.15);
    border-radius: 12px;
    padding: 10px;
}
</style>
"""
st.markdown(modern_style, unsafe_allow_html=True)

# --- INTERFAZ ---
st.title("🌐 TRADUCTOR DE VOZ")
st.subheader("Traduce lo que dices en segundos")

image = Image.open('OIG7.jpg')
st.image(image, width=300)

with st.sidebar:
    st.subheader("🎧 Instrucciones")
    st.write(
        "Presiona el botón y habla lo que quieras traducir. "
        "Luego selecciona el idioma de entrada, salida y acento preferido."
    )

st.write("Haz clic en el botón para empezar a hablar:")

# --- BOTÓN DE ESCUCHAR ---
stt_button = Button(label="🎤 Escuchar", width=300, height=50)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

if result and "GET_TEXT" in result:
    st.write("🗣️ Texto detectado:")
    st.write(result.get("GET_TEXT"))

    try:
        os.mkdir("temp")
    except:
        pass

    st.header("🔊 Conversión y Traducción")

    translator = Translator()
    text = str(result.get("GET_TEXT"))

    in_lang = st.selectbox("Idioma de entrada", ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"))
    out_lang = st.selectbox("Idioma de salida", ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"))
    english_accent = st.selectbox("Acento", ("Defecto", "Español", "Reino Unido", "Estados Unidos", "Canadá", "Australia", "Irlanda", "Sudáfrica"))

    langs = {"Inglés": "en", "Español": "es", "Bengali": "bn", "Coreano": "ko", "Mandarín": "zh-cn", "Japonés": "ja"}
    accents = {"Defecto": "com", "Español": "com.mx", "Reino Unido": "co.uk", "Estados Unidos": "com",
               "Canadá": "ca", "Australia": "com.au", "Irlanda": "ie", "Sudáfrica": "co.za"}

    input_language = langs[in_lang]
    output_language = langs[out_lang]
    tld = accents[english_accent]

    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        my_file_name = text[0:20] if text else "audio"
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text

    display_output_text = st.checkbox("Mostrar texto traducido")

    if st.button("🚀 Convertir a Audio"):
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown("### 🎧 Audio generado:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        if display_output_text:
            st.markdown("### 📝 Texto traducido:")
            st.write(output_text)

    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        if len(mp3_files) != 0:
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)

    remove_files(7)
