import glob
import os
import re
from textwrap import dedent

THEME_PATH = "/Users/Andy/Devel/hugo_tests/quickstart/themes"

partialRe = r'.*[partial|partialCached]\s"(.*)"\s.*'
finalPlantUML = ""
debug = False


def process(htmlPath):
    uml = ""
    fromFileName = os.path.basename(htmlPath)
    fromFileName = os.path.splitext(fromFileName)[0]
    with open(htmlPath) as fp:
        lines = fp.readlines()

    for line in lines:
        if "partial" in line:
            line = line.strip()
            m = re.search(partialRe, line)
            if m:
                foundStr = m.group(1)
                partialFilenameNoExt = os.path.splitext(foundStr)[0]
                if debug: print(f"✅ {line} / found match: {partialFilenameNoExt}")
                uml += f'"{fromFileName}" - "{partialFilenameNoExt}"\n'
            else:
                if debug: print(f"❌ {line} / no match?")
    return uml


# Now recurse

umls = ""
# umls += process(os.path.join(THEME_PATH, "ananke/layouts/_default/baseof.html"))

rootDir = os.path.join(THEME_PATH, "ananke/layouts/") + '/**/*.html'
for path in glob.iglob(rootDir, recursive=True):
    if debug: print(path)
    umls += process(path)

finalPlantUML = f"""
@startuml "test-uml"
skinparam backgroundcolor Ivory/Azure

{umls}

@enduml
"""
# print(finalPlantUML)
with open("out.wsd", "w") as fp:
    fp.write(finalPlantUML)

print("done")
