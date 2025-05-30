#!/usr/bin/env python
"""
Script to download JSON data for each Zettelkasten link in the index_full_links_reord folder.
The script extracts the ID from each link, constructs an API URL, and saves the JSON response
to a new file in the index_full_jsons folder.

Usage:
    python download_jsons.py           # Process all files
    python download_jsons.py <filename> # Process a specific file
"""

import os
import sys
import json
import time
import requests
from tqdm import tqdm
from urllib.parse import urlparse

def ensure_directory_exists(directory):
    """Ensure the specified directory exists, if not create it."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")
    else:
        print(f"Directory already exists: {directory}")

def read_links_from_file(filename):
    """Read links from the specified file."""
    with open(filename, 'r', encoding='utf-8') as file:
        links = [line.strip() for line in file if line.strip()]
    return links

def extract_id_from_url(url):
    """Extract the ID from a Zettelkasten link URL."""
    # Parse the URL to get the path
    parsed_url = urlparse(url)
    path = parsed_url.path
    
    # The ID is the last part of the path
    id_part = path.split('/')[-1]
    
    return id_part

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
            
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {api_url} (attempt {attempt+1}/{retry_count}): {e}")
            if attempt < retry_count - 1:
                time.sleep(delay)  # Wait before retrying
        except Exception as e:
            print(f"Unexpected error with {api_url}: {e}")
            return False
    
    return False

def process_file(input_file, output_dir):
    """Process a single file containing Zettelkasten links."""
    links = read_links_from_file(input_file)
    print(f"Found {len(links)} links in {input_file}.")
    
    success_count = 0
    
    for link in tqdm(links, desc=f"Processing {os.path.basename(input_file)}"):
        try:
            # Extract ID from the link
            id_part = extract_id_from_url(link)
            
            # Construct API URL
            api_url = construct_api_url(id_part)
            
            # Define output file path
            output_file = os.path.join(output_dir, f"{id_part}.json")
            
            # Download and save the JSON
            if download_json(api_url, output_file):
                success_count += 1
            
            # Add a small delay to avoid overwhelming the server
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error processing link {link}: {e}")
    
    print(f"Successfully downloaded {success_count} out of {len(links)} JSON files from {input_file}.")
    return success_count

def main():
    # Define input and output directories
    input_dir = "index_full_links_reord"
    output_dir = "index_full_jsons"
    
    # Ensure output directory exists
    ensure_directory_exists(output_dir)
    
    # Determine whether to process a single file or all files
    if len(sys.argv) > 1:
        # Process a single file
        target_file = sys.argv[1]
        
        # Check if the file exists
        if not os.path.exists(target_file):
            # Try with the input directory
            potential_path = os.path.join(input_dir, target_file)
            if os.path.exists(potential_path):
                target_file = potential_path
            else:
                print(f"Error: File not found - {target_file}")
                return
        
        print(f"Processing single file: {target_file}")
        process_file(target_file, output_dir)
    else:
        # Process all files in the input directory
        print(f"Processing all files in {input_dir}...")
        
        # Get list of all files in the input directory
        input_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) 
                      if os.path.isfile(os.path.join(input_dir, f)) and f.endswith('.txt')]
        
        if not input_files:
            print(f"No .txt files found in {input_dir}")
            return
        
        print(f"Found {len(input_files)} files to process.")
        
        # Process each file
        total_success = 0
        for input_file in sorted(input_files):
            success_count = process_file(input_file, output_dir)
            total_success += success_count
        
        print(f"Total: Successfully downloaded {total_success} JSON files.")

if __name__ == "__main__":
    main() 