import math

from .types import SharedTypes, FrameCounter
from .shared import hashed_as_strings
from .categories import NodeCategories


class AKPSineWave:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.frame_counter | {
                "max_value": ("FLOAT", {"default": 1.0, "multiline": False}),
                "min_value": ("FLOAT", {"default": 0.0, "multiline": False}),
                "periodicity_seconds": ("FLOAT", {"default": 10.0, "multiline": False, "min": 0.01}),
                "phase": ("FLOAT", {"default": 0.0, "multiline": False, "min": -1, "max": 1}),
            },
        }

    CATEGORY = NodeCategories.ANIMATION_CURVES
    RETURN_TYPES = ("FLOAT", "INT")
    RETURN_NAMES = ("FLOAT", "INT")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(*values)

    def result(self, frame_counter: FrameCounter, max_value, min_value, periodicity_seconds, phase):
        periodicity = max(1, round(frame_counter.frames_per_second * periodicity_seconds))
        a = (max_value - min_value) * 0.5
        v = min_value + 0.5 * a + \
            a * math.sin(phase * 2.0 * math.pi + float(frame_counter.current_frame) / periodicity * 2.0 * math.pi)
        return (v, int(round(v)))


class AKPLinear:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.frame_counter | {
                "initial_value": ("FLOAT", {"default": 0.0, "multiline": False}),
                "final_value": ("FLOAT", {"default": 100.0, "multiline": False}),
            },
        }

    CATEGORY = NodeCategories.ANIMATION_CURVES
    RETURN_TYPES = ("FLOAT", "INT")
    RETURN_NAMES = ("FLOAT", "INT")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(*values)

    def result(self, initial_value, final_value, frame_counter: FrameCounter):
        d = final_value - initial_value
        v = initial_value + frame_counter.progress * d
        return (v, int(round(v)))
