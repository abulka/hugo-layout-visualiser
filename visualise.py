import os
import re
from textwrap import dedent

THEME_PATH = "/Users/Andy/Devel/hugo_tests/quickstart/themes"
html_doc = os.path.join(THEME_PATH, "ananke/layouts/_default/baseof.html")

# from bs4 import BeautifulSoup
# with open(html_doc) as fp:
#     soup = BeautifulSoup(fp, 'html.parser')
# print(soup.prettify())
# for link in soup.find_all("link"):
#     print(link.get("href"))

partialRe = r'.*[partial|partialCached]\s"(.*)"\s.*'
finalPlantUML = ""
uml = ""

# back to basics
with open(html_doc) as fp:
    lines = fp.readlines()

for line in lines:
    if "partial" in line:
        line = line.strip()
        m = re.search(partialRe, line)
        if m:
            foundStr =m.group(1)
            partialFilenameNoExt = os.path.splitext(foundStr)[0]
            msg = f"✅ {line} / found match: {partialFilenameNoExt}"
        else:
            msg = f"❌ {line} / no match?"
        print(msg)
        uml += f'"baseof" - "{partialFilenameNoExt}"\n'

# uml = "X\n\tY"
uml = uml.rstrip()
finalPlantUML = f"""
@startuml "test-uml"
skinparam backgroundcolor Ivory/Azure

{uml}

@enduml
"""

print(finalPlantUML)
with open("out.wsd", "w") as fp:
    fp.write(finalPlantUML)

print("done")
