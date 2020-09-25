import os
from dataclasses import dataclass, field

import styles
from util import isReserved
from typing import List


@dataclass
class Stats:
    """
    Simply records the files encountered, sorting them into two sets
    so that we can later emit a list files in PlantUML syntax, each with
    a unique annotation. Partials get "P" and Html files get "H".

    Need to know which files made it into the relationships, and suppress the
    orphans when generating the uml.

    """
    relationshipEntries: List = field(default_factory=list)  # just for de-duping

    dirNodes: List = field(default_factory=list)

    html_files: set = field(default_factory=set)
    partial_files: set = field(default_factory=set)

    def addRelationship(self, fromFilePath, toFilePath):
        # TODO mark the relevant html_files/partial_files as 'in a relationship'

        if isReserved(fromFilePath):
            connector = "*--->"
        else:
            connector = f"--{styles.partialLineColour}->"

        entry = f'"{fromFilePath}" {connector} "{toFilePath}"'

        if entry not in self.relationshipEntries:
            self.relationshipEntries.append(entry)
            self.add(fromFilePath)
            self.add(toFilePath)
            return entry
        else:
            return None

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
            result += f'class "{_dir}" << (D,{styles.dirIconColour}) dir >> {{}}\n'
        return result

    def getUmlsForPartials(self):
        result = ""
        for path in self.partial_files:
            if isReserved(path):
                continue
            result += f'class "{path}" << (P,{styles.partialIconColour}) partial >> {{}}\n'
        return result

    def getUmlsForHtmlFiles(self):
        result = ""
        for path in self.html_files:
            if isReserved(path):
                continue
            result += f'class "{path}" << (H, {styles.htmlIconColour}) html >> {{}}\n'
        return result

    def report(self):
        return f"""
        FILES {self.html_files}

        PARTIALS {self.partial_files}
        """
