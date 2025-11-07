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

#-------------cumulative table config------------

def _ensure_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        out[c] = pd.to_numeric(out.get(c, 0), errors="coerce").fillna(0).astype(int) # type: ignore
    return out

def _agg_by_keys(df: pd.DataFrame, keys: list[str], numeric_cols: list[str]) -> pd.DataFrame:
    # keep only keys + numeric, coerce, then aggregate duplicates
    keep = [k for k in keys if k in df.columns] + [c for c in numeric_cols if c in df.columns]
    base = df[keep].copy()
    base = _ensure_numeric(base, numeric_cols)
    grouped = base.groupby(keys, dropna=False, as_index=False)[numeric_cols].sum()
    return grouped

def _diff_frames(cur: pd.DataFrame, prev: pd.DataFrame, keys: list[str], numeric_cols: list[str]) -> pd.DataFrame:
    # left join; missing prev treated as 0
    merged = cur.merge(prev, on=keys, how="left", suffixes=("", "_prev"))
    for c in numeric_cols:
        merged[f"{c}_prev"] = pd.to_numeric(merged[f"{c}_prev"], errors="coerce").fillna(0).astype(int)
        merged[c] = pd.to_numeric(merged[c], errors="coerce").fillna(0).astype(int) - merged[f"{c}_prev"]
        # clamp negatives to 0 to handle counter resets/corrections
        merged[c] = merged[c].where(merged[c] >= 0, 0)

    out_cols = [col for col in cur.columns]
    out = merged[out_cols].copy()
    nonzero_mask = (out[numeric_cols].sum(axis=1) != 0)
    return out[nonzero_mask].reset_index(drop=True)

def compute_daily_delta(current_df: pd.DataFrame, previous_df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes today's incremental (non-cumulative) rows, given that both
    current_df and previous_df are cumulative snapshots.
    Matching priority:
      1) ["Maker","RTO","RTO Code"] (strict)
      2) ["Maker","RTO"] (relaxed) for the rows that didn't match in (1)
    """
    numeric_cols = FUEL_COLS + ["Total"]
    strict_keys = ["Maker", "RTO", "RTO Code"]
    relaxed_keys = ["Maker", "RTO"]
    current_df_num = _ensure_numeric(current_df.copy(), numeric_cols)
    prev_strict = _agg_by_keys(previous_df, strict_keys, numeric_cols)
    cur_strict  = _agg_by_keys(current_df_num, strict_keys, numeric_cols)

    # Pass 1: strict diff
    strict_delta = _diff_frames(cur_strict, prev_strict, strict_keys, numeric_cols)

    tmp = cur_strict.merge(prev_strict, on=strict_keys, how="left", suffixes=("", "_prev"))
    no_prev_strict_mask = tmp[[f"{c}_prev" for c in numeric_cols]].isna().all(axis=1)
    cur_strict_unmatched = cur_strict[no_prev_strict_mask].copy()

    # If there are strict-unmatched rows, try relaxed diff on them
    if not cur_strict_unmatched.empty:
        prev_relaxed = _agg_by_keys(previous_df, relaxed_keys, numeric_cols)
        cur_relaxed  = _agg_by_keys(cur_strict_unmatched, relaxed_keys, numeric_cols)
        relaxed_delta = _diff_frames(cur_relaxed, prev_relaxed, relaxed_keys, numeric_cols)

        # Merge relaxed deltas back to include "RTO Code" from current where possible
        # (best-effort: join relaxed result to any representative current row)
        relaxed_with_code = relaxed_delta.merge(
            current_df_num[strict_keys].drop_duplicates(),
            on=relaxed_keys,
            how="left"
        )

        # Reorder columns to SCHEMA_ORDER if available
        cols = [c for c in SCHEMA_ORDER if c in relaxed_with_code.columns] + \
               [c for c in relaxed_with_code.columns if c not in SCHEMA_ORDER]
        relaxed_with_code = relaxed_with_code[cols]
        result = pd.concat([strict_delta, relaxed_with_code], ignore_index=True)
    else:
        result = strict_delta

    # Final tidy: ensure numeric types and column order
    result = _ensure_numeric(result, numeric_cols)
    result = result[[c for c in SCHEMA_ORDER if c in result.columns]]
    return result.reset_index(drop=True)

def load_previous_csv():
    files = sorted(BASE_DIR.glob("reportTable_*.csv"))
    if len(files) < 2:
        return None
    # second latest file is yesterday (latest is today’s being produced)
    return pd.read_csv(files[-2], dtype=str).fillna("")




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
    
    # previous_df = load_previous_csv()
    # if previous_df is None:
    #     print("⚠️ No previous CSV found → Uploading full data this time.")
    #     upload_df = final_df
    # else:
    #     print("🔄 Computing daily delta...")
    #     upload_df = compute_daily_delta(final_df.copy(), previous_df.copy())

    # print("📤 Rows to upload today:", len(upload_df))
    # temp_delta_csv = BASE_DIR / "upload_today.csv"
    # upload_df.to_csv(temp_delta_csv, index=False, encoding="utf-8-sig")

    upload_csv_to_supabase(str(OUTPUT_CSV))

    from PreProcess.monthTable_service import service_MonthTable
    service_MonthTable(str(OUTPUT_CSV))



if __name__ == "__main__":
    main()
