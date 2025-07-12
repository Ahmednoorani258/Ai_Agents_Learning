import os
from dotenv import load_dotenv
# Import the necessary classes
import chromadb                                   # ChromaDB client
from chromadb.utils import embedding_functions    # (optional, if using embedding functions directly)
from google import genai                          # Google GenAI SDK for Gemini
from google.genai.types import EmbedContentConfig
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel,function_tool, set_default_openai_client, set_tracing_disabled
from agents.run import RunConfig
import tkinter as tk
from tkinter import filedialog
from langchain_community.document_loaders import PyPDFLoader
import asyncio
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

# Initialize ChromaDB in-memory client
chroma_client = chromadb.Client()  # default uses an in-memory SQLite store

# Initialize Google GenAI client with the Gemini API key
client = genai.Client(api_key=GEMINI_API_KEY)

# Define a few short text documents (e.g., Wikipedia-style snippets)
documents = [
    "Cats are small, domesticated carnivorous mammals often valued by humans for companionship and for their ability to hunt vermin.",
    "Dogs are domesticated mammals, not natural wild animals. They were originally bred from wolves.",
    "The Apollo program was a series of space missions by NASA in the 1960s and 1970s aimed at landing humans on the Moon."
]
doc_ids = ["doc1", "doc2", "doc3"]

# (Optional) Print the documents to verify
# for i, doc in enumerate(documents, 1):
#     print(f"Document {i}: {doc[:60]}...")


# Embed each document using the Gemini embedding model
embed_model = "gemini-embedding-exp-03-07"

# Generate embeddings for all documents in one call
response = client.models.embed_content(
    model=embed_model,
    contents=documents,
    config=EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")  # optimize embeddings for retrieval
)

# Extract the embedding vectors from the response
doc_embeddings = [emb.values for emb in response.embeddings]

# # Check the number of embeddings and dimensionality of one embedding
# print(f"Generated {len(doc_embeddings)} embeddings.")
# print(f"Dimension of first embedding: {len(doc_embeddings[0])}")

# print(f"Sample of first embedding vector: {doc_embeddings[0][:5]}...")  # print first 5 values

# Create a ChromaDB collection for our documents
collection = chroma_client.create_collection(name="knowledge_base")

# Add documents, their embeddings, and IDs to the collection
collection.add(
    documents=documents,
    embeddings=doc_embeddings,
    ids=doc_ids
)

# (Optional) verify collection size
# print("Documents in collection:", collection.count())

# User's question
user_question = "What was the goal of the Apollo program?"

# Embed the user query using the same model (use task_type RETRIEVAL_QUERY for queries)
query_response = client.models.embed_content(
    model=embed_model,
    contents=[user_question],
    config=EmbedContentConfig(task_type="RETRIEVAL_QUERY")
)
query_vector = query_response.embeddings[0].values
# query_vector

# Use ChromaDB to find the most similar document(s) to the query
results = collection.query(
    query_embeddings=[query_vector],
    n_results=2,  # fetch top 2 most similar docs
    # Remove 'ids' from the include list as it's not a valid option
    include=["documents", "distances"]
)
results

# Print out the retrieved documents and their similarity scores
# print("Query:", user_question)
# for doc, score, doc_id in zip(results["documents"][0], results["distances"][0], results["ids"][0]):
#     print(f"- Retrieved {doc_id} with similarity score {score:.4f}: {doc[:60]}...")

# Prepare the context from the retrieved docs
retrieved_docs = results["documents"][0]
context = "\n\n".join(retrieved_docs)

# Formulate the prompt for the LLM
prompt = f"""Use the following context to answer the question.

Context:
{context}

Question:
{user_question}

Answer the question using only the information from the context above."""
# print(prompt)


# Use the Gemini 1.5 Flash model to get an answer based on the context
response = client.models.generate_content(
    model="gemini-1.5-flash",
    contents=prompt
)
answer = response.text

# print("Answer:", answer)

external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

set_tracing_disabled(True)


@function_tool
def answer_from_knowledge_base(query: str) -> str:
    """
    Tool: Given a user query, this tool searches the knowledge base and returns an answer using retrieved documents.
    """
    # Embed the query
    q_resp = client.models.embed_content(
        model=embed_model,
        contents=[query],
        config=EmbedContentConfig(task_type="RETRIEVAL_QUERY")
    )
    q_vector = q_resp.embeddings[0].values
    # Search the vector store
    res = collection.query(query_embeddings=[q_vector], n_results=1, include=["documents"])
    top_doc = res["documents"][0][0]  # top result's text
    # Construct prompt with retrieved context
    prompt = f"Context:\n{top_doc}\n\nQuestion:\n{query}\n\nAnswer the question using only the context above."
    # Generate answer with Gemini 1.5 Flash
    resp = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
    return resp.text

qa_agent = Agent(
    name="QA Agent",
    instructions="You are a helpful assistant. If the user asks a question, use your tools to find information in the knowledge base and answer with that information.",
    tools=[answer_from_knowledge_base],
    # Use OpenAIChatCompletionsModel with the pre-configured external_client
    model=OpenAIChatCompletionsModel(
        model="gemini-1.5-flash-001", # Specify the model name compatible with the OpenAI-like endpoint
        openai_client=external_client
    )
)

def load_and_split_pdf(file_path: str):
  """Loads a PDF and splits it into pages."""
  loader = PyPDFLoader(file_path)
  pages = loader.load_and_split()
  return pages



def upload_file():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(title="Select a PDF file", filetypes=[("PDF files", "*.pdf")])
    return file_path

pdf_file_path = upload_file()
if pdf_file_path:
    print(f"Selected file: {pdf_file_path}")
    pdf_pages = load_and_split_pdf(pdf_file_path)
else:
    print("No file selected.")
    
pdf_documents_text = [page.page_content for page in pdf_pages]
pdf_doc_ids = [f"pdf_page_{i+1}" for i in range(len(pdf_pages))]

print(f"Loaded {len(pdf_pages)} pages from {pdf_file_path}")

pdf_embeddings_response = client.models.embed_content(
    model=embed_model,
    contents=pdf_documents_text,
    config=EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
)
pdf_doc_embeddings = [emb.values for emb in pdf_embeddings_response.embeddings]

collection = chroma_client.get_or_create_collection(name="knowledge_base1")

try:
    collection.add(
        documents=pdf_documents_text,
        embeddings=pdf_doc_embeddings,
        ids=pdf_doc_ids
    )
    print(f"Added {len(pdf_pages)} PDF pages to the knowledge base.")
except Exception as e:
    print(f"Could not add PDF documents to collection, potentially they already exist: {e}")

print("Total documents in collection:", collection.count())
async def main():
    agent_question = "Which domestic animal was originally bred from wolves? what do you know about Apollo?"

    # Run the agent
    result = await Runner.run(qa_agent, agent_question,run_config=config)

    # Extract and print the final answer
    print("Agent result:", result)
    print("Agent's answer:", result.final_output)


async def main_pdf_question():
    # Ask a question that relates to the uploaded PDF content
    pdf_question = "Who is Muhammad Qasim" # Replace with a specific question about your PDF

    # Run the agent with the new question
    result = await Runner.run(qa_agent, pdf_question,run_config=config)

    # Extract and print the final answer
    print("Agent result for PDF question:", result)
    print("Agent's answer for PDF question:", result.final_output)

async def run_all():
    await main_pdf_question()
    await main()

if __name__ == "__main__":
    asyncio.run(run_all())