#!/usr/bin/env python
"""
Script to download HTML content from each "ZK_1" link in parent_links.txt
and save it to a separate text file in the index_snapshot folder.
Uses Selenium to properly render JavaScript content.
"""

import os
import time
from urllib.parse import urlparse
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def ensure_directory_exists(directory):
    """Ensure the specified directory exists, if not create it."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")
    else:
        print(f"Directory already exists: {directory}")

def read_links_from_file(filename):
    """Read links from the specified file."""
    with open(filename, 'r', encoding='utf-8') as file:
        links = [line.strip() for line in file if line.strip()]
    return links

def filter_links(links, pattern):
    """Filter links that contain the specified pattern."""
    return [link for link in links if pattern in link]

def get_filename_from_url(url):
    """Extract the filename from the URL, handling hash fragments."""
    # Parse the URL to get the fragment (part after #)
    parsed_url = urlparse(url)
    fragment = parsed_url.fragment
    
    # If there's a fragment, use it as the filename
    if fragment:
        return f"{fragment}.txt"
    
    # Fallback: use the last part of the path
    path = parsed_url.path
    filename = os.path.basename(path)
    return f"{filename}.txt"

def download_content_selenium(url, save_path, driver):
    """Download content from URL using Selenium and save it to the specified path."""
    try:
        driver.get(url)
        
        # Wait for the base page to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Wait for TOC list to be populated (which indicates the JavaScript has run)
        WebDriverWait(driver, 30).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "#toc_list li")) > 0 or 
                      "Loading failed" in d.page_source
        )
        
        # Wait additional time for visualization to render
        time.sleep(5)
        
        # Check if the content area has been populated
        content_div = driver.find_element(By.ID, "content")
        if content_div:
            # Wait for SVG elements that indicate the graph visualization has loaded
            svg_elements = driver.find_elements(By.TAG_NAME, "svg")
            if not svg_elements:
                # If no SVG elements found, wait a bit longer
                time.sleep(5)
        
        # Get the rendered HTML
        page_source = driver.page_source
        
        # Also capture any console output that might indicate errors
        logs = driver.get_log('browser')
        console_output = "\n".join([f"CONSOLE: {log['level']} - {log['message']}" for log in logs])
        
        # Write page source and any console logs to the file
        with open(save_path, 'w', encoding='utf-8') as file:
            file.write(page_source)
            if console_output:
                file.write("\n\n<!-- CONSOLE LOGS -->\n")
                file.write(console_output)
        
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def main():
    input_file = "parent_links.txt"
    output_dir = "index_snapshot"
    filter_pattern = "ZK_1"
    
    # Ensure output directory exists
    ensure_directory_exists(output_dir)
    
    # Read links from parent_links.txt
    print(f"Reading links from {input_file}...")
    links = read_links_from_file(input_file)
    print(f"Found {len(links)} links in total.")
    
    # Filter links containing "ZK_1"
    zk1_links = filter_links(links, filter_pattern)
    print(f"Found {len(zk1_links)} links containing '{filter_pattern}'.")
    
    # Set up Selenium WebDriver
    print("Setting up Chrome WebDriver...")
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    # Enable logging
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--v=1')
    # Add window size to ensure all elements are rendered
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Additional preferences for performance
    chrome_options.add_experimental_option('prefs', {
        'profile.default_content_setting_values': {
            'images': 2,  # Don't load images for faster loading
            'javascript': 1,  # 1 = Allow JavaScript
        }
    })
    
    try:
        # Use webdriver-manager to automatically download the appropriate ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(60)  # Increase timeout for slower pages
        
        # Download content from each link and save to a text file
        success_count = 0
        
        print(f"Downloading content from {len(zk1_links)} links...")
        for link in tqdm(zk1_links, desc="Downloading"):
            filename = get_filename_from_url(link)
            save_path = os.path.join(output_dir, filename)
            
            if download_content_selenium(link, save_path, driver):
                success_count += 1
            
            # Add a small delay to avoid overwhelming the server
            time.sleep(2)
        
        print(f"Downloaded {success_count} out of {len(zk1_links)} files.")
        print(f"Files are saved in the '{output_dir}' directory.")
    
    finally:
        # Make sure to close the driver
        if 'driver' in locals():
            driver.quit()
            print("WebDriver closed.")

if __name__ == "__main__":
    main() 