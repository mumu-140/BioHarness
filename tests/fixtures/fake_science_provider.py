import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--mode", choices=("success", "fail"), default="success")
    args = parser.parse_args()

    if args.mode == "fail":
        print("fake provider failure", file=sys.stderr)
        return 9

    source = Path(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    payload = source.read_bytes()
    (outdir / "result.txt").write_bytes(b"processed:" + payload)
    (outdir / "provider_evidence.json").write_text(
        json.dumps({"status": "succeeded", "exit_code": 0}, sort_keys=True),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
