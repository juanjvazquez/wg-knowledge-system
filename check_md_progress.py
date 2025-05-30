#!/usr/bin/env python3
"""
Script to check the progress of HTML to Markdown conversion:
1. Reads master_index.txt to get all unique links
2. Checks how many corresponding Markdown files exist in index_full_mds
3. Creates a list of missing files for re-running the conversion
4. Prints out the results

Usage:
    python check_md_progress.py
"""

import os
import re
from urllib.parse import urlparse
from tqdm import tqdm


def ensure_directory_exists(directory):
    """Ensure the specified directory exists, if not create it."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")


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


def check_md_files(master_index_file, json_dir, md_dir):
    """Check how many Markdown files exist for the links in the master index file."""
    # Read links from the master index file
    links = read_links_from_file(master_index_file)
    total_links = len(links)
    
    print(f"Found {total_links} unique links in the master index file.")
    
    # Check how many Markdown files exist and identify missing JSON files
    existing_md_count = 0
    missing_json_count = 0
    missing_md_count = 0
    missing_ids = []
    missing_json_ids = []
    
    for link in tqdm(links, desc="Checking files"):
        id_part = extract_id_from_url(link)
        json_file = os.path.join(json_dir, f"{id_part}.json")
        md_file = os.path.join(md_dir, f"{id_part}.txt")
        
        # Check if JSON file exists
        json_exists = os.path.exists(json_file)
        
        # Check if Markdown file exists
        md_exists = os.path.exists(md_file)
        
        if md_exists:
            existing_md_count += 1
        elif not json_exists:
            # JSON file doesn't exist, so we can't create MD
            missing_json_count += 1
            missing_json_ids.append(id_part)
        else:
            # JSON file exists but MD doesn't
            missing_md_count += 1
            missing_ids.append(id_part)
    
    # Calculate completion percentage
    completion_percentage = (existing_md_count / total_links) * 100 if total_links > 0 else 0
    
    return {
        "total_links": total_links,
        "existing_md_count": existing_md_count,
        "missing_json_count": missing_json_count,
        "missing_md_count": missing_md_count,
        "completion_percentage": completion_percentage,
        "missing_ids": missing_ids,
        "missing_json_ids": missing_json_ids
    }


def create_missing_md_file(missing_ids, output_file):
    """Create a file containing the IDs of missing Markdown files."""
    with open(output_file, 'w', encoding='utf-8') as file:
        for id_part in missing_ids:
            file.write(f"{id_part}\n")
    
    print(f"Successfully wrote {len(missing_ids)} missing IDs to {output_file}")


def main():
    # Define directories and files
    master_index_file = "master_index.txt"
    json_dir = "index_full_jsons"
    md_dir = "index_full_mds"
    missing_md_file = "missing_mds.txt"
    
    # Ensure directories exist
    ensure_directory_exists(md_dir)
    
    # Check if master_index.txt exists
    if not os.path.exists(master_index_file):
        print(f"Error: Master index file {master_index_file} does not exist.")
        print("Please run check_progress.py first to generate the master index file.")
        return
    
    # Check how many Markdown files exist
    print(f"Checking Markdown files in {md_dir}...")
    result = check_md_files(master_index_file, json_dir, md_dir)
    
    # Print out the results
    print("\n----- RESULTS -----")
    print(f"Total unique links: {result['total_links']}")
    print(f"Existing Markdown files: {result['existing_md_count']}")
    print(f"Missing Markdown files (JSON exists): {result['missing_md_count']}")
    print(f"Missing JSON files: {result['missing_json_count']}")
    print(f"Conversion completion: {result['completion_percentage']:.2f}%")
    
    # Create a file with the IDs of missing Markdown files
    if result['missing_md_count'] > 0:
        print(f"\nCreating file with missing Markdown IDs: {missing_md_file}")
        create_missing_md_file(result['missing_ids'], missing_md_file)
        print(f"You can re-run the conversion for these files with:")
        print(f"python convert_missing_md.py")
    
    # Print warning for missing JSON files
    if result['missing_json_count'] > 0:
        print(f"\nWarning: {result['missing_json_count']} JSON files are missing.")
        print(f"You need to download these JSON files first before converting to Markdown.")
        print(f"Run download_jsons_concurrent.py to download missing JSON files.")


if __name__ == "__main__":
    main() 