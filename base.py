import random

from .util import ALWAYS_CHANGED_FLAG, list_images_in_directory

_FRAME_COUNTER_TYPE = "SEQUENCE_CONTEXT"


class AKPSimpleFrameCounter:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frame_index": ("INT", {"min": 0, "default": 0}),
                "total_frames": ("INT", {"default": 100, "min": 1, "max": 24 * 3600 * 60}),
            },
        }

    CATEGORY = "AKP Animation"
    RETURN_TYPES = ("FRAME_COUNTER", "FRAME_PROGRESS")
    RETURN_NAMES = ("frame_counter", "frame_progress")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, frame_index, total_frames):
        n = frame_index
        return (n, float(n) / (max(2, total_frames) - 1))


class AKPDirectoryBackedFrameCounter:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory_path": ("STRING", {"default": '', "multiline": False}),
                "pattern": ("STRING", {"default": '*', "multiline": False}),
                "indexing": (["numeric", "alphabetic order"],),
                "total_frames": ("INT", {"default": 100, "min": 2, "max": 24 * 3600 * 60}),
            },
        }

    CATEGORY = "AKP Animation"
    RETURN_TYPES = ("FRAME_COUNTER", "FRAME_PROGRESS")
    RETURN_NAMES = ("frame_counter", "frame_progress")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, directory_path, pattern, indexing, total_frames):
        results = list_images_in_directory(directory_path, pattern, indexing == "alphabetic order")
        if not results:
            return (0, 0.0)
        n = max(results.keys()) + 1
        return (n, float(n) / (max(2, total_frames) - 1))
