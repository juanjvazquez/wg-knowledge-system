#!/usr/bin/env python
"""
Script to extract links from index.txt and save them to parent_links.txt
Each <li> element with an <a href> tag will have its href value extracted,
combined with the base URL, and written to parent_links.txt
"""

import re
from html.parser import HTMLParser
from typing import List

# Base URL to prepend to each href value
BASE_URL = "https://assets.niklas-luhmann-archiv.de/branchview"

class LinkExtractor(HTMLParser):
    """HTML Parser to extract href values from <a> tags within <li> elements"""
    
    def __init__(self):
        super().__init__()
        self.links = []
        self.in_li = False
        
    def handle_starttag(self, tag, attrs):
        if tag == 'li':
            self.in_li = True
        
        if self.in_li and tag == 'a':
            for attr in attrs:
                if attr[0] == 'href':
                    href = attr[1]
                    self.links.append(href)  # Keep the href as is, including the #
    
    def handle_endtag(self, tag):
        if tag == 'li':
            self.in_li = False

def extract_links_from_file(filename: str) -> List[str]:
    """Extract all href values from <a> tags within <li> elements in the file"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
        
        parser = LinkExtractor()
        parser.feed(content)
        
        return parser.links
    except Exception as e:
        print(f"Error reading or parsing file: {e}")
        return []

def save_links_to_file(links: List[str], output_filename: str):
    """Save the complete URLs to the output file"""
    try:
        with open(output_filename, 'w', encoding='utf-8') as file:
            for link in links:
                full_url = BASE_URL + link  # The URL will now include the hash symbol
                file.write(f"{full_url}\n")
        
        print(f"Successfully saved {len(links)} links to {output_filename}")
    except Exception as e:
        print(f"Error writing to file: {e}")

def main():
    input_file = "index.txt"
    output_file = "parent_links.txt"
    
    print(f"Extracting links from {input_file}...")
    links = extract_links_from_file(input_file)
    
    if links:
        print(f"Found {len(links)} links.")
        save_links_to_file(links, output_file)
    else:
        print("No links were found.")

if __name__ == "__main__":
    main() 