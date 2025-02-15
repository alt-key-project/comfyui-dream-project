from .categories import NodeCategories
from .dreamtypes import RGBPalette

_NOT_A_VALUE_I = 9223372036854775807
_NOT_A_VALUE_F = float(_NOT_A_VALUE_I)
_NOT_A_VALUE_S = "⭆"

def _generate_switch_input(type_nm: str, default_value=None):
    d = dict()
    for i in range(10):
        if default_value is None:
            d["input_" + str(i)] = (type_nm, {"lazy": True})
        else:
            d["input_" + str(i)] = (type_nm, {"default": default_value, "forceInput": True, "lazy": True})

    return {
        "required": {
            "select": ("INT", {"default": 0, "min": 0, "max": 9})
        },
        "optional": d
    }


def _check_big_switch_lazy_status(*args, **kwargs):
    n = int(kwargs['select'])
    input_name = f"input_{n}"
    print(f"SELECTED: {input_name}")
    if input_name in kwargs:
        return [input_name]
    else:
        return []


class DreamLazyImageSwitch:
    _switch_type = "IMAGE"
    NODE_NAME = "Lazy Image Switch"
    ICON = "⭆"
    CATEGORY = NodeCategories.UTILS_SWITCHES
    RETURN_TYPES = (_switch_type,)
    RETURN_NAMES = ("selected",)
    FUNCTION = "pick"
        
    @classmethod
    def INPUT_TYPES(cls):
        return _generate_switch_input(cls._switch_type)

    def check_lazy_status(self, *args, **kwargs):
        return _check_big_switch_lazy_status(*args, **kwargs)

    def pick(self, select, **args):
        return (args.get("input_"+str(select), None),)


class DreamLazyLatentSwitch:
    _switch_type = "LATENT"
    NODE_NAME = "Lazy Latent Switch"
    ICON = "⭆"
    CATEGORY = NodeCategories.UTILS_SWITCHES
    RETURN_TYPES = (_switch_type,)
    RETURN_NAMES = ("selected",)
    FUNCTION = "pick"

    @classmethod
    def INPUT_TYPES(cls):
        return _generate_switch_input(cls._switch_type)

    def check_lazy_status(self, *args, **kwargs):
        return _check_big_switch_lazy_status(*args, **kwargs)

    def pick(self, select, **args):
        return (args.get("input_" + str(select), None),)


class DreamLazyTextSwitch:
    _switch_type = "STRING"
    NODE_NAME = "Lazy Text Switch"
    ICON = "⭆"
    CATEGORY = NodeCategories.UTILS_SWITCHES
    RETURN_TYPES = (_switch_type,)
    RETURN_NAMES = ("selected",)
    FUNCTION = "pick"

    @classmethod
    def INPUT_TYPES(cls):
        return _generate_switch_input(cls._switch_type, _NOT_A_VALUE_S)

    def check_lazy_status(self, *args, **kwargs):
        return _check_big_switch_lazy_status(*args, **kwargs)

    def pick(self, select, **args):
        return (args.get("input_" + str(select), None),)


class DreamLazyPaletteSwitch:
    _switch_type = RGBPalette.ID
    NODE_NAME = "Lazy Palette Switch"
    ICON = "⭆"
    CATEGORY = NodeCategories.UTILS_SWITCHES
    RETURN_TYPES = (_switch_type,)
    RETURN_NAMES = ("selected",)
    FUNCTION = "pick"

    @classmethod
    def INPUT_TYPES(cls):
        return _generate_switch_input(cls._switch_type)

    def check_lazy_status(self, *args, **kwargs):
        return _check_big_switch_lazy_status(*args, **kwargs)

    def pick(self, select, **args):
        return (args.get("input_" + str(select), None),)


class DreamLazyFloatSwitch:
    _switch_type = "FLOAT"
    NODE_NAME = "Lazy Float Switch"
    ICON = "⭆"
    CATEGORY = NodeCategories.UTILS_SWITCHES
    RETURN_TYPES = (_switch_type,)
    RETURN_NAMES = ("selected",)
    FUNCTION = "pick"

    @classmethod
    def INPUT_TYPES(cls):
        return _generate_switch_input(cls._switch_type, _NOT_A_VALUE_F)

    def check_lazy_status(self, *args, **kwargs):
        return _check_big_switch_lazy_status(*args, **kwargs)

    def pick(self, select, **args):
        return (args.get("input_" + str(select), None),)


class DreamLazyIntSwitch:
    _switch_type = "INT"
    NODE_NAME = "Lazy Int Switch"
    ICON = "⭆"
    CATEGORY = NodeCategories.UTILS_SWITCHES
    RETURN_TYPES = (_switch_type,)
    RETURN_NAMES = ("selected",)
    FUNCTION = "pick"

    @classmethod
    def INPUT_TYPES(cls):
        return _generate_switch_input(cls._switch_type, _NOT_A_VALUE_I)

    def check_lazy_status(self, *args, **kwargs):
        return _check_big_switch_lazy_status(*args, **kwargs)

    def pick(self, select, **args):
        return (args.get("input_" + str(select), None),)
