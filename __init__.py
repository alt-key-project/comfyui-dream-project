from .base import *
from .curves import *
from .loaders import *

MANIFEST = {
    "name": "AKP Animation",
    "version": (0, 1, 0),
    "author": "Alt Key Project",
    "project": "https://github.com/",
    "description": "Various utility nodes for creating animations with ComfyUI",
}

NODE_CLASS_MAPPINGS = {
    "SineWave": AKPSineWave,
    "Linear": AKPLinear,
    "FrameCounter": AKPFrameCount,
    "InputImageLoader": AKPInputImageLoader
}
