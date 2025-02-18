from transformers import pipeline
import logging
import re
from datetime import datetime

class DocumentClassifier:
    def __init__(self):
        try:
            # Simple rule-based classification for now
            self.categories = ["Rechnungen", "Verträge", "Bescheinigungen", "Sonstiges"]
            
            self.sender_patterns = {
                'Telekom': r'deutsche\s*telekom | telekom',
                'Vodafone': r'vodafone',
                '1&1': r'1&1',
                'O2': r'o2',
                'E.ON': r'e\.on',
                'RWE': r'rwe',
                'EnBW': r'enbw',
                'EWE': r'ewe',
                'Stadtwerke': r'stadtwerke',
                'Amazon': r'amazon',
                'eBay': r'ebay',
                'PayPal': r'paypal',
                'Apple': r'apple',
                'Google': r'google',
                'Microsoft': r'microsoft',
                'Facebook': r'facebook',
                'Twitter': r'twitter',
                'Instagram': r'instagram',
                'WhatsApp': r'whatsapp',
                'Signal': r'signal',
                'Telegram': r'telegram',
                'Threema': r'threema',
                'Postbank': r'postbank',
                'Commerzbank': r'commerzbank',
                'Deutsche Bank': r'deutsche\s*bank',
                'ING': r'ing',
                'Sparkasse': r'sparkasse',
                'Volksbank': r'volksbank',
                'DKB': r'dkb',
                'N26': r'n26',
                'Revolut': r'revolut',
                'Fidor': r'fidor',
                'HypoVereinsbank': r'hypovereinsbank',
                'Consorsbank': r'consorsbank',
                'Deutsche Kreditbank': r'dkb',
                'Deutsche Bahn': r'deutsche\s*bahn',
                'Lufthansa': r'lufthansa',
                'Airbus': r'airbus',
                'BMW': r'bmw',
                'Mercedes': r'mercedes',
                'Volkswagen': r'volkswagen',
                'Audi': r'audi',
                'Porsche': r'porsche',
                'Opel': r'opel',
                'Ford': r'ford',
                'Renault': r'renault',
                'Peugeot': r'peugeot',
                'Citroën': r'citroën',
                'Fiat': r'fiat',
                'Toyota': r'toyota',
                'Nissan': r'nissan',
                'Honda': r'honda',
                'Mazda': r'mazda',
                'Subaru': r'subaru',
                'Mitsubishi': r'mitsubishi',
                'Bundesagentur für Arbeit': r'bundesagentur\s*für\s*arbeit',
                'Jobcenters': r'jobcenters',
                'Arbeitsamt': r'arbeitsamt',
                'Finanzamt': r'finanzamt',
                'Stadtverwaltung': r'stadtverwaltung',
                'Polizei': r'polizei',
                'Feuerwehr': r'feuerwehr',
                'Rotes Kreuz': r'rotes\s*kreuz',
                'Malteser': r'malteser',
                'Johanniter': r'johanniter',
                'DRK': r'drk',
                'THW': r'thw',
                'ADAC': r'adac',
                'Allianz': r'allianz',
                'HUK-Coburg': r'huk-coburg',
                'DEVK': r'devk',
                'AOK': r'aok',
                'Barmer': r'barmer',


            }
        except Exception as e:
            logging.error(f"Fehler beim Initialisieren des Klassifizierers: {str(e)}")
            raise
    
    def detect_sender(self, text):
        text = text.lower()
        for sender, pattern in self.sender_patterns.items():
            if re.search(pattern, text):
                return sender
        return "Unbekannt"
    
    def detect_date(self, text):
        """Versucht ein Datum im Text zu finden."""
        # Verschiedene Datumsmuster
        date_patterns = [
            r'\d{2}\.\d{2}\.\d{4}',  # DD.MM.YYYY
            r'\d{2}/\d{2}/\d{4}',    # DD/MM/YYYY
            r'\d{2}-\d{2}-\d{4}'     # DD-MM-YYYY
        ]

        for pattern in date_patterns:
            match  = re.search(pattern, text)
            if match:
                return match.group(0)
            
        return datetime.now().strftime("%d.%m.%Y")
    
    def generate_filename(self, text, category):
        """Generates a filename based on sender, date and category."""
        try:
            sender = self.detect_sender(text)
            date = self.detect_date(text)

            # Remove invalid characters from sender name
            safe_sender = re.sub(r'[<>:"/\\|?*]', '', sender)

            # Create and return filename string
            filename = f"{date} - {safe_sender} - {category}"
            return filename.strip()  # Remove any extra whitespace
        
        except Exception as e:
            logging.error(f"Fehler bei der Dateinamensgenerierung: {str(e)}")
            return "Unbenannt"
    
    def classify(self, text):
        try:
            text = text.lower()
            
            # Enhanced keyword lists for better classification
            rechnung_keywords = ['rechnung', 'betrag', 'zahlung', 'euro', '€', 'summe', 'preis']
            vertrag_keywords = ['vertrag', 'vereinbarung', 'bedingungen', 'laufzeit', 'kündigung']
            bescheinigung_keywords = ['bescheinigung', 'bestätigung', 'nachweis', 'zertifikat']
            
            if any(word in text for word in rechnung_keywords):
                category = "Rechnungen"
            elif any(word in text for word in vertrag_keywords):
                category = "Verträge"
            elif any(word in text for word in bescheinigung_keywords):
                category = "Bescheinigungen"
            else:
                category = "Sonstiges"
            
            suggested_filename = self.generate_filename(text, category)

            return category, suggested_filename
                
        except Exception as e:
            logging.error(f"Klassifizierung fehlgeschlagen: {str(e)}")
            return "Sonstiges", None