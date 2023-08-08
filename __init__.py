from .base import *
from .curves import *
from .loaders import *
from .output import *
from .utility import *
from .motion import *

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
    "Image Dimensions": AKPFrameDimensions,
    "Image Motion": AKPImageMotion,
    "Frame Counter Offset": AKPFrameCounterOffset,
    "Frame Counter (Directory)": AKPDirectoryBackedFrameCounter,
    "Frame Counter (Simple)": AKPSimpleFrameCounter,
    "Image Sequence Loader": AKPImageSequenceInput,
    "Image Sequence Loader With Fallback": AKPImageSequenceInputWithDefaultFallback,
    "Image Sequence Saver": AKPImageSequenceOutput,
}
