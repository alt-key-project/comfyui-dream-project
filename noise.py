# -*- coding: utf-8 -*-
import math

from .categories import NodeCategories
from .shared import *
from .types import *


def _generate_noise(image: DreamImage, color_function, rng: random.Random, block_size, blur_amount,
                    density) -> DreamImage:
    w = block_size[0]
    h = block_size[1]
    blur_radius = round(max(image.width, image.height) * blur_amount * 0.25)
    if w <= (image.width // 128) or h <= (image.height // 128):
        return image
    max_placements = round(density * (image.width * image.height))
    num = min(max_placements, round((image.width * image.height * 2) / (w * h)))
    for i in range(num):
        x = rng.randint(-w + 1, image.width - 1)
        y = rng.randint(-h + 1, image.height - 1)
        image.color_area(x, y, w, h, color_function(x + (w >> 1), y + (h >> 1)))
    image = image.blur(blur_radius)
    return _generate_noise(image, color_function, rng, (w >> 1, h >> 1), blur_amount, density)


class DreamNoiseFromPalette:
    NODE_NAME = "Noise from Palette"
    ICON = "🌫"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.palette | {
                "width": ("INT", {"default": 512, "min": 1, "max": 8192}),
                "height": ("INT", {"default": 512, "min": 1, "max": 8192}),
                "blur_amount": ("FLOAT", {"default": 0.3, "min": 0, "max": 1.0, "step": 0.05}),
                "density": ("FLOAT", {"default": 0.5, "min": 0.1, "max": 1.0, "step": 0.025}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})
            },
        }

    CATEGORY = NodeCategories.IMAGE_GENERATE
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, palette: Tuple[RGBPalette], width, height, seed, blur_amount, density):
        outputs = list()
        rng = random.Random()
        for p in palette:
            seed += 1
            color_iterator = p.random_iteration(seed)
            image = DreamImage(pil_image=Image.new("RGB", (width, height), color=next(color_iterator)))
            image = _generate_noise(image, lambda x, y: next(color_iterator), rng,
                                    (image.width >> 1, image.height >> 1), blur_amount, density)
            outputs.append(image)

        return (DreamImage.join_to_tensor_data(outputs),)


class DreamNoiseFromAreaPalettes:
    NODE_NAME = "Noise from Area Palettes"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "top_left_palette": (RGBPalette.ID,),
                "top_center_palette": (RGBPalette.ID,),
                "top_right_palette": (RGBPalette.ID,),
                "center_left_palette": (RGBPalette.ID,),
                "center_palette": (RGBPalette.ID,),
                "center_right_palette": (RGBPalette.ID,),
                "bottom_left_palette": (RGBPalette.ID,),
                "bottom_center_palette": (RGBPalette.ID,),
                "bottom_right_palette": (RGBPalette.ID,),
            },
            "required": {
                "area_sharpness": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "width": ("INT", {"default": 512, "min": 1, "max": 8192}),
                "height": ("INT", {"default": 512, "min": 1, "max": 8192}),
                "blur_amount": ("FLOAT", {"default": 0.3, "min": 0, "max": 1.0, "step": 0.05}),
                "density": ("FLOAT", {"default": 0.5, "min": 0.1, "max": 1.0, "step": 0.025}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
        }

    CATEGORY = NodeCategories.IMAGE_GENERATE
    ICON = "🌫"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def _area_coordinates(self, width, height):
        dx = width / 6
        dy = height / 6
        return {
            "top_left_palette": (dx, dy),
            "top_center_palette": (dx * 3, dy),
            "top_right_palette": (dx * 5, dy),
            "center_left_palette": (dx, dy * 3),
            "center_palette": (dx * 3, dy * 3),
            "center_right_palette": (dx * 5, dy * 3),
            "bottom_left_palette": (dx * 1, dy * 5),
            "bottom_center_palette": (dx * 3, dy * 5),
            "bottom_right_palette": (dx * 5, dy * 5),
        }

    def _pick_random_area(self, active_coordinates, x, y, rng, area_sharpness):
        def _dst(x1, y1, x2, y2):
            a = x1 - x2
            b = y1 - y2
            return math.sqrt(a * a + b * b)

        distances = list(map(lambda item: (item[0], _dst(item[1][0], item[1][1], x, y)), active_coordinates))
        areas_by_weight = list(
            map(lambda item: (math.pow((1.0 / max(1, item[1])), 0.5 + 4.5 * area_sharpness), item[0]), distances))
        return pick_random_by_weight(areas_by_weight, rng)

    def _setup_initial_colors(self, image: DreamImage, color_func):
        w = image.width
        h = image.height
        wpart = round(w / 3)
        hpart = round(h / 3)
        for i in range(3):
            for j in range(3):
                image.color_area(wpart * i, hpart * j, w, h,
                                 color_func(wpart * i + w // 2, hpart * j + h // 2))

    def result(self, width, height, seed, blur_amount, density, area_sharpness, **palettes):
        outputs = list()
        rng = random.Random()
        coordinates = self._area_coordinates(width, height)
        active_palettes = list(filter(lambda pair: pair[1] is not None and len(pair[1]) > 0, palettes.items()))
        active_coordinates = list(map(lambda item: (item[0], coordinates[item[0]]), active_palettes))

        n = max(list(map(len, palettes.values())) + [0])
        for b in range(n):
            batch_palettes = dict(map(lambda item: (item[0], item[1][b].random_iteration(seed)), active_palettes))

            def _color_func(x, y):
                name = self._pick_random_area(active_coordinates, x, y, rng, area_sharpness)
                rgb = batch_palettes[name]
                return next(rgb)

            image = DreamImage(pil_image=Image.new("RGB", (width, height)))
            self._setup_initial_colors(image, _color_func)
            image = _generate_noise(image, _color_func, rng, (round(image.width / 3), round(image.height / 3)),
                                    blur_amount, density)
            outputs.append(image)

        if not outputs:
            outputs.append(DreamImage(pil_image=Image.new("RGB", (width, height))))

        return (DreamImage.join_to_tensor_data(outputs),)
