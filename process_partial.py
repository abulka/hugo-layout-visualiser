import os
import re

from settings import partialRe, debug
from stats import Stats
import styles
from theme import Theme
import os


def ensureHtmlExt(foundStr, theme):
    """
    Though might get something like
        {{ partial (print "svgs/etc/" .type ".svg") (dict "width" 23 "height" 23) }}
    which produces
        "svgs/etc/"
    because the parser is just a dumb regular expression, not a proper 'go' template parser.
    So that's not a .html file its a dir, what to do?

    :param foundStr:
    :param theme: theme instance, needed for theme.layoutDirAbs
    :return:
    """
    filename, file_extension = os.path.splitext(foundStr)
    if not file_extension:
        # could be shorthand reference to a .html file or a partial with go syntax we cannot parse
        possiblePartialDir = os.path.join(theme.layoutDirAbs, "partials", foundStr)
        possiblePartialHtmlFile = possiblePartialDir + ".html"

        if os.path.isfile(possiblePartialHtmlFile):
            result = foundStr + ".html"  # repaired ok
        elif os.path.isdir(possiblePartialDir):
            raise RuntimeWarning(f"bad partials ref {foundStr} is a dir, giving up")
        else:
            raise RuntimeWarning(f"unknown partials ref {foundStr}, giving up")
    else:
        result = foundStr  # no repair needed
    return result


def getToPartial(line, theme):
    """Scan text line for the phrase {{ partial nnnn }} and return nnnn or None.
    None means there was no partial in that line. An exception means there was one
    but we couldn't figure it out (need proper go template parser).
    """
    line = line.strip()
    m = re.search(partialRe, line)
    if m:
        foundStr = m.group(2)
        if len(foundStr.split(' ')) > 1:
            raise RuntimeWarning(f"skipping difficult line {m.group(0)}")
        if debug:
            print(f"✅ {line} / found match: {foundStr}")
        foundStr = ensureHtmlExt(foundStr, theme)
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
                toPartial = getToPartial(line, theme)
            except RuntimeWarning as e:
                print(e)
                continue
            if toPartial is not None:
                toFilePath = os.path.join("partials", toPartial)
                entry = stats.addRelationship(fromFilePath, toFilePath)
                checkPartialFilePathsExists(fromFilePath, toFilePath, theme.layoutDirAbs)
                if entry:
                    uml += f'{entry}\n'
    return uml


def checkPartialFilePathsExists(fromFilePath, toFilePath, layoutDirPathAbs):
    _fromFile = os.path.join(layoutDirPathAbs, fromFilePath)
    if not os.path.exists(_fromFile):
        print(f"missing from: {_fromFile}")

    _toFile = os.path.join(layoutDirPathAbs, toFilePath)
    if not os.path.exists(_toFile):
        print(f"missing to: {_toFile} toFilePath={toFilePath}")
