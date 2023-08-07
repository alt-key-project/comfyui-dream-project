from PIL import Image
import torch
import numpy
from .types import SharedTypes
from .util import ALWAYS_CHANGED_FLAG, list_images_in_directory
import os


def _load_file(path):
    pil_image = Image.open(path)
    return torch.from_numpy(numpy.array(pil_image).astype(numpy.float32) / 255.0).unsqueeze(0)


class AKPImageSequenceInput:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.frame_counter | {
                "directory_path": ("STRING", {"default": '', "multiline": False}),
                "pattern": ("STRING", {"default": '*', "multiline": False}),
                "indexing": (["numeric", "alphabetic order"],)
            }
        }

    CATEGORY = "AKP Animation/IO"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "filename")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, frame_counter, directory_path, pattern, indexing):
        entries = list_images_in_directory(directory_path, pattern, indexing == "alphabetic order")
        entry = entries.get(frame_counter, None)
        if not entry:
            return (None, None)
        else:
            return (_load_file(entry), os.path.basename(entry))


class AKPImageSequenceInputWithDefaultFallback:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.frame_counter | {
                "directory_path": ("STRING", {"default": '', "multiline": False}),
                "pattern": ("STRING", {"default": '*', "multiline": False}),
                "indexing": (["numeric", "alphabetic order"],),
                "default_image": ("IMAGE", {"default": None})
            }
        }

    CATEGORY = "AKP Animation/IO"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "filename")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, frame_counter, directory_path, pattern, default_image, indexing):
        entries = list_images_in_directory(directory_path, pattern, indexing == "alphabetic order")
        entry = entries.get(frame_counter, None)
        if not entry:
            return (default_image, "")
        else:
            return (_load_file(entry), os.path.basename(entry))
