#!/usr/bin/env python3
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
    """Clean HTML content before conversion to Markdown."""
    # Parse HTML with BeautifulSoup to handle malformed HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Handle specific elements in a better way for Markdown conversion
    
    # Convert <table> to a more markdown-friendly format if needed
    tables = soup.find_all('table')
    for table in tables:
        # Keep table structure but make it more consistent
        # This is optional based on how complex your tables are
        pass
    
    # Convert underlines to markdown format
    underlines = soup.find_all(['span'], class_=re.compile('underline'))
    for underline in underlines:
        underline.string = f"__{underline.text}__" if underline.string else f"__{underline.text}__"
        underline.unwrap()
    
    # Handle links better
    links = soup.find_all('a')
    for link in links:
        href = link.get('href', '')
        # Convert internal links to a reference format
        if href.startswith('/bestand'):
            link['href'] = f"https://niklas-luhmann-archiv.de{href}"
    
    return str(soup)

def convert_html_to_markdown(html_content):
    """Convert HTML to Markdown with custom handling."""
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

def main():
    # Define directories
    master_index_file = "master_index.txt"
    json_dir = "index_full_jsons"
    md_dir = "index_full_mds"
    
    # Create target directory if it doesn't exist
    create_dir_if_not_exists(md_dir)
    
    # Read master index file
    with open(master_index_file, 'r', encoding='utf-8') as f:
        file_urls = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(file_urls)} URLs in master index")
    
    # Process each file in order
    successful_count = 0
    failed_count = 0
    
    for url in tqdm(file_urls, desc="Converting files"):
        # Extract ID from URL
        # Example URL: https://niklas-luhmann-archiv.de/bestand/zettelkasten/zettel/ZK_1_NB_1_1_V
        match = re.search(r'zettel/([^/]+)$', url)
        if not match:
            print(f"Warning: Could not extract ID from URL: {url}")
            failed_count += 1
            continue
        
        file_id = match.group(1)
        json_file_path = os.path.join(json_dir, f"{file_id}.json")
        md_file_path = os.path.join(md_dir, f"{file_id}.txt")
        
        # Check if JSON file exists
        if not os.path.exists(json_file_path):
            print(f"Warning: JSON file does not exist: {json_file_path}")
            failed_count += 1
            continue
        
        # Process JSON file
        markdown_content = process_json_file(json_file_path)
        
        if markdown_content:
            # Save Markdown content to file
            with open(md_file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            successful_count += 1
        else:
            failed_count += 1
    
    print(f"Conversion complete: {successful_count} successful, {failed_count} failed")
    print(f"Markdown files saved to: {md_dir}")

if __name__ == "__main__":
    main() 