#!/usr/bin/env python3
"""
Script to check which files from master_index.txt are missing in the index_full_mds directory.
This script:
1. Reads master_index.txt to get all unique links
2. Checks which Markdown files are missing in index_full_mds
3. Writes the list of missing file IDs to missing_mds.txt
4. Prints out a summary of the results

Usage:
    python check_missing_mds.py
"""

import os
import sys
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


def check_missing_mds(master_index_file, md_dir):
    """
    Check which files from master_index are missing in the index_full_mds directory.
    Returns a list of missing file IDs.
    """
    # Read links from the master index file
    links = read_links_from_file(master_index_file)
    total_links = len(links)
    
    print(f"Found {total_links} unique links in the master index file.")
    
    # Check which Markdown files are missing
    existing_md_count = 0
    missing_md_count = 0
    missing_ids = []
    
    for link in tqdm(links, desc="Checking files"):
        id_part = extract_id_from_url(link)
        md_file = os.path.join(md_dir, f"{id_part}.txt")
        
        # Check if Markdown file exists
        if os.path.exists(md_file):
            existing_md_count += 1
        else:
            missing_md_count += 1
            missing_ids.append(id_part)
    
    # Calculate completion percentage
    completion_percentage = (existing_md_count / total_links) * 100 if total_links > 0 else 0
    
    return {
        "total_links": total_links,
        "existing_md_count": existing_md_count,
        "missing_md_count": missing_md_count,
        "completion_percentage": completion_percentage,
        "missing_ids": missing_ids
    }


def write_missing_ids_to_file(missing_ids, output_file):
    """Write the list of missing file IDs to the specified output file."""
    with open(output_file, 'w', encoding='utf-8') as file:
        for id_part in missing_ids:
            file.write(f"{id_part}\n")
    
    print(f"Successfully wrote {len(missing_ids)} missing IDs to {output_file}")


def main():
    # Define directories and files
    master_index_file = "master_index.txt"
    md_dir = "index_full_mds"
    missing_md_file = "missing_mds.txt"
    
    # Check if master_index.txt exists
    if not os.path.exists(master_index_file):
        print(f"Error: Master index file {master_index_file} does not exist.")
        print("Please run check_progress.py first to generate the master index file.")
        return 1
    
    # Check if index_full_mds directory exists
    if not os.path.exists(md_dir):
        print(f"Error: Markdown directory {md_dir} does not exist.")
        print("Please create the directory or run the conversion script first.")
        return 1
    
    # Check which files are missing
    print(f"Checking for missing Markdown files...")
    result = check_missing_mds(master_index_file, md_dir)
    
    # Print out the results
    print("\n----- RESULTS -----")
    print(f"Total unique links in master_index: {result['total_links']}")
    print(f"Existing Markdown files: {result['existing_md_count']}")
    print(f"Missing Markdown files: {result['missing_md_count']}")
    print(f"Conversion completion: {result['completion_percentage']:.2f}%")
    
    # Write missing IDs to file
    if result['missing_md_count'] > 0:
        print(f"\nWriting missing Markdown IDs to {missing_md_file}...")
        write_missing_ids_to_file(result['missing_ids'], missing_md_file)
        print(f"You can now use this file to identify which files need to be converted.")
    else:
        print("\nAll files from master_index.txt exist in the index_full_mds directory!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 