import glob
import os
import re
from textwrap import dedent

THEME_PATH = "/Users/Andy/Devel/hugo_tests/quickstart/themes"

partialRe = r'.*[partial|partialCached]\s"(.*)"\s.*'
finalPlantUML = ""
debug = False
previousEntries = []


def process(htmlPath):
    uml = ""
    # fromFileName = os.path.basename(htmlPath)
    fromFileName = htmlPath
    fromFileName = os.path.splitext(fromFileName)[0]
    with open(htmlPath) as fp:
        lines = fp.readlines()

    for line in lines:
        if "partial" in line:
            line = line.strip()
            m = re.search(partialRe, line)
            if m:
                foundStr = m.group(1)
                if len(foundStr.split(' ')) > 1:
                    print(f"skipping difficult line {m.group(0)}")
                    continue
                partialFilenameNoExt = os.path.splitext(foundStr)[0]
                if debug: print(f"✅ {line} / found match: {partialFilenameNoExt}")
                if fromFileName in ["single", "baseof", "list", "index"]:
                    connector = "--->"
                else:
                    connector = "..>"
                entry = f'"{fromFileName}" {connector} "{partialFilenameNoExt}"'
                if entry not in previousEntries:
                    previousEntries.append(entry)
                    uml += f'{entry}\n'
            else:
                if debug: print(f"❌ {line} / no match?")
    return uml


# Now recurse

def scan(theme):
    umls = ""

    rootDir = os.path.join(THEME_PATH, f"{theme}/layouts/") + '/**/*.html'
    for path in glob.iglob(rootDir, recursive=True):
        if debug: print(path)
        umls += process(path)

    finalPlantUML = f"""
@startuml "test-uml"
skinparam backgroundcolor Ivory/Azure

{umls.rstrip()}

class single << (S,#FF7700) _default >>
class list << (L,#248811) _default >>
class baseof << (B,orchid) >>
class index << (I,yellow) >>

@enduml
    """
    # print(finalPlantUML)
    with open(f"out_{theme}.wsd", "w") as fp:
        fp.write(finalPlantUML.lstrip())

scan("ananke")
scan("toha")
scan("zzo")

print("done")
