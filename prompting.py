from .categories import NodeCategories
from .shared import hashed_as_strings
from .dreamtypes import PartialPrompt
import random

class DreamRandomPromptWords:
    NODE_NAME = "Random Prompt Words"
    ICON = "⚅"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "partial_prompt": (PartialPrompt.ID,)
            },
            "required": {
                "words": ("STRING", {"default": "", "multiline": True}),
                "separator": ("STRING", {"default": ",", "multiline": False}),
                "samples": ("INT", {"default": 1, "min": 1, "max": 100}),
                "min_weight": ("FLOAT", {"default": 1.0, "min": -10, "max": 10}),
                "max_weight": ("FLOAT", {"default": 1.0, "min": -10, "max": 10}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
        }

    CATEGORY = NodeCategories.CONDITIONING
    RETURN_TYPES = (PartialPrompt.ID,)
    RETURN_NAMES = ("partial_prompt",)
    FUNCTION = "result"


    @classmethod
    def IS_CHANGED(cls, *values, **kwargs):
        return hashed_as_strings(*values, **kwargs)

    def result(self, words: str, separator, samples, min_weight, max_weight, seed, **args):
        p = args.get("partial_prompt", PartialPrompt())
        rnd = random.Random()
        rnd.seed(seed)
        words = list(set(map(lambda s: s.strip(), filter(lambda s: s.strip() != "", words.split(separator)))))
        samples = min(samples, len(words))
        for i in range(samples):
            picked_word = words[rnd.randint(0, len(words)-1)]
            words = list(filter(lambda s: s!=picked_word, words))
            weight = rnd.uniform(min_weight, max_weight)
            p = p.add(picked_word, weight)
        return (p,)


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
    def IS_CHANGED(cls, *values, **kwargs):
        return hashed_as_strings(*values, **kwargs)

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
    def IS_CHANGED(cls, *values, **kwargs):
        return hashed_as_strings(*values, **kwargs)

    def result(self, partial_prompt: PartialPrompt, adjustment, adjustment_reference, clamp):
        if adjustment == "raw" or partial_prompt.is_empty():
            return partial_prompt.finalize(clamp)
        elif adjustment == "by_abs_sum":
            f = adjustment_reference / partial_prompt.abs_sum()
            return partial_prompt.scaled_by(f).finalize(clamp)
        else:
            f = adjustment_reference / partial_prompt.abs_max()
            return partial_prompt.scaled_by(f).finalize(clamp)
