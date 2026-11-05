#!/usr/bin/env python3
"""Recalculate the data-size ratios in the EK80 compression Zenodo dataset.

This script performs size accounting only. It is NOT the original EK80 layer detector.
Usage: python reproduce_compression.py /path/to/unpacked/zenodo_data
"""
import argparse
import csv
from decimal import Decimal
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('data_dir', type=Path, help='Directory containing compression_inputs.csv and the processed example CSV')
    args = parser.parse_args()
    root = args.data_dir
    with (root / 'compression_inputs.csv').open(newline='', encoding='utf-8') as fp:
        rows = list(csv.DictReader(fp))
    for row in rows:
        raw, reduced = (Decimal(row['raw_bytes']), Decimal(row['reduced_bytes'])) if row['raw_bytes'] and row['reduced_bytes'] else (Decimal(row['raw_kib']), Decimal(row['reduced_kib']))
        print(f"{row['comparison']}: {raw/reduced:,.2f}x")
    example = root / 'layer_detector_example_208_pings.csv'
    expected = next(r for r in rows if r['comparison'] == 'reconstructed_six_column_csv')
    actual_bytes = example.stat().st_size
    assert actual_bytes == int(expected['reduced_bytes']), 'Example file size differs from compression_inputs.csv'
    with example.open(newline='', encoding='utf-8') as fp:
        records = list(csv.DictReader(fp))
    assert len(records) == 208, 'Expected 208 processed pings'
    print(f'Processed example: {len(records)} pings; {actual_bytes:,} bytes')

if __name__ == '__main__':
    main()
