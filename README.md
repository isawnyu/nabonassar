# Nabonassar

Data pre-processing for the Shanati project.

## Ingest Data

1. Export "combined" dataset from excel to CSV UTF-8.
2. Run `python scripts/combined2json.py ~/Documents/files/S/shanati/data/combined_v4.csv data/clean_v4.json`.

## Extract Attested Dates

`python scripts/attestations.py data/clean_v4.json`

