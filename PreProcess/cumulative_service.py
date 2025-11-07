import pandas as pd
import os
import re
from datetime import datetime


def cumulative_function():
    folder = "."

    # --- Find all reportTable CSVs ---
    pattern = re.compile(r"reportTable_(\d{8}_\d{6})\.csv")
    files = [f for f in os.listdir(folder) if pattern.match(f)]

    if len(files) < 2:
        raise ValueError("❌ Need at least two report files to compare.")

    # --- Sort files by datetime from filename ---
    files.sort(key=lambda x: datetime.strptime(pattern.match(x).group(1), "%Y%m%d_%H%M%S")) # type: ignore

    # --- Pick latest (today) and previous ---
    prev_file = files[-2]
    today_file = files[-1]

    print(f"📂 Previous file: {prev_file}")
    print(f"📂 Today file:    {today_file}")

    # --- Load data ---
    prev = pd.read_csv(os.path.join(folder, prev_file))
    today = pd.read_csv(os.path.join(folder, today_file))

    key_cols = ['RTO', 'Maker']

    # --- Align on keys ---
    merged = pd.merge(today, prev, on=key_cols, suffixes=('_today', '_prev'))

    # --- Compute daily difference for numeric columns ---
    num_cols = [col for col in merged.columns if col.endswith('_today') and merged[col].dtype != 'object']
    for col in num_cols:
        base = col.replace('_today', '')
        merged[base + '_diff'] = merged[col] - merged[base + '_prev']

    # --- Keep only relevant columns (keys + differences) ---
    diff_cols = key_cols + [c for c in merged.columns if c.endswith('_diff')]
    daily = merged[diff_cols]

    # --- Save result ---

    output_file = f"daily_diff_{datetime.now().strftime('%Y%m%d')}.csv"
    daily.to_csv(output_file, index=False)
    return output_file
    print(f"✅ Daily difference file saved: {output_file}")

