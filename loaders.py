from PIL import Image
from .types import SharedTypes, FrameCounter
from .shared import ALWAYS_CHANGED_FLAG, list_images_in_directory, convertFromPIL
from .categories import NodeCategories
import os

class DreamImageSequenceInputWithDefaultFallback:
    NODE_NAME = "Image Sequence Loader"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.frame_counter | {
                "directory_path": ("STRING", {"default": '', "multiline": False}),
                "pattern": ("STRING", {"default": '*', "multiline": False}),
                "indexing": (["numeric", "alphabetic order"],)
            },
            "optional": {
                "default_image": ("IMAGE", {"default": None})
            }
        }

    CATEGORY = NodeCategories.IMAGE_ANIMATION
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "filename")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, frame_counter: FrameCounter, directory_path, pattern, indexing, **other):
        default_image = other.get("default_image", None)
        entries = list_images_in_directory(directory_path, pattern, indexing == "alphabetic order")
        entry = entries.get(frame_counter.current_frame, None)
        if not entry:
            return (default_image, "")
        else:
            return (convertFromPIL(Image.open(entry)), os.path.basename(entry))
