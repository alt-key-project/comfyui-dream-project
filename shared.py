import hashlib, os, json, glob

import numpy
import torch
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from typing import Dict, Tuple, List

import folder_paths as comfy_paths

NODE_FILE = os.path.abspath(__file__)
DREAM_NODES_SOURCE_ROOT = os.path.dirname(NODE_FILE)
TEMP_PATH = os.path.join(os.path.abspath(comfy_paths.temp_directory), "Dream_Anim")
ALWAYS_CHANGED_FLAG = float("NaN")


def convertTensorImageToPIL(tensor_image) -> Image:
    return Image.fromarray(numpy.clip(255. * tensor_image.cpu().numpy().squeeze(), 0, 255).astype(numpy.uint8))


def convertFromPILToTensorImage(pil_image):
    return torch.from_numpy(numpy.array(pil_image).astype(numpy.float32) / 255.0).unsqueeze(0)


def _replace_pil_image(data):
    if isinstance(data, Image.Image):
        return DreamImage(pil_image=data)
    else:
        return data


class DreamConfig:
    FILEPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

    def __init__(self):
        with open(DreamConfig.FILEPATH) as f:
            self._data = json.load(f)

    def get(self, key: str, default = None):
        key = key.split(".")
        d = self._data
        for part in key:
            d = d.get(part, {})
        if isinstance(d, dict) and not d:
            return default
        else:
            return d


class DreamImageProcessor:
    def __init__(self, inputs: torch.Tensor, **extra_args):
        self._images_in_batch = [convertTensorImageToPIL(tensor) for tensor in inputs]
        self._extra_args = extra_args
        self.is_batch = len(self._images_in_batch) > 1

    def process_PIL(self, fun):
        def _wrap(dream_image):
            pil_outputs = fun(dream_image.pil_image)
            return list(map(_replace_pil_image, pil_outputs))

        return self.process(_wrap)

    def process(self, fun):
        output = []
        batch_counter = 0 if self.is_batch else -1
        for pil_image in self._images_in_batch:
            exec_result = fun(DreamImage(pil_image=pil_image), batch_counter, **self._extra_args)
            exec_result = list(map(_replace_pil_image, exec_result))
            if not output:
                output = [list() for i in range(len(exec_result))]
            for i in range(len(exec_result)):
                output[i].append(exec_result[i].create_tensor_image())
            if batch_counter >= 0:
                batch_counter += 1
        return tuple(map(lambda l: torch.cat(l, dim=0), output))


class DreamImage:
    @classmethod
    def join_to_tensor_data(cls, images):
        l = list(map(lambda i: i.create_tensor_image(), images))
        return torch.cat(l, dim=0)

    def __init__(self, tensor_image=None, pil_image=None, file_path=None):
        if pil_image:
            self.pil_image = pil_image
        elif tensor_image:
            self.pil_image = convertTensorImageToPIL(tensor_image)
        else:
            self.pil_image = Image.open(file_path)
        if self.pil_image.mode not in ("RGB", "RGBA"):
            self.pil_image = self.pil_image.convert("RGBA")
        self.width = self.pil_image.width
        self.height = self.pil_image.height
        self.size = self.pil_image.size

    def __iter__(self):
        class _Pixels:
            def __init__(self, image: DreamImage):
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

    def create_tensor_image(self):
        return convertFromPILToTensorImage(self.pil_image)

    def get_pixel(self, x, y):
        p = self.pil_image.getpixel((x, y))
        if len(p) == 4:
            return p
        else:
            return (p[0], p[1], p[2], 255)

    def set_pixel(self, x, y, pixelvalue):
        if len(pixelvalue) == 4:
            self.pil_image.putpixel((x, y), pixelvalue)
        else:
            self.pil_image.putpixel((x, y), (pixelvalue[0], pixelvalue[1], pixelvalue[2], 255))

    def save_png(self, filepath, embed_info=False, prompt=None, extra_pnginfo=None):
        info = PngInfo()
        print(filepath)
        if extra_pnginfo is not None:
            for item in extra_pnginfo:
                info.add_text(item, json.dumps(extra_pnginfo[item]))
        if prompt is not None:
            info.add_text("prompt", json.dumps(prompt))
        if embed_info:
            self.pil_image.save(filepath, pnginfo=info, optimize=True)
        else:
            self.pil_image.save(filepath, optimize=True)

    def save_jpg(self, filepath, quality=98):
        self.pil_image.save(filepath, quality=quality, optimize=True)


class DreamMask:
    def __init__(self, tensor_image=None, pil_image=None):
        if pil_image:
            self.pil_image = pil_image
        else:
            self.pil_image = convertTensorImageToPIL(tensor_image)
        if self.pil_image.mode != "L":
            self.pil_image = self.pil_image.convert("L")

    def create_tensor_image(self):
        return torch.from_numpy(numpy.array(self.pil_image).astype(numpy.float32) / 255.0)


def list_images_in_directory(directory_path: str, pattern: str, alphabetic_index: bool) -> Dict[int, List[str]]:
    if not os.path.isdir(directory_path):
        return {}
    dirs_to_search = [directory_path]
    if os.path.isdir(os.path.join(directory_path, "batch_0001")):
        dirs_to_search = list()
        for i in range(10000):
            dirpath = os.path.join(directory_path, "batch_" + (str(i).zfill(4)))
            if not os.path.isdir(dirpath):
                break
            else:
                dirs_to_search.append(dirpath)

    def _num_from_filename(fn):
        (text, _) = os.path.splitext(fn)
        token: str = text.split("_")[-1]
        if token.isdigit():
            return int(token)
        else:
            return -1

    result = dict()
    for search_path in dirs_to_search:
        files = []
        for file_name in glob.glob(os.path.join(search_path, pattern), recursive=False):
            if file_name.lower().endswith(('.jpeg', '.jpg', '.png', '.tiff', '.gif', '.bmp', '.webp')):
                files.append(os.path.abspath(file_name))

        if alphabetic_index:
            files.sort()
            for idx, item in enumerate(files):
                lst = result.get(idx, [])
                lst.append(item)
                result[idx] = lst
        else:
            for filepath in files:
                idx = _num_from_filename(os.path.basename(filepath))
                lst = result.get(idx, [])
                lst.append(filepath)
                result[idx] = lst
    return result


class DreamStateStore:
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


class DreamStateFile:
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

    def get_section(self, name: str) -> DreamStateStore:
        return DreamStateStore(name, self._read, self._write)

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
