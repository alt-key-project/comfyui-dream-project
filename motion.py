import math

import numpy
import torch
from PIL.Image import Resampling
from PIL import Image, ImageDraw

from .shared import ALWAYS_CHANGED_FLAG, convertToPIL, convertFromPIL


class AKPImageMotion:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "zoom": ("FLOAT", {"default": 0.0, "min": -1, "max": 1, "step": 0.01}),
                "mask_feather": ("INT", {"default": 10, "min": 0}),
                "mask_overlap": ("INT", {"default": 10, "min": 0}),
                "x_translation": ("FLOAT", {"default": 0.0, "min": -1, "max": 1, "step": 0.01}),
                "y_translation": ("FLOAT", {"default": 0.0, "min": -1, "max": 1, "step": 0.01}),
            },
            "optional": {
                "noise": ("IMAGE",),
            }
        }

    CATEGORY = "AKP Animation/image"
    RETURN_TYPES = ("IMAGE", "MASK", "MASK")
    RETURN_NAMES = ("image", "overlapping_mask", "mask")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def _mk_PIL_image(self, size, color=None, mode="RGB") -> Image:
        im = Image.new(mode=mode, size=size)
        if color:
            im.paste(color, (0, 0, size[0], size[1]))
        return im

    def _paste_into(self, pasted_image, background, x_translation, y_translation):
        dx = int(round(background.width * x_translation))
        dy = int(round(background.height * y_translation))
        print("Paste of {} into {}".format(pasted_image.size, background.size))
        print("dx,dy = {} {}".format(dx, dy))
        center = (background.width // 2, background.height // 2)
        centered_paste = ((background.width - pasted_image.width) // 2, (background.height - pasted_image.height) // 2)
        print("center is {}".format(center))
        print("centered paste is {}".format(centered_paste))
        offset = (centered_paste[0] + dx, centered_paste[1] + dy)
        print("Paste offset = {}".format(offset))
        background.paste(pasted_image, offset)
        return (background, (offset[0], offset[1], offset[0] + pasted_image.width, offset[1] + pasted_image.height))

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

    def result(self, image, zoom, x_translation, y_translation, mask_feather, mask_overlap, **other):
        pil_image = convertToPIL(image)
        noise = other.get("noise", None)
        multiplier = math.pow(2, zoom)
        resized_image = pil_image.resize((round(pil_image.width * multiplier),
                                          round(pil_image.height * multiplier)), Resampling.BILINEAR)

        print("resized zoom " + str(resized_image.size))
        if noise is None:
            base_image = self._mk_PIL_image(pil_image.size, "black")
        else:
            base_image = convertToPIL(noise).resize(pil_image.size, Resampling.BILINEAR)

        mask_overlap = min(pil_image.width // 3, min(mask_overlap, pil_image.height // 3))
        print("mask_overlap = {}, feather = {}".format(mask_overlap, mask_feather))

        selection_offset = (round(x_translation * pil_image.width), round(y_translation * pil_image.height))
        selection = ((pil_image.width - resized_image.width) // 2 + selection_offset[0],
                     (pil_image.height - resized_image.height) // 2 + selection_offset[1],
                     (pil_image.width - resized_image.width) // 2 + selection_offset[0] + resized_image.width,
                     (pil_image.height - resized_image.height) // 2 + selection_offset[1] + resized_image.height)

        base_image.paste(resized_image, selection)

        mask1 = self._make_mask(pil_image.width, pil_image.height, selection, mask_feather, mask_overlap)
        mask2 = self._make_mask(pil_image.width, pil_image.height, selection, 0, 0)
        return (convertFromPIL(base_image), self._convertPILToMask(mask1), self._convertPILToMask(mask2))
