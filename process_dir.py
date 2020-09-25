import os

from stats import Stats
import styles
from theme import Theme
import settings


def processDir(path: str, theme: Theme, stats: Stats):
    relPath = os.path.relpath(path, theme.layoutDirAbs)
    relDir = os.path.dirname(relPath)

    # trailing / needed to connect up child directories in directory structure
    if os.path.isdir(path):
        relPath = f"{relPath}/"

    # change root of visualisation tree from / to layouts/
    if relDir == "":
        relDir = "layouts"

    # Add the 'from' Dir
    relDir += "/"
    stats.addDir(relDir)

    # Add the 'to' Dir or File - creates potential orphan nodes?
    if os.path.isfile(path):
        stats.add(relPath)
    else:
        stats.addDir(relPath)

    # Clever stuff about hidePartialsDirStructure
    if settings.hidePartialsDirStructure:
        if relDir == "partials" and os.path.isfile(path):
            return ""
        if "partials/" in relDir and os.path.isfile(path):
            return ""

    entry = f'"{relDir}" -{styles.dirLineColour}- "{relPath}"\n'
    if settings.debug:
        debugMsg = ""
        if os.path.isdir(path):
            debugMsg = f"(DIR -- DIR connection)"
        print(f'processDir: "{relDir}" -- "{relPath}" {debugMsg}')

    return entry
