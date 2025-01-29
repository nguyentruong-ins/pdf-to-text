import asyncio
import streamlit as st
import pdf2image
import aiopytesseract

from io import BytesIO
from googletrans import Translator


loop = asyncio.new_event_loop()
uploaded_file = None

def show_options():
    global uploaded_file
    st.sidebar.title("Upload file")
    uploaded_file = st.sidebar.file_uploader("Upload a file", type=["pdf", "png", "jpg", "jpeg"])

def format_chunk(chunk):
    lines = chunk.split('\n')
    return ''.join([line.strip() for line in lines if line.strip()])

def chunk_text(text, chunk_size=1000):
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) + 2 <= chunk_size:
            current_chunk += paragraph + "\n\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = paragraph + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

async def translate_text(text):
    translator = Translator()

    import re

    chunks = chunk_text(text, 0)
    formatted_chunks = [format_chunk(chunk) for chunk in chunks]
    cleaned_chunks = [re.sub(r'(?<=\w)-(?=\w)', '', chunk) for chunk in formatted_chunks]

    # with open("cleaned_chunks.txt", "w") as f:
    #     for chunk in cleaned_chunks:
    #         f.write("RAW: " + chunk + "\n\n")
    #         f.write("CLEANED: " + chunk.replace("- ", "") + "\n\n")
    #         f.write("==================\n\n")

    async def translate_chunk(chunk):
        return await translator.translate(chunk, dest="vi")

    translated_text = ""
    tasks = [translate_chunk(chunk) for chunk in cleaned_chunks]
    translated_chunks = await asyncio.gather(*tasks)
    for translated_chunk in translated_chunks:
        translated_text += translated_chunk.text + "\n\n"

    return translated_text

def process_uploaded_file(uploaded_file):
    st.session_state["transcribed_text"] = ""
    st.session_state["translated_text"] = ""

    if uploaded_file.type == "application/pdf":
        images = pdf2image.convert_from_bytes(uploaded_file.getvalue())
        bar = st.progress(0)
        for i, image in enumerate(images):
            bar.progress((i + 1) / len(images))

            # Convert image to bytes
            image_bytes = BytesIO()
            image.save(image_bytes, format='PNG')
            image_bytes.seek(0)

            text = loop.run_until_complete(
                aiopytesseract.image_to_string(image_bytes.getvalue())
            )
            if "transcribed_text" not in st.session_state:
                st.session_state["transcribed_text"] = ""
            st.session_state["transcribed_text"] += text

    else:
        text = loop.run_until_complete(
            aiopytesseract.image_to_string(uploaded_file.getvalue())
        )
        st.session_state["transcribed_text"] = text

    st.session_state["translated_text"] = loop.run_until_complete(translate_text(st.session_state["transcribed_text"]))

def show_results():
    column1, column2 = st.columns(2)
    if "transcribed_text" in st.session_state and "translated_text" in st.session_state:
        with column1:
            st.download_button("Download transcribed file", st.session_state["transcribed_text"], file_name=f"transcribed_{uploaded_file.name}.txt")
            st.write(st.session_state["transcribed_text"])
        with column2:
            st.download_button("Download translated file", st.session_state["translated_text"], file_name=f"translated_{uploaded_file.name}.txt")
            st.write(st.session_state["translated_text"])

def handle_uploaded_file():
    global uploaded_file

    if st.sidebar.button("Process file", disabled=uploaded_file is None):
        process_uploaded_file(uploaded_file)

def main():
    show_options()
    handle_uploaded_file()
    show_results()

if __name__ == "__main__":
    main()
