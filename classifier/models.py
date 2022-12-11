from PIL import Image
from os import stat, path

class ImageModel:
    def __init__(self, filepath):
        self.filepath = filepath
        self.label = "None"
        self.chg_filename = ""
        self._get_metadata()

    def _get_metadata(self):
        self.path, self.filename = path.split(self.filepath)
        self.name, self.extension = path.splitext(self.filename)
        with Image.open(self.filepath) as img:
            self.width, self.height = img.size

        self.size = stat(self.filepath).st_size // 1000

    def __repr__(self) -> str:
        return f"ImageModel(filepath='{self.filepath}', label='{self.label}', chg_filename='{self.chg_filename}')"