import comfy.diffusers_convert
import comfy.samplers
import comfy.sd
import comfy.utils
import hashlib
import comfy.clip_vision
import folder_paths as comfy_paths
import os, json, math

NODE_FILE = os.path.abspath(__file__)
AKP_NODES_SOURCE_ROOT = os.path.dirname(NODE_FILE)
TEMP_PATH = os.path.join(os.path.abspath(comfy_paths.temp_directory), "AKP_Anim")


class AKPStateStore:
    def __init__(self, name, read_fun, write_fun):
        self._read = read_fun
        self._write = write_fun
        self._name = name

    def _as_key(self, k):
        return self._name + "_" + k

    def get(self, key, default):
        v = self[key]
        if v is None:
            return default
        else:
            return v

    def update(self, key, default, f):
        prev = self.get(key, default)
        v = f(prev)
        self[key] = v
        return v

    def __getitem__(self, item):
        return self._read(self._as_key(item))

    def __setitem__(self, key, value):
        return self._write(self._as_key(key), value)


class AKPStateFile:
    def __init__(self, state_file_path=os.path.join(TEMP_PATH, "state.json")):
        self._dirname = os.path.dirname(state_file_path)
        self._filepath = state_file_path
        if not os.path.isdir(self._dirname):
            os.makedirs(self._dirname)
        if not os.path.isfile(self._filepath):
            self._data: dict = {}
        else:
            with open(self._filepath, encoding="utf-8") as f:
                self._data = json.load(f)

    def get_section(self, name: str) -> AKPStateStore:
        return AKPStateStore(name, self._read, self._write)

    def _read(self, key):
        return self._data.get(key, None)

    def _write(self, key, value):
        previous = self._data.get(key, None)
        if value is None:
            if key in self._data:
                del self._data[key]
        else:
            self._data[key] = value
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(self._data, f)
        print("* {} -> {}".format(key, value))
        return previous


def hashed_as_strings(*items):
    tokens = "|".join(list(map(str, items)))
    m = hashlib.sha256()
    m.update(tokens.encode(encoding="utf-8"))
    return m.digest().hex()


class _SharedTypes:
    current_frame = {"current_frame": ("INT", {"forceInput": True, "default": 0, "min": 0, "max": 24 * 3600 * 60})}
    frame_progress = {"frame_progress": ("FLOAT", {"forceInput": True, "default": 0, "min": 0.0, "max": 1.0})}

class AKPFrameCount:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "primitive_input": ("INT", {"default": 0, "min": 0, "max": 24 * 3600 * 60}),
                "total_frames": ("INT", {"default": 100, "min": 1, "max": 24 * 3600 * 60}),
            },
        }

    CATEGORY = "AKP Animation"
    RETURN_TYPES = ("INT", "FLOAT")
    RETURN_NAMES = ("current_frame", "frame_progress")
    FUNCTION = "result"

    def result(self, primitive_input, total_frames):
        primitive_input = max(min(0, primitive_input), total_frames - 1)
        return (primitive_input, primitive_input / float(total_frames - 1))


class AKPSineWave:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": _SharedTypes.current_frame | {
                "max_value": ("FLOAT", {"default": 1.0, "multiline": False}),
                "min_value": ("FLOAT", {"default": 0.0, "multiline": False}),
                "period": ("INT", {"default": 10, "multiline": False, "min": 1}),
                "phase": ("FLOAT", {"default": 0.0, "multiline": False}),
            },
        }

    CATEGORY = "AKP Animation/Curves"
    RETURN_TYPES = ("FLOAT", "INT")
    RETURN_NAMES = ("FLOAT", "INT")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(*values)

    def result(self, current_frame, max_value, min_value, period, phase):
        a = (max_value - min_value) * 0.5
        v = min_value + 0.5 * a + \
            a * math.sin(phase * 2.0 * math.pi + float(current_frame) / max(1, period) * 2.0 * math.pi)
        return (v, int(round(v)))


class AKPLinear:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": _SharedTypes.frame_progress | {
                "initial_value": ("FLOAT", {"default": 0.0, "multiline": False}),
                "final_value": ("FLOAT", {"default": 100.0, "multiline": False}),
            },
        }

    CATEGORY = "AKP Animation/Curves"
    RETURN_TYPES = ("FLOAT", "INT")
    RETURN_NAMES = ("FLOAT", "INT")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(*values)

    def result(self, initial_value, final_value, frame_progress):
        d = final_value - initial_value
        v = initial_value + frame_progress * d
        return (v, int(round(v)))


NODE_CLASS_MAPPINGS = {
    "SineWave": AKPSineWave,
    "Linear": AKPLinear,
    "FrameCounter": AKPFrameCount,
}
