import glob
import os
import re
from textwrap import dedent
from dataclasses import dataclass  # requires 3.7
from dataclasses import field
from typing import List, Set, Dict, Tuple, Optional

THEME_PATH = "/Users/Andy/Devel/hugo_tests/quickstart/themes"

partialRe = r'(partial|partialCached)[\s\w\(]*\"([\w\.\-\/]+)\"\s'
finalPlantUML = ""
debug = False


def isReserved(path):
    return path in ["_default/single", "_default/baseof", "_default/list", "index",
                    "_default/taxonomy"]


def process(themeName, themePath, htmlPath, previousEntries, stats):
    """Process a single html file looking for 'partial' entries, returns a chunk of plantUML"""
    uml = ""
    themePathInclThemeName = os.path.join(themePath, themeName, "layouts")
    relPath = os.path.relpath(htmlPath, themePathInclThemeName)
    # print(relPath)

    # fromFileName = os.path.basename(htmlPath)
    fromFileName = relPath

    fromFileName = os.path.splitext(fromFileName)[0]
    with open(htmlPath) as fp:
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
                And if it doesn't exist, then it might be higher up the directory tree
                """
                partialFilenameNoExt = os.path.splitext(foundStr)[0]
                # what is its full path? its relative to the partials dir !
                # relDir = os.path.dirname(relPath)
                partialFilenameNoExt = os.path.join("partials", partialFilenameNoExt)

                if debug: print(f"✅ {line} / found match: {partialFilenameNoExt}")
                if isReserved(fromFileName):
                    connector = "--->"
                else:
                    connector = "..>"
                entry = f'"{fromFileName}" {connector} "{partialFilenameNoExt}"'
                if entry not in previousEntries:
                    previousEntries.append(entry)
                    uml += f'{entry}\n'
                    stats.add(fromFileName, partialFilenameNoExt)

                checkPathExists(fromFileName, partialFilenameNoExt, themePathInclThemeName)
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

@dataclass
class Stats:
    html_files: set = field(default_factory=set)
    partial_files: set = field(default_factory=set)

    # partial_dirs = []

    def isEmpty(self):
        return len(self.html_files) == 0 and len(self.partial_files) == 0

    def _add(self, path):
        head, tail = os.path.split(path)
        if head.split(os.path.sep)[0] == 'partials':
            self.partial_files.add(path)
        else:
            self.html_files.add(path)

    def add(self, fromFileName, partialFilenameNoExt):
        self._add(fromFileName)
        self._add(partialFilenameNoExt)

    def getUmlsForPartials(self):
        result = ""
        for path in self.partial_files:
            if isReserved(path):
                continue
            result += f'class "{path}" << (P,cornsilk) >> {{}}\n'
        return result

    def getUmlsForHtmlFiles(self):
        result = ""
        for path in self.html_files:
            if isReserved(path):
                continue
            result += f'class "{path}" << (H, cadetblue) >> {{}}\n'
        return result

    def report(self):
        return f"""
        FILES {self.html_files}

        PARTIALS {self.partial_files}
        """


def scan(theme, themePath=THEME_PATH):
    umls = ""
    stats = Stats()
    previousEntries = []

    assert stats.isEmpty()

    rootDir = os.path.join(themePath, f"{theme}/layouts/") + '/**/*.html'
    for path in glob.iglob(rootDir, recursive=True):
        if debug: print(themePath, path)
        umls += process(theme, themePath, path, previousEntries, stats)

    finalPlantUML = f"""
@startuml "test-uml"
skinparam backgroundcolor Ivory/Azure
title Theme {theme}

{umls.rstrip()}

class "_default/single" << (S,#FF7700) >>
class "_default/list" << (L,#248811) >>
class "_default/taxonomy" << (T,red) >>
class "_default/baseof" << (B,orchid) >>
class index << (I,yellow) >>

{stats.getUmlsForPartials()}
{stats.getUmlsForHtmlFiles()}

hide empty members

@enduml
    """
    # print(finalPlantUML)
    with open(f"out_{theme}.wsd", "w") as fp:
        fp.write(finalPlantUML.lstrip())

    if debug:
        print(umls)
        print(stats.report())


scan("ananke")
scan("toha")
scan("zzo")

print("done")
