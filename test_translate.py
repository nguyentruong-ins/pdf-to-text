import asyncio

from googletrans import Translator

def format_chunk(chunk):
    lines = chunk.split('\n')
    return ''.join([line.strip() for line in lines if line.strip()])

def chunk_text(text, chunk_size=0):
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

    chunks = chunk_text(text)
    formatted_chunks = [format_chunk(chunk) for chunk in chunks]

    with open("chunks.txt", "w") as f:
        for chunk in chunks:
            f.write(chunk + "\n\n")

    with open("formatted_chunks.txt", "w") as f:
        for chunk in formatted_chunks:
            f.write(chunk + "\n\n")

    async def translate_chunk(chunk):
        return await translator.translate(chunk, dest="vi")

    translated_text = ""
    tasks = [translate_chunk(chunk) for chunk in formatted_chunks]
    translated_chunks = await asyncio.gather(*tasks)
    for translated_chunk in translated_chunks:
        translated_text += translated_chunk.text + "\n\n"

    return translated_text



async def main():
    text = None
    with open("text_Introduction to environmental engineering and science (2014).pdf.txt", "r") as f:
        text = f.read()

    translated_text = await translate_text(text)
    with open("translated_text.txt", "w") as f:
        f.write(translated_text)


if __name__ == "__main__":
    asyncio.run(main())
