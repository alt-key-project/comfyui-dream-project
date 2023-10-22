# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

import json

from .categories import *
from .shared import ALWAYS_CHANGED_FLAG, DreamStateFile
from .dreamtypes import *

_laboratory_state = DreamStateFile("laboratory")


class DreamLaboratory:
    NODE_NAME = "Laboratory"
    ICON = "🧪"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.frame_counter | {
                "key": ("STRING", {"default": "Random value " + str(random.randint(0, 1000000))}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "renew_policy": (["every frame", "first frame"],),
                "min_value": ("FLOAT", {"default": 0.0}),
                "max_value": ("FLOAT", {"default": 1.0}),
                "mode": (["random uniform", "random bell", "ladder", "random walk"],),
            },
            "optional": {
                "step_size": ("FLOAT", {"default": 0.1}),
            },
        }

    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = ("FLOAT", "INT", LogEntry.ID)
    RETURN_NAMES = ("FLOAT", "INT", "log_entry")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def _generate(self, seed, last_value, min_value, max_value, mode, step_size):
        rnd = random.Random()
        rnd.seed(seed)

        def jsonify(v: float):
            return json.loads(json.dumps(v))

        if mode == "random uniform":
            return jsonify(self._mode_uniform(rnd, last_value, min_value, max_value, step_size))
        elif mode == "random bell":
            return jsonify(self._mode_bell(rnd, last_value, min_value, max_value, step_size))
        elif mode == "ladder":
            return jsonify(self._mode_ladder(rnd, last_value, min_value, max_value, step_size))
        else:
            return jsonify(self._mode_walk(rnd, last_value, min_value, max_value, step_size))

    def _mode_uniform(self, rnd: random.Random, last_value: float, min_value: float, max_value: float, step_size):
        return rnd.random() * (max_value - min_value) + min_value

    def _mode_bell(self, rnd: random.Random, last_value: float, min_value: float, max_value: float, step_size):
        s = 0.0
        for i in range(3):
            s += rnd.random() * (max_value - min_value) + min_value
        return s / 3.0

    def _mode_ladder(self, rnd: random.Random, last_value: float, min_value: float, max_value: float, step_size):
        if last_value is None:
            last_value = min_value - step_size
        next_value = last_value + step_size
        if next_value > max_value:
            d = abs(max_value - min_value)
            next_value = (next_value - min_value) % d + min_value
        return next_value

    def _mode_walk(self, rnd: random.Random, last_value: float, min_value: float, max_value: float, step_size):
        if last_value is None:
            last_value = (max_value - min_value) * 0.5
        if rnd.random() >= 0.5:
            return min(max_value, last_value + step_size)
        else:
            return max(min_value, last_value - step_size)

    def result(self, key, frame_counter: FrameCounter, seed, renew_policy, min_value, max_value, mode, **values):
        if min_value > max_value:
            t = max_value
            max_value = min_value
            min_value = t
        step_size = values.get("step_size", abs(max_value - min_value) * 0.1)
        last_value = _laboratory_state.get_section("values").get(key, None)

        if (last_value is None) or (renew_policy == "every frame") or frame_counter.is_first_frame:
            v = _laboratory_state.get_section("values") \
                .update(key, 0, lambda old: self._generate(seed, last_value, min_value, max_value, mode, step_size))
            return v, round(v), LogEntry.new(
                "Laboratory generated new value for '{}': {} ({})".format(key, v, round(v)))
        else:
            return last_value, round(last_value), LogEntry.new("Laboratory reused value for '{}': {} ({})"
                                                               .format(key, last_value, round(last_value)))
