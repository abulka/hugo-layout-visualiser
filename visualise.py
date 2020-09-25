import glob
import os
import re
from typing import List
from stats import Stats
from util import isReserved

THEME_PATH = "/Users/Andy/Devel/hugo_tests/quickstart/themes"  # iMac
# THEME_PATH = "/Users/Andy/Devel/hugo_tests/hugo-bare1/themes"  # macbook air
partialRe = r'(partial|partialCached)[\s\w\(]*\"([\w\.\-\/]+)\"\s'
debug = True
buildDirStructure = True
scanForPartials = True

# Tip: bold breaks the dotted lines and makes them solid unless you re-specify dotted or dashed here
# dirLineColour = "[bold,#grey]"
dirLineColour = "[#grey]"
# dirLineColour = ""
# partialLineColour = "[bold,#green]"
partialLineColour = "[bold,#6666ff,dashed]"

def processDirMode(path, theme, themePath, stats: Stats):
    themePathInclThemeName = os.path.join(themePath, theme, "layouts")
    relPath = os.path.relpath(path, themePathInclThemeName)
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


def process(file: str, themeName: str, themePath: str, relationshipEntries: List, stats: Stats):
    """Process a single html file looking for 'partial' entries, returns a chunk of plantUML"""
    uml = ""
    themePathInclThemeName = os.path.join(themePath, themeName, "layouts")
    relPath = os.path.relpath(file, themePathInclThemeName)
    # relPathNoExt = os.path.splitext(relPath)[0]
    relPathNoExt = relPath
    relDir = os.path.dirname(relPath)
    partialFilenameNoExt = "??"

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
                # partialFilenameNoExt = os.path.splitext(foundStr)[0]
                partialFilenameNoExt = foundStr
                partialFilenameNoExt = os.path.join("partials", partialFilenameNoExt)

                if debug: print(f"✅ {line} / found match: {partialFilenameNoExt}")
                if isReserved(relPathNoExt):
                    connector = "*..>"
                else:
                    connector = f".{partialLineColour}.>"
                entry = f'"{relPathNoExt}" {connector} "{partialFilenameNoExt}"'
                # entry += " : {{ partial }}"
                if entry not in relationshipEntries:
                    relationshipEntries.append(entry)
                    uml += f'{entry}\n'
                    stats.add(relPathNoExt, partialFilenameNoExt)

                checkPathExists(relPathNoExt, partialFilenameNoExt, themePathInclThemeName)
            else:
                if debug: print(f"❌ {line} / no match?")

    return uml


def fileExistsLooseMatch(filename):
    return bool(glob.glob(filename))


def checkPathExists(fromFileName, partialFilenameNoExt, themePathInclThemeName):
    _fromFile = os.path.join(themePathInclThemeName, fromFileName + '.html')
    if not os.path.exists(_fromFile):
        print(f"missing from: {_fromFile}")

    _toDir = os.path.join(themePathInclThemeName, partialFilenameNoExt)
    if os.path.isdir(_toDir):
        return
    # try again, to find actual file
    _toFile = os.path.join(themePathInclThemeName, partialFilenameNoExt + '.*')
    if not fileExistsLooseMatch(_toFile):
        print(f"missing to: directory {_toDir} or file {_toFile}")


# Now recurse


def scan(theme, themePath=THEME_PATH):
    """Main entry point, scans the `theme` at `themePath` and writes a file
    of plantUML representing the them structure to `theme_out.wsd`
    """
    umls = ""
    stats = Stats()
    relationshipEntries = []

    assert stats.isEmpty()

    if buildDirStructure:
        rootDir = os.path.join(themePath, f"{theme}/layouts/") + '/**/*'
        for path in glob.iglob(rootDir, recursive=True):
            if debug: print(f"dir mode: {path}")
            umls += processDirMode(path, theme, themePath, stats)

    if scanForPartials:
        rootDir = os.path.join(themePath, f"{theme}/layouts/") + '/**/*.html'
        for path in glob.iglob(rootDir, recursive=True):
            if debug: print(themePath, path)
            umls += process(path, theme, themePath, relationshipEntries, stats)

    finalPlantUML = f"""
@startuml "test-uml"
skinparam backgroundcolor Ivory/Azure
set namespaceSeparator none
title Theme {theme}

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
    with open(f"out/{theme}.wsd", "w") as fp:
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
