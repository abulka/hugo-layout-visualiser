import glob


def isReserved(path):
    return path in ["_default/single", "_default/baseof", "_default/list", "index",
                    "_default/taxonomy"]


# unused at the moment
def fileExistsLooseMatch(filename):
    return bool(glob.glob(filename))
