import argparse
from pathlib import Path

import pandas as pd


DEFAULT_LEFT = "mockfiltersV1.csv"
DEFAULT_RIGHT = "mockfilters.csv"
DEFAULT_OUTPUT = "fillers.csv"

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


def create_delta(left_path: Path, right_path: Path, output_path: Path) -> None:
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

    for col in ["scrape_timestamp", "timestamp", "vehicle_type"]:
        if col in delta.columns:
            delta[col] = delta[col].fillna("None")

    delta = delta[ordered_cols]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    delta.to_csv(output_path, index=False)
    print(f"Saved {len(delta)} rows to {output_path}")


def main() -> None:
    args = _parse_args()
    create_delta(Path(args.left), Path(args.right), Path(args.output))


if __name__ == "__main__":
    main()
