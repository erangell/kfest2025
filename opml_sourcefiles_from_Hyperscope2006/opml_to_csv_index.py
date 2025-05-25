#!/usr/bin/env python3
"""
Script to process an OPML file and create a CSV with hierarchy levels.
For each "text" element, generates both dotted numeric and NLS-style alphanumeric identifiers.

Modified to exclude text from output CSV file so it becomes only a purple number index
Modified to add dummy first line for use by CSV join program
"""

import xml.etree.ElementTree as ET
import csv
import sys
import argparse

def convert_to_alpha(num):
    """
    Convert a numeric value to alphabetic NLS format.
    
    Args:
        num (int): A positive integer
        
    Returns:
        str: Alphabetic representation (a-z, then aa, ab, etc.)
    """
    if num <= 0:
        raise ValueError("Input must be a positive integer")
    
    # Adjust num to be 0-indexed
    num -= 1
    
    # For values 1-26, return lowercase letters a-z
    if num < 26:
        return chr(97 + num)  # 97 is ASCII for 'a'
    
    # For values > 26, use multiple letters
    quotient, remainder = divmod(num, 26)
    first_letter = chr(97 + quotient - 1)
    second_letter = chr(97 + remainder)
    
    return first_letter + second_letter

def convert_to_nls_format(dotted_numeric):
    """
    Convert a dotted numeric string to NLS alternating alphanumeric format.
    
    In NLS format:
    - Even-positioned levels (0-indexed) use numeric characters
    - Odd-positioned levels use alphabetic characters
    - For alphabetic levels with values > 26, use double letters (aa, ab, ...)
    
    Example:
    1.27.28.29 -> 1aa28ab
    
    Args:
        dotted_numeric (str): A dotted numeric string like "1.2.3.4"
        
    Returns:
        str: The NLS alternating alphanumeric representation without periods
    """
    if not dotted_numeric:
        return ""
    
    parts = dotted_numeric.split('.')
    result = []
    
    for i, part in enumerate(parts):
        # Convert to integer
        num = int(part)
        
        # Even positions (0, 2, 4...) remain numeric
        if i % 2 == 0:
            result.append(str(num))
        # Odd positions (1, 3, 5...) convert to alphabetic
        else:
            result.append(convert_to_alpha(num))
    
    return ''.join(result)

def process_outline_element(element, current_path=None, result=None):
    """
    Recursively process outline elements in the OPML file.
    
    Args:
        element (Element): Current XML element
        current_path (list): Current path in the hierarchy as list of indices
        result (list): List to store results
        
    Returns:
        list: List of tuples with (dotted_numeric, alphanumeric, text)
    """
    if current_path is None:
        current_path = []
    if result is None:
        result = []
    
    # Process outline elements
    if element.tag == 'outline':

        # Get text attribute if it exists
        text = element.get('text', '')
        prefix = '{http://www.hyperscope.org/hyperscope/opml/public/2006/05/09}'
        pnid = prefix + 'nid'
        pauthor = prefix + 'createdBy'
        pdate = prefix + 'createdOn'

        # get additional metadata for statements
        #ekeys=element.keys()
        nid= element.get(pnid, '')
        author = element.get(pauthor, '')
        dtcreated = element.get(pdate, '')
        
        # Only process if we're at level 2 or deeper
        # current_path will be empty for body element, length 1 for top level outlines
        if text and len(current_path) > 1:
            # Create dotted numeric string
            dotted_numeric = '.'.join(map(str, current_path))
            
            # For the NLS format, we want to ignore the first level in the hierarchy
            # So we use current_path[1:] to get all but the first element
            nls_numeric = '.'.join(map(str, current_path[1:]))
            nls_format = convert_to_nls_format(nls_numeric)
            
            # Add to results
            result.append((dotted_numeric, nls_format, nid, author, dtcreated))
    
    # Process children
    child_index = 0
    for child in element:
        if child.tag == 'outline':
            child_index += 1
            # Create new path for child by appending its index
            child_path = current_path + [child_index]
            # Recursively process the child
            process_outline_element(child, child_path, result)
    
    return result

def opml_to_csv(opml_file, csv_file):
    """
    Process an OPML file and create a CSV with hierarchy information.
    
    Args:
        opml_file (str): Path to input OPML file
        csv_file (str): Path to output CSV file
    """
    try:
        # Parse OPML file
        tree = ET.parse(opml_file)
        root = tree.getroot()
        
        # Find the body element which contains outlines
        body = root.find('body')
        if body is None:
            print("Error: No 'body' element found in OPML file")
            return False
        
        # Process all outline elements
        results = []

	# Manually added first line to help CSV join algorithm
        results.append(("1","","","",""))

        process_outline_element(body, [], results)
        
        # Write results to CSV
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            # Write header
            writer.writerow(["dotted_numeric", "dotted_alphanumeric", "nid", "author", "dtCreated"])
            # Write data
            for row in results:
                writer.writerow(row)
        
        print(f"Processed {len(results)} outline elements")
        print(f"Output written to {csv_file}")
        return True
        
    except ET.ParseError as e:
        print(f"Error parsing OPML file: {e}")
        return False
    except Exception as e:
        print(f"Error processing file: {e}")
        return False

def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description="Convert OPML to CSV with hierarchy information")
    parser.add_argument("input", help="Input OPML file")
    parser.add_argument("output", help="Output CSV file")
    
    args = parser.parse_args()
    
    if not opml_to_csv(args.input, args.output):
        sys.exit(1)

if __name__ == "__main__":
    main()
