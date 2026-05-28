import argparse
import json
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path

from renameCheck import KNOWN_VEHICLE_TYPES, normalize_text, split_filename

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = PROJECT_ROOT / "fix" / "rto_files_list.json"
RTO_CODE_PATTERN = re.compile(r"([A-Z]{2}\d+)")

STATE_FROM_RTO_PREFIX = {
    "TN": "Tamil_Nadu",
    "KL": "Kerala",
    "KA": "Karnataka",
    "PY": "Puducherry",
}


@dataclass(frozen=True)
class RescrapeTarget:
    rto_code: str
    vehicle_type: str
    state: str
    expected_filename: str


class MissingRtoFilesError(FileNotFoundError):
    """Raised when one or more expected RTO Excel files are absent after rename."""

    def __init__(self, folder: str, missing: list[str]):
        self.folder = folder
        self.missing = missing
        count = len(missing)
        super().__init__(
            f"{count} expected file(s) missing in {folder} after rename check"
        )


def setup_logger(log_path: str | None = None) -> logging.Logger:
    logger = logging.getLogger("file_check")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    if log_path:
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    return logger


def load_expected_files(manifest_path: str | Path) -> list[str]:
    path = Path(manifest_path)
    if not path.is_file():
        raise FileNotFoundError(f"Manifest not found: {path}")

    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Manifest must be a JSON array: {path}")

    return [str(name).strip() for name in data if str(name).strip()]


def _extract_rto_code(text: str) -> str:
    match = RTO_CODE_PATTERN.search(text.upper())
    return match.group(1) if match else ""


def file_identity(name: str) -> tuple[str, str, str]:
    """Return (rto_code, vehicle_type, normalized_rto_name) for matching."""
    base = os.path.splitext(os.path.basename(name))[0]
    rto_name, vehicle_type = split_filename(base)
    return (
        _extract_rto_code(base),
        vehicle_type.lower(),
        normalize_text(rto_name),
    )


def build_folder_index(folder: str) -> dict[tuple[str, str], list[str]]:
    """Map (rto_code, vehicle_type) -> actual filenames in folder."""
    index: dict[tuple[str, str], list[str]] = {}

    for entry in os.listdir(folder):
        if not entry.lower().endswith(".xlsx"):
            continue

        code, vehicle_type, _ = file_identity(entry)
        if not code or vehicle_type not in KNOWN_VEHICLE_TYPES:
            continue

        key = (code, vehicle_type)
        index.setdefault(key, []).append(entry)

    return index


def find_missing_files(
    folder: str,
    expected_names: list[str],
    *,
    folder_index: dict[tuple[str, str], list[str]] | None = None,
) -> list[str]:
    """Return expected filenames that are not present (exact or by RTO code match)."""
    if folder_index is None:
        folder_index = build_folder_index(folder)

    present_exact = {
        name.lower()
        for name in os.listdir(folder)
        if name.lower().endswith(".xlsx")
    }

    missing: list[str] = []
    for expected in expected_names:
        if expected.lower() in present_exact:
            continue

        code, vehicle_type, _ = file_identity(expected)
        if code and folder_index.get((code, vehicle_type)):
            continue

        missing.append(expected)

    return missing


def state_from_rto_code(rto_code: str) -> str | None:
    prefix = rto_code[:2].upper()
    return STATE_FROM_RTO_PREFIX.get(prefix)


def missing_to_rescrape_targets(missing: list[str]) -> list[RescrapeTarget]:
    """Turn missing manifest filenames into rescrape targets (deduped)."""
    seen: set[tuple[str, str]] = set()
    targets: list[RescrapeTarget] = []

    for filename in missing:
        code, vehicle_type, _ = file_identity(filename)
        if not code or vehicle_type not in KNOWN_VEHICLE_TYPES:
            continue

        state = state_from_rto_code(code)
        if not state:
            continue

        key = (code.upper(), vehicle_type)
        if key in seen:
            continue
        seen.add(key)

        targets.append(
            RescrapeTarget(
                rto_code=code.upper(),
                vehicle_type=vehicle_type,
                state=state,
                expected_filename=filename,
            )
        )

    return targets


def group_targets_by_state(
    targets: list[RescrapeTarget],
) -> dict[str, list[RescrapeTarget]]:
    grouped: dict[str, list[RescrapeTarget]] = {}
    for target in targets:
        grouped.setdefault(target.state, []).append(target)
    return grouped


def run_file_check(
    folder: str,
    manifest_path: str | Path | None = None,
    *,
    raise_on_missing: bool = True,
    log_file: str | None = None,
) -> list[str]:
    """
    Verify all manifest-listed Excel files exist in folder after rename.

    Returns the list of missing filenames. Raises MissingRtoFilesError when
    raise_on_missing is True and any file is missing.
    """
    logger = setup_logger(log_file)
    manifest = Path(manifest_path) if manifest_path else DEFAULT_MANIFEST

    if not os.path.isdir(folder):
        logger.error("Folder not found: %s", folder)
        raise FileNotFoundError(f"Folder not found: {folder}")

    expected = load_expected_files(manifest)
    folder_index = build_folder_index(folder)
    present_count = sum(
        1 for name in os.listdir(folder) if name.lower().endswith(".xlsx")
    )

    missing = find_missing_files(folder, expected, folder_index=folder_index)

    logger.info(
        "File check: expected=%s present=%s missing=%s (folder=%s)",
        len(expected),
        present_count,
        len(missing),
        folder,
    )

    if missing:
        logger.error("Missing %s file(s) after rename:", len(missing))
        for name in missing:
            logger.error("  MISSING: %s", name)
        if raise_on_missing:
            raise MissingRtoFilesError(folder, missing)
    else:
        logger.info("All expected files are present.")

    return missing


def main():
    parser = argparse.ArgumentParser(
        description="Verify expected RTO Excel files exist after rename."
    )
    parser.add_argument(
        "--folder",
        required=True,
        help="Folder containing renamed RTO .xlsx files",
    )
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_MANIFEST),
        help="JSON file listing expected filenames",
    )
    parser.add_argument(
        "--log-file",
        default=None,
        help="Optional log file path",
    )
    args = parser.parse_args()

    run_file_check(args.folder, args.manifest, log_file=args.log_file)


if __name__ == "__main__":
    main()
