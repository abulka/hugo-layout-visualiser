import glob
import os
import re

from settings import THEME_PATH, partialRe, debug, buildDirStructure, scanForPartials
from styles import dirLineColour, partialLineColour
from stats import Stats
from theme import Theme
from util import isReserved


def processDir(path: str, theme: Theme, stats: Stats):
    relPath = os.path.relpath(path, theme.layoutDirAbs)
    relDir = os.path.dirname(relPath)
    if "." not in relPath:
        relPath = f"{relPath}/"
    if relDir == "":
        relDir = "layouts"
    stats.addDir(relDir)
    if relDir == "partials" and os.path.isfile(path):
        return ""
    if "partials/" in relDir and os.path.isfile(path):
        return ""
    return f'"{relDir}/" -{dirLineColour}- "{relPath}"\n'


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
                    connector = f".{partialLineColour}.>"
                entry = f'"{fromFilePath}" {connector} "{toFilePath}"'
                # entry += " : {{ partial }}"
                if entry not in stats.relationshipEntries:
                    stats.relationshipEntries.append(entry)
                    uml += f'{entry}\n'
                    stats.add(fromFilePath, toFilePath)

                checkPartialFilePathsExists(fromFilePath, toFilePath, theme.layoutDirAbs)

    return uml


def checkPartialFilePathsExists(fromFilePath, toFilePath, layoutDirPathAbs):
    _fromFile = os.path.join(layoutDirPathAbs, fromFilePath)
    if not os.path.exists(_fromFile):
        print(f"missing from: {_fromFile}")

    _toFile = os.path.join(layoutDirPathAbs, toFilePath)
    if not os.path.exists(_toFile):
        print(f"missing to: {_toFile}")


def scan(themeName, themePath=THEME_PATH):
    """Main entry point, scans the `theme` at `themePath` and writes a file
    of plantUML representing the them structure to `theme_out.wsd`
    """
    umls = ""
    stats = Stats()
    theme = Theme(name=themeName, path=themePath)

    assert stats.isEmpty()

    if buildDirStructure:
        rootDir = os.path.join(themePath, f"{themeName}/layouts/") + '/**/*'
        for path in glob.iglob(rootDir, recursive=True):
            if debug: print(f"dir mode: {path}")
            umls += processDir(path, theme, stats)

    if scanForPartials:
        rootDir = os.path.join(themePath, f"{themeName}/layouts/") + '/**/*.html'
        for path in glob.iglob(rootDir, recursive=True):
            if debug: print(themePath, path)
            umls += processPartial(path, theme, stats)

    finalPlantUML = f"""
@startuml "test-uml"
skinparam backgroundcolor Ivory/Azure
set namespaceSeparator none
title Theme "{themeName}"

skinparam class {{ 
    BackgroundColor<<dir>> antiquewhite
    BackgroundColor<<layout>> white
}}

{umls.rstrip()}

class "_default/single.html" << (S,#FF7700) >>
class "_default/list.html" << (L,#248811) >>
class "_default/taxonomy.html" << (T,red) >>
class "_default/baseof.html" << (B,orchid) >>
class "index.html" << (I,yellow) >>

class "_default/" << (_,red) >>
class "partials/" << (P,orange) >>

{stats.getUmlsForPartials()}
{stats.getUmlsForHtmlFiles()}
{stats.getDirsUml()}

hide empty members

@enduml
    """
    # print(finalPlantUML)
    with open(f"out/{themeName}.wsd", "w") as fp:
        fp.write(finalPlantUML.lstrip())

    if debug:
        print(umls)
        print(stats.report())


scan("ananke")
# scan("toha")
# scan("zzo")
# scan("docsy", "/Users/Andy/Devel/hugo_tests/docsy-example/themes/")
# scan("diagnostic-andy", "/Users/Andy/Devel/hugo_tests/hugo-bare1/themes/")
scan("example_theme", "/Users/Andy/Devel/hugo_tests/hugo-layout-visualiser/")

print("done")
