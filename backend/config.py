import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'chromadb')
    
    # Chat configuration
    MAX_CHAT_HISTORY = 10
    
    # Assessment configuration
    ASSESSMENT_CATEGORIES = ['sleep', 'general_health', 'lifestyle']
    
    # Feedback configuration
    VALID_RATINGS = range(1, 6)  # 1-5 rating scale