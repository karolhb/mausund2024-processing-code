# Ping-dropout reference calculation and op16 figure

This directory contains a plotting script for the recorded cooperative
USV–AUV op16 decision trace and a separate acoustic ping-dropout reference
implementation.

## Requirements

Python 3.10+, NumPy, Matplotlib.

```bash
python -m pip install numpy matplotlib
```

## Reproduce the figure

Download `op16_figure_data_minimal.csv` from the accompanying Zenodo data
record. From the repository root, run:

```bash
python acoustic/ping_dropout/plot_op16.py --csv path/to/op16_figure_data_minimal.csv --output op16_decision_trace.png
```

The plotting script reads the archived time, ping-dropout, layer-intensity indicator (stored as `layer_confidence_first`),
and mission-state series. It does not calculate acoustic metrics. The
ping-dropout axis is shown as a fraction from 0 to 1.

## Reference calculation

```bash
python acoustic/ping_dropout/ping_dropout_reference.py --demo
python -m unittest discover -s acoustic/ping_dropout -p 'test_*.py'
```

`calculate_ping_dropout` accepts a generic two-dimensional array of processed
Sv measurements, arranged as recorded pings by depth bins. It excludes a
configurable near-surface region, maintains a running reference level, applies
a threshold (40 dB by default), and calculates a trailing dropout fraction.
The analysis window may be specified in seconds or recorded pings.

**Scope:** The reference calculation is separate from the onboard software.
It is not a verified numerical reproduction of the operational implementation.
The original implementation used a file-level reference and an absolute
threshold comparison. The reference calculation uses a running reference
and a directional comparison. The original conversion of 120 seconds to a
ping count is not available. Missing pings are not inferred from absent
records. The reference script does not reproduce the archived figure from
raw EK80 data. The figure is reproduced using the recorded outputs.

No instrument interfaces or raw-file parsers are included.

## Cooperative USV–AUV decision trace

The plotting command above generates the cooperative USV–AUV decision trace from the deposited mission outputs, with the normalized layer-intensity indicator labeled consistently with the manuscript.
