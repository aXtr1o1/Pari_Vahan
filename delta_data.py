import pandas as pd
from pathlib import Path
from datetime import datetime

# --- FOLDERS / FILES ---
CUMULATIVE_DIR = Path("cumulative_folder")   # folder where daily cumulative CSVs are dropped
DELTA_OUT_DIR  = Path("delta_folder")       # folder where we store per-day delta CSV
FINAL_FILE     = "final_master.csv"     
PREPROCESS_MASTER_FILE     = "master_preprocessed.csv"        

KEYS = ["RTO", "vehicle_type", "Maker"]
NO_SUBTRACT_CASELESS = {s.lower() for s in ["scrape_timestamp","timestamp", "State", "rto_number","district", *KEYS]}

HEADER_ALIASES = {
    "Maker":        ["Maker", "OEM", "manufacturer"],
    "vehicle_type": ["vehicle_type", "Vehicle Type", "type"],
    "RTO":          ["RTO", "rto"]
}


def normalize_headers(df: pd.DataFrame, aliases: dict) -> pd.DataFrame:
    df = df.rename(columns=lambda c: c.strip())
    reverse = {}
    for canon, alist in aliases.items():
        for a in alist:
            reverse[a] = canon
    rename_map = {c: reverse[c] for c in df.columns if c in reverse}
    return df.rename(columns=rename_map)


def as_str_keys(df: pd.DataFrame, keys):
    for k in keys:
        df[k] = df[k].astype(str).str.strip()
    return df


def pick_old_and_new(cumulative_dir: Path):
    """
    Look into cumulative_dir, find all *.csv files.
    - If none: raise (nothing to do).
    - If one:   return (None, newest_path)
    - If >=2:   return (second_latest, latest)
      Sorting is by date in filename 'YYYY-MM-DD.csv' if possible,
      else by file modification time.
    """
    files = [p for p in cumulative_dir.glob("*.csv") if p.is_file()]
    if not files:
        raise FileNotFoundError(f"No CSV files found in {cumulative_dir}")

    def sort_key(p: Path):
        stem = p.stem.strip()
        try:
            return datetime.strptime(stem, "%Y-%m-%d")
        except ValueError:
            return datetime.fromtimestamp(p.stat().st_mtime)

    files_sorted = sorted(files, key=sort_key)

    if datetime.today().day == 2:
        return None, files_sorted[-1]

    if len(files_sorted) == 1:
        return None, files_sorted[-1]
    return files_sorted[-2], files_sorted[-1]


def compute_delta(old_df: pd.DataFrame, new_df: pd.DataFrame):
    """
    Delta logic: (NEW - OLD) only for numeric columns,
    preserving timestamp/State/rto_number as-is.
    Returns (out_df, candidate_cols).
    """
    old_df = normalize_headers(old_df, HEADER_ALIASES)
    new_df = normalize_headers(new_df, HEADER_ALIASES)
    for k in KEYS:
        if k not in old_df.columns or k not in new_df.columns:
            raise ValueError(f"Key '{k}' missing in one/both files after normalization.")
    old_df = as_str_keys(old_df, KEYS)
    new_df = as_str_keys(new_df, KEYS)
    candidate_cols = [c for c in new_df.columns if c.lower() not in NO_SUBTRACT_CASELESS]
    for c in candidate_cols:
        new_df[c] = pd.to_numeric(new_df[c], errors="coerce")
        if c in old_df.columns:
            old_df[c] = pd.to_numeric(old_df[c], errors="coerce")

    old_numeric = [c for c in candidate_cols if c in old_df.columns]
    new_numeric = [c for c in candidate_cols if c in new_df.columns]

    old_g = old_df.groupby(KEYS, dropna=False)[old_numeric].sum(min_count=1).reset_index()
    new_g = new_df.groupby(KEYS, dropna=False)[new_numeric].sum(min_count=1).reset_index()
    
    merged = pd.merge(new_g, old_g, on=KEYS, how="left", suffixes=("", "_old"))
    out_df = new_df.copy()
    merged["_k"] = merged[KEYS].astype(str).agg("§".join, axis=1)
    out_df["_k"] = out_df[KEYS].astype(str).agg("§".join, axis=1)


    for col in candidate_cols:
        old_col = f"{col}_old"
        if old_col not in merged.columns:
            merged[old_col] = 0
        delta_series = merged[col].fillna(0) - merged[old_col].fillna(0)
        delta_map = dict(zip(merged["_k"], delta_series))
        out_df[col] = out_df["_k"].map(delta_map)

    out_df = out_df.drop(columns=["_k"])

    return out_df, candidate_cols

def drop_today_rows(csv_path):
    df = pd.read_csv(csv_path)

    if "scrape_timestamp" not in df.columns:
        print("No scrape_timestamp column found.")
        return df, 0

    scraped = pd.to_datetime(
        df["scrape_timestamp"].astype(str).str.strip(),
        errors="coerce",
        dayfirst=True,
    )
    today = datetime.today().date()
    mask_today = scraped.dt.date == today
    has_rows = mask_today.any()

    print("Yes rows exist" if has_rows else "No rows exist")

    dropped = int(mask_today.sum())
    df = df[~mask_today]

    df.to_csv(csv_path, index=False)
    print(f"Rows dropped: {dropped}")
    print(f"Saved updated file: {csv_path}")
    return df, dropped


def append_to_final(final_file: str, out_df: pd.DataFrame):
    """
    Append out_df into FINAL_FILE (CSV), keeping columns aligned.
    """
    final_path = Path(final_file)

    if final_path.exists():
        final_df = pd.read_csv(final_path)
        missing_cols = [c for c in out_df.columns if c not in final_df.columns]
        for m in missing_cols:
            final_df[m] = pd.NA


        for m in final_df.columns:
            if m not in out_df.columns:
                out_df[m] = pd.NA

        out_df = out_df[final_df.columns]


        final_df = pd.concat([final_df, out_df], ignore_index=True)
    else:

        final_df = out_df.copy()


    final_df.to_csv(final_path, index=False)
    print(f"Updated {final_file}  | total rows now = {len(final_df)}")

from mail_protocol_service.mail_protocol import upload_and_email
from preprocess import preprocess_master

def main():

    DELTA_OUT_DIR.mkdir(parents=True, exist_ok=True)


    old_path, new_path = pick_old_and_new(CUMULATIVE_DIR)

    if old_path is None:
        print(f"Only one CSV found ({new_path.name}) → skipping subtraction, appending raw file.")
        new_df = pd.read_csv(new_path)
        new_df = normalize_headers(new_df, HEADER_ALIASES)
        out_df = new_df.copy()
        out_file = DELTA_OUT_DIR / f"{new_path.stem}_delta.csv"
        out_df.to_csv(out_file, index=False)
        print(f"Wrote {out_file} (no delta; raw copy).")
    else:
        print(f"OLD = {old_path.name}  |  NEW = {new_path.name}")
        old_df = pd.read_csv(old_path)
        new_df = pd.read_csv(new_path)
        out_df, candidate_cols = compute_delta(old_df, new_df)
        out_file = DELTA_OUT_DIR / f"{new_path.stem}_delta.csv"
        out_df.to_csv(out_file, index=False)
        print(
            f"Wrote {out_file}  | rows={len(out_df)}  | delta_cols={len(candidate_cols)}"
        )


    drop_today_rows(FINAL_FILE)
    append_to_final(FINAL_FILE, out_df)
    preprocess_master()
    # upload_and_email(delta_csv_path=out_file,cumulative_csv_path=new_path,master_csv_path=PREPROCESS_MASTER_FILE, recipient_email ="sanjeevan@axtr.in,rauf@axtr.in,sanjeevanmanoranjan@gmail.com,alphaf.qcl@tatamotors.com,karthik.krishnan@tatamotors.com")
    # upload_and_email(delta_csv_path=out_file,cumulative_csv_path=new_path,master_csv_path=PREPROCESS_MASTER_FILE, recipient_email ="sanjeevan@axtr.in,alphaf.qcl@tatamotors.com")


if __name__ == "__main__":
    main()