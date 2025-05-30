#!/usr/bin/env python3
"""
Script to check for unique IDs in the index_full_mds folder.
This script:
1. Scans all filenames in the index_full_mds directory
2. Extracts the ID part of each filename (without the .txt extension)
3. Identifies any duplicate IDs
4. Outputs statistics about duplicates found
5. Writes duplicate IDs to duplicate_md_ids.txt if any are found

Usage:
    python check_unique_mds_ids.py
"""

import os
import sys
from collections import Counter
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


def check_for_duplicate_ids(files, directory):
    """
    Check for duplicate IDs in the provided list of filenames.
    Returns a dictionary with statistics and a list of duplicates.
    """
    print(f"Checking for duplicates among {len(files)} files in {directory}...")
    
    # Extract ID from each filename and track the original filename
    ids_with_filenames = []
    for filename in tqdm(files, desc="Extracting IDs"):
        id_part = extract_id_from_filename(filename)
        ids_with_filenames.append((id_part, filename))
    
    # Get all IDs
    ids = [id_part for id_part, _ in ids_with_filenames]
    
    # Count occurrences of each ID
    id_counter = Counter(ids)
    
    # Find duplicate IDs (IDs that appear more than once)
    duplicate_ids = {id_part: count for id_part, count in id_counter.items() if count > 1}
    
    # Create a list of duplicate IDs with their corresponding filenames
    duplicate_entries = []
    for id_part, count in duplicate_ids.items():
        # Find all filenames with this ID
        matching_files = [filename for i, filename in ids_with_filenames if i == id_part]
        duplicate_entries.append((id_part, matching_files, count))
    
    # Sort duplicates by count (highest first)
    duplicate_entries.sort(key=lambda x: x[2], reverse=True)
    
    return {
        "total_files": len(files),
        "unique_ids": len(id_counter),
        "duplicate_ids": len(duplicate_ids),
        "duplicate_entries": duplicate_entries
    }


def write_duplicates_to_file(duplicate_entries, output_file):
    """Write the list of duplicate IDs to the specified output file."""
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("# Duplicate IDs in index_full_mds folder\n\n")
        file.write("Format: ID (Count)\n")
        file.write("  - Filename 1\n")
        file.write("  - Filename 2\n\n")
        
        for id_part, filenames, count in duplicate_entries:
            file.write(f"{id_part} ({count})\n")
            for filename in filenames:
                file.write(f"  - {filename}\n")
            file.write("\n")
    
    print(f"Successfully wrote {len(duplicate_entries)} duplicate ID entries to {output_file}")


def main():
    # Define directories and files
    md_dir = "index_full_mds"
    duplicates_file = "duplicate_md_ids.txt"
    
    # Check if the markdown directory exists
    if not os.path.exists(md_dir):
        print(f"Error: Markdown directory {md_dir} does not exist.")
        print("Please create the directory or run the conversion scripts first.")
        return 1
    
    # Get all files in the markdown directory
    files = get_files_in_directory(md_dir)
    
    if not files:
        print(f"No files found in {md_dir}. Please run the conversion scripts first.")
        return 1
    
    # Check for duplicate IDs
    result = check_for_duplicate_ids(files, md_dir)
    
    # Print out the results
    print("\n----- RESULTS -----")
    print(f"Total files in {md_dir}: {result['total_files']}")
    print(f"Unique IDs: {result['unique_ids']}")
    
    if result['duplicate_ids'] > 0:
        print(f"Found {result['duplicate_ids']} duplicate IDs!")
        print("\nTop duplicate ID entries:")
        for i, (id_part, filenames, count) in enumerate(result['duplicate_entries'][:5], 1):
            print(f"{i}. '{id_part}' appears {count} times")
        
        # Write duplicates to file
        print(f"\nWriting duplicate ID entries to {duplicates_file}...")
        write_duplicates_to_file(result['duplicate_entries'], duplicates_file)
        
        if len(result['duplicate_entries']) > 5:
            print(f"See {duplicates_file} for the complete list of duplicates.")
    else:
        print(f"\nNo duplicate IDs found! All files in the {md_dir} directory have unique IDs.")
        print(f"Found {result['unique_ids']} unique markdown files.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 