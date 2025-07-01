# SortBench v1.1

**Sorting Benchmark Tool**  
Developed by Anurag Chattopadhyay

SortBench is a benchmarking utility designed to compare sorting algorithms, built primarily for educational and research purposes. It supports custom code integration and detailed output formats for analysis.

---

## Key Features

- 9 built-in sorting algorithms (Bubble, Selection, Insertion, Merge, Quick, Heap, Count, Radix, Tim)
- Custom algorithm and dataset support
- Multiple test states: Original, Random, Nearly-Sorted, Sorted, Reverse-Sorted
- Execution logs exportable as TXT or PDF
- Performance charts exportable as PNG
- Tabulated results exportable as CSV or Excel
- (Planned for v2.0) Oracle DB integration for benchmark result storage

---

## System Requirements

- Windows 10/11 (64-bit)
- Minimum 4GB RAM (8GB recommended)
- 1GB free disk space

---

## Getting Started

1. Select Algorithms: Choose from built-in or add custom.
2. Select Datasets: Choose from default or add custom.
3. Choose Test States: Select data arrangements (Original, Random, etc.)
4. Set Output Directory: Select where results will be saved.
5. Start Benchmarking: Begin the process with one click.

---

## Basic Usage Guide

**Configuration Tab**
- Select algorithms, datasets, and test states
- Add/remove custom code or datasets
- Set maximum time per algorithm (default: 300 seconds)
- Define output directory

**Execution Tab**
- View benchmarking progress logs
- Stop benchmarking anytime
- Save logs as TXT or PDF
- Clear console output

**Charts Tab**
- View and analyze performance results
- Adjust time units and Y-axis scale
- Export as PNG

**Tables Tab**
- View benchmarking data in table format
- Export as CSV or Excel

---

## Custom Datasets Guide

- Must be a `.txt` file with whitespace-separated numeric values
- Accepts integers, floats, positive or negative values
- Use “Browse Files” > “Add Selected Datasets” to add
- Remove with “Remove Custom Datasets”

---

## Custom Algorithms Guide

- Only `.py` files supported
- Function signature must be:

  `def function_name(arr, leftmark, rightmark, start, maxtime)`

- Sorting must be in-place. For algorithms like merge sort, copy the result to the original list

To enforce timeout:
1. Add this import: `from timeit import default_timer`
2. Inside every loop, insert as the first line: `if default_timer() - start > maxtime: raise SystemError`

- Use “Browse” to select the file
- Use “View File” to preview it
- Enter exact function and display name to add the algorithm

---

## Test States Explained

- ORIGINAL: Raw data from file
- RANDOM: Shuffled (recommended for most use cases)
- NEARLY SORTED: Minor unsortedness (avoid for small datasets)
- SORTED: Fully sorted
- REVERSE SORTED: Sorted in descending order

---

## Tips & Best Practices

- Use datasets with over 1000 elements for meaningful results
- Run multiple iterations for RANDOM and NEARLY SORTED
- Ensure available disk space before benchmarking
- Verify custom algorithm function names (case-sensitive)
- Large datasets may take longer — adjust the maximum time limit accordingly

---

## Notes

- This tool is independently developed as a hobby project and not part of any commercial or corporate release
- Oracle DB integration and source code release are planned for SortBench v2.0
- While tested thoroughly, minor bugs may exist — feel free to report issues to help improve future versions

---

Thank you for using SortBench.
