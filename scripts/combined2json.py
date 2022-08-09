#
# This file is part of nabonassar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#
"""
Convert 'combined' data in CSV+UTF8 to JSON with basic cleanup
"""

from curses import raw
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
converters = dict()
convert_fields = {
    "day",
    "king",
    "month",
    "observed-predicted",
    "regnal-year-comment",
    "regnal-year",
}
skip_fields = {
    "accession-number",
    "archive",
    "excavation-number",
    "extra-date-info",
    "id-in-this-doc",
    "location-written",
    "museum-labels",
    "other-text-and-tablet-info",
    "p-number",
    "provenience",
    "publication-labels",
    "source-detail",
    "tablet-info-notes",
    "text-content-detail",
}
integer_fields = {"king-order"}


DEFAULT_LOG_LEVEL = logging.WARNING
OPTIONAL_ARGUMENTS = [
    ["-x", "--halt", False, "halt on validation or other major error", False],
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


def get_converter(fieldname):
    global converters
    converter = None
    try:
        converter = converters[fieldname]
    except KeyError:
        cpath = (
            Path(__file__).parent.parent / "data" / "converters" / f"{fieldname}.json"
        )
        logger.debug(cpath)
        try:
            vfp = open(cpath, "r", encoding="utf-8")
        except FileNotFoundError:
            logger.warning(f"No converter defined for fieldname '{fieldname}'.")
            converters[fieldname] = None
        else:
            logger.warning(f"Loading from file: converter for {fieldname}.")
            raw_converter = json.load(vfp)
            vfp.close()
            del vfp
            if isinstance(raw_converter, dict):
                converters[fieldname] = raw_converter
            else:
                raise RuntimeError("phooey")
        converter = converters[fieldname]
    logger.debug(pformat(converter, indent=4))
    return converter


def convert_field(fieldname, value):
    converter = get_converter(fieldname)
    try:
        converter_object = converter[value]
    except KeyError:
        msg = f"Unconvertable value '{value}' in field '{fieldname}'."
        raise ValueError(msg)
    else:
        try:
            new_value = converter_object["conversion"]
        except KeyError:
            new_value = None
    return new_value


def convert_rows(rows: list, fn_crosswalk: dict):
    """Convert a list of dictionaries to a list of JSON-compatible objects using the crosswalk"""
    objs = list()
    for i, row in enumerate(rows):
        obj = dict()
        for k, v in row.items():
            clean_v = " ".join(v.strip().split())
            if clean_v:
                obj_k = fn_crosswalk[k]
                if obj_k in integer_fields:
                    try:
                        clean_v = int(clean_v)
                    except ValueError:
                        logger.error(
                            f"Unexpected non-integer value for field '{k}' in row {i}: '{clean_v}'"
                        )
                        continue
                if obj_k in convert_fields:
                    logger.debug(f"{obj_k} before: {clean_v}")
                    clean_v = convert_field(obj_k, clean_v)
                    logger.debug(f"{obj_k} after: {clean_v}")
                    if clean_v is None:
                        continue
                try:
                    previous_value = obj[obj_k]
                except KeyError:
                    obj[obj_k] = clean_v
                else:
                    if isinstance(previous_value, list):
                        obj[obj_k].append(clean_v)
                    else:
                        obj[obj_k] = [previous_value, clean_v]
        objs.append(obj)
    return objs


def get_vocab(fieldname: str):
    """Get available vocabulary."""
    global vocabularies
    vocab = None
    try:
        vocab = vocabularies[fieldname]
    except KeyError:
        vpath = (
            Path(__file__).parent.parent / "data" / "vocabularies" / f"{fieldname}.json"
        )
        logger.debug(vpath)
        try:
            vfp = open(vpath, "r", encoding="utf-8")
        except FileNotFoundError:
            logger.warning(f"No vocabulary defined for fieldname '{fieldname}'.")
            vocabularies[fieldname] = None
        else:
            raw_vocab = json.load(vfp)
            vfp.close()
            del vfp
            if isinstance(raw_vocab, dict):
                vocabularies[fieldname] = raw_vocab
            else:
                vocabularies[fieldname] = {v: True for v in raw_vocab}
        vocab = vocabularies[fieldname]
    logger.debug(pformat(vocab, indent=4))
    return vocab


def validate_objects(objs: list, halt_on_error: bool):
    for i, obj in enumerate(objs):
        for k, v in obj.items():
            if k in skip_fields:
                continue
            if k in integer_fields:
                if not isinstance(v, int):
                    raise ValueError("gack")
                else:
                    continue
            vocab = get_vocab(k)
            if vocab is not None:
                try:
                    vocab[v]
                except KeyError:
                    msg = f"Invalid value '{v}' in field '{k}' for object at sequence {i}."
                    if halt_on_error:
                        raise ValueError(msg)
                    else:
                        logger.error(msg)


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
    objs = convert_rows(rows, fn_csv2json)
    validate_objects(objs, kwargs["halt"])

    if kwargs["pretty"]:
        indent = 4
        sort_keys = True
    else:
        indent = None
        sort_keys = False
    s = json.dumps(objs, ensure_ascii=False, indent=indent, sort_keys=sort_keys)
    print(s)


if __name__ == "__main__":
    main(
        **configure_commandline(
            OPTIONAL_ARGUMENTS, POSITIONAL_ARGUMENTS, DEFAULT_LOG_LEVEL
        )
    )
