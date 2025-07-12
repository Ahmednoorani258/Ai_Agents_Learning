import tkinter as tk
from tkinter import filedialog
from langchain_community.document_loaders import PyPDFLoader

def upload_file():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(title="Select a PDF file", filetypes=[("PDF files", "*.pdf")])
    return file_path

def load_and_split_pdf(file_path: str):
  """Loads a PDF and splits it into pages."""
  loader = PyPDFLoader(file_path)
  pages = loader.load_and_split()
  return pages

