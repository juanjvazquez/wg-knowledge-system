#!/usr/bin/env python
"""
Script to download JSON data for each Zettelkasten link using concurrent workers.

Features:
1. Uses concurrent.futures to download multiple JSONs simultaneously
2. Checks master_index.txt or missing_jsons.txt to only download missing JSONs
3. Shows overall progress with tqdm
4. Handles errors gracefully with retries

Usage:
    python download_jsons_concurrent.py           # Download all missing JSONs
    python download_jsons_concurrent.py --workers 16  # Specify number of concurrent workers
"""

import os
import sys
import json
import time
import argparse
import requests
import concurrent.futures
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


def read_ids_from_file(filename):
    """Read IDs from the specified file."""
    with open(filename, 'r', encoding='utf-8') as file:
        ids = [line.strip() for line in file if line.strip()]
    return ids


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


def download_json(params):
    """Download JSON data from the API URL and save it to the specified path."""
    id_part, api_url, save_path, retry_count, delay = params
    
    for attempt in range(retry_count):
        try:
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            # Parse and save the JSON data
            json_data = response.json()
            with open(save_path, 'w', encoding='utf-8') as file:
                json.dump(json_data, file, ensure_ascii=False, indent=2)
            
            return (True, id_part)
        except requests.exceptions.RequestException as e:
            if attempt < retry_count - 1:
                time.sleep(delay)  # Wait before retrying
            else:
                return (False, id_part)
        except Exception as e:
            return (False, id_part)


def get_missing_ids(json_dir, source='master_index.txt'):
    """Get a list of missing JSON files.
    
    Args:
        json_dir: The directory where JSON files are stored
        source: Either 'master_index.txt' or 'missing_jsons.txt'
    
    Returns:
        A list of IDs for which JSON files are missing
    """
    missing_ids = []
    
    # If missing_jsons.txt exists and is specified as the source, use it
    if source == 'missing_jsons.txt' and os.path.exists('missing_jsons.txt'):
        print("Using missing_jsons.txt to identify missing files...")
        return read_ids_from_file('missing_jsons.txt')
    
    # Otherwise, use master_index.txt
    if not os.path.exists('master_index.txt'):
        print("Error: master_index.txt not found. Run check_progress.py first.")
        sys.exit(1)
    
    print("Using master_index.txt to identify missing files...")
    links = read_links_from_file('master_index.txt')
    
    # Check each link
    for link in tqdm(links, desc="Checking existing files"):
        id_part = extract_id_from_url(link)
        json_file = os.path.join(json_dir, f"{id_part}.json")
        
        if not os.path.exists(json_file):
            missing_ids.append(id_part)
    
    print(f"Found {len(missing_ids)} missing JSON files out of {len(links)} total.")
    return missing_ids


def download_missing_jsons(json_dir, missing_ids, max_workers=8):
    """Download missing JSON files using concurrent workers."""
    # Ensure output directory exists
    ensure_directory_exists(json_dir)
    
    # Prepare parameters for each download
    download_params = []
    for id_part in missing_ids:
        api_url = construct_api_url(id_part)
        save_path = os.path.join(json_dir, f"{id_part}.json")
        # Parameters: id_part, api_url, save_path, retry_count, delay
        download_params.append((id_part, api_url, save_path, 3, 1))
    
    # Download using concurrent workers
    success_count = 0
    failed_ids = []
    
    with tqdm(total=len(missing_ids), desc="Downloading JSONs") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all download tasks
            future_to_params = {executor.submit(download_json, params): params for params in download_params}
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_params):
                success, id_part = future.result()
                if success:
                    success_count += 1
                else:
                    failed_ids.append(id_part)
                pbar.update(1)
    
    # Report results
    print(f"\nDownload complete!")
    print(f"Successfully downloaded: {success_count} files")
    print(f"Failed downloads: {len(failed_ids)} files")
    
    # Write failed IDs to a file if there are any
    if failed_ids:
        with open("failed_downloads.txt", 'w', encoding='utf-8') as file:
            for id_part in failed_ids:
                file.write(f"{id_part}\n")
        print(f"List of failed downloads written to failed_downloads.txt")
    
    return success_count, failed_ids


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Download missing JSON files with concurrent workers')
    parser.add_argument('--workers', type=int, default=8, help='Number of concurrent workers (default: 8)')
    parser.add_argument('--source', choices=['master_index.txt', 'missing_jsons.txt'], 
                        default='missing_jsons.txt', help='Source file to check for missing JSONs')
    args = parser.parse_args()
    
    # Define output directory
    json_dir = "index_full_jsons"
    
    # Get list of missing JSON files
    missing_ids = get_missing_ids(json_dir, args.source)
    
    if not missing_ids:
        print("No missing JSON files found. All files are already downloaded.")
        return
    
    print(f"Starting download of {len(missing_ids)} JSON files using {args.workers} concurrent workers...")
    
    # Download missing JSON files
    success_count, failed_ids = download_missing_jsons(json_dir, missing_ids, args.workers)
    
    # Print completion message
    if not failed_ids:
        print("All JSON files have been successfully downloaded!")
    else:
        print(f"Downloaded {success_count} out of {len(missing_ids)} JSON files.")
        print(f"To retry failed downloads, run: python download_jsons_concurrent.py --source failed_downloads.txt")


if __name__ == "__main__":
    main() 