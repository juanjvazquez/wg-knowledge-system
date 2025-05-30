#!/usr/bin/env python3
"""
Script to download JSON files and convert them to Markdown for the IDs in missing_specific_ids.txt.
This script:
1. Reads the specific IDs from missing_specific_ids.txt
2. Downloads the corresponding JSON files using the API
3. Converts the JSON files to Markdown format
4. Saves the result to the index_full_mds directory
5. Provides statistics about the process

Usage:
    python process_missing_specific_ids.py [--workers N]
"""

import os
import sys
import json
import requests
import argparse
import html2text
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm


def read_ids_from_file(filename):
    """Read IDs from the specified file."""
    if not os.path.exists(filename):
        print(f"Error: File {filename} does not exist.")
        return []
    
    with open(filename, 'r', encoding='utf-8') as file:
        # Skip lines starting with '#' (header)
        ids = [line.strip() for line in file if line.strip() and not line.startswith('#')]
    return ids


def ensure_directory_exists(directory):
    """Ensure the specified directory exists, if not create it."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")


def download_json(id_part, json_dir, api_base_url="https://v0.api.niklas-luhmann-archiv.de/ZK/zettel/"):
    """
    Download JSON data for the specified ID.
    Returns a tuple of (success, id_part) where success is a boolean.
    """
    url = f"{api_base_url}{id_part}"
    json_file = os.path.join(json_dir, f"{id_part}.json")
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(json_file, 'w', encoding='utf-8') as file:
                json.dump(response.json(), file, ensure_ascii=False, indent=2)
            return (True, id_part)
        else:
            print(f"Error: Failed to download {id_part}, status code: {response.status_code}")
            return (False, id_part)
    except Exception as e:
        print(f"Error: Exception when downloading {id_part}: {str(e)}")
        return (False, id_part)


def convert_json_to_md(id_part, json_dir, md_dir):
    """
    Convert JSON file to Markdown for the specified ID.
    Returns a tuple of (success, id_part) where success is a boolean.
    """
    json_file = os.path.join(json_dir, f"{id_part}.json")
    md_file = os.path.join(md_dir, f"{id_part}.txt")
    
    if not os.path.exists(json_file):
        print(f"Error: JSON file {json_file} does not exist.")
        return (False, id_part)
    
    try:
        # Read JSON file
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Extract transcription HTML content
        if "transcription" in data and "html" in data["transcription"]:
            html_content = data["transcription"]["html"]
            
            # Convert HTML to Markdown
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.escape_snob = True
            h.body_width = 0  # No wrapping
            markdown_content = h.handle(html_content)
            
            # Save to MD file
            with open(md_file, 'w', encoding='utf-8') as file:
                file.write(markdown_content)
            
            return (True, id_part)
        else:
            print(f"Error: Could not find transcription HTML content in {json_file}")
            return (False, id_part)
    except Exception as e:
        print(f"Error: Exception when converting {id_part} to Markdown: {str(e)}")
        return (False, id_part)


def process_ids(ids, json_dir, md_dir, workers=8):
    """Process the list of IDs by downloading JSON files and converting them to Markdown."""
    # Ensure directories exist
    ensure_directory_exists(json_dir)
    ensure_directory_exists(md_dir)
    
    download_results = {"success": [], "failed": []}
    convert_results = {"success": [], "failed": []}
    
    # Download JSON files using ThreadPoolExecutor
    print(f"\nDownloading {len(ids)} JSON files with {workers} workers...")
    with ThreadPoolExecutor(max_workers=workers) as executor:
        # Submit all download tasks
        future_to_id = {
            executor.submit(download_json, id_part, json_dir): id_part for id_part in ids
        }
        
        # Process results as they complete
        for future in tqdm(future_to_id, desc="Downloading JSONs"):
            success, id_part = future.result()
            if success:
                download_results["success"].append(id_part)
            else:
                download_results["failed"].append(id_part)
    
    # Print download results
    print(f"\nJSON Download Results:")
    print(f"  Successfully downloaded: {len(download_results['success'])}")
    print(f"  Failed to download: {len(download_results['failed'])}")
    
    # Only proceed with conversion for successfully downloaded files
    ids_to_convert = download_results["success"]
    
    if ids_to_convert:
        # Convert JSON files to Markdown
        print(f"\nConverting {len(ids_to_convert)} JSON files to Markdown...")
        for id_part in tqdm(ids_to_convert, desc="Converting to Markdown"):
            success, _ = convert_json_to_md(id_part, json_dir, md_dir)
            if success:
                convert_results["success"].append(id_part)
            else:
                convert_results["failed"].append(id_part)
        
        # Print conversion results
        print(f"\nMarkdown Conversion Results:")
        print(f"  Successfully converted: {len(convert_results['success'])}")
        print(f"  Failed to convert: {len(convert_results['failed'])}")
    
    # Save failed IDs to files
    if download_results["failed"]:
        with open("failed_specific_downloads.txt", 'w', encoding='utf-8') as file:
            for id_part in download_results["failed"]:
                file.write(f"{id_part}\n")
        print(f"\nSaved failed download IDs to failed_specific_downloads.txt")
    
    if convert_results["failed"]:
        with open("failed_specific_conversions.txt", 'w', encoding='utf-8') as file:
            for id_part in convert_results["failed"]:
                file.write(f"{id_part}\n")
        print(f"\nSaved failed conversion IDs to failed_specific_conversions.txt")
    
    return download_results, convert_results


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Process missing specific IDs')
    parser.add_argument('--workers', type=int, default=8, help='Number of worker threads for downloading (default: 8)')
    args = parser.parse_args()
    
    # Define files and directories
    missing_ids_file = "missing_specific_ids.txt"
    json_dir = "index_full_jsons"
    md_dir = "index_full_mds"
    
    # Read missing IDs
    print(f"Reading missing IDs from {missing_ids_file}...")
    ids = read_ids_from_file(missing_ids_file)
    
    if not ids:
        print("Error: No IDs found in the input file.")
        print("Please run find_missing_ids.py first to generate the missing_specific_ids.txt file.")
        return 1
    
    print(f"Found {len(ids)} missing IDs to process.")
    
    # Process the IDs
    download_results, convert_results = process_ids(ids, json_dir, md_dir, workers=args.workers)
    
    # Print final summary
    print("\n----- FINAL SUMMARY -----")
    print(f"Total IDs processed: {len(ids)}")
    print(f"Successfully downloaded JSON files: {len(download_results['success'])}")
    print(f"Successfully converted to Markdown: {len(convert_results['success'])}")
    print(f"Overall success rate: {(len(convert_results['success']) / len(ids)) * 100:.2f}%")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 