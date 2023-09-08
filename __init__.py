from typing import Type

from .base import *
from .colors import *
from .curves import *
from .image_processing import *
from .loaders import *
from .noise import *
from .output import *
from .seq_processing import *
from .utility import *

_NODE_CLASSES: List[Type] = [DreamSineWave, DreamLinear, DreamCSVCurve, DreamBeatCurve, DreamFrameDimensions,
                             DreamImageMotion, DreamNoiseFromPalette, DreamAnalyzePalette, DreamColorShift,
                             DreamDirectoryFileCount, DreamFrameCounterOffset, DreamDirectoryBackedFrameCounter,
                             DreamSimpleFrameCounter, DreamImageSequenceInputWithDefaultFallback,
                             DreamImageSequenceOutput, DreamCSVGenerator, DreamImageAreaSampler,
                             DreamVideoEncoder, DreamSequenceTweening, DreamSequenceBlend, DreamColorAlign,
                             DreamImageSampler, DreamNoiseFromAreaPalettes]
_SIGNATURE_SUFFIX = " [Dream]"

MANIFEST = {
    "name": "Dream Project Animation",
    "version": (2, 0, 0),
    "author": "Dream Project",
    "project": "https://github.com/alt-key-project/comfyui-dream-project",
    "description": "Various utility nodes for creating animations with ComfyUI",
}

NODE_CLASS_MAPPINGS = {}

NODE_DISPLAY_NAME_MAPPINGS = {}

for cls in _NODE_CLASSES:
    clsname = cls.__name__
    if "NODE_NAME" in cls.__dict__:
        node_name = cls.__dict__["NODE_NAME"] + _SIGNATURE_SUFFIX
        NODE_CLASS_MAPPINGS[node_name] = cls
        display_name = cls.__dict__.get("DISPLAY_NAME", cls.__dict__["NODE_NAME"]) + _SIGNATURE_SUFFIX
        NODE_DISPLAY_NAME_MAPPINGS[node_name] = display_name
    else:
        raise Exception("Class {} is missing NODE_NAME!".format(str(cls)))


def update_node_index():
    node_list_path = os.path.join(os.path.dirname(__file__), "node_list.json")
    with open(node_list_path) as f:
        node_list = json.loads(f.read())
    updated = False
    for nodename in NODE_CLASS_MAPPINGS.keys():
        if nodename not in node_list:
            node_list[nodename] = ""
            updated = True
    if updated or True:
        with open(node_list_path, "w") as f:
            f.write(json.dumps(node_list, indent=2, sort_keys=True))


update_node_index()
