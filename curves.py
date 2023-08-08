import math

from .types import SharedTypes
from .shared import hashed_as_strings


class AKPSineWave:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.frame_counter | {
                "max_value": ("FLOAT", {"default": 1.0, "multiline": False}),
                "min_value": ("FLOAT", {"default": 0.0, "multiline": False}),
                "periodicity": ("INT", {"default": 10, "multiline": False, "min": 1}),
                "phase": ("FLOAT", {"default": 0.0, "multiline": False, "min": -1, "max": 1}),
            },
        }

    CATEGORY = "AKP Animation/Curves"
    RETURN_TYPES = ("FLOAT", "INT")
    RETURN_NAMES = ("FLOAT", "INT")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(*values)

    def result(self, frame_counter, max_value, min_value, periodicity, phase):
        a = (max_value - min_value) * 0.5
        v = min_value + 0.5 * a + \
            a * math.sin(phase * 2.0 * math.pi + float(frame_counter) / max(1, periodicity) * 2.0 * math.pi)
        return (v, int(round(v)))


class AKPLinear:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.frame_progress | {
                "initial_value": ("FLOAT", {"default": 0.0, "multiline": False}),
                "final_value": ("FLOAT", {"default": 100.0, "multiline": False}),
            },
        }

    CATEGORY = "AKP Animation/Curves"
    RETURN_TYPES = ("FLOAT", "INT")
    RETURN_NAMES = ("FLOAT", "INT")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(*values)

    def result(self, initial_value, final_value, frame_progress):
        d = final_value - initial_value
        v = initial_value + frame_progress * d
        return (v, int(round(v)))
