import pandas as pd
import os
import random
import json

def generate_random_ip():
    """Generates a random IP address."""
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"

def generate_random_zone():
    """Generates a random zone."""
    return random.choice(["LAN", "WAN", "DMZ"])

def generate_random_service():
    """Generates a random service."""
    return random.choice(["HTTP", "HTTPS", "FTP", "SSH", "Telnet", "RDP", "Any"])

def create_sample_dataset(num_records=10000):
    """Generates a dataset of firewall rule prompts with annotations for entities."""
    # Ensure directory exists
    os.makedirs('data/raw', exist_ok=True)
    
    sample_data = {
        'Prompt': [],
        'Entities': [],
    }
    
    for _ in range(num_records):
        source_ip = generate_random_ip()
        destination_ip = generate_random_ip()
        source_zone = generate_random_zone()
        destination_zone = generate_random_zone()
        service = generate_random_service()
        
        # Generate prompt text
        prompt = f"Allow access for IP \"{destination_ip}\" from \"{source_ip}\" source and \"{source_zone}\" zone to \"{destination_zone}\" zone with Service \"{service}\""
        
        # Annotate entities
        entities = {
            "IP": [destination_ip, source_ip],
            "SourceZone": source_zone,
            "DestinationZone": destination_zone,
            "Service": service,
        }
        
        # Append generated data
        sample_data['Prompt'].append(prompt)
        sample_data['Entities'].append(json.dumps(entities))
    
    # Create a DataFrame and save it as CSV
    df = pd.DataFrame(sample_data)
    file_path = 'data/raw/firewall_rules_annotated.csv'
    df.to_csv(file_path, index=False)
    print(f"Dataset with {num_records} records created successfully at {file_path}")

if __name__ == '__main__':
    create_sample_dataset()
