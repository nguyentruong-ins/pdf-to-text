import asyncio
import streamlit as st
import pdf2image
import aiopytesseract

from streamlit.runtime.uploaded_file_manager import UploadedFile
from io import BytesIO


loop = asyncio.new_event_loop()
uploaded_file = None

def show_options():
    global uploaded_file
    st.sidebar.title("Upload file")
    uploaded_file = st.sidebar.file_uploader("Upload a file", type=["pdf", "png", "jpg", "jpeg"])

def handle_uploaded_file():
    global uploaded_file

    download_text = ""

    if st.sidebar.button("Process file", disabled=uploaded_file is None):
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
                download_text += text
                st.write(text)

        else:
            text = loop.run_until_complete(
                aiopytesseract.image_to_string(uploaded_file.getvalue())
            )
            download_text = text
            st.write(text)

        st.download_button("Download text file", download_text, file_name=f"text_{uploaded_file.name}.txt")

def main():
    show_options()
    handle_uploaded_file()

if __name__ == "__main__":
    main()
