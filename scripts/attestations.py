#
# This file is part of nabonassar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#
"""
Determine attestations
"""

from airtight.cli import configure_commandline
import json
import logging
from pathlib import Path
from pprint import pformat, pprint

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
    ["from", str, "json source file"]
]


def main(**kwargs):
    """
    main function
    """
    # logger = logging.getLogger(sys._getframe().f_code.co_name)
    whence = Path(kwargs["from"]).expanduser().resolve()
    with open(whence, "r", encoding="utf-8") as fp:
        raw_data = json.load(fp)
    del fp
    documents = {d["id-in-this-doc"]: d for d in raw_data}
    del raw_data
    logger.info(f"Read {len(documents)} document objects from file")
    dates = dict()
    fieldnames = ["king", "regnal-year", "month", "day"]
    for docid, docdata in documents.items():
        skip = False
        for fn in fieldnames:
            try:
                docdata[fn]
            except KeyError:
                try:
                    comment = docdata[f"{fn}-comment"]
                except KeyError:
                    comment = None
                else:
                    skip = True
                    break
                logger.warning(
                    f"No '{fn}' field in docdata for docid = {docid} and comment == '{comment}'"
                )
                skip = True
                break
            try:
                docdata[fn + "-comment"]
            except KeyError:
                pass
            else:
                skip = True
                break
        if not skip:
            try:
                dates[docdata["king"]]
            except KeyError:
                dates[docdata["king"]] = dict()
            finally:
                era = dates[docdata["king"]]
            try:
                era[docdata["regnal-year"]]
            except KeyError:
                era[docdata["regnal-year"]] = dict()
            finally:
                year = era[docdata["regnal-year"]]
            try:
                year[docdata["month"]]
            except KeyError:
                year[docdata["month"]] = dict()
            finally:
                month = year[docdata["month"]]
            try:
                month[docdata["day"]]
            except KeyError:
                month[docdata["day"]] = list()
            finally:
                month[docdata["day"]].append(docid)

    pprint(dates, indent=4)


if __name__ == "__main__":
    main(
        **configure_commandline(
            OPTIONAL_ARGUMENTS, POSITIONAL_ARGUMENTS, DEFAULT_LOG_LEVEL
        )
    )
