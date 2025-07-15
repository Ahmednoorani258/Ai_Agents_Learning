from agents import function_tool
from chroma_client import get_or_create_collection
from gemini_embedder import embed_query,generate_answer


@function_tool
def answer_from_knowledge_base(query: str) -> str:
    collection = get_or_create_collection()
    query_vector = embed_query(query)
    results = collection.query(query_embeddings=[query_vector], n_results=1, include=["documents"])

    if not results["documents"] or not results["documents"][0]:
        return "No relevant information found."

    top_doc = results["documents"][0][0]
    prompt = f"Context:\n{top_doc}\n\nQuestion:\n{query}\n\nAnswer the question using only the context above."
    print("🔍 Query vector:", query_vector[:5])
    print("📚 Results:", results)

    return generate_answer(prompt)