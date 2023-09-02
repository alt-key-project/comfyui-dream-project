from .seq_processing import DreamVideoEncoder, DreamSequenceBlur, DreamSequenceTweening
from typing import List, Type

from .base import *
from .curves import *
from .loaders import *
from .output import *
from .utility import *
from .image_processing import *

_NODE_CLASSES: List[Type] = [DreamSineWave, DreamLinear, DreamCSVCurve, DreamBeatCurve, DreamFrameDimensions,
                             DreamImageMotion,
                             DreamDirectoryBackedFrameTotal, DreamFrameCounterOffset, DreamDirectoryBackedFrameCounter,
                             DreamSimpleFrameCounter, DreamImageSequenceInputWithDefaultFallback,
                             DreamImageSequenceOutput,
                             DreamNamedImageSaver, DreamVideoEncoder, DreamSequenceTweening, DreamSequenceBlur]
_SIGNATURE_SUFFIX = " [Dream]"

MANIFEST = {
    "name": "Dream Project Animation",
    "version": (1, 0, 0),
    "author": "Dream Project",
    "project": "https://github.com/alt-key-project/comfyui-dream-project",
    "description": "Various utility nodes for creating animations with ComfyUI",
}

NODE_CLASS_MAPPINGS = { }

NODE_DISPLAY_NAME_MAPPINGS = {}

for cls in _NODE_CLASSES:
    clsname = cls.__name__
    NODE_CLASS_MAPPINGS[clsname] = cls
    if "NODE_NAME" in cls.__dict__:
        NODE_DISPLAY_NAME_MAPPINGS[clsname] = cls.__dict__["NODE_NAME"] + _SIGNATURE_SUFFIX
    else:
        nodename = clsname + _SIGNATURE_SUFFIX

