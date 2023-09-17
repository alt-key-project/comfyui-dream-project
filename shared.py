# -*- coding: utf-8 -*-

import hashlib
import json
import os
import random
import time

import folder_paths as comfy_paths
import glob
import numpy
import torch
from PIL import Image, ImageFilter, ImageEnhance
from PIL.ImageDraw import ImageDraw
from PIL.PngImagePlugin import PngInfo
from typing import Dict, Tuple, List

from .dreamlogger import DreamLog
from .embedded_config import EMBEDDED_CONFIGURATION

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


_config_data = None


class DreamConfig:
    FILEPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    DEFAULT_CONFIG = EMBEDDED_CONFIGURATION

    def __init__(self):
        global _config_data
        if not os.path.isfile(DreamConfig.FILEPATH):
            self._data = DreamConfig.DEFAULT_CONFIG
            self._save()
        if _config_data is None:
            with open(DreamConfig.FILEPATH, encoding="utf-8") as f:
                self._data = json.load(f)
                if self._merge_with_defaults(self._data, DreamConfig.DEFAULT_CONFIG):
                    self._save()
                _config_data = self._data
        else:
            self._data = _config_data

    def _save(self):
        with open(DreamConfig.FILEPATH, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    def _merge_with_defaults(self, config: dict, default_config: dict) -> bool:
        changed = False
        for key in default_config.keys():
            if key not in config:
                changed = True
                config[key] = default_config[key]
            elif isinstance(default_config[key], dict):
                changed = changed or self._merge_with_defaults(config[key], default_config[key])
        return changed

    def get(self, key: str, default=None):
        key = key.split(".")
        d = self._data
        for part in key:
            d = d.get(part, {})
        if isinstance(d, dict) and not d:
            return default
        else:
            return d


def get_logger():
    config = DreamConfig()
    return DreamLog(config.get("debug", False))


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


def pick_random_by_weight(data: List[Tuple[float, object]], rng: random.Random):
    total_weight = sum(map(lambda item: item[0], data))
    r = rng.random()
    for (weight, obj) in data:
        r -= weight / total_weight
        if r <= 0:
            return obj
    return data[0][1]


class DreamImage:
    @classmethod
    def join_to_tensor_data(cls, images):
        l = list(map(lambda i: i.create_tensor_image(), images))
        return torch.cat(l, dim=0)

    def __init__(self, tensor_image=None, pil_image=None, file_path=None, with_alpha=False):
        if pil_image is not None:
            self.pil_image = pil_image
        elif tensor_image is not None:
            self.pil_image = convertTensorImageToPIL(tensor_image)
        else:
            self.pil_image = Image.open(file_path)
        if with_alpha and self.pil_image.mode != "RGBA":
            self.pil_image = self.pil_image.convert("RGBA")
        else:
            if self.pil_image.mode not in ("RGB", "RGBA"):
                self.pil_image = self.pil_image.convert("RGB")
        self.width = self.pil_image.width
        self.height = self.pil_image.height
        self.size = self.pil_image.size
        self._draw = ImageDraw(self.pil_image)

    def change_brightness(self, factor):
        enhancer = ImageEnhance.Brightness(self.pil_image)
        return DreamImage(pil_image=enhancer.enhance(factor))

    def change_contrast(self, factor):
        enhancer = ImageEnhance.Contrast(self.pil_image)
        return DreamImage(pil_image=enhancer.enhance(factor))

    def numpy_array(self):
        return numpy.array(self.pil_image)

    def _renew(self, pil_image):
        self.pil_image = pil_image
        self._draw = ImageDraw(self.pil_image)

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

    def convert(self, mode="RGB"):
        if self.pil_image.mode == mode:
            return self
        return DreamImage(pil_image=self.pil_image.convert(mode))

    def create_tensor_image(self):
        return convertFromPILToTensorImage(self.pil_image)

    def blend(self, other, weight_self: float = 0.5, weight_other: float = 0.5):
        alpha = 1.0 - weight_self / (weight_other + weight_self)
        return DreamImage(pil_image=Image.blend(self.pil_image, other.pil_image, alpha))

    def color_area(self, x, y, w, h, col):
        self._draw.rectangle((x, y, x + w - 1, y + h - 1), fill=col, outline=col)

    def blur(self, amount):
        return DreamImage(pil_image=self.pil_image.filter(ImageFilter.GaussianBlur(amount)))

    def adjust_colors(self, red_factor=1.0, green_factor=1.0, blue_factor=1.0):
        # newRed   = 1.1*oldRed  +  0*oldGreen    +  0*oldBlue  + constant
        # newGreen = 0*oldRed    +  0.9*OldGreen  +  0*OldBlue  + constant
        # newBlue  = 0*oldRed    +  0*OldGreen    +  1*OldBlue  + constant
        matrix = (red_factor, 0, 0, 0,
                  0, green_factor, 0, 0,
                  0, 0, blue_factor, 0)
        return DreamImage(pil_image=self.pil_image.convert("RGB", matrix))

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

    @classmethod
    def from_file(cls, file_path):
        return DreamImage(pil_image=Image.open(file_path))


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
    def __init__(self, state_collection_name="state"):
        self._filepath = os.path.join(TEMP_PATH, state_collection_name+".json")
        self._dirname = os.path.dirname(self._filepath)
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
        return previous


def hashed_as_strings(*items):
    tokens = "|".join(list(map(str, items)))
    m = hashlib.sha256()
    m.update(tokens.encode(encoding="utf-8"))
    return m.digest().hex()


class MpegEncoderUtility:
    def __init__(self, video_path: str, bit_rate_factor: float, width: int, height: int, files: List[str],
                 fps: float, encoding_threads: int, codec_name, max_b_frame):
        import mpegCoder
        self._files = files
        self._logger = get_logger()
        self._enc = mpegCoder.MpegEncoder()
        bit_rate = self._calculate_bit_rate(width, height, fps, bit_rate_factor)
        self._logger.info("Bitrate " + str(bit_rate))
        self._enc.setParameter(
            videoPath=video_path, codecName=codec_name,
            nthread=encoding_threads, bitRate=bit_rate, width=width, height=height, widthSrc=width,
            heightSrc=height,
            GOPSize=len(files), maxBframe=max_b_frame, frameRate=self._fps_to_tuple(fps))

    def _calculate_bit_rate(self, width: int, height: int, fps: float, bit_rate_factor: float):
        bits_per_pixel_base = 0.5
        return round(max(10, float(width * height * fps * bits_per_pixel_base * bit_rate_factor * 0.001)))

    def encode(self):
        if not self._enc.FFmpegSetup():
            raise Exception("Failed to setup MPEG Encoder - check parameters!")
        try:
            t = time.time()

            for filepath in self._files:
                self._logger.debug("Encoding frame {}", filepath)
                image = DreamImage.from_file(filepath).convert("RGB")
                self._enc.EncodeFrame(image.numpy_array())
            self._enc.FFmpegClose()
            self._logger.info("Completed video encoding of {n} frames in {t} seconds", n=len(self._files),
                              t=round(time.time() - t))
        finally:
            self._enc.clear()

    def _fps_to_tuple(self, fps: float):
        def _is_almost_int(f: float):
            return abs(f - int(f)) < 0.001

        a = fps
        b = 1
        while not _is_almost_int(a) and b < 100:
            a /= 10
            b *= 10
        a = round(a)
        b = round(b)
        self._logger.info("Video specified as {fps} fps - encoder framerate {a}/{b}", fps=fps, a=a, b=b)
        return (a, b)
