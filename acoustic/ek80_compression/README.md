# EK80 data-size comparison

The script `reproduce_compression.py` checks the two data-size ratios reported for the acoustic processing example in the accompanying manuscript.

The input files are provided in `ek80_compression_data.zip` in the [Mausund 2024 processed dataset](https://doi.org/10.5281/zenodo.23917413). Extract the archive and run the script from the root of this GitHub repository:

```bash
python acoustic/ek80_compression/reproduce_compression.py /path/to/ek80_compression_data
```

The script uses only the Python standard library. It calculates the ratios from `compression_inputs.csv`, checks that `layer_detector_example_208_pings.csv` has the expected byte size, and confirms that it contains 208 records.

The two comparisons have different bases: one uses the rounded sizes reported in the manuscript, and the other uses the measured raw-file size and a reconstructed six-column processed CSV. The reconstructed CSV is not the original transmitted V2ROC file. This script does not perform acoustic feature extraction or validate the detector outputs. See the Zenodo data README for the source-file descriptions, units, and processing limitations.
