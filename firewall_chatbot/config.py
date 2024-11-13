import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Flask settings
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    PORT = int(os.getenv('PORT', 5000))
    
    # Model settings
    MODEL_PATH = os.getenv('MODEL_PATH', './models/saved_models')
    
    # Data settings
    RAW_DATA_PATH = 'data/raw/firewall_rules.csv'
    PROCESSED_DATA_PATH = 'data/processed/'
    
    # Logging settings
    LOG_FILE = 'logs/app.log'