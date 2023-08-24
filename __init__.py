from .base import *
from .curves import *
from .loaders import *
from .output import *
from .utility import *
from .image_processing import *

MANIFEST = {
    "name": "AKP Animation",
    "version": (0, 1, 0),
    "author": "Alt Key Project",
    "project": "https://github.com/",
    "description": "Various utility nodes for creating animations with ComfyUI",
}

NODE_CLASS_MAPPINGS = {
    "Sine Wave": AKPSineWave,
    "Linear": AKPLinear,
    "CSV Curve": AKPCSVCurve,
    "Beat Curve": AKPBeatCurve,
    "Image Dimensions": AKPFrameDimensions,
    "Image Motion": AKPImageMotion,
    "Frame Total (Directory)": AKPDirectoryBackedFrameTotal,
    "Frame Counter Offset": AKPFrameCounterOffset,
    "Frame Counter (Directory)": AKPDirectoryBackedFrameCounter,
    "Frame Counter (Simple)": AKPSimpleFrameCounter,
    "Image Sequence Loader With Fallback": AKPImageSequenceInputWithDefaultFallback,
    "Image Sequence Saver": AKPImageSequenceOutput,
    "Named Image Saver": AKPNamedImageSaver
}

RENAMED = {
    "Image Sequence Loader With Fallback": "Image Sequence Loader"
}

NODE_DISPLAY_NAME_MAPPINGS = {
}

for name in NODE_CLASS_MAPPINGS.keys():
    NODE_DISPLAY_NAME_MAPPINGS[name] = "AKP " + RENAMED.get(name, name)
