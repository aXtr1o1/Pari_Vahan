import sys
from pathlib import Path
import subprocess


def main() -> None:
    root = Path(__file__).resolve().parent

    # 1) Generate mockfiltersV1.csv (latest cumulative) and mockfilters.csv (final_master)
    subprocess.run(
        [sys.executable, str(root / "fillers" / "mockfillers_generate.py")],
        check=True,
    )

    # 2) Run fillers.py to produce fillers/fillers.csv
    subprocess.run(
        [sys.executable, str(root / "fillers" / "fillers.py"), "--append-to-master"],
        check=True,
    )


if __name__ == "__main__":
    main()
