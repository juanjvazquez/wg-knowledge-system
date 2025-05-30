#!/usr/bin/env python3
"""
Script to check for duplicate IDs in the master_index.txt file.
This script:
1. Reads all links from master_index.txt
2. Extracts the ID part from each link (e.g., "ZK_1_NB_108-6_V")
3. Identifies any duplicate IDs (even if the full links are different)
4. Outputs statistics about duplicates found
5. Writes duplicate IDs to duplicates.txt if any are found

Usage:
    python check_duplicate_links.py
"""

import os
import sys
from collections import Counter
from urllib.parse import urlparse
from tqdm import tqdm


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


def check_for_duplicate_ids(links):
    """
    Check for duplicate IDs (last parts of links) in the provided list.
    Returns a dictionary with statistics and a list of duplicates.
    """
    print(f"Extracting IDs and checking for duplicates among {len(links)} links...")
    
    # Extract ID from each link and track the original link
    ids_with_links = []
    for link in tqdm(links, desc="Extracting IDs"):
        id_part = extract_id_from_url(link)
        ids_with_links.append((id_part, link))
    
    # Get all IDs
    ids = [id_part for id_part, _ in ids_with_links]
    
    # Count occurrences of each ID
    id_counter = Counter(ids)
    
    # Find duplicate IDs (IDs that appear more than once)
    duplicate_ids = {id_part: count for id_part, count in id_counter.items() if count > 1}
    
    # Create a list of duplicate IDs with their corresponding links
    duplicate_entries = []
    for id_part, count in duplicate_ids.items():
        # Find all links with this ID
        matching_links = [link for i, link in ids_with_links if i == id_part]
        duplicate_entries.append((id_part, matching_links, count))
    
    # Sort duplicates by count (highest first)
    duplicate_entries.sort(key=lambda x: x[2], reverse=True)
    
    return {
        "total_links": len(links),
        "unique_ids": len(id_counter),
        "duplicate_ids": len(duplicate_ids),
        "duplicate_entries": duplicate_entries
    }


def write_duplicates_to_file(duplicate_entries, output_file):
    """Write the list of duplicate IDs to the specified output file."""
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("# Duplicate IDs in master_index.txt\n\n")
        file.write("Format: ID (Count)\n")
        file.write("  - Link 1\n")
        file.write("  - Link 2\n\n")
        
        for id_part, links, count in duplicate_entries:
            file.write(f"{id_part} ({count})\n")
            for link in links:
                file.write(f"  - {link}\n")
            file.write("\n")
    
    print(f"Successfully wrote {len(duplicate_entries)} duplicate ID entries to {output_file}")


def main():
    # Define files
    master_index_file = "master_index.txt"
    duplicates_file = "duplicate_ids.txt"
    
    # Check if master_index.txt exists
    if not os.path.exists(master_index_file):
        print(f"Error: Master index file {master_index_file} does not exist.")
        print("Please run check_progress.py first to generate the master index file.")
        return 1
    
    # Read links from the master index file
    links = read_links_from_file(master_index_file)
    
    # Check for duplicate IDs
    result = check_for_duplicate_ids(links)
    
    # Print out the results
    print("\n----- RESULTS -----")
    print(f"Total links in master_index: {result['total_links']}")
    print(f"Unique IDs: {result['unique_ids']}")
    
    if result['duplicate_ids'] > 0:
        print(f"Found {result['duplicate_ids']} duplicate IDs!")
        print("\nTop duplicate ID entries:")
        for i, (id_part, links, count) in enumerate(result['duplicate_entries'][:5], 1):
            print(f"{i}. '{id_part}' appears {count} times")
        
        # Write duplicates to file
        print(f"\nWriting duplicate ID entries to {duplicates_file}...")
        write_duplicates_to_file(result['duplicate_entries'], duplicates_file)
        
        if len(result['duplicate_entries']) > 5:
            print(f"See {duplicates_file} for the complete list of duplicates.")
    else:
        print("\nNo duplicate IDs found! All links in master_index.txt point to unique Zettelkasten cards.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 