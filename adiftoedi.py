#!/usr/bin/env python3
"""
WSJT-X ADIF to EDI Log Converter
Converts WSJT-X ADIF format to EDI log format
"""

import re
import sys
from datetime import datetime
from collections import defaultdict

def parse_wsjtx_adif_file(filename):
    """Parse WSJT-X ADIF file and return list of QSO records"""
    qsos = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return qsos
    except Exception as e:
        print(f"Error reading file: {e}")
        return qsos
    
    # Split into records (each record ends with <eor>)
    records = re.findall(r'(.*?<eor>)', content, re.DOTALL)
    
    for record in records:
        qso = {}
        
        # Extract fields using regex with exact format matching
        field_patterns = {
            'call': r'<call:(\d+)>([^<]+)',
            'gridsquare': r'<gridsquare:(\d+)>([^<]+)',
            'mode': r'<mode:(\d+)>([^<]+)',
            'rst_sent': r'<rst_sent:(\d+)>([^<]+)',
            'rst_rcvd': r'<rst_rcvd:(\d+)>([^<]+)',
            'qso_date': r'<qso_date:(\d+)>([^<]+)',
            'time_on': r'<time_on:(\d+)>([^<]+)',
            'qso_date_off': r'<qso_date_off:(\d+)>([^<]+)',
            'time_off': r'<time_off:(\d+)>([^<]+)',
            'band': r'<band:(\d+)>([^<]+)',
            'freq': r'<freq:(\d+)>([^<]+)',
            'station_callsign': r'<station_callsign:(\d+)>([^<]+)',
            'my_gridsquare': r'<my_gridsquare:(\d+)>([^<]+)',
            'comment': r'<comment:(\d+)>([^<]+)',
            'stx': r'<stx:(\d+)>([^<]+)',
            'srx': r'<srx:(\d+)>([^<]+)'
        }
        
        for field, pattern in field_patterns.items():
            match = re.search(pattern, record, re.IGNORECASE)
            if match:
                qso[field] = match.group(2).strip()
        
        # Convert date and time to standard format
        if 'qso_date' in qso and 'time_on' in qso:
            try:
                # WSJT-X date format: YYYYMMDD
                date_str = qso['qso_date']
                time_str = qso['time_on']
                
                # Format time: HHMMSS -> HH:MM:SS
                if len(time_str) == 6:
                    formatted_time = f"{time_str[:2]}{time_str[2:4]}"
                elif len(time_str) == 4:
                    formatted_time = f"{time_str[:2]}{time_str[2:4]}"
                else:
                    formatted_time = time_str
                
                # Convert date to YYMMDD format (for EDI)
                year = date_str[:4]
                month = date_str[4:6]
                day = date_str[6:8]
                formatted_date = f"{year[2:4]}{month}{day}"
                
                qso['date_edi'] = formatted_date
                qso['time_edi'] = formatted_time
                qso['datetime'] = datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H%M%S")
            except ValueError:
                qso['datetime'] = None
        
        if qso:
            qsos.append(qso)
    
    return qsos

def format_edi_qso(qso):
    """Format QSO record in EDI format based on WSJT-X output structure"""
    # EDI format: YYMMDD;HHMM;CALLSIGN;BAND;RST_SENT;FREQ;RST_RCVD;GRID;STX;SRX;MODE;COMMENT
    # Based on your example: 260725;2012;ESOCB;6;59;;59;;;KO18OQ;0;;N;N;
    
    if not qso.get('datetime'):
        return ""
    
    # Extract fields with defaults
    date_edi = qso.get('date_edi', '000000')
    time_edi = qso.get('time_edi', '0000')
    call = qso.get('call', '').upper() or 'UNKNOWN'
    
    # Band conversion (6m -> 6, 20m -> 20, etc.)
    band = qso.get('band', '0')
    # Convert band names to numbers if needed
    band_map = {'160m': '160', '80m': '80', '60m': '60', '40m': '40', '30m': '30', 
                '20m': '20', '17m': '17', '15m': '15', '12m': '12', '10m': '10', 
                '6m': '6', '2m': '2', '1.25m': '125', '70cm': '70', '23cm': '23', 
                '13cm': '13', '9cm': '9', '6cm': '6', '3cm': '3', '1.25cm': '125'}
    
    band_num = '7'
    
    rst_sent = qso.get('rst_sent', '59') or '59'
    freq = qso.get('freq', '') or ''
    rst_rcvd = qso.get('rst_rcvd', '59') or '59'
    grid = qso.get('gridsquare', '') or ''
    stx = qso.get('stx', '') or ''
    srx = qso.get('srx', '') or ''
    mode = qso.get('mode', 'SSB').upper() or 'SSB'
    
    # Format EDI line - adjust based on your specific EDI format requirements
    edi_line = f"{date_edi};{time_edi};{call};{band_num};{rst_sent};;{rst_rcvd};;;{grid};{stx};;{mode};{srx}"
    
    return edi_line

def convert_wsjtx_adif_to_edi(adif_filename, edi_filename=None):
    """Convert WSJT-X ADIF file to EDI format"""
    print(f"Converting WSJT-X ADIF file: {adif_filename}")
    
    qsos = parse_wsjtx_adif_file(adif_filename)
    
    if not qsos:
        print("No QSO records found in the ADIF file.")
        return False
    
    print(f"Found {len(qsos)} QSO records")
    
    if edi_filename is None:
        # Generate output filename
        base_name = adif_filename.rsplit('.', 1)[0]
        edi_filename = f"{base_name}.edi"
    
    try:
        with open(edi_filename, 'w', encoding='utf-8') as file:
            # Write header if needed
            # file.write("EDI Log File\n")
            
            for qso in qsos:
                edi_line = format_edi_qso(qso)
                if edi_line:
                    file.write(f"{edi_line}\n")
        
        print(f"Successfully converted to {edi_filename}")
        return True
        
    except Exception as e:
        print(f"Error writing EDI file: {e}")
        return False

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("Usage: python wsjtx_adif_to_edi.py <input_adif_file> [output_edi_file]")
        print("Example: python wsjtx_adif_to_edi.py wsjtx_log.adif")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = convert_wsjtx_adif_to_edi(input_file, output_file)
    
    if success:
        print("Conversion completed successfully!")
    else:
        print("Conversion failed!")

if __name__ == "__main__":
    main()
