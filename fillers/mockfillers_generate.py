import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd


DEFAULT_INPUT = r"C:\\Users\\sanje_3wfdh8z\\OneDrive\\Desktop\\Pari\\cumulative_folder\\2026-03-27.csv"
DEFAULT_OUTPUT = "mockfiltersV1.csv"

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
        description="Create per-RTO and maker monthly summaries."
    )
    parser.add_argument(
        "--input",
        default=DEFAULT_INPUT,
        help="Input CSV path.",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help="Output CSV path for grouped results.",
    )
    parser.add_argument(
        "--month",
        type=int,
        default=datetime.today().month,
        help="Month number (1-12). Defaults to current month.",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=datetime.today().year,
        help="Year (e.g. 2026). Defaults to current year.",
    )
    return parser.parse_args()


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


def _resolve_column(df: pd.DataFrame, options: list[str]) -> str:
    for name in options:
        if name in df.columns:
            return name
    raise ValueError(f"Missing required column. Expected one of: {options}")


def create_monthly_rto_maker_csv(
    input_path: Path, output_path: Path, month: int, year: int
) -> None:
    df = pd.read_csv(input_path)

    if "timestamp" not in df.columns:
        raise ValueError("Input file must include a 'timestamp' column.")

    df["timestamp"] = pd.to_datetime(
        df["timestamp"], dayfirst=True, format="mixed", errors="coerce"
    )

    filtered = df[
        (df["timestamp"].dt.month == month)
        & (df["timestamp"].dt.year == year)
    ].copy()

    if filtered.empty:
        print(f"No rows found for {month:02d}-{year}.")
        return

    numeric_cols = _get_numeric_columns(filtered)
    if not numeric_cols:
        raise ValueError("No numeric columns found to sum.")

    rto_col = _resolve_column(filtered, ["RTO", "rto"])
    maker_col = _resolve_column(filtered, ["Maker", "maker"])

    extra_cols = [col for col in ["state", "rto_number", "district"] if col in filtered.columns]

    grouped = (
        filtered.groupby([rto_col, maker_col] + extra_cols, dropna=False)[numeric_cols]
        .sum()
        .reset_index()
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    grouped.to_csv(output_path, index=False)
    print(f"Saved {len(grouped)} rows to {output_path}")


def main() -> None:
    args = _parse_args()
    create_monthly_rto_maker_csv(
        Path(args.input),
        Path(args.output),
        args.month,
        args.year,
    )


if __name__ == "__main__":
    main()
