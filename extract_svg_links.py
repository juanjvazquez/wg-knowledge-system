#!/usr/bin/env python3
import os
import re
import sys
import argparse
from collections import OrderedDict

def find_svg_elements(file_content):
    """Find all SVG elements in the content using regex"""
    # Pattern to match SVG elements - from opening <svg to closing </svg>
    svg_pattern = re.compile(r'<svg.*?</svg>', re.DOTALL)
    return svg_pattern.findall(file_content)

def extract_href_links(svg_content):
    """Extract all href and xlink:href attributes from the SVG content"""
    # Pattern to match href and xlink:href attributes
    href_pattern = re.compile(r'(?:xlink:)?href=["\'](.*?)["\']', re.DOTALL)
    return href_pattern.findall(svg_content)

def process_file(file_path):
    """Process a single file to extract SVG elements and href links"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        svg_elements = find_svg_elements(content)
        num_svg_elements = len(svg_elements)
        
        if num_svg_elements == 0:
            return num_svg_elements, []
        
        # If there's exactly one SVG element, extract unique href links
        if num_svg_elements == 1:
            href_links = extract_href_links(svg_elements[0])
            # Use OrderedDict to maintain order while removing duplicates
            unique_links = list(OrderedDict.fromkeys(href_links))
            return num_svg_elements, unique_links
        
        # If there are multiple SVG elements, just return the count
        return num_svg_elements, []
    
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return 0, []

def process_directory(input_dir):
    """Process all files in the directory and collect results"""
    results = {}
    anomalies = []
    
    for filename in os.listdir(input_dir):
        if not filename.endswith('.txt'):
            continue
        
        file_path = os.path.join(input_dir, filename)
        num_svg, href_links = process_file(file_path)
        
        if num_svg > 0:
            results[filename] = (num_svg, href_links)
            
            if num_svg > 1:
                anomalies.append(f"{filename}: {num_svg} SVG elements")
    
    return results, anomalies

def write_links_files(results, output_dir):
    """Write extracted links to files in the output directory"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for filename, (num_svg, links) in results.items():
        if num_svg == 1 and links:
            output_filename = f"links_{filename}"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for link in links:
                    f.write(f"{link}\n")
            
            print(f"Created {output_path} with {len(links)} unique links")

def update_readme(anomalies):
    """Update README.md with the anomalies section"""
    readme_path = "README.md"
    
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if ANOMALIES section already exists
        anomalies_section = "## ANOMALIES\n\n"
        if "## ANOMALIES" in content:
            # Replace existing ANOMALIES section
            pattern = re.compile(r'## ANOMALIES\n\n.*?(?=\n##|\Z)', re.DOTALL)
            updated_content = pattern.sub(anomalies_section, content)
        else:
            # Add ANOMALIES section at the end
            updated_content = content + "\n\n" + anomalies_section
        
        # Add anomalies to the section
        anomalies_text = "\n".join([f"- {anomaly}" for anomaly in anomalies])
        updated_content = updated_content.replace(anomalies_section, 
                                                 anomalies_section + anomalies_text + "\n")
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"Updated {readme_path} with anomalies section")
    else:
        print(f"Warning: {readme_path} not found, couldn't update anomalies")

def main():
    parser = argparse.ArgumentParser(description='Extract SVG links from files')
    parser.add_argument('--input', default='index_snapshot', 
                        help='Input directory containing files to process')
    parser.add_argument('--output', default='index_full_links', 
                        help='Output directory for extracted links')
    parser.add_argument('--file', help='Process a single file instead of the whole directory')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    
    # Process single file or entire directory
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File {args.file} not found")
            return
        
        filename = os.path.basename(args.file)
        print(f"Processing single file: {filename}")
        
        num_svg, href_links = process_file(args.file)
        
        if num_svg == 0:
            print(f"No SVG elements found in {filename}")
        elif num_svg == 1:
            output_filename = f"links_{filename}"
            output_path = os.path.join(args.output, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for link in href_links:
                    f.write(f"{link}\n")
            
            print(f"Created {output_path} with {len(href_links)} unique links")
        else:
            print(f"Anomaly detected: {filename} contains {num_svg} SVG elements")
    else:
        print(f"Processing all files in {args.input}")
        results, anomalies = process_directory(args.input)
        
        if results:
            write_links_files(results, args.output)
            
            if anomalies:
                print("\nAnomalies found:")
                for anomaly in anomalies:
                    print(f"- {anomaly}")
                
                update_readme(anomalies)
            else:
                print("\nNo anomalies found")
        else:
            print("No files with SVG elements found")

if __name__ == "__main__":
    main() 