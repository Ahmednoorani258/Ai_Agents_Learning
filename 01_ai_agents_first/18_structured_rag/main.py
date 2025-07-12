
import asyncio
from agents import Runner
from setupconfig import config
from qa_agent import qa_agent
from pdf_utils import load_and_split_pdf,upload_file
from gemini_embedder import embed_documents
from chroma_client import get_or_create_collection


async def main_question():
    question = "What do you know about the Apollo program?"
    result = await Runner.run(qa_agent, question, run_config=config)
    print("Answer:", result.final_output)

async def main_pdf():
    file_path = upload_file()
    if not file_path:
        print("No file selected.")
        return

    pages = load_and_split_pdf(file_path)
    documents = [p.page_content for p in pages]
    doc_ids = [f"pdf_{i+1}" for i in range(len(documents))]

    embeddings = embed_documents(documents)
    collection = get_or_create_collection("pdf_kb")
    try:
        collection.add(documents=documents, embeddings=embeddings, ids=doc_ids)
    except Exception as e:
        print(f"Error adding PDF to ChromaDB: {e}")
    
    print(f"Added {len(documents)} pages.")

    question = "Who is Muhammad Qasim?"
    result = await Runner.run(qa_agent, question, run_config=config)
    print("PDF Question Answer:", result.final_output)

async def run_all():
    await main_pdf()
    await main_question()

if __name__ == "__main__":
    asyncio.run(run_all())