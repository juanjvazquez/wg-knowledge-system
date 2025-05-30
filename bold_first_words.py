#!/usr/bin/env python3
"""
Script to bold the first set of characters until a space or newline in all .txt files
in the index_full_mds directory. Skips files where the first set is longer 
than 12 characters.
"""

import os
import glob

def bold_first_word(input_file):
    """Bold the first set of characters until a space or newline in a text file."""
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Skip empty files
        if not content.strip():
            print(f"Skipping empty file: {input_file}")
            return
            
        # Find the first non-empty line
        lines = content.split('\n')
        start_line_idx = 0
        while start_line_idx < len(lines) and not lines[start_line_idx].strip():
            start_line_idx += 1
            
        if start_line_idx >= len(lines):
            print(f"No content in file: {input_file}")
            return
            
        first_line = lines[start_line_idx]
        
        # Find the first space
        space_index = first_line.find(' ')
        
        # Find the first newline (if any) within this line
        newline_index = first_line.find('\n')
        
        # Determine the end index for the first word
        # If both space and newline exist, take the minimum (first occurrence)
        # If only one exists, take that one
        # If neither exists, take the whole line
        if space_index != -1 and newline_index != -1:
            end_index = min(space_index, newline_index)
        elif space_index != -1:
            end_index = space_index
        elif newline_index != -1:
            end_index = newline_index
        else:
            end_index = len(first_line)
        
        # If the first word is too long, skip this file
        if end_index > 12:
            print(f"Skipping file (first word too long): {input_file}")
            return
            
        # Apply the bolding: wrap the first word in **
        first_word = first_line[:end_index]
        new_first_line = f"**{first_word}**{first_line[end_index:]}"
        
        # Replace the line in the content
        lines[start_line_idx] = new_first_line
        new_content = '\n'.join(lines)
        
        # Write the updated content back to the file
        with open(input_file, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
    except Exception as e:
        print(f"Error processing {input_file}: {str(e)}")

def main():
    # Define the directory containing the text files
    directory = "index_full_mds"
    
    # Get all .txt files in the directory
    txt_files = glob.glob(os.path.join(directory, "*.txt"))
    
    print(f"Found {len(txt_files)} .txt files in {directory}")
    
    # Process each file
    skipped_count = 0
    processed_count = 0
    
    for txt_file in txt_files:
        try:
            # Get the first line to check if it needs to be skipped
            with open(txt_file, 'r', encoding='utf-8') as file:
                # Skip empty files
                content = file.read().strip()
                if not content:
                    print(f"Skipping empty file: {txt_file}")
                    skipped_count += 1
                    continue
                
                # Get the first non-empty line
                lines = content.split('\n')
                start_line_idx = 0
                while start_line_idx < len(lines) and not lines[start_line_idx].strip():
                    start_line_idx += 1
                
                if start_line_idx >= len(lines):
                    print(f"No content in file: {txt_file}")
                    skipped_count += 1
                    continue
                
                first_line = lines[start_line_idx]
                
                # Check for space and newline to determine end of first word
                space_index = first_line.find(' ')
                newline_index = first_line.find('\n')
                
                # Determine the end index for the first word
                if space_index != -1 and newline_index != -1:
                    end_index = min(space_index, newline_index)
                elif space_index != -1:
                    end_index = space_index
                elif newline_index != -1:
                    end_index = newline_index
                else:
                    end_index = len(first_line)
                
                # Check if first word is too long
                if end_index > 12:
                    print(f"Skipping file (first word too long): {os.path.basename(txt_file)}")
                    skipped_count += 1
                    continue
            
            # Bold the first word
            bold_first_word(txt_file)
            processed_count += 1
            
        except Exception as e:
            print(f"Error with file {txt_file}: {str(e)}")
            skipped_count += 1
    
    print(f"Processing complete. Processed: {processed_count}, Skipped: {skipped_count}")

if __name__ == "__main__":
    main() 