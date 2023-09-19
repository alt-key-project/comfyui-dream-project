# -*- coding: utf-8 -*-
import glob

from .categories import NodeCategories
from .shared import *
from .types import *


class DreamFrameCounterInfo:
    NODE_NAME = "Frame Counter Info"
    ICON = "⚋"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.frame_counter
        }

    CATEGORY = NodeCategories.ANIMATION
    RETURN_TYPES = ("INT", "INT", "BOOLEAN", "BOOLEAN", "FLOAT", "FLOAT", "FLOAT", "FLOAT")
    RETURN_NAMES = ("frames_completed", "total_frames", "first_frame", "last_frame",
                    "elapsed_seconds", "remaining_seconds", "total_seconds", "completion")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *v):
        return ALWAYS_CHANGED_FLAG

    def result(self, frame_counter: FrameCounter):
        return (frame_counter.current_frame,
                frame_counter.total_frames,
                frame_counter.is_first_frame,
                frame_counter.is_final_frame,
                frame_counter.current_time_in_seconds,
                frame_counter.remaining_time_in_seconds,
                frame_counter.total_time_in_seconds,
                frame_counter.current_time_in_seconds / max(0.01, frame_counter.total_time_in_seconds))


class DreamDirectoryFileCount:
    NODE_NAME = "File Count"
    ICON = "📂"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory_path": ("STRING", {"default": '', "multiline": False}),
                "patterns": ("STRING", {"default": '*.jpg|*.png|*.jpeg', "multiline": False}),
            },
        }

    CATEGORY = NodeCategories.ANIMATION
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("TOTAL",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *v):
        return ALWAYS_CHANGED_FLAG

    def result(self, directory_path, patterns):
        if not os.path.isdir(directory_path):
            return (0,)
        total = 0
        for pattern in patterns.split("|"):
            files = list(glob.glob(pattern, root_dir=directory_path))
            total += len(files)
        print("total " + str(total))
        return (total,)


class DreamFrameCounterOffset:
    NODE_NAME = "Frame Counter Offset"

    ICON = "±"

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

class DreamFrameCounterTimeOffset:
    NODE_NAME = "Frame Counter Time Offset"

    ICON = "±"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.frame_counter | {
                "offset_seconds": ("FLOAT", {"default": 0.0}),
            },
        }

    CATEGORY = NodeCategories.ANIMATION
    RETURN_TYPES = (FrameCounter.ID,)
    RETURN_NAMES = ("frame_counter",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, frame_counter, offset):
        return hashed_as_strings(frame_counter, offset)

    def result(self, frame_counter: FrameCounter, offset_seconds):
        offset = offset_seconds * frame_counter.frames_per_second
        return (frame_counter.incremented(offset),)


class DreamSimpleFrameCounter:
    NODE_NAME = "Frame Counter (Simple)"
    ICON = "⚋"

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
        return (FrameCounter(n, total_frames, frames_per_second),)


class DreamDirectoryBackedFrameCounter:
    NODE_NAME = "Frame Counter (Directory)"
    ICON = "⚋"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory_path": ("STRING", {"default": '', "multiline": False}),
                "pattern": ("STRING", {"default": '*', "multiline": False}),
                "indexing": (["numeric", "alphabetic order"],),
                "total_frames": ("INT", {"default": 100, "min": 2, "max": 24 * 3600 * 60}),
                "frames_per_second": ("INT", {"min": 1, "default": 30}),
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


class DreamFrameCountCalculator:
    NODE_NAME = "Frame Count Calculator"
    ICON = "⌛"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "hours": ("INT", {"min": 0, "default": 0, "max": 23}),
                "minutes": ("INT", {"min": 0, "default": 0, "max": 59}),
                "seconds": ("INT", {"min": 0, "default": 10, "max": 59}),
                "milliseconds": ("INT", {"min": 0, "default": 0, "max": 59}),
                "frames_per_second": ("INT", {"min": 1, "default": 30})
            },
        }

    CATEGORY = NodeCategories.ANIMATION
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("TOTAL",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *v):
        return ALWAYS_CHANGED_FLAG

    def result(self, hours, minutes, seconds, milliseconds, frames_per_second):
        total_s = seconds + 0.001 * milliseconds + minutes * 60 + hours * 3600
        return (round(total_s * frames_per_second),)
