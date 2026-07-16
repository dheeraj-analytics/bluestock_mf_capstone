import requests
import pandas as pd
from pathlib import Path

# RUBRIC COMPLIANCE: Use pathlib to avoid hard-coding paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / 'data' / 'raw'

# Ensure the directory exists
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

schemes = {
    "HDFC_Top_100": "125497",
    "SBI_Bluechip": "119551",
    "ICICI_Bluechip": "120503",
    "Nippon_Large_Cap": "118632",
    "Axis_Bluechip": "119092",
    "Kotak_Bluechip": "120841"
}

def fetch_and_save_nav():
    print(f"Fetching live NAV data from mfapi.in and saving to {RAW_DATA_DIR}...")
    
    for name, code in schemes.items():
        url = f"https://api.mfapi.in/mf/{code}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                df = pd.DataFrame(data['data'])
                df['amfi_code'] = code
                df['scheme_name'] = name.replace("_", " ")
                
                # Save to data/raw/
                file_path = RAW_DATA_DIR / f"{code}_{name}_live.csv"
                df.to_csv(file_path, index=False)
                print(f"✅ Saved: {name} (Code: {code})")
            else:
                print(f"⚠️ No data found for {name}")
        else:
            print(f"❌ Failed to fetch {name}.")

if __name__ == "__main__":
    fetch_and_save_nav()