import glob
import os
import re
from typing import List

from styles import dirLineColour, partialLineColour
from stats import Stats
from theme import Theme
from util import isReserved

THEME_PATH = "/Users/Andy/Devel/hugo_tests/quickstart/themes"  # iMac
# THEME_PATH = "/Users/Andy/Devel/hugo_tests/hugo-bare1/themes"  # macbook air
partialRe = r'(partial|partialCached)[\s\w\(]*\"([\w\.\-\/]+)\"\s'
debug = False
buildDirStructure = True
scanForPartials = True


def processDir(path, theme: Theme, stats: Stats):
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


def process(file: str, theme: Theme, relationshipEntries: List, stats: Stats):
    """Process a single html file looking for 'partial' entries, returns a chunk of plantUML"""
    uml = ""
    layoutDirPathAbs = theme.layoutDirAbs
    relPath = os.path.relpath(file, layoutDirPathAbs)
    partialHtmlFile = relPath
    # relDir = os.path.dirname(relPath)

    with open(file) as fp:
        lines = fp.readlines()
    for line in lines:
        if "partial" in line:
            line = line.strip()
            m = re.search(partialRe, line)
            if m:
                foundStr = m.group(2)
                if len(foundStr.split(' ')) > 1:
                    print(f"skipping difficult line {m.group(0)}")
                    continue

                """
                this is the tricky bit.
                where is the partial? we have a basename only at this point.
                what is its full path? its relative to the partials dir !
                And if it doesn't exist, then it might be higher up the directory tree?
                """
                partialFilePath = os.path.join("partials", foundStr)
                if debug: print(f"✅ {line} / found match: {partialFilePath}")
                if isReserved(partialHtmlFile):
                    connector = "*..>"
                else:
                    connector = f".{partialLineColour}.>"
                entry = f'"{partialHtmlFile}" {connector} "{partialFilePath}"'
                # entry += " : {{ partial }}"
                if entry not in relationshipEntries:
                    relationshipEntries.append(entry)
                    uml += f'{entry}\n'
                    stats.add(partialHtmlFile, partialFilePath)

                checkPartialFilePathsExists(partialHtmlFile, partialFilePath, layoutDirPathAbs)
            else:
                if debug: print(f"❌ {line} / no match?")

    return uml


def fileExistsLooseMatch(filename):
    return bool(glob.glob(filename))


def checkPartialFilePathsExists(partialHtmlFile, partialFilePath, layoutDirPathAbs):
    _fromFile = os.path.join(layoutDirPathAbs, partialHtmlFile)
    if not os.path.exists(_fromFile):
        print(f"missing from: {_fromFile}")

    _toFile = os.path.join(layoutDirPathAbs, partialFilePath)
    if not os.path.exists(_toFile):
        print(f"missing to: {_toFile}")


def scan(themeName, themePath=THEME_PATH):
    """Main entry point, scans the `theme` at `themePath` and writes a file
    of plantUML representing the them structure to `theme_out.wsd`
    """
    umls = ""
    stats = Stats()
    relationshipEntries = []
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
            umls += process(path, theme, relationshipEntries, stats)

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
