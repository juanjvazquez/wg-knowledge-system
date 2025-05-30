#!/usr/bin/env python3
"""
Script to:
1. Clean up double-bolded text in files (e.g., ****text**** → **text**)
2. Bold the first set of characters until a space, newline, or "[" in .txt files that aren't already bolded
3. Skip files where the first set is longer than 20 characters
"""

import os
import glob
import re

def fix_double_bolding(input_file):
    """Fix files that have double-bolded text at the beginning."""
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Skip empty files
        if not content.strip():
            return False, content
        
        # Find the first non-empty line
        lines = content.split('\n')
        start_line_idx = 0
        while start_line_idx < len(lines) and not lines[start_line_idx].strip():
            start_line_idx += 1
            
        if start_line_idx >= len(lines):
            return False, content
            
        # Check if the line starts with double-bolding pattern (****text****)
        first_line = lines[start_line_idx]
        double_bold_pattern = r'^\*\*\*\*([^*]+)\*\*\*\*'
        match = re.match(double_bold_pattern, first_line)
        
        if match:
            # Fix double-bolded text
            text_to_bold = match.group(1)
            fixed_line = f"**{text_to_bold}**{first_line[len(match.group(0)):]}"
            lines[start_line_idx] = fixed_line
            new_content = '\n'.join(lines)
            print(f"Fixed double-bolding in: {input_file}")
            return True, new_content
        
        return False, content
        
    except Exception as e:
        print(f"Error checking double-bolding in {input_file}: {str(e)}")
        return False, None

def is_already_bolded(input_file):
    """Check if the first set of characters is already bolded."""
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Skip empty files
        if not content.strip():
            return True  # Skip empty files
            
        # Find the first non-empty line
        lines = content.split('\n')
        start_line_idx = 0
        while start_line_idx < len(lines) and not lines[start_line_idx].strip():
            start_line_idx += 1
            
        if start_line_idx >= len(lines):
            return True  # Skip files with no content
            
        # Check if the line already starts with bolding pattern (**text**)
        first_line = lines[start_line_idx]
        bold_pattern = r'^\*\*[^*]+\*\*'
        
        return bool(re.match(bold_pattern, first_line))
        
    except Exception as e:
        print(f"Error checking bolding in {input_file}: {str(e)}")
        return True  # Skip on error

def bold_first_word(input_file):
    """Bold the first set of characters until a space, newline, or "[" in a text file."""
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
        
        # Find the first "[" character (if any) within this line
        bracket_index = first_line.find('[')
        
        # Determine the end index for the first word
        # Initialize with a large value
        end_index = len(first_line)
        
        # Check each delimiter and update end_index if a delimiter is found and has a smaller index
        if space_index != -1 and space_index < end_index:
            end_index = space_index
            
        if newline_index != -1 and newline_index < end_index:
            end_index = newline_index
            
        if bracket_index != -1 and bracket_index < end_index:
            end_index = bracket_index
        
        # If the first word is too long, skip this file
        if end_index > 20:
            print(f"Skipping file (first word too long): {os.path.basename(input_file)}")
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
    fixed_count = 0
    skipped_count = 0
    processed_count = 0
    already_bolded_count = 0
    
    # First pass: Fix double-bolded files
    for txt_file in txt_files:
        fixed, new_content = fix_double_bolding(txt_file)
        if fixed and new_content:
            with open(txt_file, 'w', encoding='utf-8') as file:
                file.write(new_content)
            fixed_count += 1
    
    print(f"Fixed {fixed_count} files with double-bolding")
    
    # Second pass: Bold files that aren't already bolded
    for txt_file in txt_files:
        try:
            # Skip files that are already bolded
            if is_already_bolded(txt_file):
                already_bolded_count += 1
                continue
                
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
                
                # Find the first space
                space_index = first_line.find(' ')
                
                # Find the first newline (if any) within this line
                newline_index = first_line.find('\n')
                
                # Find the first "[" character (if any) within this line
                bracket_index = first_line.find('[')
                
                # Determine the end index for the first word
                # Initialize with a large value
                end_index = len(first_line)
                
                # Check each delimiter and update end_index if a delimiter is found and has a smaller index
                if space_index != -1 and space_index < end_index:
                    end_index = space_index
                    
                if newline_index != -1 and newline_index < end_index:
                    end_index = newline_index
                    
                if bracket_index != -1 and bracket_index < end_index:
                    end_index = bracket_index
                
                # Check if first word is too long
                if end_index > 20:
                    print(f"Skipping file (first word too long): {os.path.basename(txt_file)}")
                    skipped_count += 1
                    continue
            
            # Bold the first word
            bold_first_word(txt_file)
            processed_count += 1
            
        except Exception as e:
            print(f"Error with file {txt_file}: {str(e)}")
            skipped_count += 1
    
    print(f"Processing complete.")
    print(f"- Fixed double-bolded files: {fixed_count}")
    print(f"- Already bolded (skipped): {already_bolded_count}")
    print(f"- Newly bolded files: {processed_count}")
    print(f"- Skipped files (empty or too long): {skipped_count}")

if __name__ == "__main__":
    main() 