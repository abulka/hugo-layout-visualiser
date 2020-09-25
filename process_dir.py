import os

from stats import Stats
from styles import dirLineColour
from theme import Theme
import settings


def processDir(path: str, theme: Theme, stats: Stats):
    if settings.debug:
        print(f"processDir: {path}")

    relPath = os.path.relpath(path, theme.layoutDirAbs)
    relDir = os.path.dirname(relPath)
    if os.path.isfile(path):
        stats.add(relPath)
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
