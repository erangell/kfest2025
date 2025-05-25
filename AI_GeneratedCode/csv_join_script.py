#!/usr/bin/env python3
"""
CSV Join Script - Joins two CSV files on the first column
File A: Contains unique primary keys in first column
File B: Contains multiple rows per primary key from File A
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
            writer = csv.writer(output_file)
            
            # Read headers
            try:
                header_a = next(reader_a)
                header_b = next(reader_b)
            except StopIteration:
                print("Error: One or both files are empty")
                return False
            
            # Write combined header (file A + file B columns, avoiding duplicate key column)
            combined_header = header_a + header_b[1:]  # Skip first column of file B
            writer.writerow(combined_header)
            
            # Initialize for merge process
            row_a = None
            row_b = None
            
            # Read first data rows
            try:
                row_a = next(reader_a)
            except StopIteration:
                print("File A has no data rows")
                return False
            
            try:
                row_b = next(reader_b)
            except StopIteration:
                print("File B has no data rows")
                return False
            
            rows_written = 0
            
            # Main merge loop - since both files are sorted, we can do an efficient merge
            while row_a is not None and row_b is not None:
                key_a = row_a[0] if row_a else None
                key_b = row_b[0] if row_b else None
                
                if key_a == key_b:
                    # Match found - write joined row
                    joined_row = row_a + row_b[1:]  # Combine row A with row B (skip key column)
                    writer.writerow(joined_row)
                    rows_written += 1
                    
                    # Advance row B to get next row with same or different key
                    try:
                        row_b = next(reader_b)
                    except StopIteration:
                        row_b = None
                        
                elif key_a < key_b:
                    # Key in A is smaller - advance A (no match for this A key)
                    print(f"Warning: Key '{key_a}' from file A has no matches in file B")
                    try:
                        row_a = next(reader_a)
                    except StopIteration:
                        row_a = None
                        
                else:  # key_a > key_b
                    # Key in B is smaller - advance B (orphaned B record)
                    print(f"Warning: Key '{key_b}' from file B has no match in file A")
                    try:
                        row_b = next(reader_b)
                    except StopIteration:
                        row_b = None
            
            # Check for remaining unprocessed rows
            if row_a is not None:
                remaining_a = 1 + sum(1 for _ in reader_a)
                print(f"Warning: {remaining_a} keys from file A had no matches in file B")
            
            if row_b is not None:
                remaining_b = 1 + sum(1 for _ in reader_b)
                print(f"Warning: {remaining_b} keys from file B had no matches in file A")
            
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
