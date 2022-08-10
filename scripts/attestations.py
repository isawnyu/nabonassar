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
from pprint import pformat

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
                logger.warning(f"No '{fn}' field in docdata for docid = {docid}")
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
            d = dates
            for i, fn in enumerate(fieldnames):
                k = docdata[fn]
                try:
                    d[k]
                except KeyError:
                    if i < len(fieldnames) - 1:
                        d[k] = dict()
                    else:
                        d[k] = set()
                if isinstance(d[k], dict):
                    d = d[k]
                elif isinstance(d[k], set):
                    d[k].add(docid)
                else:
                    raise RuntimeError("kerblooee")
    logger.debug(pformat(dates, indent=4))


if __name__ == "__main__":
    main(
        **configure_commandline(
            OPTIONAL_ARGUMENTS, POSITIONAL_ARGUMENTS, DEFAULT_LOG_LEVEL
        )
    )
