import os
import re

def extract_id_from_url(url: str) -> str:
    """
    Given a Luhmann archive URL like:
      https://niklas-luhmann-archiv.de/bestand/zettelkasten/zettel/ZK_1_NB_1-5A1c_V
    Extract the portion we want to compare, e.g. '1-5A1c'.
    """
    # 1) Get the last portion of the path after the final '/'
    filename = url.rsplit('/', 1)[-1]  # e.g. 'ZK_1_NB_1-5A1c_V'
    # 2) Remove trailing '_V'
    if filename.endswith('_V'):
        filename = filename[:-2]  # e.g. 'ZK_1_NB_1-5A1c'
    # 3) Remove the leading 'ZK_1_NB_' (if it exists)
    prefix = 'ZK_1_NB_'
    if filename.startswith(prefix):
        filename = filename[len(prefix):]  # e.g. '1-5A1c'
    return filename


def tokenize_label(label: str):
    """
    Convert something like '1-5A1c3' into a list of tokens with typed info:
      '1-5A1c3' -> [ (0, 1), (0, 5), (2, 'A'), (0, 1), (1, 'c'), (0, 3) ]
    
    Explanation of tuples (token_type, value):
      token_type = 0 for numbers, 1 for lowercase letters, 2 for uppercase letters
      value      = integer or the letter itself
    """
    # Remove all hyphens (treat them as delimiters but we don't keep them)
    label = label.replace('-', '')
    
    # Use a regex to split into numeric chunks OR single letters.
    # Example: '5A1c3' -> ['5', 'A', '1', 'c', '3']
    chunks = re.findall(r'\d+|[A-Za-z]', label)
    
    token_list = []
    for chunk in chunks:
        if chunk.isdigit():
            # numeric token
            token_list.append((0, int(chunk)))
        elif chunk.isalpha():
            if len(chunk) == 1:
                if chunk.islower():
                    token_list.append((1, chunk))  # lowercase letter
                else:
                    token_list.append((2, chunk))  # uppercase letter
            else:
                # Safety check: we expect only single letters per token
                # but if there's a multi-letter chunk, you could handle it differently.
                pass
        else:
            # If there's any unexpected character, handle it as needed
            pass
    return token_list


def compare_token_lists(t1, t2):
    """
    Compare two lists of (type, value) tokens lexicographically
    with the rule: number < lowercase letter < uppercase letter.
    Python's default tuple comparison actually does exactly that
    if we order type as 0 < 1 < 2.
    We just need to make sure we break ties properly and treat
    short-lists as 'less' if they are a prefix of the longer one.
    """
    # Compare pairwise
    for (x_type, x_val), (y_type, y_val) in zip(t1, t2):
        if x_type != y_type:
            return x_type - y_type  # smaller type => sorts earlier
        else:
            # If same type, compare the values
            if x_type == 0:
                # numeric comparison
                if x_val != y_val:
                    return x_val - y_val
            else:
                # letter comparison
                if x_val != y_val:
                    # normal string comparison, e.g. 'a' < 'b'
                    return -1 if x_val < y_val else 1
    # If we exit the loop, then one is a prefix of the other or they are the same
    return len(t1) - len(t2)


def custom_sort_key(url: str):
    """
    Create a sort key for each URL by:
      1) Extracting the relevant ID portion (e.g. '1-5A1c3')
      2) Tokenizing to e.g. [(0, 1), (0, 5), (2, 'A'), (0, 1), (1, 'c'), (0, 3)]
      3) Return that token list. Python will use the default tuple-based lexicographic comparison.
         (We rely on the fact that (0,<num>) < (1,<letter>) < (2,<letter>) as we want.)
    """
    label = extract_id_from_url(url)
    return tokenize_label(label)


def process_files():
    """
    Process all files in the index_full_links directory,
    sort the links in each file, and save to index_full_links_reord directory.
    """
    input_dir = 'index_full_links'
    output_dir = 'index_full_links_reord'
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all files in the input directory
    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        
        # Skip if not a file
        if not os.path.isfile(input_path):
            continue
        
        # Read the links from the input file
        with open(input_path, 'r', encoding='utf-8') as f:
            links = [line.strip() for line in f if line.strip()]
        
        # Sort the links
        sorted_links = sorted(links, key=custom_sort_key)
        
        # Write the sorted links to the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            for link in sorted_links:
                f.write(f"{link}\n")
        
        print(f"Processed {filename}: {len(links)} links sorted")


if __name__ == "__main__":
    process_files()
    print("All files processed successfully.") 