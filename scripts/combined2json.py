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
vocabularies = dict()


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
    """Cleanup and determine crosswalk for fieldnames"""
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


def convert_rows(rows: list, fn_crosswalk: dict):
    """Convert a list of dictionaries to a list of JSON-compatible objects using the crosswalk"""
    objects = list()
    for row in rows:
        obj = dict()
        for k, v in row.items():
            clean_v = " ".join(v.strip().split())
            obj_k = fn_crosswalk[k]
            if clean_v:
                try:
                    previous_value = obj[obj_k]
                except KeyError:
                    obj[obj_k] = clean_v
                else:
                    if isinstance(previous_value, list):
                        obj[obj_k].append(clean_v)
                    else:
                        obj[obj_k] = [previous_value, clean_v]
        objects.append(obj)
    return objects


def get_vocab(fieldname: str):
    """Get available vocabulary."""
    global vocabularies
    try:
        vocab = vocabularies[fieldname]
    except KeyError:
        try:
            vfp = open(
                Path(__file__).parent / "data" / "vocabularies" / f"{fieldname}.json",
                "r",
                encoding="utf-8",
            )
        except FileNotFoundError:
            logger.warning(f"No vocabulary defined for fieldname '{fieldname}'.")
            vocabularies[fieldname] = None
        else:
            vocabularies[fieldname] = json.load(vfp)
            vfp.close()
            del vfp
        vocab = vocabularies[fieldname]
    return vocab


def validate_objects(objects: list):
    for obj in objects:
        for k, v in obj.items():
            vocab = get_vocab(k)
            if vocab:
                pass


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
    objects = convert_rows(rows, fn_csv2json)
    validate_objects(objects)

    if kwargs["pretty"]:
        indent = 4
        sort_keys = True
    else:
        indent = None
        sort_keys = False
    s = json.dumps(objects, ensure_ascii=False, indent=indent, sort_keys=sort_keys)
    print(s)


if __name__ == "__main__":
    main(
        **configure_commandline(
            OPTIONAL_ARGUMENTS, POSITIONAL_ARGUMENTS, DEFAULT_LOG_LEVEL
        )
    )
