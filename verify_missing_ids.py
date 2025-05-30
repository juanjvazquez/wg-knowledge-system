#!/usr/bin/env python3
"""
Script to verify if the files for the previously missing IDs now exist in the index_full_mds directory.
This script:
1. Reads the specific IDs from missing_specific_ids.txt
2. Directly checks if each corresponding file exists in the index_full_mds directory
3. Provides a summary of the verification results

Usage:
    python verify_missing_ids.py
"""

import os
import sys


def read_ids_from_file(filename):
    """Read IDs from the specified file."""
    if not os.path.exists(filename):
        print(f"Error: File {filename} does not exist.")
        return []
    
    with open(filename, 'r', encoding='utf-8') as file:
        # Skip lines starting with '#' (header)
        ids = [line.strip() for line in file if line.strip() and not line.startswith('#')]
    return ids


def verify_files_exist(ids, directory):
    """Verify if files for the given IDs exist in the specified directory."""
    existing_files = []
    missing_files = []
    
    print(f"Verifying {len(ids)} files in {directory}...")
    
    for id_part in ids:
        file_path = os.path.join(directory, f"{id_part}.txt")
        if os.path.exists(file_path):
            existing_files.append(id_part)
        else:
            missing_files.append(id_part)
    
    return {
        "existing_files": existing_files,
        "missing_files": missing_files
    }


def main():
    # Define files and directories
    missing_ids_file = "missing_specific_ids.txt"
    md_dir = "index_full_mds"
    
    # Read missing IDs
    print(f"Reading missing IDs from {missing_ids_file}...")
    ids = read_ids_from_file(missing_ids_file)
    
    if not ids:
        print("Error: No IDs found in the input file.")
        print("Please run find_missing_ids.py first to generate the missing_specific_ids.txt file.")
        return 1
    
    print(f"Found {len(ids)} IDs to verify.")
    
    # Verify files exist
    result = verify_files_exist(ids, md_dir)
    
    # Print results
    print("\n----- VERIFICATION RESULTS -----")
    print(f"Total IDs checked: {len(ids)}")
    print(f"Files that exist: {len(result['existing_files'])} ({(len(result['existing_files']) / len(ids)) * 100:.2f}%)")
    print(f"Files still missing: {len(result['missing_files'])} ({(len(result['missing_files']) / len(ids)) * 100:.2f}%)")
    
    if result['missing_files']:
        print("\nFiles still missing:")
        for id_part in result['missing_files']:
            print(f"  - {id_part}")
    else:
        print("\nGreat! All previously missing files now exist in the index_full_mds directory.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 