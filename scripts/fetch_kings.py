#
# This file is part of nabonassar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#
"""
Fetch king info from Wikipedia
"""

from airtight.cli import configure_commandline
import json
import logging
from pathlib import Path
from pprint import pprint
from wikidataintegrator import wdi_core


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
    raw_kings = set()
    for datum in raw_data:
        try:
            king_id = datum["king"]
        except KeyError:
            continue
        raw_kings.add(king_id)
    kings = dict()
    for king_id in list(raw_kings):
        if king_id.startswith("Q"):
            king_data = wdi_core.WDItemEngine(wd_item_id=king_id)
            king_data = king_data.get_wd_json_representation()
            kings[king_id] = {
                "label": king_data["labels"]["en"]["value"],
                "description": king_data["descriptions"]["en"]["value"],
            }
        else:
            kings[king_id] = {"label": king_id, "description": ""}
    print(json.dumps(kings, ensure_ascii=False, indent=4, sort_keys=False))


if __name__ == "__main__":
    main(
        **configure_commandline(
            OPTIONAL_ARGUMENTS, POSITIONAL_ARGUMENTS, DEFAULT_LOG_LEVEL
        )
    )
