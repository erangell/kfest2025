import csv
import sys
import os

def clean_value(value, force_quotes=False):
    """Clean and format a value for BASIC DATA statements"""
    if value is None or value == '':
        return '""'
    
    value_str = str(value).strip()
    
    # Handle empty strings
    if value_str == '':
        return '""'
    
    # Force quotes for specific fields (like nid)
    if force_quotes:
        # Escape internal quotes and wrap in quotes
        escaped_value = value_str.replace('"', '""')
        return f'"{escaped_value}"'
    
    # If it's a number, return as-is (unless force_quotes is True)
    try:
        float(value_str)
        return value_str
    except ValueError:
        # For strings, escape quotes and wrap in quotes
        escaped_value = value_str.replace('"', '""')
        return f'"{escaped_value}"'

def convert_csv_to_basic(input_file, output_file):
    """Convert CSV file to BASIC DATA statements"""
    required_fields = [
        'dotted_numeric', 'dotted_alphanumeric', 'nid', 'author', 
        'dtCreated', 'level', 'Match_Count', 'Line Number', 'Text'
    ]
    
    basic_lines = []
    line_number = 10000
    
    try:
        with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
            # Detect delimiter and read CSV
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            
            # Validate required fields
            fieldnames = reader.fieldnames or []
            missing_fields = [field for field in required_fields if field not in fieldnames]
            
            if missing_fields:
                print(f"Error: Missing required fields: {', '.join(missing_fields)}")
                print(f"Available fields: {', '.join(fieldnames)}")
                return False
            
            print(f"Processing CSV file: {input_file}")
            print(f"Found fields: {', '.join(fieldnames)}")
            
            row_count = 0
            for row in reader:
                row_count += 1
                try:
                    # Check if Match_Count is not blank to determine type
                    match_count = (row.get('Match_Count', '') or '').strip()
                    is_type1 = match_count != '' and match_count.lower() not in ['null', 'none', 'undefined']
                    
                    if is_type1:
                        # Type 1: Match_Count, dotted_alphanumeric, nid, author, dtCreated, level
                        data_items = [
                            '1',  # Type
                            clean_value(row['Match_Count']),
                            clean_value(row['dotted_alphanumeric'],force_quotes=True),
                            clean_value(row['nid'], force_quotes=True),  # Force quotes around nid
                            clean_value(row['author']),
                            clean_value(row['dtCreated']),
                            clean_value(row['level'])
                        ]
                    else:
                        # Type 2: Line Number, Text
                        data_items = [
                            '2',  # Type
                            clean_value(row['Line Number']),
                            clean_value(row['Text'])
                        ]
                    
                    basic_line = f"{line_number} DATA {','.join(data_items)}"
                    basic_lines.append(basic_line)
                    line_number += 1
                    
                except Exception as e:
                    print(f"Error processing row {row_count}: {e}")
                    continue
            
            print(f"Processed {row_count} rows, generated {len(basic_lines)} DATA statements")
    
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return False
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return False
    
    # Write BASIC DATA statements to output file
    try:
        with open(output_file, 'w', encoding='utf-8') as txtfile:
            for line in basic_lines:
                txtfile.write(line + '\n')
        
        print(f"Successfully created BASIC DATA file: {output_file}")
        print(f"BASIC line numbers: {10000} to {line_number - 1}")
        return True
        
    except Exception as e:
        print(f"Error writing output file: {e}")
        return False

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) != 3:
        print("CSV to BASIC DATA Converter")
        print("Usage: python csv_to_basic.py <input_csv_file> <output_txt_file>")
        print("nExample: python csv_to_basic.py data.csv basic_data.txt")
        print("nInput CSV must contain these fields:")
        print("  dotted_numeric, dotted_alphanumeric, nid, author, dtCreated,")
        print("  level, Match_Count, Line Number, Text")
        print("nOutput format:")
        print("  Type 1 (Match_Count not blank): Type, Match_Count, dotted_alphanumeric, nid, author, dtCreated, level")
        print("  Type 2 (Match_Count blank): Type, Line Number, Text")
        print("  BASIC line numbers start at 10000 and increment by 1")
        print("  nid field will always have double quotes")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)
    
    # Convert the file
    success = convert_csv_to_basic(input_file, output_file)
    
    if success:
        print("nConversion completed successfully!")
        
        # Show a preview of the first few lines
        #try:
        #    with open(output_file, 'r', encoding='utf-8') as f:
        #        lines = f.readlines()[:5]
        #        print(f"nPreview of {output_file} (first 5 lines):")
        #        print("-" * 50)
        #        for line in lines:
        #            print(line.rstrip())
        #        if len(lines) == 5 and len(f.readlines()) > 5:
        #            f.seek(0)
        #            total_lines = len(f.readlines())
        #            print(f"... ({total_lines - 5} more lines)")
        #except Exception as e:
        #    print(f"Could not preview file: {e}")
    else:
        print("nConversion failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
