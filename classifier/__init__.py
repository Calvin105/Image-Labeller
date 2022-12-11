from flask import Flask

app = Flask(__name__)
app.config["SECRET_KEY"] = "dbfb7366eb5b6ecfd2012f7ea69c64cf"

# Picture will be extracted only in static folder
static_extraction = "picture/default_folder"
relative_extraction = "classifier/static/" + static_extraction

# Remember to add newly created folder into LABELS
# "Label name": ["static", "picture/directory name"]
LABELS = {"None": None,
            "Fruits": ["static", "picture/fruits"],
            "Natural": ["static", "picture/natural"]
}
START_NUM = {k:0 for k in LABELS.keys()}
START_NUM["None"] = None
ZFILL = 3

from classifier import routes
