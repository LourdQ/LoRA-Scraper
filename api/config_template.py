import os
from dotenv import load_dotenv

load_dotenv()

# Airtable Configuration
AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_LORA_TABLE = os.getenv('AIRTABLE_LORA_TABLE', 'LORA Models')
AIRTABLE_EXAMPLES_TABLE = os.getenv('AIRTABLE_EXAMPLES_TABLE', 'Generation Examples')
PORT = int(os.getenv('PORT', 8000))
