import os
import requests
from pyairtable import Table
from datetime import datetime
import time
from dotenv import load_dotenv

load_dotenv()

class LoRAScraper:
    def __init__(self):
        self.civitai_api = "https://civitai.com/api/v1"
        
        # Debug print environment variables
        print("Environment Variables:")
        print(f"AIRTABLE_TOKEN: {'Set' if os.getenv('AIRTABLE_TOKEN') else 'Not Set'}")
        print(f"AIRTABLE_BASE_ID: {'Set' if os.getenv('AIRTABLE_BASE_ID') else 'Not Set'}")
        print(f"AIRTABLE_LORA_TABLE: {os.getenv('AIRTABLE_LORA_TABLE', 'Not Set')}")
        print(f"AIRTABLE_EXAMPLES_TABLE: {os.getenv('AIRTABLE_EXAMPLES_TABLE', 'Not Set')}")
        
        # Validate environment variables
        token = os.getenv('AIRTABLE_TOKEN')
        base_id = os.getenv('AIRTABLE_BASE_ID')
        
        if not token or not base_id:
            raise ValueError("AIRTABLE_TOKEN and AIRTABLE_BASE_ID must be set in environment variables")
            
        self.lora_table = Table(token, base_id, os.getenv('AIRTABLE_LORA_TABLE', 'LORA Models'))
        self.examples_table = Table(token, base_id, os.getenv('AIRTABLE_EXAMPLES_TABLE', 'Generation Examples'))

    def fetch_model(self, model_id):
        """Fetch model data from CivitAI"""
        url = f"{self.civitai_api}/models/{model_id}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                error_message = f"Error fetching model {model_id}: {response.status_code}"
                if response.status_code == 404:
                    error_message = f"Model {model_id} not found on CivitAI"
                print(error_message)
                return None
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching model {model_id}: {e}")
            return None

    def extract_lora_data(self, model_data):
        """Extract relevant data from the model"""
        version = model_data['modelVersions'][0]  # Latest version
        
        # Format the date properly
        created_at = version.get('createdAt')
        if created_at:
            try:
                # Parse ISO format date and convert to YYYY-MM-DD
                date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                formatted_date = date_obj.strftime('%Y-%m-%d')
            except:
                formatted_date = None
        else:
            formatted_date = None
        
        # Basic LORA info matching exact Airtable field names
        lora_data = {
            'Name': model_data['name'],
            'Author': model_data.get('creator', {}).get('username'),
            'CivitAI ID': str(model_data['id']),
            'Published Date': formatted_date,  # Using formatted date
            'Base Model': version.get('baseModel'),
            'Trigger Words': ', '.join(version.get('trainedWords', [])),
            'Type': model_data.get('type', 'LORA'),
            'Download URL': version.get('downloadUrl'),
            'Version': version.get('name'),
            'Description': model_data.get('description', ''),
            'Rating': None,
            'Test Image Prompt': ''
        }
        
        # Example images and their parameters
        examples = []
        for image in version.get('images', []):
            meta = image.get('meta', {})
            if meta:
                examples.append({
                    'Prompt': meta.get('prompt', ''),
                    'Negative Prompt': meta.get('negativePrompt', ''),
                    'Guidance Scale': float(meta.get('cfgScale', 0)),
                    'Steps': int(meta.get('steps', 0)),
                    'Seed': int(meta.get('seed', 0)),
                    'Sampler': meta.get('sampler', '')
                })
        
        return lora_data, examples

    def save_to_airtable(self, lora_data, examples):
        """Save LORA and its examples to Airtable"""
        try:
            # Save main LORA data
            print("Attempting to save LORA data:", lora_data['Name'])
            lora_record = self.lora_table.create(lora_data)
            print(f"Saved LORA: {lora_data['Name']}")
            
            # Save examples with link to main LORA
            for example in examples:
                example_data = {
                    'LORA': [lora_record['id']],  # Link to main LORA record
                    'Prompt': example['Prompt'],
                    'Negative Prompt': example['Negative Prompt'],
                    'Guidance Scale': example['Guidance Scale'],
                    'Steps': example['Steps'],
                    'Seed': example['Seed'],
                    'Sampler': example['Sampler']
                }
                self.examples_table.create(example_data)
            print(f"Saved {len(examples)} examples")
            
            return True
        except Exception as e:
            print(f"Error saving to Airtable: {e}")
            return False

    def process_model(self, model_id):
        """Process a single model"""
        print(f"Processing model {model_id}...")
        model_data = self.fetch_model(model_id)
        if model_data:
            lora_data, examples = self.extract_lora_data(model_data)
            if self.save_to_airtable(lora_data, examples):
                print(f"Successfully processed model {model_id}")
            else:
                print(f"Failed to save model {model_id}")
        time.sleep(1)  # Rate limiting

# Test the scraper
if __name__ == "__main__":
    scraper = LoRAScraper()
    
    # Test with a single model ID
    model_id = input("Enter a CivitAI model ID to test: ")
    scraper.process_model(int(model_id))
