# wg-knowledge-system

#### things to open
- To check e.g. note `ZK_1_NB_1-1b_V` use the link `https://niklas-luhmann-archiv.de/bestand/zettelkasten/zettel/ZK_1_NB_1-1b_V`.
- This map shows the full index of notes `https://assets.niklas-luhmann-archiv.de/branchview/#ZK_1_NB_1_1_V`.

TLDR: Putting the entire knowledge system from [Niklas Luhmann](https://niklas-luhmann-archiv.de/bestand/zettelkasten/inhaltsuebersicht) into Mardown.

# CODE STRUCTURE

- `index.txt`: Contains the HTML structure with links to different sections of the Niklas Luhmann archive
- `extract_links.py`: Python script that extracts links from the index.txt file and saves them to parent_links.txt
- `parent_links.txt`: Generated file containing the complete URLs for each link in the index.txt file
- `download_snapshots.py`: Python script that downloads HTML content from each "ZK_1" link in parent_links.txt using Selenium to properly render JavaScript content, and saves it to a separate text file in the index_snapshot folder
- `extract_svg_links.py`: Python script that analyzes SVG elements in the index_snapshot files, extracts unique href links, and outputs them to the index_full_links folder
- `reorder_links.py`: Python script that reorders the links in each file in the index_full_links directory according to a custom sorting algorithm and saves the results to index_full_links_reord
- `download_jsons.py`: Python script that downloads JSON data for each Zettelkasten link in the index_full_links_reord folder, extracting the ID from each link, constructing an API URL, and saving the JSON response
- `download_jsons_concurrent.py`: Improved version that uses concurrent workers to speed up JSON downloads and only downloads missing files based on master_index.txt or missing_jsons.txt
- `download_jsons_from_txt_ids.py`: Python script that downloads JSON data specifically for the IDs listed in missing_specific_ids.txt file, skipping files that already exist and saving the JSON responses to the index_full_jsons folder
- `check_progress.py`: Python script that generates a master index file of all unique links and checks download progress of JSON files
- `convert_html_to_md.py`: Python script that extracts the "transcription.html" element from JSON files, converts it to markdown, and saves the result to a new folder index_full_mds
- `check_md_progress.py`: Python script that checks the progress of HTML to Markdown conversion, identifies missing files, and creates a missing_mds.txt file
- `check_missing_mds.py`: Python script that checks which files from master_index.txt are missing in the index_full_mds directory and outputs the results to missing_mds.txt
- `check_duplicate_links.py`: Python script that checks for duplicate IDs (last parts of links like "ZK_1_NB_108-6_V") in the master_index.txt file and outputs any duplicates found to duplicate_ids.txt
- `check_unique_mds_ids.py`: Python script that checks for unique IDs in the index_full_mds folder by analyzing filenames and outputs any duplicates found to duplicate_md_ids.txt
- `extract_qa_ids.py`: Python script that extracts IDs from both index_full_mds directory and master_index.txt file, writing them to qa_mds_ids.txt and qa_master_ids.txt for further QA analysis
- `find_missing_ids.py`: Python script that identifies specific IDs that are in master_index.txt but not in the index_full_mds directory and writes them to missing_specific_ids.txt
- `process_missing_specific_ids.py`: Python script that downloads JSON files for IDs in missing_specific_ids.txt and converts them to Markdown files, completing the collection
- `verify_missing_ids.py`: Python script that directly verifies if the files for the previously missing IDs now exist in the index_full_mds directory
- `convert_missing_md.py`: Python script that processes only the missing Markdown files listed in missing_mds.txt
- `bold_first_words.py`: Python script that processes all .txt files in index_full_mds directory, making the first set of characters (until a space or newline is found) bold by wrapping them in ** markers, while skipping files where the first set is longer than 20 characters
- `cleanup_and_bold_first_words.py`: Enhanced script that first fixes double-bolded text, skips files that are already properly bolded, and applies bolding to remaining files according to the same rules as bold_first_words.py
- `check_bolding_quality.py`: Quality assurance script that analyzes all files in index_full_mds to check how many asterisks they start with, reporting statistics and identifying files that don't start with exactly "**" for proper markdown bolding
- `master_index.txt`: Generated file containing all unique Zettelkasten links compiled from all files in index_full_links_reord
- `missing_jsons.txt`: Generated file containing IDs of missing JSON files that need to be downloaded
- `missing_mds.txt`: Generated file containing IDs of missing Markdown files that need to be converted
- `duplicate_ids.txt`: Generated file containing duplicate IDs found in master_index.txt, if any
- `duplicate_md_ids.txt`: Generated file containing duplicate IDs found in the index_full_mds folder, if any
- `qa_mds_ids.txt`: Generated file containing all unique IDs from the index_full_mds directory
- `qa_master_ids.txt`: Generated file containing all IDs from the master_index.txt file
- `missing_specific_ids.txt`: Generated file containing the specific IDs that are in master_index.txt but missing from index_full_mds
- `failed_specific_downloads.txt`: Generated file containing IDs from missing_specific_ids.txt that failed to download
- `failed_specific_conversions.txt`: Generated file containing IDs from missing_specific_ids.txt that failed to convert to Markdown
- `failed_downloads.txt`: Generated file containing IDs of JSON files that failed to download
- `index_snapshot/`: Directory containing the downloaded HTML content of each "ZK_1" link as text files
- `index_full_links/`: Directory containing text files with extracted href links from SVG elements in the index_snapshot files
- `index_full_links_reord/`: Directory containing the same links as index_full_links but sorted in a custom order based on the Luhmann numbering system
- `index_full_jsons/`: Directory containing JSON files downloaded from the API for each Zettelkasten link, with each file named after its corresponding ID
- `index_full_mds/`: Directory containing markdown text files converted from the transcription HTML content in the JSON files
- `requirements.txt`: Contains all the Python dependencies required to run the scripts

# CHANGES LOG

- 2023-04-09: Added `extract_links.py` script to extract links from index.txt and save them to parent_links.txt
- 2023-04-09: Added `download_snapshots.py` script to download HTML content from "ZK_1" links and save them as text files
- 2023-04-15: Updated `download_snapshots.py` to use Selenium for better content extraction, properly rendering JavaScript-dependent content
- 2023-04-15: Added `requirements.txt` file with all necessary dependencies
- 2023-04-15: Enhanced Selenium implementation in `download_snapshots.py` with advanced waiting strategies, browser console logging, and optimized rendering settings
- 2023-04-16: Added `extract_svg_links.py` script to analyze SVG elements in index_snapshot files, extract unique href links, and identify files with multiple SVG elements as anomalies
- 2023-04-17: Added `reorder_links.py` script to reorder the links in each file following a custom sorting algorithm based on the Luhmann numbering system, creating an index_full_links_reord directory with properly ordered links
- 2023-04-18: Added `download_jsons.py` script to download JSON data for each Zettelkasten link in the index_full_links_reord folder, creating an index_full_jsons directory with JSON files named after their corresponding IDs
- 2023-04-19: Added `check_progress.py` script to generate a master index file of all unique links and check download progress of JSON files, creating master_index.txt and missing_jsons.txt files
- 2023-04-20: Added `download_jsons_concurrent.py` script for faster JSON downloads using concurrent workers, with features to only download missing files based on master_index.txt or missing_jsons.txt
- 2023-04-25: Added `convert_html_to_md.py` script to extract the "transcription.html" element from JSON files, convert it to markdown, and save the result to a new folder index_full_mds
- 2023-04-26: Added `check_md_progress.py` script to check the progress of HTML to Markdown conversion, identify missing files, and create a missing_mds.txt file
- 2023-04-26: Added `convert_missing_md.py` script to process only the missing Markdown files listed in missing_mds.txt
- 2023-08-11: Added `bold_first_words.py` script to make the first set of characters (until a space or newline is found) bold in each .txt file in index_full_mds directory by wrapping them in ** markers, skipping files where the first set is longer than 20 characters
- 2023-08-12: Added `cleanup_and_bold_first_words.py` script that improves upon bold_first_words.py by first fixing double-bolded text (****text**** → **text**), skipping files that are already properly bolded, and applying bolding to remaining files according to the same rules
- 2023-08-12: Updated `cleanup_and_bold_first_words.py` to increase the character limit from 12 to 20 characters
- 2023-08-12: Enhanced `cleanup_and_bold_first_words.py` to also consider "[" as a delimiter for stopping bolding, in addition to spaces and newlines
- 2023-08-12: Added `check_bolding_quality.py` script to analyze bolding quality across all files, providing statistics on how many asterisks each file starts with and identifying files without proper markdown bolding
- 2023-08-13: Added `check_missing_mds.py` script to check which files from master_index.txt are missing in the index_full_mds directory and output the results to missing_mds.txt
- 2023-08-13: Added `check_duplicate_links.py` script to identify any duplicate IDs (last parts of links) in master_index.txt and output them to duplicate_ids.txt
- 2023-08-13: Added `check_unique_mds_ids.py` script to check for unique IDs in the index_full_mds folder by analyzing filenames and output any duplicate IDs to duplicate_md_ids.txt
- 2023-08-13: Added `extract_qa_ids.py` script to extract IDs from both index_full_mds directory and master_index.txt file, writing them to separate files for QA analysis
- 2023-08-13: Added `find_missing_ids.py` script to identify the specific IDs that are in master_index.txt but not in the index_full_mds directory
- 2023-08-13: Added `process_missing_specific_ids.py` script to download JSON files for IDs in missing_specific_ids.txt and convert them to Markdown files
- 2023-08-13: Added `verify_missing_ids.py` script to directly check if the files for the previously missing IDs now exist in the index_full_mds directory
- 2023-08-14: Added `download_jsons_from_txt_ids.py` script to download JSON data specifically for the IDs listed in missing_specific_ids.txt file, providing a more targeted approach than the original download_jsons.py script

# CURRENT CAPABILITIES OF THE SYSTEM

- Extract links from the index.txt file containing HTML structure
- Generate a parent_links.txt file with complete URLs to access different sections of the Niklas Luhmann archive
- Download HTML content from all "ZK_1" links using Selenium WebDriver to ensure proper JavaScript rendering
- Capture dynamically generated content by waiting for specific elements to appear (TOC list, SVG visualizations)
- Save console logs along with the HTML content to help debug any issues with page rendering
- Save dynamically rendered content as individual text files in the index_snapshot folder
- Each text file is named after the corresponding entry ID (e.g., "ZK_1_NB_1_1_V.txt")
- Analyze SVG elements in the downloaded files and extract unique href links
- Identify anomalies where files contain multiple SVG elements
- Create a structured directory of extracted links in the index_full_links folder
- Reorder the links in each file according to a custom sorting algorithm based on the Luhmann numbering system, following these rules:
  - Numbers (e.g., 1, 2, 3) sort before lowercase letters (e.g., a, b, c), which sort before uppercase letters (e.g., A, B, C)
  - Sort links hierarchically based on the parsed structure of the Luhmann IDs (e.g., "1-5A1c3")
- Download JSON data for each Zettelkasten link by:
  - Extracting the ID from the URL (e.g., "ZK_1_NB_1-1aa_V" from "https://niklas-luhmann-archiv.de/bestand/zettelkasten/zettel/ZK_1_NB_1-1aa_V")
  - Constructing an API URL (e.g., "https://v0.api.niklas-luhmann-archiv.de/ZK/zettel/ZK_1_NB_1-1aa_V")
  - Downloading and saving the JSON response to a file named after the ID in the index_full_jsons directory
  - Supporting processing of either a single file or all files in the index_full_links_reord directory
- Track download progress by:
  - Generating a master index file containing all unique links from all files in index_full_links_reord
  - Checking how many JSON files exist in index_full_jsons compared to the total unique links
  - Providing completion statistics and a list of missing JSON files
  - Creating a missing_jsons.txt file with IDs of JSON files that need to be downloaded
- Speed up JSON downloads using concurrent workers:
  - Download multiple JSON files simultaneously using ThreadPoolExecutor
  - Only download missing files identified by master_index.txt or missing_jsons.txt
  - Track overall download progress with a single progress bar
  - Handle failures gracefully and save failed download IDs to a file for retry
- Convert JSON files to Markdown by:
  - Using the order specified in master_index.txt
  - Extracting the "transcription.html" element from JSON files
  - Properly converting HTML to Markdown with special handling for tables, links, and formatting
  - Saving the result as text files in the index_full_mds directory
  - Preserving the original file names to maintain the same ID system
- Track Markdown conversion progress by:
  - Checking how many Markdown files exist compared to the total unique links
  - Identifying which files are missing (differentiating between missing JSON files and missing Markdown files)
  - Creating a missing_mds.txt file with IDs of Markdown files that need to be converted
  - Providing completion statistics for the HTML to Markdown conversion process
- Process only missing Markdown files by:
  - Reading the missing_mds.txt file
  - Converting only the missing files to avoid redundant processing
  - Maintaining the same conversion quality and formatting as the main conversion script
- Format Markdown files by:
  - Making the first set of characters (until a space, newline, or "[" character is found) bold in all Markdown files in index_full_mds
  - Skipping files where the first set is longer than 20 characters
  - Reporting only skipped files and overall statistics for monitoring progress
  - Intelligently handling files that are already bolded and fixing double-bolded text
  - Providing detailed statistics on processing operations (fixed, skipped, processed files)
- Quality assurance for Markdown bolding:
  - Analyzing all files to count how many asterisks they start with
  - Identifying files that don't have the correct pattern of two asterisks at the beginning
  - Generating comprehensive statistics on bolding quality
  - Producing a list of problematic files for targeted fixes
- Quality assurance for missing Markdown files:
  - Checking which files from master_index.txt are missing in the index_full_mds directory
  - Writing the list of missing file IDs to missing_mds.txt
  - Providing completion statistics to track conversion progress
  - Enabling targeted conversion of only the missing files
- Quality assurance for master_index.txt:
  - Checking for duplicate IDs (like "ZK_1_NB_108-6_V") in the master index file
  - Identifying and counting occurrences of duplicate card identifiers
  - Generating statistics about the uniqueness of the Zettelkasten card references
  - Outputting detailed information about duplicates to duplicate_ids.txt
- Quality assurance for markdown file integrity:
  - Scanning all files in the index_full_mds directory to check for duplicate IDs in filenames
  - Ensuring each markdown file represents a unique Zettelkasten card
  - Providing statistics about the uniqueness of the markdown files
  - Writing any duplicate filename IDs to duplicate_md_ids.txt for investigation
- Quality assurance data extraction for further analysis:
  - Extracting all IDs from filenames in the index_full_mds directory
  - Extracting all IDs from links in the master_index.txt file
  - Writing sorted lists of IDs to separate files for further QA operations
  - Providing comparison statistics between the two sources
- Quality assurance for identifying specific missing files:
  - Reading IDs from previously generated QA files
  - Identifying precisely which IDs are in master_index.txt but missing from index_full_mds
  - Writing detailed list of missing specific IDs to missing_specific_ids.txt
  - Providing comprehensive statistics about the missing IDs
- Process missing specific IDs to complete the collection:
  - Reading specific IDs from missing_specific_ids.txt
  - Downloading JSON files for these IDs using concurrent workers
  - Converting the downloaded JSON files to Markdown format
  - Saving detailed statistics and tracking any failures
  - Writing lists of failed downloads or conversions for further investigation
- Verify the existence of previously missing files:
  - Directly checking if files for previously identified missing IDs now exist
  - Providing comprehensive verification statistics
  - Identifying any files that still need to be processed

# TESTS

No formal tests have been implemented yet. Basic functionality can be tested by running:
```
pip install -r requirements.txt
python extract_links.py
python download_snapshots.py
python extract_svg_links.py
python reorder_links.py
python check_progress.py
python download_jsons_concurrent.py
python convert_html_to_md.py
python check_md_progress.py
python convert_missing_md.py
python cleanup_and_bold_first_words.py
python check_bolding_quality.py
python check_missing_mds.py
python check_duplicate_links.py
python check_unique_mds_ids.py
python extract_qa_ids.py
python find_missing_ids.py
python download_jsons_from_txt_ids.py
python process_missing_specific_ids.py
python verify_missing_ids.py
```
The first command installs all required dependencies.
The second command generates a parent_links.txt file containing URLs.
The third command downloads HTML content from each "ZK_1" link using Selenium WebDriver and saves it as a text file in the index_snapshot folder.
The fourth command analyzes SVG elements in the downloaded files, extracts href links, and identifies anomalies.
The fifth command reorders the links in each file in the index_full_links directory and saves the sorted results to the index_full_links_reord directory.
The sixth command generates a master index file and checks download progress, reporting statistics on existing and missing JSON files.
The seventh command downloads missing JSON files using concurrent workers based on the missing_jsons.txt file.
The eighth command extracts HTML content from JSON files, converts it to markdown, and saves the result to the index_full_mds directory.
The ninth command checks the progress of the HTML to Markdown conversion and creates a missing_mds.txt file.
The tenth command processes only the missing Markdown files listed in missing_mds.txt.
The seventeenth command downloads JSON data specifically for the IDs listed in missing_specific_ids.txt file, providing a more targeted approach for fetching specific missing files.

To test the SVG extraction on a single file:
```
