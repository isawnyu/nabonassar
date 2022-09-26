# Nabonassar

Data pre-processing for the Shanati project.

## Install

1. Fork this repository then clone to your local context.
2. Create and activate a python virtual environment. Module has been tested under python 3.10.6.
3. Change working directory to the local clone and then install dependencies:

```
$ pip install -U pip
$ pip install -U -r requirements_dev.txt
```

All dev and runtime dependencies will be installed. This module will be installed in "editable" fashion, so that local modifications can be tested immediately.

## Ingest Data

1. Export "combined" dataset from excel to CSV UTF-8.
2. Run `python scripts/combined2json.py --pretty ~/somewhere/combined_v4.csv ~/somethere/clean_v4.json`.

```
$ python scripts/combined2json.py -h
usage: combined2json.py [-h] [-x] [-l LOGLEVEL] [-p] [-v] [-w] [-f FORMAT] from to

Convert 'combined' data in CSV+UTF8 to JSON with basic cleanup

positional arguments:
  from                  source CSV file
  to                    destination filename

options:
  -h, --help            show this help message and exit
  -x, --halt            halt on validation or other major error (default: False)
  -l LOGLEVEL, --loglevel LOGLEVEL
                        desired logging level (case-insensitive string: DEBUG, INFO,
                        WARNING, or ERROR (default: NOTSET)
  -p, --pretty          pretty-print the output JSON for easy readability (default:
                        False)
  -v, --verbose         verbose output (logging level == INFO) (default: False)
  -w, --veryverbose     very verbose output (logging level == DEBUG) (default: False)
  -f FORMAT, --format FORMAT
                        output format (json or csv) (default: json)
```

## Extract Attested Dates

`python scripts/attestations.py ~/somewhere/clean_v4.json`

