# Tip: bold breaks the dotted lines and makes them solid unless you re-specify dotted or dashed here

dirColour = "lightgrey"
dirIconColour = "silver"
dirBorderColour = "grey"
# dirLineColour = "[bold,#grey]"
dirLineColour = "[#grey,dashed]"

htmlColour = "beige"
htmlIconColour = "cadetblue"
htmlBorderColour = "cadetblue"
# htmlLineColour = "cadetblue"
cadetblue = "#6BA9AA"
cadetblueDarker = "#548485"

partialColour = "cornsilk"
partialIconColour = "cornsilk"
partialsBorderColour = "LightCoral"
# partialLineColour = f"[bold,{cadetblueDarker},dashed]"
partialLineColour = f"[{cadetblueDarker}]"

reservedUmlClasses = """
class "_default/single.html" << (S,#FF7700) >>
class "_default/list.html" << (L,#248811) >>
class "_default/taxonomy.html" << (T,red) >>
class "_default/baseof.html" << (B,orchid) >>
class "index.html" << (I,yellow) >>

class "_default/" << (_,red) >>
class "partials/" << (P,orange) >>
"""
