#!/usr/bin/env python3
"""
OPML to CSV Converter

This script reads an OPML file and outputs a CSV file with the following fields:
1. A dotted numeric string indicating the outline level (e.g., "1.2.3")
2. Line number within the text block (for text broken into multiple lines)
3. Text content (segments of up to 64 characters per line)
"""

import argparse
import csv
import xml.etree.ElementTree as ET
import textwrap
from typing import List, Tuple, Generator


def parse_opml(file_path: str) -> ET.Element:
    """Parse the OPML file and return the root element."""
    tree = ET.parse(file_path)
    return tree.getroot()


def process_outlines(outline_elements: List[ET.Element], parent_index: str = "") -> Generator[Tuple[str, str], None, None]:
    """
    Process outline elements recursively, yielding (index, text) tuples.
    
    Args:
        outline_elements: List of outline XML elements to process
        parent_index: String representing the parent's dotted index (e.g., "1.2")
        
    Yields:
        Tuples of (dotted_index, text_content)
    """
    for i, outline in enumerate(outline_elements, 1):
        # Create the dotted index
        current_index = f"{parent_index}{i}" if parent_index else f"{i}"
        
        # Get text content (defaults to empty string if not present)
        text = outline.get("text", "")
        
        # Yield the current outline's information
        yield (current_index, text)
        
        # Process any child outlines recursively
        child_outlines = outline.findall("outline")
        if child_outlines:
            yield from process_outlines(child_outlines, f"{current_index}.")


def break_text(text: str, max_length: int = 64) -> List[str]:
    """
    Break text into lines with a maximum length, preferring to break at spaces.
    
    Args:
        text: The text to break into lines
        max_length: Maximum length for each line
        
    Returns:
        List of text segments
    """
    if not text:
        return [""]
    
    # Use textwrap to handle line breaking at appropriate places
    lines = textwrap.wrap(text, width=max_length, break_long_words=True)
    
    # Handle case where textwrap returns empty list (e.g., for whitespace-only input)
    return lines if lines else [""]


def opml_to_csv(input_file: str, output_file: str, max_line_length: int = 64) -> None:
    """
    Convert OPML file to CSV with specified format.
    
    Args:
        input_file: Path to input OPML file
        output_file: Path to output CSV file
        max_line_length: Maximum length for each line of text
    """
    root = parse_opml(input_file)
    
    # Find all outline elements under the body
    body = root.find("body")
    if body is None:
        raise ValueError("Invalid OPML format: body element not found")
    
    outlines = body.findall("outline")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        
        # Write header row
        csv_writer.writerow(["Index", "Line Number", "Text"])
        
        # Process all outlines
        for dotted_index, text in process_outlines(outlines):
            # Break the text into lines
            text_lines = break_text(text, max_line_length)
            
            # Write each line as a separate CSV row
            for line_num, line_text in enumerate(text_lines, 1):
                csv_writer.writerow([dotted_index, line_num, line_text])


def main():
    """Main function to handle command line interface."""
    parser = argparse.ArgumentParser(description='Convert OPML file to CSV with specific formatting.')
    parser.add_argument('input', help='Input OPML file path')
    parser.add_argument('output', help='Output CSV file path')
    parser.add_argument('--max-length', type=int, default=64,
                        help='Maximum length of each text line (default: 64)')
    
    args = parser.parse_args()
    
    try:
        opml_to_csv(args.input, args.output, args.max_length)
        print(f"Successfully converted {args.input} to {args.output}")
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
