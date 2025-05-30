#!/usr/bin/env python3
"""
Script to identify the specific IDs that are in master_index.txt but not in the index_full_mds directory.
This script:
1. Reads the IDs from qa_master_ids.txt and qa_mds_ids.txt
2. Identifies IDs that are in master_index.txt but not in the index_full_mds directory
3. Writes these missing IDs to missing_specific_ids.txt
4. Provides statistics about the missing IDs

Usage:
    python find_missing_ids.py
"""

import os
import sys


def read_ids_from_file(filename):
    """Read IDs from the specified file."""
    if not os.path.exists(filename):
        print(f"Error: File {filename} does not exist.")
        return []
    
    with open(filename, 'r', encoding='utf-8') as file:
        ids = [line.strip() for line in file if line.strip()]
    return ids


def find_missing_ids(master_ids, mds_ids):
    """Find IDs that are in master_ids but not in mds_ids."""
    # Convert mds_ids to a set for faster lookup
    mds_ids_set = set(mds_ids)
    
    # Find missing IDs
    missing_ids = []
    for id_part in master_ids:
        if id_part not in mds_ids_set:
            missing_ids.append(id_part)
    
    return missing_ids


def write_ids_to_file(ids, output_file):
    """Write the list of IDs to the specified output file."""
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("# IDs present in master_index.txt but missing in index_full_mds\n\n")
        for id_part in ids:
            file.write(f"{id_part}\n")
    
    print(f"Successfully wrote {len(ids)} missing IDs to {output_file}")


def main():
    # Define files
    master_ids_file = "qa_master_ids.txt"
    mds_ids_file = "qa_mds_ids.txt"
    missing_ids_file = "missing_specific_ids.txt"
    
    # Read IDs from files
    print(f"Reading IDs from {master_ids_file}...")
    master_ids = read_ids_from_file(master_ids_file)
    
    print(f"Reading IDs from {mds_ids_file}...")
    mds_ids = read_ids_from_file(mds_ids_file)
    
    if not master_ids or not mds_ids:
        print("Error: Could not read IDs from the input files.")
        print("Please run extract_qa_ids.py first to generate the necessary input files.")
        return 1
    
    # Find missing IDs
    print(f"\nComparing {len(master_ids)} master IDs with {len(mds_ids)} MDS IDs...")
    missing_ids = find_missing_ids(master_ids, mds_ids)
    
    # Print out the results
    print("\n----- RESULTS -----")
    print(f"IDs in master_index.txt: {len(master_ids)}")
    print(f"IDs in index_full_mds: {len(mds_ids)}")
    print(f"IDs missing from index_full_mds: {len(missing_ids)}")
    
    if missing_ids:
        print("\nTop missing IDs:")
        for i, id_part in enumerate(missing_ids[:10], 1):
            print(f"{i}. {id_part}")
        
        # Write missing IDs to file
        print(f"\nWriting missing IDs to {missing_ids_file}...")
        write_ids_to_file(missing_ids, missing_ids_file)
        
        if len(missing_ids) > 10:
            print(f"See {missing_ids_file} for the complete list of missing IDs.")
    else:
        print("\nNo missing IDs found! All IDs in master_index.txt are present in index_full_mds.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 