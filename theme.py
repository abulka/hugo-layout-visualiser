import os
from dataclasses import dataclass


@dataclass
class Theme:
    name: str
    path: str

    @property
    def layoutDirAbs(self):
        return os.path.join(self.path, self.name, "layouts")
