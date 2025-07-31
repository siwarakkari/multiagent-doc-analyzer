import os
import time
from pathlib import Path
from typing import List, Dict

import pymupdf  # PyMuPDF for PDF
import pytesseract
from PIL import Image
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

class PDFProcessorr:
    def __init__(self, temp_dir="./tmp/pdf_pages"):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)

    def extract_text(self, pdf_path: str) -> List[Dict]:
        """Extract text from PDF, apply OCR when needed, and return list of pages with metadata."""
        doc = pymupdf.open(pdf_path)
        extracted_pages = []

        for i, page in enumerate(doc):
            text = page.get_text()

            if not text.strip():
                # Page might be scanned - perform OCR
                pix = page.get_pixmap(dpi=300)
                image_path = self.temp_dir / f"page_{i}.png"
                pix.save(str(image_path))
                image = Image.open(image_path)
                text = pytesseract.image_to_string(image)

            extracted_pages.append({
                "page_number": i + 1,
                "text": text,
            })

        return extracted_pages


class PDFChunker:
    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def chunk(self, pages: List[Dict], source_name: str) -> List[Dict]:
        """Chunk text and attach metadata for each chunk."""
        all_chunks = []

        for page in pages:
            chunks = self.splitter.split_text(page["text"])
            for i, chunk in enumerate(chunks):
                all_chunks.append({
                    "text": chunk,
                    "metadata": {
                        "source": source_name,
                        "page_number": page["page_number"],
                        "chunk_id": f"{source_name}_p{page['page_number']}_c{i}",
                        "timestamp": time.time()
                    }
                })

        return all_chunks


class VectorStoreIndexer:
    def __init__(self, persist_directory="./db"):
        self.embedding_fn = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.persist_directory = persist_directory
        self.vector_db = Chroma(
            embedding_function=self.embedding_fn,
            persist_directory=self.persist_directory
        )
        
    def add_chunks(self, chunks: List[Dict]):
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        self.vector_db.add_texts(texts, metadatas)
      
    def visualize_indexed_data(self, n=5):
        """
        Print a preview of the content stored in the vector DB.
        :param n: Number of items to show.
        """
        print(f"\n📦 Visualizing top {n} indexed items in Chroma DB:\n")
        collection = self.vector_db._collection
        results = collection.get(include=["documents", "metadatas"], limit=n)

        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])

        for i, (doc, meta) in enumerate(zip(documents, metadatas)):
            print(f"--- Document #{i+1} ---")
            print(f"📄 Text:\n{doc[:300]}{'...' if len(doc) > 300 else ''}")
            print(f"🧾 Metadata: {meta}")
            print()   
  


class PDFWorker:
    def __init__(self, storage_path="./db"):
        self.processor = PDFProcessorr()
        self.chunker = PDFChunker()
        self.indexer = VectorStoreIndexer(persist_directory=storage_path)

    def process_pdf(self, pdf_path: str):
        file_name = Path(pdf_path).name
        print(f"[Worker] Processing {file_name}")

        pages = self.processor.extract_text(pdf_path)
        chunks = self.chunker.chunk(pages, source_name=file_name)
        self.indexer.add_chunks(chunks)
        self.indexer.visualize_indexed_data()

        print(f"[Worker] Finished indexing {file_name}. Chunks: {len(chunks)}")
