#!/usr/bin/env python
"""
Script to download JSON data for the Zettelkasten IDs listed in missing_specific_ids.txt.
The script reads the IDs from the file, constructs API URLs, and saves the JSON responses
to the index_full_jsons folder.

Usage:
    python download_jsons_from_txt_ids.py
"""

import os
import json
import time
import requests
from tqdm import tqdm

def ensure_directory_exists(directory):
    """Ensure the specified directory exists, if not create it."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")
    else:
        print(f"Directory already exists: {directory}")

def read_ids_from_file(filename):
    """Read IDs from the specified file."""
    with open(filename, 'r', encoding='utf-8') as file:
        ids = [line.strip() for line in file if line.strip()]
    return ids

def construct_api_url(id_part):
    """Construct the API URL from the ID."""
    base_url = "https://v0.api.niklas-luhmann-archiv.de/ZK/zettel/"
    return f"{base_url}{id_part}"

def download_json(api_url, save_path, retry_count=3, delay=1):
    """Download JSON data from the API URL and save it to the specified path."""
    for attempt in range(retry_count):
        try:
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            # Parse and save the JSON data
            json_data = response.json()
            with open(save_path, 'w', encoding='utf-8') as file:
                json.dump(json_data, file, ensure_ascii=False, indent=2)
            
            print(f"Successfully downloaded: {os.path.basename(save_path)}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {api_url} (attempt {attempt+1}/{retry_count}): {e}")
            if attempt < retry_count - 1:
                time.sleep(delay)  # Wait before retrying
        except Exception as e:
            print(f"Unexpected error with {api_url}: {e}")
            return False
    
    return False

def main():
    # Define input file and output directory
    input_file = "missing_specific_ids.txt"
    output_dir = "index_full_jsons"
    
    # Ensure output directory exists
    ensure_directory_exists(output_dir)
    
    # Read IDs from the input file
    ids = read_ids_from_file(input_file)
    print(f"Found {len(ids)} IDs in {input_file}.")
    
    success_count = 0
    
    # Process each ID
    for id_part in tqdm(ids, desc="Downloading JSONs"):
        try:
            # Construct API URL
            api_url = construct_api_url(id_part)
            
            # Define output file path
            output_file = os.path.join(output_dir, f"{id_part}.json")
            
            # Skip if the file already exists
            if os.path.exists(output_file):
                print(f"File already exists: {output_file}. Skipping...")
                success_count += 1
                continue
            
            # Download and save the JSON
            if download_json(api_url, output_file):
                success_count += 1
            
            # Add a small delay to avoid overwhelming the server
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error processing ID {id_part}: {e}")
    
    print(f"Successfully downloaded {success_count} out of {len(ids)} JSON files.")

if __name__ == "__main__":
    main() 