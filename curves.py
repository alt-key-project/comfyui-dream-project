import math, csv

from .types import SharedTypes, FrameCounter
from .shared import hashed_as_strings
from .categories import NodeCategories


class DreamSineWave:
    NODE_NAME = "Sine Curve"

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


class DreamBeatCurve:
    NODE_NAME = "Beat Curve"


    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.frame_counter | {
                "bpm": ("FLOAT", {"default": 100.0, "multiline": False}),
                "measure_length": ("INT", {"default": 4, "min": 1}),
                "low_value": ("FLOAT", {"default": 0.0}),
                "high_value": ("FLOAT", {"default": 1.0}),
                "invert": (["no", "yes"]),
                "power": ("FLOAT", {"default": 2.0, "min": 0.25, "max": 4}),
                "accent_1": ("INT", {"default": 1, "min": 1, "max": 24}),
            },
            "optional": {
                "accent_2": ("INT", {"default": 3, "min": 1, "max": 24}),
                "accent_3": ("INT", {"default": 0}),
                "accent_4": ("INT", {"default": 0}),
            }
        }

    CATEGORY = NodeCategories.ANIMATION_CURVES
    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("FLOAT",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(*values)

    def _get_value_for_accent(self, accent, measure_length, bpm, frame_counter: FrameCounter):
        frames_per_minute = frame_counter.frames_per_second * 60.0
        frames_per_beat = frames_per_minute / bpm
        frames_per_measure = frames_per_beat * measure_length
        frame = (frame_counter.current_frame % frames_per_measure)
        accent_start = (accent - 1) * frames_per_beat
        accent_end = accent * frames_per_beat
        if frame >= accent_start and frame < accent_end:
            return 1.0 - ((frame - accent_start) / frames_per_beat)
        return 0

    def result(self, bpm, frame_counter: FrameCounter, measure_length, low_value, high_value, power, invert, **accents):
        accents_set = set(filter(lambda v: v >= 1 and v <= measure_length,
                                 map(lambda i: accents.get("accent_" + str(i), -1), range(30))))
        v = 0.0
        for a in accents_set:
            v += math.pow(self._get_value_for_accent(a, measure_length, bpm, frame_counter), power)
        if invert == "yes":
            v = 1.0 - v

        return (low_value + v * (high_value - low_value),)


class DreamLinear:
    NODE_NAME = "Linear Curve"

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


def _is_as_float(s: str):
    try:
        float(s)
        return True
    except ValueError:
        return False


class DreamCSVGenerator:
    NODE_NAME = "CSV Generator"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.frame_counter | {
                "value": ("FLOAT", ),
                "csvfile": ("STRING",),
                "csv_dialect": (csv.list_dialects(),)
            },
        }

    CATEGORY = NodeCategories.ANIMATION_CURVES
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(*values)

    def result(self, csvfile, frame_counter: FrameCounter, value, csv_dialect):
        if frame_counter.is_first_frame and csvfile:
            with open(csvfile, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile, dialect=csv_dialect)
                csvwriter.writerow(['Frame', 'Value'])
                csvwriter.writerow([frame_counter.current_frame, str(value)])
        else:
            with open(csvfile, 'a', newline='') as csvfile:
                csvwriter = csv.writer(csvfile, dialect=csv_dialect)
                csvwriter.writerow([frame_counter.current_frame, str(value)])

class DreamCSVCurve:
    NODE_NAME = "CSV Curve"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.frame_counter | {
                "csvfile": ("STRING", {"default": "", "multiline": False}),
                "first_column_type": (["seconds", "frames"],),
                "interpolate": (["true", "false"],),
                "csv_dialect": (csv.list_dialects(),)
            },
        }

    CATEGORY = NodeCategories.ANIMATION_CURVES
    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("FLOAT",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(*values)

    def _row_yield(self, file, csv_dialect):
        prev_row = None
        for row in csv.reader(file, dialect=csv_dialect):
            if len(row) == 2 and _is_as_float(row[0]) and _is_as_float(row[1]):
                row = list(map(float, row))
                yield (prev_row, row)
                prev_row = row
        if prev_row is not None:
            yield (prev_row, None)

    def result(self, csvfile, frame_counter: FrameCounter, first_column_type, interpolate, csv_dialect):
        interpolate = interpolate == "true"

        def _first_col_to_frame(v: float):
            if first_column_type == "frames":
                return round(v)
            else:
                return round(v * frame_counter.frames_per_second)

        with open(csvfile) as f:
            for (prev, current) in self._row_yield(f, csv_dialect):
                if prev is None and frame_counter.current_frame < _first_col_to_frame(current[0]):
                    # before first row
                    return (current[1],)
                if current is None:
                    # after last row
                    return (prev[1],)
                if prev is not None and current is not None:
                    frame1 = _first_col_to_frame(prev[0])
                    value1 = prev[1]
                    frame2 = _first_col_to_frame(current[0])
                    value2 = current[1]
                    if frame1 <= frame_counter.current_frame and interpolate and frame2 > frame_counter.current_frame:
                        offset = (frame_counter.current_frame - frame1) / float(frame2 - frame1)
                        return (value1 * (1.0 - offset) + value2 * offset,)
                    elif frame1 <= frame_counter.current_frame and frame2 > frame_counter.current_frame:
                        return (value1,)
        return (0.0,)
