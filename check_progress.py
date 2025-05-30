#!/usr/bin/env python
"""
Script to check the progress of JSON downloads:
1. Checks if master_index.txt exists, if not creates it from all files in index_full_links_reord
2. Reads master_index.txt to get all unique links
3. Checks how many corresponding JSON files exist in index_full_jsons
4. Prints out the results

Usage:
    python check_progress.py
"""

import os
import glob
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


def extract_id_from_filename(filename):
    """Extract the Luhmann ID from a filename."""
    base = os.path.basename(filename)
    match = re.search(r'links_ZK_1_NB_(.+?)\.txt', base)
    if match:
        return match.group(1)
    return ""


def luhmann_sort_key(filename):
    """Create a sort key for Luhmann notation that preserves the intended ordering."""
    id_part = extract_id_from_filename(filename)
    
    # Replace underscores with a character that sorts before hyphens
    # This ensures that 1_1 comes before 1-2
    id_part = id_part.replace('_', '.')
    
    # Split parts into components
    # We need to separate numbers and letters for proper numerical sorting
    parts = []
    current_part = ""
    current_type = None

    for char in id_part:
        # Determine the type of the current character
        if char.isdigit():
            char_type = 'digit'
        elif char.isalpha():
            char_type = 'alpha'
        else:
            char_type = 'special'
        
        # If this is a new type or a special character, start a new part
        if current_type != char_type or char_type == 'special':
            if current_part:
                parts.append(current_part)
            current_part = char
            current_type = char_type
        else:
            current_part += char
    
    # Add the last part
    if current_part:
        parts.append(current_part)
    
    # Convert parts to a sortable tuple
    result = []
    for part in parts:
        if part.isdigit():
            # Convert digits to integers for proper numerical sorting
            result.append((0, int(part)))
        elif part == '.':
            # Underscore (replaced with .) should sort before hyphen
            result.append((1, part))
        elif part == '-':
            # Hyphen sorts after underscore
            result.append((2, part))
        elif part.islower():
            # Lowercase letters come after special characters
            result.append((3, part))
        elif part.isupper():
            # Uppercase letters come after lowercase
            result.append((4, part))
        else:
            # Any other cases
            result.append((5, part))
    
    return result


def get_proper_ordering():
    """Define proper file order based on Luhmann numbering system."""
    # Define the expected ordering of top-level entries
    # This helps ensure we start with Zettel 1 and go in the correct order
    proper_order = [
        "1_1", "1-2", "1-3", "1-5", "1-6", "1-8", "1-9", "1-12"
    ]
    return proper_order


def generate_master_index(input_dir, output_file):
    """Generate a master index file containing all links from all files in the input directory."""
    print(f"Generating master index file: {output_file}")
    
    # Get list of all files in the input directory
    input_files = glob.glob(os.path.join(input_dir, "*.txt"))
    
    if not input_files:
        print(f"No .txt files found in {input_dir}")
        return False
    
    print(f"Found {len(input_files)} files to process.")
    
    # Sort files according to Luhmann system ordering
    input_files.sort(key=luhmann_sort_key)
    
    # Get a list of Zettel 1 files to make sure they're at the top
    zettel_1_files = [f for f in input_files if extract_id_from_filename(f).startswith('1_') or extract_id_from_filename(f).startswith('1-')]
    
    # Define the proper order for Zettel 1 files
    proper_order = get_proper_ordering()
    
    # Sort Zettel 1 files in the proper order
    zettel_1_files.sort(key=lambda f: next(
        (i for i, prefix in enumerate(proper_order) if extract_id_from_filename(f).startswith(prefix)), 
        len(proper_order)
    ))
    
    # Remove Zettel 1 files from the main list
    other_files = [f for f in input_files if f not in set(zettel_1_files)]
    
    # Combine the two lists to get the final order
    ordered_files = zettel_1_files + other_files
    
    # For debugging: print the first few file IDs to check ordering
    print("First 10 files in order:")
    for i, file in enumerate(ordered_files[:10]):
        print(f"{i+1}. {extract_id_from_filename(file)}")
    
    # To maintain a list of all links preserving order but avoiding duplicates
    all_links = []
    seen_links = set()
    
    # Process each file
    for input_file in tqdm(ordered_files, desc="Processing files"):
        links = read_links_from_file(input_file)
        for link in links:
            if link not in seen_links:
                all_links.append(link)
                seen_links.add(link)
    
    # Write unique links to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        for link in all_links:
            file.write(f"{link}\n")
    
    print(f"Successfully wrote {len(all_links)} unique links to {output_file}")
    return True


def check_json_files(master_index_file, json_dir):
    """Check how many JSON files exist for the links in the master index file."""
    # Read links from the master index file
    links = read_links_from_file(master_index_file)
    total_links = len(links)
    
    print(f"Found {total_links} unique links in the master index file.")
    
    # Check how many JSON files exist
    existing_count = 0
    missing_ids = []
    
    for link in tqdm(links, desc="Checking JSON files"):
        id_part = extract_id_from_url(link)
        json_file = os.path.join(json_dir, f"{id_part}.json")
        
        if os.path.exists(json_file):
            existing_count += 1
        else:
            missing_ids.append(id_part)
    
    # Calculate completion percentage
    completion_percentage = (existing_count / total_links) * 100 if total_links > 0 else 0
    
    return {
        "total_links": total_links,
        "existing_count": existing_count,
        "completion_percentage": completion_percentage,
        "missing_count": len(missing_ids),
        "missing_ids": missing_ids
    }


def main():
    # Define directories and files
    input_dir = "index_full_links_reord"
    json_dir = "index_full_jsons"
    master_index_file = "master_index.txt"
    
    # Ensure output directory exists
    ensure_directory_exists(json_dir)
    
    # Step 1 & 2: Check if master_index.txt exists, if not generate it
    if not os.path.exists(master_index_file):
        print(f"Master index file {master_index_file} does not exist.")
        generate_master_index(input_dir, master_index_file)
    else:
        print(f"Master index file {master_index_file} already exists.")
        # Ask if the user wants to regenerate it
        regenerate = input("Do you want to regenerate the master index file? (y/n): ").lower()
        if regenerate == 'y':
            print("Regenerating master index file...")
            generate_master_index(input_dir, master_index_file)
    
    # Step 3: Check how many JSON files exist
    print(f"Checking JSON files in {json_dir}...")
    result = check_json_files(master_index_file, json_dir)
    
    # Step 4: Print out the results
    print("\n----- RESULTS -----")
    print(f"Total unique links: {result['total_links']}")
    print(f"Existing JSON files: {result['existing_count']}")
    print(f"Missing JSON files: {result['missing_count']}")
    print(f"Completion: {result['completion_percentage']:.2f}%")
    
    # Optionally, if there are not too many missing files, print them out
    if 0 < result['missing_count'] <= 20:
        print("\nMissing JSON files:")
        for id_part in result['missing_ids']:
            print(f"  - {id_part}")
    elif result['missing_count'] > 20:
        print(f"\nThere are {result['missing_count']} missing JSON files. Run the download_jsons.py script to download them.")
    
    # Write missing IDs to a file if there are any
    if result['missing_count'] > 0:
        with open("missing_jsons.txt", 'w', encoding='utf-8') as file:
            for id_part in result['missing_ids']:
                file.write(f"{id_part}\n")
        print(f"\nList of missing JSON files written to missing_jsons.txt")


if __name__ == "__main__":
    main() 