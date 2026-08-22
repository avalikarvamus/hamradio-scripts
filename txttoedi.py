#!/usr/bin/env python3

import sys
import os
from datetime import datetime, timedelta

def convert_time_to_utc(time_str):
    """
    Convert local time to UTC by subtracting 3 hours
    Example: 1708 -> 1408
    """
    if len(time_str) == 4:
        try:
            # Extract hours and minutes
            hours = int(time_str[:2])
            minutes = int(time_str[2:])
            
            # Convert to total minutes
            total_minutes = hours * 60 + minutes
            
            # Subtract 3 hours (180 minutes)
            total_minutes_utc = total_minutes - 180
            
            # Handle negative minutes (previous day)
            if total_minutes_utc < 0:
                total_minutes_utc += 24 * 60  # Add 24 hours
            
            # Convert back to hours and minutes
            utc_hours = total_minutes_utc // 60
            utc_minutes = total_minutes_utc % 60
            
            # Format as HHMM
            return f"{utc_hours:02d}{utc_minutes:02d}"
        except ValueError:
            return time_str  # Return original if conversion fails
    return time_str

def convert_qso_line(line):
    """
    Convert a space-separated line to EDI format with UTC time
    
    Input format: ES8TJM  017 ko18um  fm  1824    001 145.400
    Output format: "260815;1708;ES8TJM;6;59;001;59;017;;KO17JM;0;;N;N;"
    
    Format breakdown:
    - Date: YYMMDD (150826)
    - Time: HHMM (1708)
    - Callsign: ES8TJM
    - Mode: 6 (FM)
    - RST Sent: 59
    - Serial: 001
    - RST Recv: 59
    - Info: 017
    - Grid: KO17JM (from location field)
    - Power: 0
    - Comment: (empty)
    - QSL: N
    - QSL Sent: N
    """
    # Split by whitespace (handles multiple spaces)
    fields = line.strip().split()
    
    if len(fields) < 7:
        return None
    
    # Extract fields
    callsign = fields[0].strip().upper()
    info = fields[1].strip()
    location = fields[2].strip()
    mode = fields[3].strip()
    time = fields[4].strip()
    serial = fields[5].strip()
    frequency = fields[6].strip()
    
    # Convert time from HHmm to UTC by removing 3 hours
    utc_time = convert_time_to_utc(time)
    
    # Get current date in YYMMDD format
    current_date = datetime.now().strftime("%y%m%d")
    
    # Convert mode to EDI format (6 for FM)
    mode_map = {
        'fm': '6',
        'am': '5',
        'cw': '4',
        'ssb': '3',
        'data': '2'
    }
    mode_edi = mode_map.get(mode.lower(), '6')  # Default to FM
    
    # Generate the EDI line
    edi_line = f"{current_date};{utc_time};{callsign};{mode_edi};59;{serial};59;{info};;{location.upper()};0;;N;N;"
    
    return edi_line

def process_file(input_file):
    """
    Process the input file and create output .edi file
    """
    # Get the base name without extension
    base_name = os.path.splitext(input_file)[0]
    output_file = base_name + '.edi'
    
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line_num, line in enumerate(infile, 1):
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                
                edi_line = convert_qso_line(line)
                if edi_line:
                    outfile.write(edi_line + '\n')
                else:
                    print(f"Warning: Skipping invalid line {line_num}: {line}")
        
        print(f"Successfully converted {input_file} to {output_file}")
        
    except FileNotFoundError:
        print(f"Error: File {input_file} not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_file>")
        print("Example: python script.py contacts.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    process_file(input_file)

if __name__ == "__main__":
    main()
