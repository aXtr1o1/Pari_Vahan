import pandas as pd

# --------- Inputs ----------
# INPUT_CSV  = r"reportTable_supabase_ready.csv"   # from the previous step
def service_MonthTable(INPUT_CSV):
    OUTPUT_CSV = r"month_main_table.csv"

    STATE_DEFAULT = "Tamil Nadu"   

    # --------- Columns per month_main_table (excluding id) ----------
    TARGET_COLS = [
        "created_at","State","RTO","OEM",
        "CNG ONLY","DIESEL","DIESEL/HYBRID","ELECTRIC(BOV)",
        "Petrol","Petrol /CNG","Petrol /HYBRID",
        "PURE EV","STRONG HYBRID EV","PETROL/ETHANOL",
        "Total","EV"
    ]


    df = pd.read_csv(INPUT_CSV, dtype=str).fillna("")

    # Coerce numeric columns we’ll use
    def to_int(s):
        try:
            s = str(s).replace(",", "").strip()
            if s == "" or s.lower() == "nan": return 0
            return int(float(s))
        except:
            return 0

    num_cols_src = [
        "CNG ONLY","DIESEL","DIESEL/HYBRID","ELECTRIC(BOV)",
        "PETROL","PETROL/CNG","PETROL/HYBRID",
        "PURE EV","STRONG HYBRID EV","PETROL/ETHANOL"
    ]
    for c in num_cols_src:
        if c not in df.columns:
            df[c] = 0
        df[c] = df[c].apply(to_int)

    # --------- Build month_main_table dataframe ----------
    out = pd.DataFrame()

    # Direct copies / renames
    out["created_at"] = df["created_at"]
    out["State"]      = STATE_DEFAULT
    out["RTO"]        = df["RTO"]
    out["OEM"]        = df["Maker"]             # Maker -> OEM
    out["CNG ONLY"]        = df["CNG ONLY"]
    out["DIESEL"]          = df["DIESEL"]
    out["DIESEL/HYBRID"]   = df["DIESEL/HYBRID"]
    out["ELECTRIC(BOV)"]   = df["ELECTRIC(BOV)"]
    out["Petrol"]          = df["PETROL"]
    out["Petrol /CNG"]     = df["PETROL/CNG"]
    out["Petrol /HYBRID"]  = df["PETROL/HYBRID"]
    out["PURE EV"]         = df["PURE EV"]
    out["STRONG HYBRID EV"]= df["STRONG HYBRID EV"]
    out["PETROL/ETHANOL"]  = df["PETROL/ETHANOL"]
    out["EV"] = out["ELECTRIC(BOV)"].apply(to_int) + out["PURE EV"].apply(to_int)

    total_cols = [
        "CNG ONLY","DIESEL","DIESEL/HYBRID","ELECTRIC(BOV)",
        "Petrol","Petrol /CNG","Petrol /HYBRID",
        "PURE EV","STRONG HYBRID EV","PETROL/ETHANOL"
    ]
    out["Total"] = sum(out[c].apply(to_int) for c in total_cols)

    out = out[TARGET_COLS]
    out.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print(f"✅ Wrote: {OUTPUT_CSV}")
    upload_csv_to_supabase(OUTPUT_CSV)
    print(f"Rows: {len(out)} | Columns: {list(out.columns)}")


import os
from supabase import create_client
import dotenv

dotenv.load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME   = "month_main_table"
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
    from rto_ev_pv import Preprocessingev_pv
    from rto_ev import Preprocessing_ev
    Preprocessing_ev(csv_path)
    Preprocessingev_pv(csv_path)
    print("✅ Supabase upload complete.")

