# -*- coding: utf-8 -*-
from typing import Type

from .base import *
from .colors import *
from .curves import *
from .image_processing import *
from .inputfields import *
from .loaders import *
from .noise import *
from .output import *
from .prompting import *
from .seq_processing import *
from .switches import *
from .utility import *
from .calculate import *
from .laboratory import *

_NODE_CLASSES: List[Type] = [DreamSineWave, DreamLinear, DreamCSVCurve, DreamBeatCurve, DreamFrameDimensions,
                             DreamImageMotion, DreamNoiseFromPalette, DreamAnalyzePalette, DreamColorShift,
                             DreamDirectoryFileCount, DreamFrameCounterOffset, DreamDirectoryBackedFrameCounter,
                             DreamSimpleFrameCounter, DreamImageSequenceInputWithDefaultFallback,
                             DreamImageSequenceOutput, DreamCSVGenerator, DreamImageAreaSampler,
                             DreamVideoEncoder, DreamSequenceTweening, DreamSequenceBlend, DreamColorAlign,
                             DreamImageSampler, DreamNoiseFromAreaPalettes, DreamVideoEncoderMpegCoder,
                             DreamInputString, DreamInputFloat, DreamInputInt, DreamInputText, DreamBigLatentSwitch,
                             DreamFrameCountCalculator, DreamBigImageSwitch, DreamBigTextSwitch, DreamBigFloatSwitch,
                             DreamBigIntSwitch, DreamBigPaletteSwitch, DreamWeightedPromptBuilder, DreamPromptFinalizer,
                             DreamFrameCounterInfo, DreamBoolToFloat, DreamBoolToInt, DreamSawWave, DreamTriangleWave,
                             DreamTriangleEvent, DreamSmoothEvent, DreamCalculation, DreamImageColorShift,
                             DreamComparePalette, DreamImageContrast, DreamImageBrightness, DreamLogFile,
                             DreamLaboratory, DreamStringToLog, DreamIntToLog, DreamFloatToLog, DreamJoinLog,
                             DreamStringTokenizer, DreamWavCurve, DreamFrameCounterTimeOffset]
_SIGNATURE_SUFFIX = " [Dream]"

MANIFEST = {
    "name": "Dream Project Animation",
    "version": (4, 3, 0),
    "author": "Dream Project",
    "project": "https://github.com/alt-key-project/comfyui-dream-project",
    "description": "Various utility nodes for creating animations with ComfyUI",
}

NODE_CLASS_MAPPINGS = {}

NODE_DISPLAY_NAME_MAPPINGS = {}

config = DreamConfig()


def update_category(cls):
    top = config.get("ui.top_category", "").strip().strip("/")
    leaf_icon = ""
    if top and "CATEGORY" in cls.__dict__:
        cls.CATEGORY = top + "/" + cls.CATEGORY.lstrip("/")
    if "CATEGORY" in cls.__dict__:
        joined = []
        for partial in cls.CATEGORY.split("/"):
            icon = config.get("ui.category_icons." + partial, "")
            if icon:
                leaf_icon = icon
            if config.get("ui.prepend_icon_to_category", False):
                partial = icon.lstrip() + " " + partial
            if config.get("ui.append_icon_to_category", False):
                partial = partial + " " + icon.rstrip()
            joined.append(partial)
        cls.CATEGORY = "/".join(joined)
    return leaf_icon


def update_display_name(cls, category_icon, display_name):
    icon = cls.__dict__.get("ICON", category_icon)
    if config.get("ui.prepend_icon_to_node", False):
        display_name = icon.lstrip() + " " + display_name
    if config.get("ui.append_icon_to_node", False):
        display_name = display_name + " " + icon.rstrip()
    return display_name


for cls in _NODE_CLASSES:
    category_icon = update_category(cls)
    clsname = cls.__name__
    if "NODE_NAME" in cls.__dict__:
        node_name = cls.__dict__["NODE_NAME"] + _SIGNATURE_SUFFIX
        NODE_CLASS_MAPPINGS[node_name] = cls
        NODE_DISPLAY_NAME_MAPPINGS[node_name] = update_display_name(cls, category_icon,
                                                                    cls.__dict__.get("DISPLAY_NAME",
                                                                                     cls.__dict__["NODE_NAME"]))
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
