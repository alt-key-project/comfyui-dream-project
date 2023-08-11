import math

import numpy
import torch
from PIL.Image import Resampling
from PIL import Image, ImageDraw
from .categories import *
from .types import SharedTypes, FrameCounter

from .shared import ALWAYS_CHANGED_FLAG, convertToPIL, convertFromPIL, ImageWrapper


class AKPImage3WayBlend:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image1": ("IMAGE",),
                "image2": ("IMAGE",),
                "image3": ("IMAGE",),
                "min_max_weight": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 100.0}),
                "median_weight": ("FLOAT", {"default": 10.0, "min": 1.0, "max": 100.0})
            }
        }

    CATEGORY = NodeCategories.IMAGE_POSTPROCESSING
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, image1, image2, image3, min_max_weight, median_weight):
        wrapper_image_1 = ImageWrapper(sd_image=image1)
        wrapper_image_2 = ImageWrapper(sd_image=image2)
        wrapper_image_3 = ImageWrapper(sd_image=image3)
        w = min(wrapper_image_1.width, wrapper_image_2.width, wrapper_image_3.width)
        h = min(wrapper_image_1.height, wrapper_image_2.height, wrapper_image_3.height)
        total_weight = median_weight + 2 * min_max_weight
        result = ImageWrapper(pil_image=Image.new("RGBA", size=(w, h)))

        for (_, x, y) in result:
            p1 = wrapper_image_1.get_pixel(x, y)
            p2 = wrapper_image_2.get_pixel(x, y)
            p3 = wrapper_image_2.get_pixel(x, y)
            new_pixel = []
            for i in range(4):
                values = [p1[i], p2[i], p3[i]]
                values.sort()
                v = round((min_max_weight * values[0] + median_weight * values[1] + min_max_weight * values[2]) /
                          total_weight)
                new_pixel.append(v)
            result.set_pixel(x, y, tuple(new_pixel))
        return result.get_sd_image()


class AKPImageMotion:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "zoom": ("FLOAT", {"default": 0.0, "min": -10, "max": 10, "step": 0.01}),
                "mask_1_feather": ("INT", {"default": 0, "min": 0}),
                "mask_1_overlap": ("INT", {"default": 0, "min": 0}),
                "mask_2_feather": ("INT", {"default": 10, "min": 0}),
                "mask_2_overlap": ("INT", {"default": 5, "min": 0}),
                "mask_3_feather": ("INT", {"default": 15, "min": 0}),
                "mask_3_overlap": ("INT", {"default": 5, "min": 0}),
                "x_translation": ("FLOAT", {"default": 0.0, "min": -10, "max": 10, "step": 0.01}),
                "y_translation": ("FLOAT", {"default": 0.0, "min": -10, "max": 10, "step": 0.01}),
            } | SharedTypes.frame_counter,
            "optional": {
                "noise": ("IMAGE",),
                "output_resize_width": ("INT", {"default": 0, "min": 0}),
                "output_resize_height": ("INT", {"default": 0, "min": 0})
            }
        }

    CATEGORY = NodeCategories.ANIMATION_TRANSFORMS
    RETURN_TYPES = ("IMAGE", "MASK", "MASK", "MASK")
    RETURN_NAMES = ("image", "mask1", "mask2", "mask3")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def _mk_PIL_image(self, size, color=None, mode="RGB") -> Image:
        im = Image.new(mode=mode, size=size)
        if color:
            im.paste(color, (0, 0, size[0], size[1]))
        return im

    def _convertPILToMask(self, image):
        return torch.from_numpy(numpy.array(image.convert("L")).astype(numpy.float32) / 255.0)

    def _apply_feather(self, pil_image, area, feather):
        feather = min((area[2] - area[0]) // 2 - 1, feather)
        draw = ImageDraw.Draw(pil_image)
        for i in range(1, feather + 1):
            rect = [(area[0] + i - 1, area[1] + i - 1), (area[2] - i + 1, area[3] - i + 1)]
            c = 255 - int(round(255.0 * (i / (feather + 1))))
            draw.rectangle(rect, fill=None, outline=(c, c, c))
        return pil_image

    def _make_mask(self, width, height, selection_area, feather, overlap):
        complete_area = self._mk_PIL_image((width, height), "white")
        draw = ImageDraw.Draw(complete_area)
        (left, top, right, bottom) = selection_area
        area = (left + overlap, top + overlap, right - overlap - 1, bottom - overlap - 1)
        draw.rectangle(area, fill="black", width=0)
        return self._apply_feather(complete_area, area, feather)

    def _make_resizer(self, output_resize_width, output_resize_height):
        def bound(i):
            return min(max(i, 1), 32767)

        if output_resize_height and output_resize_width:
            return lambda img: img.resize((bound(output_resize_width), bound(output_resize_height)), Resampling.NEAREST)
        else:
            return lambda img: img

    def result(self, image, zoom, x_translation, y_translation, mask_1_feather, mask_1_overlap,
               mask_2_feather, mask_2_overlap, mask_3_feather, mask_3_overlap, frame_counter : FrameCounter,
               **other):

        def _limit_range(f):
            return max(-1.0, min(1.0, f))

        zoom = _limit_range(zoom / frame_counter.frames_per_second)
        x_translation = _limit_range(x_translation / frame_counter.frames_per_second)
        y_translation = _limit_range(y_translation / frame_counter.frames_per_second)
        pil_image = convertToPIL(image)
        sz = self._make_resizer(other.get("output_resize_width", None), other.get("output_resize_height", None))
        noise = other.get("noise", None)
        multiplier = math.pow(2, zoom)
        resized_image = pil_image.resize((round(pil_image.width * multiplier),
                                          round(pil_image.height * multiplier)), Resampling.BILINEAR)

        if noise is None:
            base_image = self._mk_PIL_image(pil_image.size, "black")
        else:
            base_image = convertToPIL(noise).resize(pil_image.size, Resampling.BILINEAR)

        selection_offset = (round(x_translation * pil_image.width), round(y_translation * pil_image.height))
        selection = ((pil_image.width - resized_image.width) // 2 + selection_offset[0],
                     (pil_image.height - resized_image.height) // 2 + selection_offset[1],
                     (pil_image.width - resized_image.width) // 2 + selection_offset[0] + resized_image.width,
                     (pil_image.height - resized_image.height) // 2 + selection_offset[1] + resized_image.height)
        base_image.paste(resized_image, selection)

        mask_1_overlap = min(pil_image.width // 3, min(mask_1_overlap, pil_image.height // 3))
        mask_2_overlap = min(pil_image.width // 3, min(mask_2_overlap, pil_image.height // 3))
        mask_3_overlap = min(pil_image.width // 3, min(mask_3_overlap, pil_image.height // 3))
        mask1 = self._make_mask(pil_image.width, pil_image.height, selection, mask_1_feather, mask_1_overlap)
        mask2 = self._make_mask(pil_image.width, pil_image.height, selection, mask_2_feather, mask_2_overlap)
        mask3 = self._make_mask(pil_image.width, pil_image.height, selection, mask_3_feather, mask_3_overlap)
        return (convertFromPIL(sz(base_image)), self._convertPILToMask(sz(mask1)),
                self._convertPILToMask(sz(mask2)), self._convertPILToMask(sz(mask3)))