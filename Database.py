from dotenv import load_dotenv, find_dotenv
from supabase import create_client
import os

class DatabaseHandler:
    def __init__(self):
        dotenv_path = find_dotenv()
        load_dotenv(dotenv_path)
        
        self._url = os.getenv("SUPABASE_URL")
        self._key = os.getenv("SUPABASE_KEY")
        self._client = create_client(self._url, self._key)
    
    @property
    def client(self):
        return self._client
    