from PIL import Image
import torch
import numpy
from .types import SharedTypes
from .util import ALWAYS_CHANGED_FLAG
import os
import glob


class AKPInputImageLoader:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.current_frame | {
                "directory_path": ("STRING", {"default": '', "multiline": False}),
                "pattern": ("STRING", {"default": '*', "multiline": False}),
            },
        }

    CATEGORY = "AKP Animation/Loaders"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "filename")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def list_directory_entries(self, directory_path, pattern):
        if not os.path.isdir(directory_path):
            return []
        files = []
        for file_name in glob.glob(os.path.join(directory_path, pattern), recursive=True):
            if file_name.lower().endswith(('.jpeg', '.jpg', '.png', '.tiff', '.gif', '.bmp', '.webp')):
                files.append(os.path.abspath(file_name))
        files.sort()
        return files

    def load_file(self, path):
        pil_image = Image.open(path)
        return torch.from_numpy(numpy.array(pil_image).astype(numpy.float32) / 255.0).unsqueeze(0)

    def result(self, current_frame, directory_path, pattern):
        entries = self.list_directory_entries(directory_path, pattern)
        if not entries:
            return (None, None)
        entry = entries[min(len(entries) - 1, max(0, current_frame))]
        print("LOAD {}".format(entry))
        image = self.load_file(entry)
        return (image, os.path.basename(entry))
