# AlphaMike

A Bachelor's thesis project focused on protein structural domain creation and structural alignments using MUSTANG, refactored in 2026 with the help of Antigravity.

## Scope
AlphaMike automates the process of fetching protein structural domain boundaries from CATH, extracting the corresponding structural data from PDB files, and running multiple structural alignments using MUSTANG. It aggregates the alignment identities and structural similarities into consolidated CSV reports.

## Setup

Before running AlphaMike, you must ensure that the path to the MUSTANG binary is correctly configured in your `.env` file. The code is currently programmed to use **MUSTANG v3.2.3**.

## Commands

Run the main application. The command requires three positional arguments:
1. `input_file`: Path to the text file containing the list of structures and domains to process.
2. `result_folder`: Directory where the individual MUSTANG HTML reports will be saved.
3. `aggregate_result_file`: Path to the output CSV file where the aggregated identity/similarity results will be written.

```powershell
uv run alphamike <input_file> <result_folder> <aggregate_result_file>
```

## Build Instructions

Build the package using `uv`:
```powershell
uv build
```

## Testing

Run the test suite with coverage using `uv`:
```powershell
uv run pytest --cov=.\src\alphamike .\tests\
```
