"""Plot the cooperative USV–AUV op16 decision trace from archived CSV values.

This script does not process raw acoustic measurements.
"""

from __future__ import annotations

import argparse
import ast
import csv
from datetime import datetime
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

STATE_CODES = {"INIT": 0, "SCOUT": 1, "EVAL": 2, "LAUNCH": 3}


def _confidence_first(row: dict[str, str]) -> float:
    if row.get("layer_confidence_first") not in (None, ""):
        return float(row["layer_confidence_first"])
    raw = row.get("layer_confidence", "")
    val = ast.literal_eval(raw)
    if not isinstance(val, (tuple, list)) or len(val) < 1:
        raise ValueError(f"unexpected layer_confidence tuple: {raw!r}")
    return float(val[0])


def read_op16_csv(path: Path):
    """Return times, dropout fraction, confidence, and enumerated mission state."""
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        header = f.readline()
        has_metadata_line = "," not in header
        if not has_metadata_line:
            f.seek(0)
        reader = csv.DictReader(f)
        required = {"time", "ping_drop", "current_state"}
        absent = required - set(reader.fieldnames or [])
        if absent:
            raise ValueError(f"input is missing required columns: {sorted(absent)}")
        if "layer_confidence_first" not in (reader.fieldnames or []) and "layer_confidence" not in (reader.fieldnames or []):
            raise ValueError("input must include layer_confidence or layer_confidence_first")
        times, dropout, confidence, state = [], [], [], []
        for line_no, row in enumerate(reader, start=3 if has_metadata_line else 2):
            try:
                times.append(datetime.fromisoformat(row["time"].strip()))
                dropout.append(float(row["ping_drop"]))
                confidence.append(_confidence_first(row))
                current_state = row["current_state"].strip()
                if current_state not in STATE_CODES:
                    raise ValueError(f"unknown mission state: {current_state!r}")
                state.append(STATE_CODES[current_state])
            except (ValueError, TypeError, SyntaxError) as exc:
                raise ValueError(f"invalid CSV record at line {line_no}: {exc}") from exc

    if not times:
        raise ValueError("input CSV has no data rows")
    if any(b < a for a, b in zip(times, times[1:])):
        raise ValueError("timestamps are not monotonically increasing")
    return times, np.array(dropout), np.array(confidence), np.array(state)



def plot_op16(path: Path, output: Path) -> None:
    times, dropout, confidence, states = read_op16_csv(path)
    if np.any((dropout < 0) | (dropout > 1)):
        raise ValueError("ping_drop values must lie between 0 and 1")

    fig, ax_drop = plt.subplots(figsize=(8.3, 4.15))
    fig.subplots_adjust(left=0.13, right=0.74, bottom=0.17, top=0.96)
    ax_conf = ax_drop.twinx()
    ax_state = ax_drop.twinx()
    ax_state.spines["right"].set_position(("axes", 1.20))

    ax_drop.plot(times, dropout, lw=1.0, color="tab:red")
    ax_conf.plot(times, confidence, lw=0.85, color="tab:blue")
    ax_state.plot(times, states, lw=1.0, color="tab:green")

    ax_drop.set_ylabel("Ping dropout fraction", color="tab:red")
    ax_drop.set_ylim(-0.05, 1.05)
    ax_drop.set_yticks(np.arange(0.0, 1.01, 0.2))
    ax_drop.tick_params(axis="y", colors="tab:red")

    ax_conf.set_ylim(-1.1, 1.1)
    ax_conf.tick_params(axis="y", colors="tab:blue")

    ax_state.set_ylim(-0.15, 3.15)
    ax_state.set_yticks(list(STATE_CODES.values()), list(STATE_CODES.keys()))
    ax_state.tick_params(axis="y", colors="tab:green")

    ax_drop.xaxis.set_major_locator(mdates.MinuteLocator(byminute=range(0, 60, 5)))
    ax_drop.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax_drop.set_xlabel("Time")
    ax_conf.set_ylabel("Layer intensity indicator $I$", color="tab:blue")
    ax_state.set_ylabel("Current State", color="tab:green")
    ax_drop.tick_params(axis="both", labelsize=9)
    ax_conf.tick_params(axis="y", labelsize=9)
    ax_state.tick_params(axis="y", labelsize=9)
    ax_drop.xaxis.label.set_size(10)
    ax_drop.yaxis.label.set_size(10)
    ax_conf.yaxis.label.set_size(10)
    ax_state.yaxis.label.set_size(10)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True, help="original or minimal op16 CSV")
    parser.add_argument("--output", type=Path, default=Path("op16_decision_trace.png"))
    args = parser.parse_args()
    plot_op16(args.csv, args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
