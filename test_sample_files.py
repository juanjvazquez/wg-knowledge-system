#!/usr/bin/env python3
"""
Test script to analyze a sample of files for bolding quality.
This script:
1. Takes 5 samples each from various bolding patterns
2. Shows detailed information about each sample
3. Provides overall statistics
"""

import os
import glob
import re
import random
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
            return 0, True, None, None  # Return 0 asterisks, issue flag, no preview, no bolding status
            
        # Find the first non-empty line
        lines = content.split('\n')
        start_line_idx = 0
        while start_line_idx < len(lines) and not lines[start_line_idx].strip():
            start_line_idx += 1
            
        if start_line_idx >= len(lines):
            return 0, True, None, None  # Return 0 asterisks, issue flag, no preview, no bolding status
            
        first_line = lines[start_line_idx]
        asterisk_count = count_leading_asterisks(first_line)
        
        # Check for the pattern **text** (correctly bolded)
        # This helps identify if the file has proper markdown bolding
        is_correctly_bolded = bool(re.match(r'^\*\*[^*]+\*\*', first_line))
        
        # Also check for the pattern **text without closing asterisks
        has_opening_bold = bool(re.match(r'^\*\*[^*]+', first_line))
        
        # Define bolding status
        if is_correctly_bolded:
            bolding_status = "Complete (**text**)"
        elif has_opening_bold:
            bolding_status = "Partial (**text)"
        elif asterisk_count > 0:
            bolding_status = f"Incorrect ({asterisk_count} asterisks)"
        else:
            bolding_status = "None"
        
        # If asterisk count is not 2 or the pattern doesn't match proper bolding,
        # flag it as an issue
        has_issue = (asterisk_count != 2) or not is_correctly_bolded
        
        # Get a preview of the first line (up to 40 characters)
        preview = first_line[:min(40, len(first_line))]
        
        return asterisk_count, has_issue, preview, bolding_status
        
    except Exception as e:
        print(f"Error analyzing {file_path}: {str(e)}")
        return 0, True, None, None  # Return 0 asterisks, issue flag, no preview, no bolding status

def main():
    # Define the directory containing the text files
    directory = "index_full_mds"
    
    # Get all .txt files in the directory
    txt_files = glob.glob(os.path.join(directory, "*.txt"))
    
    print(f"Found {len(txt_files)} .txt files in {directory}")
    
    # Initialize categorization structures
    categorized_files = defaultdict(list)
    
    # Analyze each file and categorize by asterisk count
    for txt_file in txt_files:
        asterisk_count, has_issue, preview, bolding_status = analyze_file(txt_file)
        categorized_files[asterisk_count].append((txt_file, has_issue, preview, bolding_status))
    
    # Print distribution
    print("\n=== DISTRIBUTION OF LEADING ASTERISKS ===")
    for count in sorted(categorized_files.keys()):
        files_count = len(categorized_files[count])
        percentage = (files_count / len(txt_files)) * 100
        print(f"{count} asterisks: {files_count} files ({percentage:.2f}%)")
    
    # Print samples of each category
    print("\n=== SAMPLES BY CATEGORY ===")
    for count in sorted(categorized_files.keys()):
        category_files = categorized_files[count]
        sample_size = min(5, len(category_files))
        samples = random.sample(category_files, sample_size)
        
        print(f"\n-- {count} asterisks (showing {sample_size} of {len(category_files)} files) --")
        for file_path, has_issue, preview, bolding_status in samples:
            preview_str = preview if preview else "No content"
            issue_str = "ISSUE" if has_issue else "OK"
            file_name = os.path.basename(file_path)
            print(f"{file_name}: {bolding_status} - {preview_str}... - {issue_str}")
    
    # Count issues
    issues_count = sum(1 for count in categorized_files.keys() 
                     for _, has_issue, _, _ in categorized_files[count] if has_issue)
    
    print(f"\n=== SUMMARY ===")
    print(f"Total files analyzed: {len(txt_files)}")
    print(f"Files with bolding issues: {issues_count} ({(issues_count / len(txt_files)) * 100:.2f}%)")
    print(f"Files with correct bolding: {len(txt_files) - issues_count} ({((len(txt_files) - issues_count) / len(txt_files)) * 100:.2f}%)")

if __name__ == "__main__":
    main() 