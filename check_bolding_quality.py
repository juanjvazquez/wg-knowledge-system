#!/usr/bin/env python3
"""
Quality Assurance script to check bolding in text files.
This script analyzes files in the index_full_mds directory to:
1. Count how many files start with different numbers of asterisks (*, **, ***, etc.)
2. Print files that don't start with exactly "**" (two asterisks)
"""

import os
import glob
import re
from collections import defaultdict

def count_leading_asterisks(line):
    """Count the number of consecutive asterisks at the beginning of a line."""
    if not line or not line.strip():
        return 0
        
    # Count consecutive asterisks at the start
    count = 0
    for char in line:
        if char == '*':
            count += 1
        else:
            break
    return count

def analyze_file(file_path):
    """Analyze a file to determine how many asterisks it starts with."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Skip empty files
        if not content.strip():
            return 0, True  # Return 0 asterisks and flag as an issue
            
        # Find the first non-empty line
        lines = content.split('\n')
        start_line_idx = 0
        while start_line_idx < len(lines) and not lines[start_line_idx].strip():
            start_line_idx += 1
            
        if start_line_idx >= len(lines):
            return 0, True  # Return 0 asterisks and flag as an issue
            
        first_line = lines[start_line_idx]
        asterisk_count = count_leading_asterisks(first_line)
        
        # Check for the pattern **text** (correctly bolded)
        # This helps identify if the file has proper markdown bolding
        is_correctly_bolded = bool(re.match(r'^\*\*[^*]+\*\*', first_line))
        
        # If asterisk count is not 2 or the pattern doesn't match proper bolding,
        # flag it as an issue
        has_issue = (asterisk_count != 2) or not is_correctly_bolded
        
        return asterisk_count, has_issue
        
    except Exception as e:
        print(f"Error analyzing {file_path}: {str(e)}")
        return 0, True  # Return 0 asterisks and flag as an issue

def main():
    # Define the directory containing the text files
    directory = "index_full_mds"
    
    # Get all .txt files in the directory
    txt_files = glob.glob(os.path.join(directory, "*.txt"))
    
    print(f"Found {len(txt_files)} .txt files in {directory}")
    
    # Initialize counters
    asterisk_counts = defaultdict(int)
    problematic_files = []
    
    # Analyze each file
    for txt_file in txt_files:
        asterisk_count, has_issue = analyze_file(txt_file)
        asterisk_counts[asterisk_count] += 1
        
        if has_issue:
            problematic_files.append(txt_file)
    
    # Print summary statistics
    print("\n=== SUMMARY STATISTICS ===")
    print(f"Total files analyzed: {len(txt_files)}")
    
    print("\nDistribution of leading asterisks:")
    for count in sorted(asterisk_counts.keys()):
        percentage = (asterisk_counts[count] / len(txt_files)) * 100
        print(f"  {count} asterisks: {asterisk_counts[count]} files ({percentage:.2f}%)")
    
    print(f"\nFiles with bolding issues: {len(problematic_files)} ({(len(problematic_files) / len(txt_files)) * 100:.2f}%)")
    
    # Print problematic files
    if problematic_files:
        print("\n=== FILES WITHOUT PROPER BOLDING ===")
        print("The following files don't start with exactly '**' followed by text and then '**':")
        for file in problematic_files:
            print(f"  {file}")
        
        # Write problematic files to a file for easier reference
        with open("bolding_issues.txt", "w", encoding="utf-8") as issue_file:
            issue_file.write("Files without proper bolding (should start with ** and have closing **):\n")
            for file in problematic_files:
                issue_file.write(f"{file}\n")
        print(f"\nList of problematic files saved to bolding_issues.txt")
    else:
        print("\nAll files have correct bolding! Great job!")

if __name__ == "__main__":
    main() 