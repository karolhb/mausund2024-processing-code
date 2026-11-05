"""Reference ping-dropout calculation for processed acoustic Sv profiles.

This implementation is not the original onboard algorithm.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass
class PingDropoutResult:
    peak_sv_db: np.ndarray
    reference_sv_db: np.ndarray
    dropped: np.ndarray
    fraction: np.ndarray

    @property
    def percent(self) -> np.ndarray:
        """Return the dropout fraction on a 0–100 scale."""
        return self.fraction * 100.0


def _numeric_seconds(times: Sequence[object]) -> np.ndarray:
    """Return timestamps in seconds relative to the first observation."""
    arr = np.asarray(times)
    if arr.ndim != 1:
        raise ValueError("times must be a 1-D array")
    if np.issubdtype(arr.dtype, np.datetime64):
        numeric = arr.astype("datetime64[ns]").astype(np.int64) / 1e9
    elif np.issubdtype(arr.dtype, np.number):
        numeric = arr.astype(float)
    else:
        try:
            numeric = np.asarray(times, dtype="datetime64[ns]").astype(np.int64) / 1e9
        except (ValueError, TypeError) as exc:
            raise ValueError("times must contain datetime-like values or seconds") from exc
    if not np.all(np.isfinite(numeric)) or np.any(np.diff(numeric) < 0):
        raise ValueError("times must be finite and in chronological order")
    return numeric - numeric[0] if len(numeric) else numeric


def _window_fractions(
    dropped: np.ndarray,
    *,
    times: Sequence[object] | None,
    window_seconds: float | None,
    window_pings: int | None,
) -> np.ndarray:
    """Fraction of classified recorded pings in the trailing window."""
    n = len(dropped)
    valid = np.isfinite(dropped)
    cumulative_count = np.r_[0, np.cumsum(valid.astype(int))]
    cumulative_drops = np.r_[0, np.cumsum(np.where(valid, dropped, 0))]

    if (window_seconds is None) == (window_pings is None):
        raise ValueError("Specify exactly one of window_seconds or window_pings")
    if window_pings is not None:
        if not isinstance(window_pings, (int, np.integer)) or window_pings < 1:
            raise ValueError("window_pings must be a positive integer")
        start = np.maximum(0, np.arange(n) - window_pings + 1)
    else:
        if times is None:
            raise ValueError("times are required when window_seconds is supplied")
        if window_seconds is None or not np.isfinite(window_seconds) or window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        seconds = _numeric_seconds(times)
        if len(seconds) != n:
            raise ValueError("times must have one entry per ping")
        start = np.searchsorted(seconds, seconds - window_seconds, side="right")

    end = np.arange(n) + 1
    count = cumulative_count[end] - cumulative_count[start]
    drops = cumulative_drops[end] - cumulative_drops[start]
    out = np.full(n, np.nan, dtype=float)
    np.divide(drops, count, out=out, where=count > 0)
    return out


def calculate_ping_dropout(
    sv: np.ndarray,
    *,
    surface_cutoff_bin: int,
    tolerance_db: float = 40.0,
    times: Sequence[object] | None = None,
    window_seconds: float | None = None,
    window_pings: int | None = None,
    file_ids: Sequence[object] | None = None,
) -> PingDropoutResult:
    """Calculate ping-dropout fractions from a 2D array of Sv values.

    Rows are recorded pings, columns are shallow-to-deep depth bins.
    Select exactly one of window_seconds and window_pings.
    File IDs reset the running reference at file boundaries.
    Missing pings are not reconstructed.
    """
    sv = np.asarray(sv, dtype=float)
    if sv.ndim != 2 or sv.shape[0] == 0 or sv.shape[1] == 0:
        raise ValueError("sv must be a nonempty 2-D array [pings, depth bins]")
    if not isinstance(surface_cutoff_bin, (int, np.integer)) or not 0 <= surface_cutoff_bin < sv.shape[1]:
        raise ValueError("surface_cutoff_bin must be a valid nonnegative depth-bin index")
    if tolerance_db <= 0 or not np.isfinite(tolerance_db):
        raise ValueError("tolerance_db must be a positive finite dB difference")

    n = sv.shape[0]
    if file_ids is not None and len(file_ids) != n:
        raise ValueError("file_ids must contain one entry per ping")
    if times is not None and len(times) != n:
        raise ValueError("times must contain one entry per ping")

    peaks = np.full(n, np.nan)
    for idx, profile in enumerate(sv[:, surface_cutoff_bin:]):
        finite = profile[np.isfinite(profile)]
        if finite.size:
            peaks[idx] = finite.max()

    references = np.full(n, np.nan)
    dropped = np.full(n, np.nan)
    current_reference = np.nan
    for i, peak in enumerate(peaks):
        if i > 0 and file_ids is not None and file_ids[i] != file_ids[i - 1]:
            current_reference = np.nan
        if np.isfinite(peak):
            if not np.isfinite(current_reference) or peak > current_reference:
                current_reference = peak
            dropped[i] = float((current_reference - peak) > tolerance_db)
        references[i] = current_reference

    fraction = _window_fractions(
        dropped, times=times, window_seconds=window_seconds, window_pings=window_pings
    )
    return PingDropoutResult(peaks, references, dropped, fraction)


def _demo() -> None:
    """Run a calculation with example values."""
    sv = np.array([
        [-5, -20, -26],
        [-5, -22, -24],
        [-5, -77, -82],
        [-5, -80, -78],
        [-5, -21, -25],
    ], dtype=float)
    times = np.array([0, 10, 20, 30, 40], dtype=float)
    result = calculate_ping_dropout(
        sv, surface_cutoff_bin=1, tolerance_db=40,
        times=times, window_seconds=30,
    )
    print("Example (surface bin excluded)")
    print("time_s,peak_sv_db,reference_sv_db,flag,fraction,percent")
    for i in range(len(times)):
        print(f"{times[i]:.0f},{result.peak_sv_db[i]:.1f},"
              f"{result.reference_sv_db[i]:.1f},{result.dropped[i]:.0f},"
              f"{result.fraction[i]:.3f},{result.percent[i]:.1f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="run on a tiny synthetic example")
    args = parser.parse_args()
    if args.demo:
        _demo()
    else:
        parser.print_help()
