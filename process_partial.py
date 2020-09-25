import os
import re

from settings import partialRe, debug
from stats import Stats
import styles
from theme import Theme
from util import isReserved


def getToPartial(line):
    """Scan text line for the phrase {{ partial nnnn }} and return nnnn or None."""
    line = line.strip()
    m = re.search(partialRe, line)
    if m:
        foundStr = m.group(2)
        if len(foundStr.split(' ')) > 1:
            raise RuntimeWarning(f"skipping difficult line {m.group(0)}")
        if debug:
            print(f"✅ {line} / found match: {foundStr}")
        return foundStr
    else:
        if debug:
            print(f"❌ {line} / no match?")
        return None


def processPartial(file: str, theme: Theme, stats: Stats):
    """Process a single html file looking for 'partial' entries, returns a chunk of plantUML"""
    if debug:
        print("processPartial", theme, file)

    uml = ""
    fromFilePath = os.path.relpath(file, theme.layoutDirAbs)

    with open(file) as fp:
        lines = fp.readlines()
    for line in lines:
        if "partial" in line:
            try:
                toPartial = getToPartial(line)
            except RuntimeWarning:
                continue
            if toPartial is not None:
                toFilePath = os.path.join("partials", toPartial)
                if isReserved(fromFilePath):
                    connector = "*..>"
                else:
                    connector = f".{styles.partialLineColour}.>"
                entry = f'"{fromFilePath}" {connector} "{toFilePath}"'
                if entry not in stats.relationshipEntries:
                    stats.relationshipEntries.append(entry)
                    stats.add(fromFilePath)
                    stats.add(toFilePath)
                    uml += f'{entry}\n'

                checkPartialFilePathsExists(fromFilePath, toFilePath, theme.layoutDirAbs)

    return uml


def checkPartialFilePathsExists(fromFilePath, toFilePath, layoutDirPathAbs):
    _fromFile = os.path.join(layoutDirPathAbs, fromFilePath)
    if not os.path.exists(_fromFile):
        print(f"missing from: {_fromFile}")

    _toFile = os.path.join(layoutDirPathAbs, toFilePath)
    if not os.path.exists(_toFile):
        print(f"missing to: {_toFile}")