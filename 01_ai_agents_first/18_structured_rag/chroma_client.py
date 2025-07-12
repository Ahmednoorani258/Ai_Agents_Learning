import chromadb 
chroma_client = chromadb.Client() 

def get_or_create_collection(name="knowledge_base"):
    return chroma_client.get_or_create_collection(name=name)