# Mausund 2024 — acoustic processing and figure reproduction

This repository contains supporting analysis code for:

Barstein K, Rogge R, Olaisen A, Abdelgayed A, Dunn M, Stevenson-Jones R, Davies E, Grimsmo L, Ludvigsen M. *A remote operations center framework for heterogeneous robotic zooplankton sampling: System design and field case study*. PLOS ONE manuscript.

The study examines remote coordination of a heterogeneous robotic fleet during a June 2024 field campaign near Mausund, Norway. The scripts here reproduce selected reported outputs and illustrate an acoustic data-quality calculation. They do not constitute the complete onboard processing or vehicle-control software used during the campaign.

## Code and supporting data

| Location | Description |
| --- | --- |
| `acoustic/ping_dropout/plot_op16.py` | Plots the cooperative USV–AUV decision trace (Fig. 5) from recorded, processed mission outputs. |
| `acoustic/ping_dropout/ping_dropout_reference.py` | Reference calculation of a ping-dropout fraction from generic acoustic `Sv` arrays. |
| `acoustic/ping_dropout/test_ping_dropout_reference.py` | Unit tests for the reference calculation. |
| `acoustic/ping_dropout/figures/op16_decision_trace.png` | Decision-trace figure. |
| `acoustic/ek80_compression/reproduce_compression.py` | Recalculates the two documented acoustic data-size ratios and verifies the reconstructed 208-ping CSV export. |

The accompanying processed dataset is available under Zenodo DOI [10.5281/zenodo.23917413](https://doi.org/10.5281/zenodo.23917413). It contains `ping_dropout_processed_data.zip` and `ek80_compression_data.zip`, together with adaptive AUV observations and a representative EK80 raw recording. The archive README files document the data columns and their provenance.

The acoustic scattering-layer detector and example processed acoustic data are provided separately in the [SSL detector demonstration](https://github.com/Ahmed-Abdelgayed/SSL-detector-demo), archived under Zenodo DOI [10.5281/zenodo.23975650](https://doi.org/10.5281/zenodo.23975650).

## Requirements

Python 3.10 or later. The decision-trace plot and ping-dropout example require NumPy and Matplotlib. The data-size accounting script uses the Python standard library.

```bash
python -m pip install numpy matplotlib
```

## Cooperative USV–AUV decision trace

Extract `op16_figure_data_minimal.csv` from `ping_dropout_processed_data.zip`. From the repository root, run:

```bash
python acoustic/ping_dropout/plot_op16.py \
  --csv /path/to/op16_figure_data_minimal.csv \
  --output op16_decision_trace.png
```

The input contains recorded timestamps, ping-dropout fractions, a layer-intensity indicator recorded under `layer_confidence_first`, and mission-state labels. The plotting script displays these recorded values; it does not derive them from raw acoustic data or reconstruct the onboard mission decisions. The layer-intensity indicator is not a detection probability. A value of `-1` denotes an invalid or unavailable estimate.

## Ping-dropout reference calculation

Run the included demonstration and unit tests:

```bash
python acoustic/ping_dropout/ping_dropout_reference.py --demo
python -m unittest discover -s acoustic/ping_dropout -p 'test_*.py'
```

The reference function accepts processed acoustic `Sv` profiles arranged as pings by depth bins. It excludes a specified near-surface range, applies a 40 dB threshold by default relative to a running reference, and reports the fraction of classified recorded pings in a trailing time- or ping-based window.

This reference calculation is not the original onboard implementation and has not been shown to reproduce its outputs numerically. In particular, the original method used a file-level reference and an absolute threshold comparison. The reference implementation uses a running reference and a directional comparison. It also does not infer pings absent from the input data.

## EK80 data-size comparison

Extract `ek80_compression_data.zip`, retaining its `ek80_compression_data` directory, and run from the repository root:

```bash
python acoustic/ek80_compression/reproduce_compression.py \
  /path/to/ek80_compression_data
```

The script reproduces two separate comparisons: the ratio calculated from rounded sizes reported in the manuscript and the ratio based on the measured size of a raw EK80 file and a later six-column export. The latter export is not the original transmitted V2ROC file. The script verifies the reconstructed CSV's byte count and number of rows; it does not repeat acoustic feature extraction or verify the raw recording's checksum.

## Scope of reproducibility

The released scripts reproduce the selected figure and size-accounting results described above. They do not reconstruct the complete acquisition-to-decision workflow from raw sensor data. The original onboard adaptive-controller implementation is not included. The associated acoustic detection demonstration is maintained in the separate repository linked above.

## License

The code in this repository is licensed under the [MIT License](LICENSE). Associated research data are available separately on Zenodo under the license stated in the dataset record.
