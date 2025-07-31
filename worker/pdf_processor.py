import os
import time
import redis
import traceback
from azure.storage.blob import BlobServiceClient
from worker import PDFWorker


class PDFProcessor:
    def __init__(self, redis_host, redis_port, connection_string, input_container_name, output_container_name, redis_db=0):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.input_container_client = self.blob_service_client.get_container_client(input_container_name)
        self.output_container_client = self.blob_service_client.get_container_client(output_container_name)
        self.pdf_queue_name = "pdf_queue"
        self.pdf_status_prefix = "pdf_status:"
        self.local_download_dir = "./tmp/pdfs" 
        self.local_output_dir = "./tmp/output" 

        os.makedirs(self.local_download_dir, exist_ok=True)
        os.makedirs(self.local_output_dir, exist_ok=True)

    def start_processing(self):
        print("[Worker] Démarrage du traitement des PDF...")
        while True:
            try:
                queue_name, blob_name = self.redis_client.brpop(self.pdf_queue_name)
                blob_name = blob_name.decode("utf-8")

                print(f"[Worker] Récupéré le blob: {blob_name}")

                # Mettre à jour le statut à 'in_process'
                self._update_status(blob_name, "in_process", start_time=time.time())

                local_pdf_path = os.path.join(self.local_download_dir, blob_name)
                output_file_name = f"{os.path.splitext(blob_name)[0]}.txt"
                local_output_path = os.path.join(self.local_output_dir, output_file_name)

                try:
                    # Télécharger le PDF depuis Azure Blob
                    print(f"[Worker] Téléchargement de {blob_name} vers {local_pdf_path}")
                    with open(local_pdf_path, "wb") as download_file:
                        download_file.write(self.input_container_client.download_blob(blob_name).readall())

                    # --- Logique de traitement du PDF --- #
                        process= PDFWorker()
                        process.process_pdf(local_pdf_path)
                    time.sleep(2) # Simuler un travail long

                  
                    print(f"[Worker] Traitement terminé pour {blob_name}. Résultat uploadé.")
                    self._update_status(blob_name, "success", end_time=time.time(), output_blob=output_file_name)

                except Exception as e:
                    error_msg = f"Erreur lors du traitement du PDF {blob_name}: {e}\n{traceback.format_exc()}"
                    print(f"[Worker] Erreur de traitement: {error_msg}")
                    self._update_status(blob_name, "failed", error_message=error_msg, end_time=time.time())
                finally:
                    if os.path.exists(local_pdf_path):
                        os.remove(local_pdf_path)
                    if os.path.exists(local_output_path):
                        os.remove(local_output_path)

            except redis.exceptions.ConnectionError as e:
                print(f"[Worker] Erreur de connexion Redis: {e}. Réessai dans 5 secondes...")
                time.sleep(5)
            except Exception as e:
                print(f"[Worker] Erreur inattendue: {e}\n{traceback.format_exc()}")
                time.sleep(1)

    def _update_status(self, blob_name, status, **kwargs):
        update_data = {"status": status}
        for key, value in kwargs.items():
            update_data[key] = value
        self.redis_client.hset(f"{self.pdf_status_prefix}{blob_name}", mapping=update_data)
