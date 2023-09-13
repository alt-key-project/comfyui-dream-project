from .categories import NodeCategories
from .err import *
from .shared import ALWAYS_CHANGED_FLAG, hashed_as_strings
from .types import RGBPalette


def _generate_switch_input(type: str):
    d = dict()
    for i in range(10):
        d["input_" + str(i)] = (type,)
    return {
        "required": {
            "select": ("INT", {"defualt": 0, "min": 0, "max": 9}),
            "on_missing": (["previous", "next"],)
        },
        "optional": d
    }


def _do_pick(cls, select, on_missing, **args):
    direction = 1
    if on_missing == "previous":
        direction = -1
    if len(args) == 0:
        on_error(cls, "No inputs provided!")
    while args.get("input_" + str(select), None) is None:
        select = (select + direction) % 10
    return args["input_" + str(select)],


class DreamBigImageSwitch:
    _switch_type = "IMAGE"
    NODE_NAME = "Big Image Switch"
    ICON = "⭆"
    CATEGORY = NodeCategories.UTILS_SWITCHES
    RETURN_TYPES = (_switch_type,)
    RETURN_NAMES = ("selected",)
    FUNCTION = "pick"

    @classmethod
    def INPUT_TYPES(cls):
        return _generate_switch_input(cls._switch_type)

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def pick(self, select, on_missing, **args):
        return _do_pick(self.__class__, select, on_missing, **args)


class DreamBigLatentSwitch:
    _switch_type = "LATENT"
    NODE_NAME = "Big Latent Switch"
    ICON = "⭆"
    CATEGORY = NodeCategories.UTILS_SWITCHES
    RETURN_TYPES = (_switch_type,)
    RETURN_NAMES = ("selected",)
    FUNCTION = "pick"

    @classmethod
    def INPUT_TYPES(cls):
        return _generate_switch_input(cls._switch_type)

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def pick(self, select, on_missing, **args):
        return _do_pick(self.__class__, select, on_missing, **args)


class DreamBigTextSwitch:
    _switch_type = "STRING"
    NODE_NAME = "Big Text Switch"
    ICON = "⭆"
    CATEGORY = NodeCategories.UTILS_SWITCHES
    RETURN_TYPES = (_switch_type,)
    RETURN_NAMES = ("selected",)
    FUNCTION = "pick"

    @classmethod
    def INPUT_TYPES(cls):
        return _generate_switch_input(cls._switch_type)

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(values)

    def pick(self, select, on_missing, **args):
        return _do_pick(self.__class__, select, on_missing, **args)


class DreamBigPaletteSwitch:
    _switch_type = RGBPalette.ID
    NODE_NAME = "Big Palette Switch"
    ICON = "⭆"
    CATEGORY = NodeCategories.UTILS_SWITCHES
    RETURN_TYPES = (_switch_type,)
    RETURN_NAMES = ("selected",)
    FUNCTION = "pick"

    @classmethod
    def INPUT_TYPES(cls):
        return _generate_switch_input(cls._switch_type)

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def pick(self, select, on_missing, **args):
        return _do_pick(self.__class__, select, on_missing, **args)


class DreamBigFloatSwitch:
    _switch_type = "FLOAT"
    NODE_NAME = "Big Float Switch"
    ICON = "⭆"
    CATEGORY = NodeCategories.UTILS_SWITCHES
    RETURN_TYPES = (_switch_type,)
    RETURN_NAMES = ("selected",)
    FUNCTION = "pick"

    @classmethod
    def INPUT_TYPES(cls):
        return _generate_switch_input(cls._switch_type)

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(values)

    def pick(self, select, on_missing, **args):
        return _do_pick(self.__class__, select, on_missing, **args)


class DreamBigIntSwitch:
    _switch_type = "INT"
    NODE_NAME = "Big Int Switch"
    ICON = "⭆"
    CATEGORY = NodeCategories.UTILS_SWITCHES
    RETURN_TYPES = (_switch_type,)
    RETURN_NAMES = ("selected",)
    FUNCTION = "pick"

    @classmethod
    def INPUT_TYPES(cls):
        return _generate_switch_input(cls._switch_type)

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(values)

    def pick(self, select, on_missing, **args):
        return _do_pick(self.__class__, select, on_missing, **args)


class DreamBoolToFloat:
    NODE_NAME = "Boolean To Float"
    ICON = "⬖"
    CATEGORY = NodeCategories.UTILS_SWITCHES
    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("result",)
    FUNCTION = "pick"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean": ("BOOLEAN", {"default": False}),
                "on_true": ("FLOAT", {"default": 1.0}),
                "on_false": ("FLOAT", {"default": 0.0})
            }
        }

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(values)

    def pick(self, boolean, on_true, on_false):
        if boolean:
            return (on_true,)
        else:
            return (on_false,)


class DreamBoolToInt:
    NODE_NAME = "Boolean To Int"
    ICON = "⬖"
    CATEGORY = NodeCategories.UTILS_SWITCHES
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("result",)
    FUNCTION = "pick"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean": ("BOOLEAN", {"default": False}),
                "on_true": ("INT", {"default": 1}),
                "on_false": ("INT", {"default": 0})
            }
        }

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(values)

    def pick(self, boolean, on_true, on_false):
        if boolean:
            return (on_true,)
        else:
            return (on_false,)
