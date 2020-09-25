import glob
import os

from process_dir import processDir
from process_partial import processPartial
from settings import THEME_PATH, debug, buildDirStructure, scanForPartials
from stats import Stats
from theme import Theme
import styles


def scan(themeName, themePath=THEME_PATH):
    """Main entry point, scans the `theme` at `themePath` and writes a file
    of plantUML representing the them structure to `theme_out.wsd`
    """
    umls = ""
    stats = Stats()
    theme = Theme(name=themeName, path=themePath)

    assert stats.isEmpty()

    rootDir = os.path.join(themePath, f"{themeName}/layouts/")
    assert os.path.exists(rootDir), f"no such dir {rootDir}"

    if buildDirStructure:
        for path in glob.iglob(rootDir + '/**/*', recursive=True):
            umls += processDir(path, theme, stats)

    if scanForPartials:
        for path in glob.iglob(rootDir + '/**/*.html', recursive=True):
            umls += processPartial(path, theme, stats)

    finalPlantUML = f"""
@startuml "test-uml"
skinparam backgroundcolor Ivory/Azure
set namespaceSeparator none
title Theme "{themeName}"

skinparam class {{ 
    BackgroundColor<<dir>> {styles.dirColour}
    BorderColor<<dir>> {styles.dirBorderColour}

    BackgroundColor<<html>> {styles.htmlColour}
    BorderColor<<html>> {styles.htmlBorderColour}

    BackgroundColor<<partial>> {styles.partialColour}
    BorderColor<<partial>> {styles.partialsBorderColour}
}}

{umls.rstrip()}

{styles.reservedUmlClasses}

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
scan("zzo")
# scan("docsy", "/Users/Andy/Devel/hugo_tests/docsy-example/themes/")
# scan("diagnostic-andy", "/Users/Andy/Devel/hugo_tests/hugo-bare1/themes/")
# scan("example_theme", "/Users/Andy/Devel/hugo_tests/hugo-layout-visualiser/")

print("done")
