import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
GEMINI_EMBED_MODEL = "gemini-embedding-exp-03-07"
GENERATION_MODEL = "gemini-1.5-flash"
