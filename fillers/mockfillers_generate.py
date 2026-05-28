import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd


DEFAULT_OUTPUT_V1 = "mockfiltersV1.csv"
DEFAULT_OUTPUT_MASTER = "mockfilters.csv"

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


def _repo_root() -> Path:
    # fillers/mockfillers_generate.py -> repo root is one level above fillers/
    return Path(__file__).resolve().parents[1]


def _find_latest_dated_csv(folder: Path) -> Path:
    """
    Prefer files named YYYY-MM-DD.csv. If none match, fall back to newest *.csv by mtime.
    """
    folder = folder.resolve()
    candidates = [p for p in folder.glob("*.csv") if p.is_file()]
    if not candidates:
        raise FileNotFoundError(f"No .csv files found in: {folder}")

    dated: list[tuple[datetime, Path]] = []
    for p in candidates:
        try:
            d = datetime.strptime(p.stem, "%Y-%m-%d")
        except ValueError:
            continue
        dated.append((d, p))

    if dated:
        return max(dated, key=lambda t: t[0])[1]

    return max(candidates, key=lambda p: p.stat().st_mtime)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create per-RTO and maker monthly summaries."
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "single"],
        default="auto",
        help=(
            "auto: generate both outputs automatically (latest cumulative -> mockfiltersV1, "
            "final_master -> mockfilters). single: generate one output from --input/--output."
        ),
    )
    parser.add_argument(
        "--input",
        default=None,
        help="(single mode) Input CSV path.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="(single mode) Output CSV path for grouped results.",
    )
    parser.add_argument(
        "--cumulative-folder",
        default=None,
        help="(auto mode) Folder containing dated cumulative CSVs.",
    )
    parser.add_argument(
        "--final-master",
        default=None,
        help="(auto mode) Path to final_master.csv.",
    )
    parser.add_argument(
        "--output-v1",
        default=None,
        help="(auto mode) Output path for mockfiltersV1.csv.",
    )
    parser.add_argument(
        "--output-master",
        default=None,
        help="(auto mode) Output path for mockfilters.csv.",
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

    root = _repo_root()

    if args.mode == "single":
        if not args.input or not args.output:
            raise ValueError("In single mode, both --input and --output are required.")
        create_monthly_rto_maker_csv(
            Path(args.input),
            Path(args.output),
            args.month,
            args.year,
        )
        return

    cumulative_folder = Path(args.cumulative_folder) if args.cumulative_folder else (root / "cumulative_folder")
    final_master = Path(args.final_master) if args.final_master else (root / "final_master.csv")

    output_v1 = Path(args.output_v1) if args.output_v1 else (root / "fillers" / DEFAULT_OUTPUT_V1)
    output_master = Path(args.output_master) if args.output_master else (root / "fillers" / DEFAULT_OUTPUT_MASTER)

    latest_cumulative = _find_latest_dated_csv(cumulative_folder)

    # Run 1: latest cumulative -> fillers/mockfiltersV1.csv
    create_monthly_rto_maker_csv(latest_cumulative, output_v1, args.month, args.year)

    # Run 2: final_master.csv -> fillers/mockfilters.csv
    create_monthly_rto_maker_csv(final_master, output_master, args.month, args.year)


if __name__ == "__main__":
    main()
