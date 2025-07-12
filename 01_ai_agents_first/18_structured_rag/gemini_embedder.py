from google import genai                          # Google GenAI SDK for Gemini
from google.genai.types import EmbedContentConfig
from settings import GEMINI_API_KEY,GEMINI_EMBED_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)

def embed_documents(documents: list[str]) -> list[list[float]]:
    response = client.models.embed_content(
        model=GEMINI_EMBED_MODEL,
        contents=documents,
        config=EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
    )
    return [emb.values for emb in response.embeddings]

def embed_query(query: str) -> list[float]:
    response = client.models.embed_content(
        model=GEMINI_EMBED_MODEL,
        contents=[query],
        config=EmbedContentConfig(task_type="RETRIEVAL_QUERY")
    )
    return response.embeddings[0].values

def generate_answer(prompt: str, model="gemini-1.5-flash"):
    return client.models.generate_content(model=model, contents=prompt).text