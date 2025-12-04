import pandas as pd
from pathlib import Path
from datetime import datetime

# --- FOLDERS / FILES ---
CUMULATIVE_DIR = Path("cumulative_folder")   # folder where daily cumulative CSVs are dropped
DELTA_OUT_DIR  = Path("delta_folder")       # folder where we store per-day delta CSV
FINAL_FILE     = "final_master.xlsx"        # cumulative Excel

# --- KEYS (join keys) ---
KEYS = ["RTO", "vehicle_type", "Maker"]

# --- DO NOT SUBTRACT / DO NOT COERCE (case-insensitive) ---
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
        # Try filename as date: 2025-11-13
        try:
            return datetime.strptime(stem, "%Y-%m-%d")
        except ValueError:
            # Fallback to modification time
            return datetime.fromtimestamp(p.stat().st_mtime)

    files_sorted = sorted(files, key=sort_key)

    if len(files_sorted) == 1:
        # Only one file → no 'old' file
        return None, files_sorted[-1]

    # At least two files → use last as NEW, previous as OLD
    return files_sorted[-2], files_sorted[-1]


def compute_delta(old_df: pd.DataFrame, new_df: pd.DataFrame):
    """
    Delta logic: (NEW - OLD) only for numeric columns,
    preserving timestamp/State/rto_number as-is.
    Returns (out_df, candidate_cols).
    """
    # Normalize headers
    old_df = normalize_headers(old_df, HEADER_ALIASES)
    new_df = normalize_headers(new_df, HEADER_ALIASES)

    # Check keys exist
    for k in KEYS:
        if k not in old_df.columns or k not in new_df.columns:
            raise ValueError(f"Key '{k}' missing in one/both files after normalization.")

    # Stringify keys
    old_df = as_str_keys(old_df, KEYS)
    new_df = as_str_keys(new_df, KEYS)

    # Determine candidate numeric columns from NEW (exclude NO_SUBTRACT case-insensitively)
    candidate_cols = [c for c in new_df.columns if c.lower() not in NO_SUBTRACT_CASELESS]

    # Coerce ONLY candidate columns to numeric (do not touch timestamp/State/rto_number/keys)
    for c in candidate_cols:
        new_df[c] = pd.to_numeric(new_df[c], errors="coerce")
        if c in old_df.columns:
            old_df[c] = pd.to_numeric(old_df[c], errors="coerce")

    # Aggregate duplicates by keys (sum numeric only)
    old_numeric = [c for c in candidate_cols if c in old_df.columns]
    new_numeric = [c for c in candidate_cols if c in new_df.columns]

    old_g = old_df.groupby(KEYS, dropna=False)[old_numeric].sum(min_count=1).reset_index()
    new_g = new_df.groupby(KEYS, dropna=False)[new_numeric].sum(min_count=1).reset_index()

    # Left join on NEW to keep latest rows as base
    merged = pd.merge(new_g, old_g, on=KEYS, how="left", suffixes=("", "_old"))

    # Start from exact NEW sheet; untouched non-numerics (timestamp/State/rto_number) remain as-is
    out_df = new_df.copy()

    # Build composite keys for mapping deltas back
    merged["_k"] = merged[KEYS].astype(str).agg("§".join, axis=1)
    out_df["_k"] = out_df[KEYS].astype(str).agg("§".join, axis=1)

    # Overwrite only numeric candidate columns with (NEW - OLD)
    for col in candidate_cols:
        old_col = f"{col}_old"
        if old_col not in merged.columns:
            merged[old_col] = 0
        delta_series = merged[col].fillna(0) - merged[old_col].fillna(0)
        delta_map = dict(zip(merged["_k"], delta_series))
        out_df[col] = out_df["_k"].map(delta_map)

    # Drop helper
    out_df = out_df.drop(columns=["_k"])

    return out_df, candidate_cols


def append_to_final(final_file: str, out_df: pd.DataFrame):
    """
    Append out_df into FINAL_FILE (Excel), keeping columns aligned.
    """
    final_path = Path(final_file)

    if final_path.exists():
        final_df = pd.read_excel(final_path)

        # Align headers (ensure consistent column order)
        missing_cols = [c for c in out_df.columns if c not in final_df.columns]
        for m in missing_cols:
            final_df[m] = pd.NA

        # Add missing in the other direction (rare but safe)
        for m in final_df.columns:
            if m not in out_df.columns:
                out_df[m] = pd.NA

        # Reorder column order to match existing file
        out_df = out_df[final_df.columns]

        # Append
        final_df = pd.concat([final_df, out_df], ignore_index=True)
    else:
        # No file exists → create master with this delta
        final_df = out_df.copy()

    final_df.to_excel(final_path, index=False)
    print(f"Updated {final_file}  | total rows now = {len(final_df)}")


def main():
    # Ensure delta output dir exists
    DELTA_OUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- pick files from cumulative_folder ---
    old_path, new_path = pick_old_and_new(CUMULATIVE_DIR)

    if old_path is None:
        # Only one file present → no delta logic, just use as-is
        print(f"Only one CSV found ({new_path.name}) → skipping subtraction, appending raw file.")
        new_df = pd.read_csv(new_path)
        new_df = normalize_headers(new_df, HEADER_ALIASES)
        out_df = new_df.copy()

        # Write a _delta CSV (identical to input) into delta_folder
        out_file = DELTA_OUT_DIR / f"{new_path.stem}_delta.csv"
        out_df.to_csv(out_file, index=False)
        print(f"Wrote {out_file} (no delta; raw copy).")
    else:
        print(f"OLD = {old_path.name}  |  NEW = {new_path.name}")
        old_df = pd.read_csv(old_path)
        new_df = pd.read_csv(new_path)

        out_df, candidate_cols = compute_delta(old_df, new_df)

        # Write delta into delta_folder (outside cumulative_folder)
        out_file = DELTA_OUT_DIR / f"{new_path.stem}_delta.csv"
        out_df.to_csv(out_file, index=False)
        print(
            f"Wrote {out_file}  | rows={len(out_df)}  | delta_cols={len(candidate_cols)}"
        )

    # --- append to final master Excel ---
    append_to_final(FINAL_FILE, out_df)


if __name__ == "__main__":
    main()
