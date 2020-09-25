import glob
import os

from process_dir import processDir
from process_partial import processPartial
from settings import THEME_PATH, debug, buildDirStructure, scanForPartials
from stats import Stats
from theme import Theme


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
            umls += processDir(path, theme, stats)

    if scanForPartials:
        rootDir = os.path.join(themePath, f"{themeName}/layouts/") + '/**/*.html'
        for path in glob.iglob(rootDir, recursive=True):
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
