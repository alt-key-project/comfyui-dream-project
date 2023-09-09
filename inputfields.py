from .categories import *
from .shared import *

class DreamInputText:
    NODE_NAME = "Text Input"
    ICON = "✍"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("STRING", {"default": "", "multiline": True}),
            },
        }

    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "noop"

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(*values)

    def noop(self, value):
        return (value,)

class DreamInputString:
    NODE_NAME = "String Input"
    ICON = "✍"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("STRING", {"default": "", "multiline": False}),
            },
        }

    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "noop"

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(*values)

    def noop(self, value):
        return (value,)


class DreamInputFloat:
    NODE_NAME = "Float Input"
    ICON = "✍"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("FLOAT", {"default": 0.0}),
            },
        }

    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("FLOAT",)
    FUNCTION = "noop"

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(*values)

    def noop(self, value):
        return (value,)


class DreamInputInt:
    NODE_NAME = "Int Input"
    ICON = "✍"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("INT", {"default": 0}),
            },
        }

    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("INT",)
    FUNCTION = "noop"

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(*values)

    def noop(self, value):
        return (value,)
