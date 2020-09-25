import os
from dataclasses import dataclass, field

from styles import dirShapeColour, partialsShapeColour
from util import isReserved
from typing import List


@dataclass
class Stats:
    """
    Simply records the files encountered, sorting them into two sets
    so that we can later emit a list files in PlantUML syntax, each with
    a unique annotation. Partials get "P" and Html files get "H".
    """
    relationshipEntries: List = field(default_factory=list)  # just for de-duping

    dirNodes: List = field(default_factory=list)

    html_files: set = field(default_factory=set)
    partial_files: set = field(default_factory=set)

    # partial_dirs = []

    def isEmpty(self):
        return len(self.html_files) == 0 and len(self.partial_files) == 0

    def add(self, path):
        head, tail = os.path.split(path)
        if head.split(os.path.sep)[0] == 'partials':
            self.partial_files.add(path)
        else:
            self.html_files.add(path)

    def addDir(self, path: str):
        self.dirNodes.append(path)

    def getDirsUml(self):
        result = ""
        for _dir in self.dirNodes:
            result += f'class "{_dir}/" << (D,{dirShapeColour}) dir >> {{}}\n'
        return result

    def getUmlsForPartials(self):
        result = ""
        for path in self.partial_files:
            if isReserved(path):
                continue
            result += f'class "{path}" << (P,{partialsShapeColour}) layout >> {{}}\n'
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