import sys
import os
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from scanner.document_processor import DocumentProcessor
from config.settings import WATCHED_FOLDER


class DocumentHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.processor = DocumentProcessor()

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.lower().endswith(('.jpg', '.png', '.jpeg', '.heic', '.pdf')):
            logging.info(f"Neues Dokument erkannt: {event.src_path}")
            self.processor.process_document(event.src_path)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    if not os.path.exists(WATCHED_FOLDER):
        logging.error(f"Überwachter Ordner existiert nicht: {WATCHED_FOLDER}")
        os.makedirs(WATCHED_FOLDER)
        logging.info(f"Ordner wurde erstellt: {WATCHED_FOLDER}")

    handler = DocumentHandler()
    observer = Observer()
    observer.schedule(handler, WATCHED_FOLDER, recursive=False)
    observer.start()

    logging.info(f"Überwache Ordner: {WATCHED_FOLDER}")
    logging.info("Warte auf neue Dokumente...")

    try:
        while True:
            observer.join(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Programm beendet")

    observer.join()


if __name__ == "__main__":
    main()