import pandas as pd
import os
from datetime import date
import re
import json
from datetime import date, timedelta

# Load district map
with open("district.json", "r", encoding="utf-8") as f:
    DISTRICT_MAP = json.load(f)

TARGET_MAKERS = {
    "MARUTI SUZUKI INDIA LTD",
    "HONDA CARS INDIA LTD",
    "HYUNDAI MOTOR INDIA LTD",
    "JSW MG MOTOR INDIA PVT LTD",
    "KIA INDIA PRIVATE LIMITED",
    "MAHINDRA & MAHINDRA LIMITED",
    "NISSAN MOTOR INDIA PVT LTD",
    "SKODA AUTO VOLKSWAGEN INDIA PVT LTD",
    "TATA MOTORS PASSENGER VEHICLES LTD",
    "TATA PASSENGER ELECTRIC MOBILITY LTD",
    "TOYOTA KIRLOSKAR MOTOR PVT LTD",
    "RENAULT INDIA PVT LTD",
    "MAHINDRA ELECTRIC AUTOMOBILE LTD",
    "STELLANTIS AUTOMOBILES INDIA PVT LTD",
    "STELLANTIS INDIA PVT LTD",
    "BYD INDIA PRIVATE LIMITED",
    "VINFAST AUTO INDIA PVT LTD",
    "VOLKSWAGEN AG",
    "TATA MOTORS LTD",
    "SKODA AUTO AS",
}



def parse_filename(filename):
    """Extract RTO details from filename"""
    filename_without_ext = filename.replace('.xlsx', '').replace('.csv', '')
    parts = filename_without_ext.split('_')
    vehicle_type = '_'.join(parts[1:]) if len(parts) > 1 else 'unknown'
    first_part = parts[0]

    match = re.match(r'(.+?)\s*-\s*([A-Z]+\d+)', first_part)
    if match:
        rto_name = match.group(1).strip()
        rto_number = match.group(2).strip()
        if rto_number.startswith('TN'):
            state = 'Tamil Nadu'
        elif rto_number.startswith('KL'):
            state = 'Kerala'
        elif rto_number.startswith('KA'):
            state = 'Karnataka'
        elif rto_number.startswith('PY'):
            state = 'Puducherry'
        else:
            state = 'Unknown'
        return {
            'state': state,
            'rto': rto_name,
            'rto_number': rto_number,
            'vehicle_type': vehicle_type
        }
    
    return None


def process_rto_file(filepath):
    """Process a single RTO Excel file"""
    try:
        df = pd.read_excel(filepath, header=3)
        
        filename = os.path.basename(filepath)
        file_info = parse_filename(filename)
        
        if not file_info:
            print(f"Could not parse filename: {filename}")
            return None
        
        # Remove the first column (S No) if it exists
        if 'S No' in df.columns or 'Unnamed: 0' in df.columns:
            df = df.iloc[:, 1:]
        columns = df.columns.tolist()
        if len(columns) > 0:
            columns[0] = 'Maker'
            df.columns = columns
        yesterday = (date.today() - timedelta(days=1)).strftime('%d-%m-%y')
        # Remove empty rows (where Maker is NaN)
        df = df[df['Maker'].notna() & (df['Maker'] != '')]
        df = df[~df['Maker'].str.strip().isin(['Maker', 'TOTAL', ''])]
        df.insert(0, 'scrape_timestamp', date.today().strftime('%d-%m-%y'))
        df.insert(1, 'timestamp', yesterday)
        df.insert(2, 'state', file_info['state'])
        df.insert(3, 'rto', file_info['rto'])
        df.insert(4, 'rto_number', file_info['rto_number'])
        df.insert(5, 'vehicle_type', file_info['vehicle_type'])
        district = DISTRICT_MAP.get(file_info['rto'].upper(), "Unknown")
        df.insert(6, 'district', district)
        
        # Clean up maker names (strip whitespace)
        df['Maker'] = df['Maker'].str.strip()
        df = df[df['Maker'].isin(TARGET_MAKERS)]
        last_col = df.columns[-1]
        if 'Unnamed' in str(last_col):
            df.rename(columns={last_col: 'TOTAL'}, inplace=True)
        for col in df.columns[7:]:
            if col != 'Maker':
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        return df
    
    except Exception as e:
        print(f"Error processing {filepath}: {str(e)}")
        return None

def consolidate_rto_files(input_folder, output_csv):
    """Process all Excel files in folder and create consolidated CSV"""
    
    all_data = []
    xlsx_files = [f for f in os.listdir(input_folder) if f.endswith('.xlsx')]
    
    if not xlsx_files:
        print(f"No Excel files found in {input_folder}")
        return
    
    print(f"Found {len(xlsx_files)} Excel files to process")
    for filename in xlsx_files:
        filepath = os.path.join(input_folder, filename)
        print(f"Processing: {filename}")
        
        df = process_rto_file(filepath)
        if df is not None and not df.empty:
            all_data.append(df)
            print(f"  ✓ Added {len(df)} records")
        else:
            print(f"  ✗ No data extracted")
    

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df.to_csv(output_csv, index=False)
        print(f"\n✓ Successfully created {output_csv}")
        print(f"  Total records: {len(final_df)}")
        print(f"  Total columns: {len(final_df.columns)}")
    else:
        print("No data was processed!")


if __name__ == "__main__":

    INPUT_FOLDER = "C:\\Users\\sanje_3wfdh8z\\Downloads\\2025-12-02_RTO_Files"
    OUTPUT_CSV = f"cumulative_folder/{date.today().strftime('%Y-%m-%d')}.csv"

    consolidate_rto_files(INPUT_FOLDER, OUTPUT_CSV)
    print("\nDone!")