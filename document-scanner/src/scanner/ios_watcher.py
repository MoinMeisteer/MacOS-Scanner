import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from document_processor import DocumentProcessor

class DocumentHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.processor = DocumentProcessor()

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.lower().endswith(('.jpg', '.png', '.pdf', '.jpeg', '.heic')):
            logging.info(f"Neues Dokument erkannt: {event.src_path}")
            self.processor.process_document(event.src_path)

def ensure_directories():
    # Debug: Zeige alle verfügbaren Pfade
    home = os.path.expanduser("~")
    icloud_dir = os.path.join(home, "Library/Mobile Documents/com~apple~CloudDocs")
    documents_dir = os.path.join(home, "Documents")
    
    logging.info(f"Home Directory: {home}")
    logging.info(f"iCloud Directory: {icloud_dir}")
    logging.info(f"Documents Directory: {documents_dir}")
    
    # Frage den Benutzer nach dem gewünschten Pfad
    base_dir = icloud_dir  # oder documents_dir, je nachdem wo Sie die Dateien haben möchten
    scan_dir = os.path.join(base_dir, "Dokumente/Scan")
    
    # Rest des Codes bleibt gleich
    directories = [
        scan_dir,
        os.path.join(base_dir, "Dokumente/Rechnungen"),
        os.path.join(base_dir, "Dokumente/Verträge"),
        os.path.join(base_dir, "Dokumente/Bescheinigungen"),
        os.path.join(base_dir, "Dokumente/Sonstiges")
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logging.info(f"Ordner erstellt: {directory}")
    
    return scan_dir

def start_watching(directory):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Stelle sicher, dass der Ordner existiert
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Scan-Ordner erstellt: {directory}")
    
    event_handler = DocumentHandler()
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=False)
    observer.start()
    
    logging.info(f"Überwache Ordner: {directory}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Überwachung beendet")
    observer.join()

if __name__ == "__main__":
    scan_dir = ensure_directories()
    start_watching(scan_dir)