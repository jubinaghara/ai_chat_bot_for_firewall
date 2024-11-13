# app/chat_bot.py
import os
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
from flask import Blueprint, jsonify, request
import json
import pandas as pd
import logging
import re
from typing import Dict, List, Optional

# Create blueprint
bp = Blueprint('chat', __name__)

logger = logging.getLogger(__name__)

class FirewallChatbot:
    def __init__(self, model_path=None, dataset_path=None):
        """
        Initialize the chatbot with model and dataset
        """
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        if dataset_path is None:
            dataset_path = os.path.join(root_dir, 'data', 'raw', 'firewall_rules.csv')
        if model_path is None:
            model_path = os.path.join(root_dir, 'models', 'saved_models', 'ner_model')
        
        self.load_dataset(dataset_path)
        self.load_model(model_path)
        
        # Regular expressions for entity extraction
        self.patterns = {
            'IP': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'SourceZone': r"(?:from |source )['\"](.*?)['\"](?: zone)?",
            'DestinationZone': r"to ['\"](.*?)['\"](?: zone)?",
            'Service': r"(?:service |with service )['\"](.*?)['\"]"
        }
    
    def load_dataset(self, dataset_path: str) -> None:
        """Load and prepare the training dataset."""
        try:
            if not os.path.exists(dataset_path):
                raise FileNotFoundError(f"Dataset not found at {dataset_path}")
            
            self.df = pd.read_csv(dataset_path)
            self.df['Entities'] = self.df['Entities'].apply(json.loads)

            logger.info(f"Dataset loaded successfully from {dataset_path}")
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            raise

    def load_model(self, model_path: str) -> None:
        """Load the pre-trained model and tokenizer"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")
            self.model = AutoModelForTokenClassification.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    def extract_entities_regex(self, prompt: str) -> Dict[str, Optional[str]]:
        """Extract entities using regex patterns"""
        entities = {
            'IP': [],
            'SourceZone': None,
            'DestinationZone': None,
            'Service': None
        }
        
        # Extract IPs
        ip_matches = re.findall(self.patterns['IP'], prompt)
        entities['IP'] = ip_matches
        
        # Extract other entities
        for entity_type in ['SourceZone', 'DestinationZone', 'Service']:
            match = re.search(self.patterns[entity_type], prompt)
            if match:
                entities[entity_type] = match.group(1)
        
        return entities

    def process_request(self, prompt: str) -> Dict:
        """Process user input and return appropriate response"""
        try:
            logger.info(f"Received prompt: {prompt}")
            
            # Extract entities using regex
            entities = self.extract_entities_regex(prompt)
            logger.info(f"Extracted entities: {entities}")
            
            # Find matching rules in the dataset
            matching_rules = self.df
            for entity_type, entity_value in entities.items():
                if entity_type == 'IP' and entity_value:
                    matching_rules = matching_rules[
                        matching_rules['Entities'].apply(
                            lambda x: any(ip in x.get('IP', []) for ip in entity_value)
                        )
                    ]
            
            if not matching_rules.empty:
                response = matching_rules.iloc[0]['Response']
                return {
                    'status': 'success',
                    'entities': entities,
                }
            else:
                return {
                    'status': 'error',
                    'extracted_entities': entities
                }
                
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }

# Create chatbot instance
chatbot = FirewallChatbot()

# Define routes using blueprint
@bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        if 'prompt' not in data:
            return jsonify({'error': 'No prompt provided'}), 400
        
        prompt = data['prompt']
        response = chatbot.process_request(prompt)
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({'error': str(e)}), 500
