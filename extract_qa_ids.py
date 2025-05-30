#!/usr/bin/env python3
"""
Script to extract IDs from both index_full_mds directory and master_index.txt.
This script:
1. Extracts IDs from all filenames in the index_full_mds directory and writes them to qa_mds_ids.txt
2. Extracts IDs from all links in master_index.txt and writes them to qa_master_ids.txt
3. Provides statistics about the number of IDs extracted from each source

Usage:
    python extract_qa_ids.py
"""

import os
import sys
from urllib.parse import urlparse
from tqdm import tqdm


def get_files_in_directory(directory):
    """Get all files in the specified directory."""
    if not os.path.exists(directory):
        print(f"Error: Directory {directory} does not exist.")
        return []
    
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]


def extract_id_from_filename(filename):
    """Extract the ID from a filename by removing the .txt extension."""
    # Remove the .txt extension
    id_part = filename.replace('.txt', '')
    return id_part


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


def extract_and_write_mds_ids(md_dir, output_file):
    """
    Extract IDs from all filenames in the specified directory and write them to an output file.
    Returns the number of IDs written.
    """
    # Get all files in the markdown directory
    files = get_files_in_directory(md_dir)
    
    if not files:
        print(f"No files found in {md_dir}. Please run the conversion scripts first.")
        return 0
    
    print(f"Extracting IDs from {len(files)} files in {md_dir}...")
    
    # Extract ID from each filename
    ids = []
    for filename in tqdm(files, desc="Processing filenames"):
        id_part = extract_id_from_filename(filename)
        ids.append(id_part)
    
    # Sort the IDs for easier comparison
    ids.sort()
    
    # Write IDs to output file
    with open(output_file, 'w', encoding='utf-8') as file:
        for id_part in ids:
            file.write(f"{id_part}\n")
    
    print(f"Successfully wrote {len(ids)} IDs from {md_dir} to {output_file}")
    return len(ids)


def extract_and_write_master_ids(master_index_file, output_file):
    """
    Extract IDs from all links in the master index file and write them to an output file.
    Returns the number of IDs written.
    """
    # Check if the master index file exists
    if not os.path.exists(master_index_file):
        print(f"Error: Master index file {master_index_file} does not exist.")
        print("Please run check_progress.py first to generate the master index file.")
        return 0
    
    # Read links from the master index file
    links = read_links_from_file(master_index_file)
    
    print(f"Extracting IDs from {len(links)} links in {master_index_file}...")
    
    # Extract ID from each link
    ids = []
    for link in tqdm(links, desc="Processing links"):
        id_part = extract_id_from_url(link)
        ids.append(id_part)
    
    # Sort the IDs for easier comparison
    ids.sort()
    
    # Write IDs to output file
    with open(output_file, 'w', encoding='utf-8') as file:
        for id_part in ids:
            file.write(f"{id_part}\n")
    
    print(f"Successfully wrote {len(ids)} IDs from {master_index_file} to {output_file}")
    return len(ids)


def main():
    # Define directories and files
    md_dir = "index_full_mds"
    master_index_file = "master_index.txt"
    mds_ids_file = "qa_mds_ids.txt"
    master_ids_file = "qa_master_ids.txt"
    
    # Extract and write IDs from index_full_mds directory
    mds_count = extract_and_write_mds_ids(md_dir, mds_ids_file)
    
    # Extract and write IDs from master_index.txt
    master_count = extract_and_write_master_ids(master_index_file, master_ids_file)
    
    # Print summary
    if mds_count > 0 and master_count > 0:
        print("\n----- SUMMARY -----")
        print(f"IDs extracted from {md_dir}: {mds_count}")
        print(f"IDs extracted from {master_index_file}: {master_count}")
        print(f"Difference (master - mds): {master_count - mds_count}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 