import argparse
from datetime import date, timedelta
from pathlib import Path

import pandas as pd


_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
DEFAULT_LEFT = str(_HERE / "mockfiltersV1.csv")
DEFAULT_RIGHT = str(_HERE / "mockfilters.csv")
DEFAULT_OUTPUT = str(_HERE / "fillers.csv")
DEFAULT_MASTER = str(_ROOT / "final_master.csv")

ID_COLUMNS = {
    "scrape_timestamp",
    "timestamp",
    "state",
    "RTO",
    "rto",
    "rto_number",
    "vehicle_type",
    "district",
    "Maker",
    "maker",
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create delta (left - right) between two mockfilters files."
    )
    parser.add_argument(
        "--left",
        default=DEFAULT_LEFT,
        help="Left CSV path (minuend).",
    )
    parser.add_argument(
        "--right",
        default=DEFAULT_RIGHT,
        help="Right CSV path (subtrahend).",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help="Output CSV path for the delta.",
    )
    parser.add_argument(
        "--append-to-master",
        action="store_true",
        help="Append the generated output CSV rows into final_master.csv.",
    )
    parser.add_argument(
        "--master",
        default=DEFAULT_MASTER,
        help="Master CSV path to append into (used with --append-to-master).",
    )
    return parser.parse_args()


def _resolve_column(df: pd.DataFrame, options: list[str]) -> str:
    for name in options:
        if name in df.columns:
            return name
    raise ValueError(f"Missing required column. Expected one of: {options}")


def _get_numeric_columns(df: pd.DataFrame) -> list[str]:
    numeric_cols = []
    for col in df.columns:
        if col in ID_COLUMNS:
            continue
        series = pd.to_numeric(df[col], errors="coerce")
        if series.notna().any():
            df[col] = series.fillna(0)
            numeric_cols.append(col)
    return numeric_cols


def _normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    rto_col = _resolve_column(df, ["RTO", "rto"])
    maker_col = _resolve_column(df, ["Maker", "maker"])
    normalized = df.copy()
    normalized = normalized.rename(columns={rto_col: "RTO", maker_col: "Maker"})
    return normalized


def create_delta(left_path: Path, right_path: Path, output_path: Path) -> Path:
    left = pd.read_csv(left_path)
    right = pd.read_csv(right_path)

    left = _normalize_keys(left)
    right = _normalize_keys(right)

    left_numeric = _get_numeric_columns(left)
    right_numeric = _get_numeric_columns(right)
    numeric_cols = sorted(set(left_numeric) | set(right_numeric))

    extra_cols = [
        col
        for col in ["state", "rto_number", "district"]
        if col in left.columns and col in right.columns
    ]
    key_cols = ["RTO", "Maker"] + extra_cols

    left = left.set_index(key_cols)
    right = right.set_index(key_cols)

    left = left.reindex(columns=numeric_cols, fill_value=0)
    right = right.reindex(columns=numeric_cols, fill_value=0)

    delta = left.subtract(right, fill_value=0).reset_index()

    ordered_cols = [
        "scrape_timestamp",
        "timestamp",
        "state",
        "RTO",
        "rto_number",
        "vehicle_type",
        "district",
        "Maker",
        "BIO-CNG/BIO-GAS",
        "BIO-DIESEL(B100)",
        "BIO-METHANE",
        "CNG ONLY",
        "DIESEL",
        "DIESEL/HYBRID",
        "DI-METHYL ETHER",
        "DUAL DIESEL/BIO CNG",
        "DUAL DIESEL/CNG",
        "DUAL DIESEL/LNG",
        "ELECTRIC(BOV)",
        "ETHANOL",
        "FLEX-FUEL(BIO-DIESEL)",
        "FLEX-FUEL(ETHANOL)",
        "FUEL CELL HYDROGEN",
        "HCNG",
        "HYDROGEN(ICE)",
        "LNG",
        "LPG ONLY",
        "METHANOL",
        "NOT APPLICABLE",
        "PETROL",
        "PETROL/CNG",
        "PETROL(E20)/CNG",
        "PETROL(E20)/HYBRID",
        "PETROL(E20)/HYBRID/CNG",
        "PETROL(E20)/LPG",
        "PETROL/ETHANOL",
        "PETROL/HYBRID",
        "PETROL/HYBRID/CNG",
        "PETROL/LPG",
        "PETROL/METHANOL",
        "PLUG-IN HYBRID EV",
        "PURE EV",
        "SOLAR",
        "STRONG HYBRID EV",
        "TOTAL",
    ]

    for col in ordered_cols:
        if col not in delta.columns:
            delta[col] = "None"

    today_str = date.today().strftime("%d-%m-%Y")
    yesterday_str = (date.today() - timedelta(days=1)).strftime("%d-%m-%Y")

    # These fields are required by downstream reports; populate them deterministically.
    delta["vehicle_type"] = "motor_car"
    delta["timestamp"] = yesterday_str
    delta["scrape_timestamp"] = today_str

    delta = delta[ordered_cols]
    output_path.parent.mkdir(parents=True, exist_ok=True)

    written_path = output_path
    try:
        delta.to_csv(written_path, index=False)
    except PermissionError:
        # Common on Windows when the CSV is open in Excel/Power BI.
        written_path = output_path.with_name(
            f"{output_path.stem}_generated{output_path.suffix}"
        )
        delta.to_csv(written_path, index=False)
        print(
            f"Could not write to {output_path} (file is locked). "
            f"Wrote output to {written_path} instead."
        )

    print(f"Saved {len(delta)} rows to {written_path}")
    return written_path


def append_csv(source_csv: Path, master_csv: Path) -> None:
    print(f"[append] source_csv: {source_csv}")
    print(f"[append] master_csv: {master_csv}")

    source = pd.read_csv(source_csv, low_memory=False)
    print(f"[append] source rows: {len(source)} | source cols: {len(source.columns)}")

    if master_csv.exists():
        master = pd.read_csv(master_csv, low_memory=False)
        print(f"[append] master exists: yes | master rows: {len(master)}")
    else:
        master = pd.DataFrame(columns=source.columns)
        print("[append] master exists: no | master rows: 0 (will create)")

    # Align columns (even if order differs) and preserve any extra columns.
    all_cols = list(dict.fromkeys(list(master.columns) + list(source.columns)))
    master = master.reindex(columns=all_cols)
    source = source.reindex(columns=all_cols)
    print(f"[append] aligned cols: {len(all_cols)}")

    combined = pd.concat([master, source], ignore_index=True)
    master_csv.parent.mkdir(parents=True, exist_ok=True)
    try:
        combined.to_csv(master_csv, index=False)
        print("[append] status: SUCCESS")
        print(f"[append] rows appended: {len(source)}")
        print(f"[append] total rows after append: {len(combined)}")
        print(f"[append] written to: {master_csv}")
        return
    except PermissionError:
        # Common on Windows when the CSV is open in Excel/Power BI.
        fallback = master_csv.with_name(f"{master_csv.stem}_appended{master_csv.suffix}")
        combined.to_csv(fallback, index=False)
        print("[append] status: FALLBACK (master file locked)")
        print(f"[append] rows appended: {len(source)}")
        print(f"[append] total rows after append: {len(combined)}")
        print(f"[append] written to: {fallback}")


def main() -> None:
    args = _parse_args()
    output_written = create_delta(Path(args.left), Path(args.right), Path(args.output))

    if args.append_to_master:
        append_csv(output_written, Path(args.master))


if __name__ == "__main__":
    main()
