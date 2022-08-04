#
# This file is part of nabonassar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#
"""
Convert 'combined' data in CSV+UTF8 to JSON with basic cleanup
"""

from airtight.cli import configure_commandline
import csv
import json
import logging
from pathlib import Path
from pprint import pformat
import re
from slugify import slugify

logger = logging.getLogger(__name__)

DEFAULT_LOG_LEVEL = logging.WARNING
OPTIONAL_ARGUMENTS = [
    [
        "-l",
        "--loglevel",
        "NOTSET",
        "desired logging level ("
        + "case-insensitive string: DEBUG, INFO, WARNING, or ERROR",
        False,
    ],
    [
        "-p",
        "--pretty",
        False,
        "pretty-print the output JSON for easy readability",
        False,
    ],
    ["-v", "--verbose", False, "verbose output (logging level == INFO)", False],
    [
        "-w",
        "--veryverbose",
        False,
        "very verbose output (logging level == DEBUG)",
        False,
    ],
]
POSITIONAL_ARGUMENTS = [
    # each row is a list with 3 elements: name, type, help
    ["from", str, "source CSV file"]
]


def normalize_fieldnames(raw: list):
    cooked = [slugify(n) for n in raw]
    cooked = [n.replace("musuem", "museum") for n in cooked]
    packaged = list()
    rx_publication_labels = re.compile(r"^publication-\d+-label$")
    rx_museum_labels = re.compile(r"^museum-label-\d+$")
    for n in cooked:
        if rx_publication_labels.match(n) is not None:
            packaged.append("publication-labels")
        elif rx_museum_labels.match(n) is not None:
            packaged.append("museum-labels")
        else:
            packaged.append(n)
    return dict(zip(raw, packaged))


def main(**kwargs):
    """
    main function
    """
    whence = Path(kwargs["from"]).expanduser().resolve()
    with open(whence, "r", encoding="utf-8-sig") as fp:
        reader = csv.DictReader(fp)
        rows = [r for r in reader]
    del fp
    logger.debug(f"rows: {len(rows)}")
    fieldnames = list(rows[0].keys())
    logger.debug(f"fieldnames: {fieldnames}")
    fn_csv2json = normalize_fieldnames(fieldnames)
    logger.debug(
        f"normalized fieldnames crosswalk for JSON: {pformat(fn_csv2json, indent='4')}"
    )


if __name__ == "__main__":
    main(
        **configure_commandline(
            OPTIONAL_ARGUMENTS, POSITIONAL_ARGUMENTS, DEFAULT_LOG_LEVEL
        )
    )
