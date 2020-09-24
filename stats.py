import os
from dataclasses import dataclass, field

from util import isReserved


@dataclass
class Stats:
    """
    Simply records the files encountered, sorting them into two sets
    so that we can later emit a list files in PlantUML syntax, each with
    a unique annotation. Partials get "P" and Html files get "H".
    """
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