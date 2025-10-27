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
st.set_page_config(page_title="Traductor de Voz", page_icon="🎙️", layout="wide")

# --- CSS PERSONALIZADO ---
page_style = """
<style>
[data-testid="stAppViewContainer"] {
    background-color: #f4e1c1; /* Fondo café claro */
    background-image: linear-gradient(to bottom right, #f7e7ce, #f4d6a1, #e6b980);
    color: #3b2f2f;
    font-family: 'Georgia', serif;
}

[data-testid="stSidebar"] {
    background-color: #f3d9b1 !important;
    color: #3b2f2f;
}

h1, h2, h3 {
    color: #5a3825 !important;
    text-shadow: 1px 1px 2px rgba(70, 45, 25, 0.4);
    font-family: 'Georgia', serif;
}

.stButton>button {
    background-color: #8b5e3c;
    color: white;
    border-radius: 10px;
    border: none;
    font-size: 17px;
    font-weight: bold;
    padding: 10px 25px;
    transition: 0.3s;
}

.stButton>button:hover {
    background-color: #a1724e;
    transform: scale(1.05);
}
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

# --- INTERFAZ PRINCIPAL ---
st.title("🎙️ TRADUCTOR")
st.subheader("Escucho lo que quieres traducir")

image = Image.open('OIG7.jpg')
st.image(image, width=300)

with st.sidebar:
    st.subheader("🗣️ Traductor por voz")
    st.write(
        "Presiona el botón, cuando escuches la señal habla lo que quieres traducir. "
        "Luego selecciona la configuración de lenguaje que necesites."
    )

st.write("Toca el botón y habla lo que quieres traducir:")

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
    st.write(result.get("GET_TEXT"))
    try:
        os.mkdir("temp")
    except:
        pass

    st.header("Texto a Audio")
    translator = Translator()
    text = str(result.get("GET_TEXT"))

    in_lang = st.selectbox("Selecciona el lenguaje de Entrada", ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"))
    out_lang = st.selectbox("Selecciona el lenguaje de Salida", ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"))
    english_accent = st.selectbox("Selecciona el acento", ("Defecto", "Español", "Reino Unido", "Estados Unidos", "Canadá", "Australia", "Irlanda", "Sudáfrica"))

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

    display_output_text = st.checkbox("Mostrar el texto traducido")

    if st.button("🔊 Convertir"):
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown("### 🎧 Tu audio generado:")
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
