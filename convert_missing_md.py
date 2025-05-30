#!/usr/bin/env python3
"""
Script to convert missing JSON files to Markdown:
1. Reads missing_mds.txt to get the IDs of missing Markdown files
2. Extracts the "transcription.html" element from the corresponding JSON files
3. Converts it to markdown in the best way possible
4. Writes this to the index_full_mds folder with the same filename but as a txt

Usage:
    python convert_missing_md.py
"""

import os
import json
import html2text
import re
from tqdm import tqdm
from bs4 import BeautifulSoup
from pathlib import Path


def create_dir_if_not_exists(dir_path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Created directory: {dir_path}")


def clean_html(html_content):
    """
    Clean HTML content before conversion to Markdown.
    Uses a more robust approach to handle malformed HTML.
    """
    try:
        # Parse HTML with BeautifulSoup to handle malformed HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Handle specific elements in a better way for Markdown conversion
        
        # Process tables if needed
        tables = soup.find_all('table')
        for table in tables:
            # Tables are challenging to convert to Markdown
            # For now, we'll just make sure they're structured correctly
            pass
        
        # Process underlines more safely - find them but don't modify yet
        underlines = soup.find_all(['span'], class_=re.compile('underline'))
        for underline in underlines:
            # Create a new string with the formatting
            formatted_text = f"__{underline.get_text()}__"
            # Replace the element with a new text node
            new_tag = soup.new_string(formatted_text)
            underline.replace_with(new_tag)
        
        # Handle links better - find them but don't modify directly
        links = soup.find_all('a')
        for link in links:
            href = link.get('href', '')
            # Convert internal links to a reference format
            if href and href.startswith('/bestand'):
                link['href'] = f"https://niklas-luhmann-archiv.de{href}"
        
        return str(soup)
    except Exception as e:
        # If BeautifulSoup fails, try a simpler approach
        print(f"BeautifulSoup failed: {e}. Using fallback approach.")
        
        # Simple regex-based fallback for underlines
        html_content = re.sub(r'<span class="underline[^"]*">([^<]+)</span>', r'__\1__', html_content)
        
        # Simple regex-based fallback for internal links
        html_content = re.sub(r'href="(/bestand[^"]+)"', r'href="https://niklas-luhmann-archiv.de\1"', html_content)
        
        return html_content


def convert_html_to_markdown(html_content):
    """Convert HTML to Markdown with custom handling."""
    try:
        # Clean HTML before conversion
        cleaned_html = clean_html(html_content)
        
        # Configure html2text
        h2t = html2text.HTML2Text()
        h2t.body_width = 0  # Don't wrap lines
        h2t.ignore_links = False
        h2t.ignore_images = True
        h2t.ignore_tables = False
        h2t.unicode_snob = True  # Use Unicode instead of ASCII
        h2t.mark_code = False
        h2t.protect_links = False  # Don't protect links with <>
        h2t.single_line_break = False  # Use two line breaks for new paragraphs
        
        # Convert to markdown
        markdown = h2t.handle(cleaned_html)
        
        # Post-process markdown
        markdown = markdown.strip()
        
        # Fix double spaces and excessive newlines
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        
        return markdown
    except Exception as e:
        # If HTML to Markdown conversion fails, return a simple error message with the original HTML
        print(f"HTML to Markdown conversion failed: {e}. Using fallback approach.")
        return f"# Conversion Error\n\nThere was an error converting this HTML to Markdown.\n\n```html\n{html_content}\n```"


def process_json_file(json_file_path):
    """Extract HTML content from JSON and convert to Markdown."""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if the required field exists
        if 'transcription' in data and 'html' in data['transcription'] and data['transcription']['readyForPublication']:
            html_content = data['transcription']['html']
            
            # Convert HTML to Markdown
            markdown_content = convert_html_to_markdown(html_content)
            
            return markdown_content
        else:
            print(f"Warning: Missing required fields in {json_file_path}")
            return None
    except Exception as e:
        print(f"Error processing {json_file_path}: {e}")
        return None


def read_missing_ids(missing_file):
    """Read missing IDs from the specified file."""
    if not os.path.exists(missing_file):
        print(f"Error: Missing file {missing_file} does not exist.")
        return []
    
    with open(missing_file, 'r', encoding='utf-8') as file:
        ids = [line.strip() for line in file if line.strip()]
    
    return ids


def direct_html_to_md(html_content):
    """
    Direct conversion from HTML to Markdown using regex patterns.
    This is a fallback method when the normal conversion process fails.
    """
    # Replace common HTML elements with Markdown equivalents
    md_content = html_content
    
    # Remove <div> tags
    md_content = re.sub(r'<div[^>]*>', '', md_content)
    md_content = re.sub(r'</div>', '', md_content)
    
    # Convert paragraphs
    md_content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', md_content, flags=re.DOTALL)
    
    # Convert spans with underline class to bold
    md_content = re.sub(r'<span class="underline[^"]*">(.*?)</span>', r'**\1**', md_content, flags=re.DOTALL)
    
    # Convert other spans
    md_content = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', md_content, flags=re.DOTALL)
    
    # Convert links
    md_content = re.sub(r'<a href="([^"]+)"[^>]*>(.*?)</a>', r'[\2](\1)', md_content, flags=re.DOTALL)
    
    # Convert tables (simplistic approach - tables are hard to convert with regex)
    md_content = re.sub(r'<table[^>]*>(.*?)</table>', r'\1', md_content, flags=re.DOTALL)
    md_content = re.sub(r'<tr[^>]*>(.*?)</tr>', r'\1\n', md_content, flags=re.DOTALL)
    md_content = re.sub(r'<td[^>]*>(.*?)</td>', r'\1 | ', md_content, flags=re.DOTALL)
    
    # Clean up extra whitespace
    md_content = re.sub(r'\n{3,}', '\n\n', md_content)
    md_content = re.sub(r' {2,}', ' ', md_content)
    
    return md_content.strip()


def main():
    # Define directories and files
    missing_file = "missing_mds.txt"
    json_dir = "index_full_jsons"
    md_dir = "index_full_mds"
    
    # Create target directory if it doesn't exist
    create_dir_if_not_exists(md_dir)
    
    # Read missing IDs
    missing_ids = read_missing_ids(missing_file)
    
    if not missing_ids:
        print("No missing Markdown files found in missing_mds.txt.")
        return
    
    print(f"Found {len(missing_ids)} missing Markdown files.")
    
    # Process each missing ID
    successful_count = 0
    failed_count = 0
    
    for file_id in tqdm(missing_ids, desc="Converting files"):
        json_file_path = os.path.join(json_dir, f"{file_id}.json")
        md_file_path = os.path.join(md_dir, f"{file_id}.txt")
        
        # Check if JSON file exists
        if not os.path.exists(json_file_path):
            print(f"Warning: JSON file does not exist: {json_file_path}")
            failed_count += 1
            continue
        
        try:
            # Process JSON file
            markdown_content = process_json_file(json_file_path)
            
            if markdown_content:
                # Save Markdown content to file
                with open(md_file_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                successful_count += 1
            else:
                # Try the fallback approach for problematic files
                try:
                    with open(json_file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if 'transcription' in data and 'html' in data['transcription']:
                        html_content = data['transcription']['html']
                        # Use the direct conversion method
                        markdown_content = direct_html_to_md(html_content)
                        
                        with open(md_file_path, 'w', encoding='utf-8') as f:
                            f.write(markdown_content)
                        successful_count += 1
                        print(f"Successfully used fallback conversion for {file_id}")
                    else:
                        failed_count += 1
                except Exception as e:
                    print(f"Error in fallback processing {json_file_path}: {e}")
                    failed_count += 1
        except Exception as e:
            print(f"Unexpected error processing {json_file_path}: {e}")
            failed_count += 1
    
    print(f"Conversion complete: {successful_count} successful, {failed_count} failed")
    print(f"Markdown files saved to: {md_dir}")


if __name__ == "__main__":
    main() 