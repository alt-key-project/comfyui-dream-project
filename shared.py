import hashlib, os, json, glob

import numpy
import torch
from PIL import Image
from typing import Dict

import folder_paths as comfy_paths

NODE_FILE = os.path.abspath(__file__)
AKP_NODES_SOURCE_ROOT = os.path.dirname(NODE_FILE)
TEMP_PATH = os.path.join(os.path.abspath(comfy_paths.temp_directory), "AKP_Anim")
ALWAYS_CHANGED_FLAG = float("NaN")


def convertToPIL(image) -> Image:
    return Image.fromarray(numpy.clip(255. * image.cpu().numpy().squeeze(), 0, 255).astype(numpy.uint8))


def convertFromPIL(image):
    return torch.from_numpy(numpy.array(image).astype(numpy.float32) / 255.0).unsqueeze(0)


def list_images_in_directory(directory_path: str, pattern: str, alphabetic_index: bool) -> Dict[int, str]:
    if not os.path.isdir(directory_path):
        return {}
    files = []
    for file_name in glob.glob(os.path.join(directory_path, pattern), recursive=True):
        if file_name.lower().endswith(('.jpeg', '.jpg', '.png', '.tiff', '.gif', '.bmp', '.webp')):
            files.append(os.path.abspath(file_name))
    result = dict()

    def _num_from_filename(fn):
        (text, _) = os.path.splitext(fn)
        token: str = text.split("_")[-1]
        if token.isdigit():
            return int(token)
        else:
            return -1

    if alphabetic_index:
        files.sort()
        for idx, item in enumerate(files):
            result[idx] = item
    else:
        for filepath in files:
            result[_num_from_filename(os.path.basename(filepath))] = filepath
    return result


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
