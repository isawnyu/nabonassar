#
# This file is part of nabonassar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#
"""
Produce a vocab of observed/predicted values from the converter json
"""

from airtight.cli import configure_commandline
import json
import logging
from pathlib import Path

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
]


def main(**kwargs):
    """
    main function
    """
    # logger = logging.getLogger(sys._getframe().f_code.co_name)
    name = "observed-predicted"
    whence = Path(__file__).parent.parent / "data" / "converters" / f"{name}.json"
    with open(whence, "r", encoding="utf-8") as fp:
        converter = json.load(fp)
    del fp
    ids = sorted(list({v["conversion"] for v in converter.values() if v}))
    thence = Path(__file__).parent.parent / "data" / "vocabularies" / f"{name}.json"
    with open(thence, "w", encoding="utf-8") as fp:
        json.dump(ids, fp, ensure_ascii=False, indent=4, sort_keys=True)
    del fp
    print(
        f"Wrote {len(ids)} unique IDs from {'/'.join(str(whence).split('/')[-4:])} to {'/'.join(str(thence).split('/')[-4:])}"
    )


if __name__ == "__main__":
    main(
        **configure_commandline(
            OPTIONAL_ARGUMENTS, POSITIONAL_ARGUMENTS, DEFAULT_LOG_LEVEL
        )
    )
