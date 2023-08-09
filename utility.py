from .shared import hashed_as_strings
import math

def _align_num(n: int, alignment: int, type: str):
    if alignment <= 1:
        return n
    if type == "ceil":
        return int(math.ceil(float(n) / alignment)) * alignment
    elif type == "floor":
        return int(math.floor(float(n) / alignment)) * alignment
    else:
        return int(round(float(n) / alignment)) * alignment


class AKPFrameDimensions:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "size": (["3840", "1920", "1440", "1280", "768", "720", "640", "512"],),
                "aspect_ratio": (["16:9", "16:10", "4:3", "1:1", "5:4", "3:2", "21:9", "14:9"],),
                "orientation": (["wide", "tall"],),
                "divisor": (["8", "4", "2", "1"],),
                "alignment": ("INT", {"default": 64, "min": 1, "max": 512}),
                "alignment_type": (["ceil", "floor", "nearest"],),
            },
        }

    CATEGORY = "AKP Animation/Util"
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(*values)

    def result(self, size, aspect_ratio, orientation, divisor, alignment, alignment_type):
        ratio = tuple(map(int, aspect_ratio.split(":")))
        width = _align_num(int(round(int(size) / float(divisor))), alignment, alignment_type)
        height = _align_num((float(width) * ratio[1]) / ratio[0], alignment, alignment_type)
        if orientation == "wide":
            return (width, height)
        else:
            return (height, width)
