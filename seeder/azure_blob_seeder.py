import os
import time
import redis
import logging
from azure.storage.blob import BlobServiceClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("AzureBlobSeeder")

class AzureBlobSeeder:
    def __init__(self, redis_host, redis_port, connection_string, container_name, redis_db=0):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = self.blob_service_client.get_container_client(container_name)
        self.container_name = container_name
        self.pdf_queue_name = "pdf_queue"
        self.pdf_status_prefix = "pdf_status:"
        self.processed_blobs_key = "processed_blobs"  # Redis Set to store processed blob names

    def start_watching(self, interval=30):
        logger.info(f"Démarrage de la surveillance du conteneur Azure Blob: {self.container_name}")
        while True:
            try:
                self._check_for_new_blobs()
            except Exception as e:
                logger.exception(f"Erreur lors de la surveillance d'Azure Blob: {e}")
            time.sleep(interval)

    def _check_for_new_blobs(self):
        logger.info(f"Vérification des nouveaux blobs dans {self.container_name}...")
        blob_list = self.container_client.list_blobs()
        for blob in blob_list:
            blob_name = blob.name
            logger.debug(f"Blob trouvé: {blob_name}")
            if blob_name.lower().endswith(".pdf") and not self.redis_client.sismember(self.processed_blobs_key, blob_name):
                self.process_new_pdf(blob_name)

    def process_new_pdf(self, blob_name):
        logger.info(f"Nouveau PDF détecté dans Azure Blob: {blob_name}")

        self.redis_client.lpush(self.pdf_queue_name, blob_name)

        # Initialiser le statut dans Redis
        self.redis_client.hset(f"{self.pdf_status_prefix}{blob_name}", mapping={
            "status": "pending",
            "blob_name": blob_name,
            "timestamp": time.time()
        })

        self.redis_client.sadd(self.processed_blobs_key, blob_name)

        logger.info(f"Ajouté {blob_name} à la file d'attente Redis et statut initialisé à 'pending'.")
