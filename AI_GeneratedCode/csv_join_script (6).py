#!/usr/bin/env python3
"""
CSV Join Script - Joins two CSV files with grouped output format
File A: Contains unique primary keys in first column  
File B: Contains multiple rows per primary key from File A
Output: File A row with match count, followed by matching File B rows
Both files must be sorted by the primary key (first column)
"""

import csv
import sys
from pathlib import Path

def join_csv_files(file_a_path, file_b_path, output_path):
    """
    Join two CSV files on their first column.
    
    Args:
        file_a_path (str): Path to file A (unique keys)
        file_b_path (str): Path to file B (multiple rows per key)
        output_path (str): Path for the output joined file
    """
    
    try:
        with open(file_a_path, 'r', newline='', encoding='utf-8') as file_a, \
             open(file_b_path, 'r', newline='', encoding='utf-8') as file_b, \
             open(output_path, 'w', newline='', encoding='utf-8') as output_file:
            
            reader_a = csv.reader(file_a)
            reader_b = csv.reader(file_b)
            writer = csv.writer(output_file, quoting=csv.QUOTE_ALL)
            
            # Read headers
            try:
                header_a = next(reader_a)
                header_b = next(reader_b)
            except StopIteration:
                print("Error: One or both files are empty")
                return False
            
            # Write combined header (file A + count column + file B columns minus first column)
            combined_header = header_a + ['Match_Count'] + header_b[1:]  # Skip first column of file B
            writer.writerow(combined_header)
            
            # Write special first row with primary key "1" and all other fields blank
            first_row = ['1'] + [''] * (len(combined_header) - 1)
            writer.writerow(first_row)
            rows_written += 1
            
            # Initialize for merge process
            row_a = None
            row_b = None
            rows_written = 0  # Initialize counter early to avoid UnboundLocalError
            
            # Read first data rows
            try:
                row_a = next(reader_a)
                print(f"Debug: First row from file A: {row_a}")
            except StopIteration:
                print("File A has no data rows")
                return False
            
            try:
                row_b = next(reader_b)
                print(f"Debug: First row from file B: {row_b}")
            except StopIteration:
                print("File B has no data rows")
                return False
            
            # Main merge loop - since both files are sorted, we can do an efficient merge
            print(f"Debug: Starting merge loop. Header A: {header_a}, Header B: {header_b}")
            while row_a is not None and row_b is not None:
                key_a = row_a[0] if row_a and len(row_a) > 0 else None
                key_b = row_b[0] if row_b and len(row_b) > 0 else None
                
                print(f"Debug: Comparing keys - A: '{key_a}', B: '{key_b}'")
                
                # Skip empty rows
                if not key_a:
                    print(f"Debug: Skipping empty row A: {row_a}")
                    try:
                        row_a = next(reader_a)
                        continue
                    except StopIteration:
                        row_a = None
                        continue
                        
                if not key_b:
                    print(f"Debug: Skipping empty row B: {row_b}")
                    try:
                        row_b = next(reader_b)
                        continue
                    except StopIteration:
                        row_b = None
                        continue
                
                if key_a == key_b:
                    # Match found - collect all B rows with this key and count them
                    current_key = key_a
                    matching_b_rows = []
                    
                    # Collect all rows from B that match current key
                    while row_b is not None and row_b[0] == current_key:
                        matching_b_rows.append(row_b)
                        try:
                            row_b = next(reader_b)
                        except StopIteration:
                            row_b = None
                    
                    # Write the A row first with count appended
                    count = len(matching_b_rows)
                    a_row_with_count = row_a + [str(count)] + [''] * len(header_b[1:])  # Empty cols for B data minus key
                    writer.writerow(a_row_with_count)
                    rows_written += 1
                    
                    # Write all matching B rows (with empty A columns except key)
                    for b_row in matching_b_rows:
                        # Create row with empty A columns (except key) + empty count + B data (minus key)
                        empty_a_cols = [''] * (len(header_a) - 1)  # Empty for all A cols except key
                        b_output_row = [b_row[0]] + empty_a_cols + [''] + b_row[1:]  # Skip first column of B
                        writer.writerow(b_output_row)
                        rows_written += 1
                    
                    # Advance to next A row
                    try:
                        row_a = next(reader_a)
                    except StopIteration:
                        row_a = None
                        
                elif key_a < key_b:
                    # Key in A is smaller - advance A (no match for this A key)
                    print(f"Warning: Key '{key_a}' from file A has no matches in file B")
                    # Write A row with count of 0
                    a_row_with_count = row_a + ['0'] + [''] * len(header_b[1:])  # Empty cols for B data minus key
                    writer.writerow(a_row_with_count)
                    rows_written += 1
                    
                    try:
                        row_a = next(reader_a)
                    except StopIteration:
                        row_a = None
                        
                else:  # key_a > key_b
                    # Key in B is smaller - add orphaned B record to output
                    print(f"Info: Key '{key_b}' from file B has no match in file A - adding to output")
                    try:
                        # Create row with B key + empty A columns + empty count + B data (minus key)
                        empty_a_cols = [''] * (len(header_a) - 1)  # Empty for all A cols except key
                        orphaned_b_row = [key_b] + empty_a_cols + [''] + row_b[1:]  # Skip first column of B
                        writer.writerow(orphaned_b_row)
                        rows_written += 1
                    except Exception as e:
                        print(f"Error processing orphaned B row with key '{key_b}': {e}")
                        print(f"Row data: {row_b}")
                        print(f"Header A length: {len(header_a)}, Header B length: {len(header_b)}")
                    
                    try:
                        row_b = next(reader_b)
                    except StopIteration:
                        row_b = None
            
            # Handle remaining A rows (no matches in B)
            while row_a is not None:
                # Write A row with count of 0
                a_row_with_count = row_a + ['0'] + [''] * len(header_b[1:])  # Empty cols for B data minus key
                writer.writerow(a_row_with_count)
                rows_written += 1
                try:
                    row_a = next(reader_a)
                except StopIteration:
                    row_a = None
            
            # Handle remaining B rows (no matches in A) - add them to output
            while row_b is not None:
                if row_b and len(row_b) > 0 and row_b[0]:  # Check for valid row
                    print(f"Info: Key '{row_b[0]}' from file B has no match in file A - adding to output")
                    try:
                        # Create row with B key + empty A columns + empty count + B data (minus key)
                        empty_a_cols = [''] * (len(header_a) - 1)  # Empty for all A cols except key
                        orphaned_b_row = [row_b[0]] + empty_a_cols + [''] + row_b[1:]  # Skip first column of B
                        writer.writerow(orphaned_b_row)
                        rows_written += 1
                    except Exception as e:
                        print(f"Error processing remaining B row with key '{row_b[0]}': {e}")
                        print(f"Row data: {row_b}")
                
                try:
                    row_b = next(reader_b)
                except StopIteration:
                    row_b = None
            
            # Check for remaining unprocessed B rows
            # Note: All remaining B rows are now processed above
            
            print(f"Successfully joined files. {rows_written} rows written to {output_path}")
            return True
            
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        return False
    except PermissionError as e:
        print(f"Error: Permission denied - {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function to handle command line arguments and execute join"""
    
    if len(sys.argv) != 4:
        print("Usage: python csv_join.py <file_a.csv> <file_b.csv> <output.csv>")
        print("\nDescription:")
        print("  file_a.csv: CSV file with unique keys in first column")
        print("  file_b.csv: CSV file with multiple rows per key")
        print("  output.csv: Output file for joined results")
        print("\nBoth input files must be sorted by the first column (primary key)")
        sys.exit(1)
    
    file_a_path = sys.argv[1]
    file_b_path = sys.argv[2]
    output_path = sys.argv[3]
    
    # Validate input files exist
    if not Path(file_a_path).exists():
        print(f"Error: File A '{file_a_path}' does not exist")
        sys.exit(1)
    
    if not Path(file_b_path).exists():
        print(f"Error: File B '{file_b_path}' does not exist")
        sys.exit(1)
    
    # Perform the join
    success = join_csv_files(file_a_path, file_b_path, output_path)
    
    if success:
        print("Join completed successfully!")
        sys.exit(0)
    else:
        print("Join failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
