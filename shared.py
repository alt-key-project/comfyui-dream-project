import hashlib, os, json, glob

import numpy
import torch
from PIL import Image
from typing import Dict, Tuple

import folder_paths as comfy_paths

NODE_FILE = os.path.abspath(__file__)
AKP_NODES_SOURCE_ROOT = os.path.dirname(NODE_FILE)
TEMP_PATH = os.path.join(os.path.abspath(comfy_paths.temp_directory), "AKP_Anim")
ALWAYS_CHANGED_FLAG = float("NaN")


def convertToPIL(image) -> Image:
    return Image.fromarray(numpy.clip(255. * image.cpu().numpy().squeeze(), 0, 255).astype(numpy.uint8))


def convertFromPIL(image):
    return torch.from_numpy(numpy.array(image).astype(numpy.float32) / 255.0).unsqueeze(0)


class ImageWrapper:
    def __init__(self, sd_image=None, pil_image=None):
        if pil_image:
            self._pil_image = pil_image
        else:
            self._pil_image = convertToPIL(sd_image)
        if self._pil_image.mode not in ("RGB", "RGBA"):
            raise Exception("Unsupported image mode '{}'".format(self._pil_image.mode))
        self.width = self._pil_image.width
        self.height = self._pil_image.height
        self.size = self._pil_image.size

    def __iter__(self):
        class _Pixels:
            def __init__(self, image: ImageWrapper):
                self.x = 0
                self.y = 0
                self._img = image

            def __next__(self) -> Tuple[int, int, int, int]:
                if self.x >= self._img.width:
                    self.y += 1
                    self.x = 1
                if self.y >= self._img.height:
                    raise StopIteration
                p = self._img.get_pixel(self.x, self.y)
                self.x += 1
                return (p, self.x, self.y)

        return _Pixels(self)

    def get_sd_image(self):
        return convertFromPIL(self._pil_image)

    def get_pixel(self, x, y):
        p = self._pil_image.getpixel((x, y))
        if len(p) == 4:
            return p
        else:
            return (p[0], p[1], p[2], 255)

    def set_pixel(self, x, y, pixelvalue):
        if len(pixelvalue) == 4:
            self._pil_image.putpixel((x, y), pixelvalue)
        else:
            self._pil_image.putpixel((x, y), (pixelvalue[0], pixelvalue[1], pixelvalue[2], 255))


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
