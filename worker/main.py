import os
from pdf_processor import PDFProcessor
from dotenv import load_dotenv
load_dotenv() 

if __name__ == "__main__":
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    AZURE_BLOB_CONTAINER_NAME= os.getenv("AZURE_BLOB_INPUT_CONTAINER_NAME", "docsbucket")
    AZURE_BLOB_OUTPUT_CONTAINER_NAME = os.getenv("AZURE_BLOB_OUTPUT_CONTAINER_NAME", "outputbucket")

    if not AZURE_STORAGE_CONNECTION_STRING:
        print("Erreur: AZURE_STORAGE_CONNECTION_STRING n'est pas défini.")
        exit(1)

    worker = PDFProcessor(
        REDIS_HOST, REDIS_PORT,
        AZURE_STORAGE_CONNECTION_STRING,
        AZURE_BLOB_CONTAINER_NAME,
        AZURE_BLOB_OUTPUT_CONTAINER_NAME
    )
    worker.start_processing()