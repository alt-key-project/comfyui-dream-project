from .categories import NodeCategories
from .shared import *
from .types import *


class DreamDirectoryBackedFrameTotal:
    NODE_NAME = "Frame Total (Directory)"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory_path": ("STRING", {"default": '', "multiline": False}),
                "pattern": ("STRING", {"default": '*', "multiline": False}),
                "indexing": (["numeric", "alphabetic order"],),
            },
        }

    CATEGORY = NodeCategories.ANIMATION
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("TOTAL",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *v):
        return ALWAYS_CHANGED_FLAG

    def result(self, directory_path, pattern, indexing):
        items = list_images_in_directory(directory_path, pattern, indexing == "alphabetic order")
        return (max(items.keys()),)


class DreamFrameCounterOffset:
    NODE_NAME = "Frame Counter Offset"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.frame_counter | {
                "offset": ("INT", {"default": -1}),
            },
        }

    CATEGORY = NodeCategories.ANIMATION
    RETURN_TYPES = (FrameCounter.ID,)
    RETURN_NAMES = ("frame_counter",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, frame_counter, offset):
        return hashed_as_strings(frame_counter, offset)

    def result(self, frame_counter: FrameCounter, offset):
        return (frame_counter.incremented(offset),)


class DreamSimpleFrameCounter:
    NODE_NAME = "Frame Counter (Simple)"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frame_index": ("INT", {"min": 0, "default": 0}),
                "total_frames": ("INT", {"default": 100, "min": 1, "max": 24 * 3600 * 60}),
                "frames_per_second": ("INT", {"min": 1, "default": 25}),
            },
        }

    CATEGORY = NodeCategories.ANIMATION
    RETURN_TYPES = (FrameCounter.ID,)
    RETURN_NAMES = ("frame_counter",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, frame_index, total_frames, frames_per_second):
        n = frame_index
        return (FrameCounter(n, float(n) / (max(2, total_frames) - 1)), frames_per_second)


class DreamDirectoryBackedFrameCounter:
    NODE_NAME = "Frame Counter (Directory)"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory_path": ("STRING", {"default": '', "multiline": False}),
                "pattern": ("STRING", {"default": '*', "multiline": False}),
                "indexing": (["numeric", "alphabetic order"],),
                "total_frames": ("INT", {"default": 100, "min": 2, "max": 24 * 3600 * 60}),
                "frames_per_second": ("INT", {"min": 1, "default": 25}),
            },
        }

    CATEGORY = NodeCategories.ANIMATION
    RETURN_TYPES = (FrameCounter.ID,)
    RETURN_NAMES = ("frame_counter",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, directory_path, pattern, indexing, total_frames, frames_per_second):
        results = list_images_in_directory(directory_path, pattern, indexing == "alphabetic order")
        if not results:
            return (FrameCounter(0, total_frames, frames_per_second),)
        n = max(results.keys()) + 1
        return (FrameCounter(n, total_frames, frames_per_second),)
