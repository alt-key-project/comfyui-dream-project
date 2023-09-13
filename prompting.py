from .categories import NodeCategories
from .shared import hashed_as_strings
from .types import PartialPrompt


class DreamWeightedPromptBuilder:
    NODE_NAME = "Build Prompt"
    ICON = "⚖"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "partial_prompt": (PartialPrompt.ID,)
            },
            "required": {
                "added_prompt": ("STRING", {"default": "", "multiline": True}),
                "weight": ("FLOAT", {"default": 1.0}),
            },
        }

    CATEGORY = NodeCategories.CONDITIONING
    RETURN_TYPES = (PartialPrompt.ID,)
    RETURN_NAMES = ("partial_prompt",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(*values)

    def result(self, added_prompt, weight, **args):
        input = args.get("partial_prompt", PartialPrompt())
        p = input.add(added_prompt, weight)
        return (p,)


class DreamPromptFinalizer:
    NODE_NAME = "Finalize Prompt"
    ICON = "🗫"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "partial_prompt": (PartialPrompt.ID,),
                "adjustment": (["raw", "by_abs_max", "by_abs_sum"],),
                "clamp": ("FLOAT", {"default": 2.0, "min": 0.1, "step": 0.1}),
                "adjustment_reference": ("FLOAT", {"default": 1.0, "min": 0.1}),
            },
        }

    CATEGORY = NodeCategories.CONDITIONING
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("positive", "negative")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(*values)

    def result(self, partial_prompt: PartialPrompt, adjustment, adjustment_reference, clamp):
        if adjustment == "raw" or partial_prompt.is_empty():
            return partial_prompt.finalize(clamp)
        elif adjustment == "by_abs_sum":
            f = adjustment_reference / partial_prompt.abs_sum()
            return partial_prompt.scaled_by(f).finalize(clamp)
        else:
            f = adjustment_reference / partial_prompt.abs_max()
            return partial_prompt.scaled_by(f).finalize(clamp)
