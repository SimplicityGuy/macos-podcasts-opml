#!/usr/bin/env python3

import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterator
from typing import cast
from xml.dom import minidom

DB_FILE = (
    "Library/Group Containers/*.groups.com.apple.podcasts/Documents/MTLibrary.sqlite"
)


def podcasts(connection: sqlite3.Connection) -> Iterator[sqlite3.Row]:
    cursor = connection.cursor()
    for p in cursor.execute("SELECT * FROM ZMTPODCAST"):
        yield p


def podcasts_as_opml(connection: sqlite3.Connection) -> str:
    root = ET.fromstring('<opml version="1.0"></opml>')

    head = ET.SubElement(root, "head")
    ET.SubElement(head, "title").text = "MacOS Podcasts"

    body = ET.SubElement(root, "body")
    for p in podcasts(connection):
        ET.SubElement(
            body,
            "outline",
            attrib={
                "type": "rss",
                "text": p["ZTITLE"],
                "xmlUrl": p["ZFEEDURL"],
                "htmlUrl": p["ZWEBPAGEURL"],
            },
        )

    dom = minidom.parseString(ET.tostring(root, encoding="utf-8", method="xml"))
    return cast(str, dom.toprettyxml())


def main() -> None:
    home = Path("~").expanduser()
    db_file = next(home.glob(DB_FILE), None)

    if db_file is None:
        raise SystemExit(f"Unable to find database file {DB_FILE!r}.")
    try:
        connection = sqlite3.connect(db_file.as_posix())
    except OSError as e:
        raise SystemExit(f"Unable to open database file {db_file!r}: {e}")
    else:
        connection.row_factory = sqlite3.Row
        print(podcasts_as_opml(connection))


if __name__ == "__main__":
    main()
