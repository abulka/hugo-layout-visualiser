import os
from dataclasses import dataclass, field

from styles import dirShapeColour, partialsShapeColour
from util import isReserved
from typing import List


@dataclass
class Theme:
    name: str
    path: str

    @property
    def layoutDirAbs(self):
        return os.path.join(self.path, self.name, "layouts")
