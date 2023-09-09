# -*- coding: utf-8 -*-
import math

import numpy
import torch
from PIL import Image, ImageDraw
from PIL.Image import Resampling

from .categories import *
from .shared import ALWAYS_CHANGED_FLAG, convertTensorImageToPIL, DreamImageProcessor, \
    DreamImage, DreamMask
from .types import SharedTypes, FrameCounter


class DreamImageMotion:
    NODE_NAME = "Image Motion"

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

    def result(self, image: torch.Tensor, zoom, x_translation, y_translation, mask_1_feather, mask_1_overlap,
               mask_2_feather, mask_2_overlap, mask_3_feather, mask_3_overlap, frame_counter: FrameCounter,
               **other):
        def _limit_range(f):
            return max(-1.0, min(1.0, f))

        def _motion(image: DreamImage, batch_counter, zoom, x_translation, y_translation, mask_1_overlap,
                    mask_2_overlap,
                    mask_3_overlap):
            zoom = _limit_range(zoom / frame_counter.frames_per_second)
            x_translation = _limit_range(x_translation / frame_counter.frames_per_second)
            y_translation = _limit_range(y_translation / frame_counter.frames_per_second)
            pil_image = image.pil_image
            sz = self._make_resizer(other.get("output_resize_width", None), other.get("output_resize_height", None))
            noise = other.get("noise", None)
            multiplier = math.pow(2, zoom)
            resized_image = pil_image.resize((round(pil_image.width * multiplier),
                                              round(pil_image.height * multiplier)), Resampling.BILINEAR)

            if noise is None:
                base_image = self._mk_PIL_image(pil_image.size, "black")
            else:
                base_image = convertTensorImageToPIL(noise).resize(pil_image.size, Resampling.BILINEAR)

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

            return (DreamImage(pil_image=sz(base_image)),
                    DreamMask(pil_image=sz(mask1)),
                    DreamMask(pil_image=sz(mask2)),
                    DreamMask(pil_image=sz(mask3)))

        proc = DreamImageProcessor(image,
                                   zoom=zoom,
                                   x_translation=x_translation,
                                   y_translation=y_translation,
                                   mask_1_overlap=mask_1_overlap,
                                   mask_2_overlap=mask_2_overlap,
                                   mask_3_overlap=mask_3_overlap)
        return proc.process(_motion)
