# stack_reports.py
import re, os, glob
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
import os, math
from supabase import create_client
import pandas as pd
import dotenv

#----------supabase config----------

dotenv.load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME   = "raw_data_table"
CHUNK_SIZE   = 500  # tune if needed

def upload_csv_to_supabase(csv_path: str):
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_KEY env vars.")

    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    df = pd.read_csv(csv_path, dtype=str).fillna("")
    records = df.replace({"\u00A0":" ", "\u2007":" ", "\u202F":" "}, regex=True)\
                .to_dict(orient="records")

    total = len(records)
    if total == 0:
        print("No rows to upload.")
        return

    print(f"Uploading {total} rows to '{TABLE_NAME}' in chunks of {CHUNK_SIZE}...")
    for i in range(0, total, CHUNK_SIZE):
        chunk = records[i:i+CHUNK_SIZE]
        resp = client.table(TABLE_NAME).insert(chunk).execute()

        if hasattr(resp, "data") and resp.data is None:
            print(f"Chunk {i//CHUNK_SIZE+1}: uploaded.")
        else:
            print(f"Chunk {i//CHUNK_SIZE+1}: uploaded.")

    print("✅ Supabase upload complete.")


# ---------- CONFIG ----------
BASE_DIR   = Path(__file__).resolve().parent
INPUT_DIR  = BASE_DIR / "imported_data"
OUTPUT_CSV = BASE_DIR / f"reportTable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

FUEL_COLS = [
    "BIO-CNG/BIO-GAS","BIO-DIESEL(B100)","BIO-METHANE","CNG ONLY","DIESEL","DIESEL/HYBRID",
    "DI-METHYL ETHER","DUAL DIESEL/BIO CNG","DUAL DIESEL/CNG","DUAL DIESEL/LNG","ELECTRIC(BOV)",
    "ETHANOL","FLEX-FUEL(BIO-DIESEL)","FLEX-FUEL(ETHANOL)","FUEL CELL HYDROGEN","HCNG","HYDROGEN(ICE)",
    "LNG","LPG ONLY","METHANOL","NOT APPLICABLE","PETROL","PETROL/CNG","PETROL(E20)/CNG",
    "PETROL(E20)/HYBRID","PETROL(E20)/HYBRID/CNG","PETROL(E20)/LPG","PETROL/ETHANOL","PETROL/HYBRID",
    "PETROL/HYBRID/CNG","PETROL/LPG","PETROL/METHANOL","PLUG-IN HYBRID EV","PURE EV","SOLAR","STRONG HYBRID EV"
]
SCHEMA_ORDER = (["created_at","Maker"] + FUEL_COLS + ["Total","RTO","RTO Code"])

def norm_space(s: str) -> str:
    if not isinstance(s, str): return ""
    s = s.replace("\u00A0"," ").replace("\u2007"," ").replace("\u202F"," ")
    s = re.sub(r"\s+"," ", s)
    return s.strip()

def parse_rto_title_from_text(text: str):
    if not text: return None, None
    t = norm_space(text)
    m = re.search(r"\bof\b\s+([^,]+)", t, flags=re.IGNORECASE)
    if not m: return None, None
    segment = m.group(1).strip()
    parts = re.split(r"\s*[-–—]\s*", segment, maxsplit=1)
    if len(parts) == 2:
        rto_name, code = parts[0].strip(), parts[1].strip()
    else:
        m2 = re.search(r"([A-Za-z]{1,3}\d{2,4})$", segment)
        code = m2.group(1).strip() if m2 else ""
        rto_name = segment.replace(code, "").strip()
    rto_name = re.sub(r"\([^)]*\)", "", rto_name).strip()
    rto_name = re.sub(r"\bUO\b$", "", rto_name, flags=re.IGNORECASE).strip()
    rto_name = norm_space(rto_name)
    code = re.sub(r"[^A-Za-z0-9]", "", code)
    if not rto_name or not code: return None, None
    return rto_name, code

def coerce_int(x):
    try:
        s = str(x).strip()
        if s in ("","nan","None"): return 0
        s = s.replace(",","").replace(" ","")
        return int(float(s))
    except:
        return 0

def process_excel_to_df(xlsx_path: Path) -> pd.DataFrame:
    raw = pd.read_excel(xlsx_path, header=None, dtype=str).fillna("")
    rto = rto_code = None
    for i in range(min(8, len(raw))):
        row_text = " ".join([str(v) for v in raw.iloc[i].tolist() if str(v).strip()])
        rto, rto_code = parse_rto_title_from_text(row_text)
        if rto and rto_code:
            break
    if not (rto and rto_code):
        raise ValueError(f"[{xlsx_path.name}] Could not parse RTO and RTO Code from title rows.")

    header_row_idx = None
    for i in range(min(len(raw), 30)):
        row_vals = [norm_space(v) for v in raw.iloc[i].tolist()]
        if any("BIO-CNG/BIO-GAS" in v for v in row_vals):
            header_row_idx = i
            break
    if header_row_idx is None:
        raise ValueError(f"[{xlsx_path.name}] Could not locate fuel header row.")

    data_start_idx = header_row_idx + 1
    maker_col = 1
    fuel_start_col = 2
    fuel_end_col = fuel_start_col + len(FUEL_COLS) - 1
    total_col = fuel_end_col + 1

    data = raw.iloc[data_start_idx:].reset_index(drop=True)
    needed_cols = [maker_col] + list(range(fuel_start_col, fuel_end_col + 1)) + [total_col]
    data_needed = data[needed_cols].copy()
    data_needed.columns = ["Maker"] + FUEL_COLS + ["Total"]
    data_needed["Maker"] = data_needed["Maker"].astype(str).map(norm_space)
    data_needed = data_needed[data_needed["Maker"] != ""].reset_index(drop=True)

    for c in FUEL_COLS + ["Total"]:
        data_needed[c] = data_needed[c].apply(coerce_int)

    now_iso = datetime.now(timezone.utc).isoformat()
    data_needed.insert(0, "created_at", now_iso)
    data_needed["RTO"] = rto
    data_needed["RTO Code"] = rto_code
    return data_needed[SCHEMA_ORDER]


def main():
    # Pattern setup
    pattern_exact = str(INPUT_DIR / "reportTable (*.xlsx)")
    pattern_loose = str(INPUT_DIR / "reportTable*.xlsx")

    # collect all .xlsx files starting with 'reportTable'
    files = sorted(glob.glob(pattern_exact))
    if not files:
        files = sorted(
            f for f in glob.glob(pattern_loose)
            if re.search(r"reportTable(?: \(\d+\))?\.xlsx$", os.path.basename(f))
        )

    if not files:
        print(f"❗ No .xlsx files found in {INPUT_DIR}")
        for p in INPUT_DIR.glob("*"):
            print("  -", p.name)
        return

    print(f"Found {len(files)} file(s): {[Path(f).name for f in files][:5]}{' ...' if len(files)>5 else ''}")

    frames = []
    for fp in files:
        try:
            df = process_excel_to_df(Path(fp))
            frames.append(df)
            print(f"✅ {Path(fp).name}: {len(df)} rows")
        except Exception as e:
            print(f"⚠️  Skipped {Path(fp).name}: {e}")

    if not frames:
        print("❗ No valid data parsed.")
        return

    final_df = pd.concat(frames, ignore_index=True)
    final_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    
    print("\n🎯 Final CSV:", OUTPUT_CSV)
    
    print("   Total rows:", len(final_df))
    from cumulative_service import cumulative_function
    present_file=cumulative_function()
    upload_csv_to_supabase(str(present_file))
    from PreProcess.monthTable_service import service_MonthTable
    service_MonthTable(str(present_file))

if __name__ == "__main__":
    main()
