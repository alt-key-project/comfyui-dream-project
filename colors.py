# -*- coding: utf-8 -*-
from .categories import NodeCategories
from .shared import *
from .types import *


class DreamImageAreaSampler:
    NODE_NAME = "Sample Image Area as Palette"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "samples": ("INT", {"default": 256, "min": 1, "max": 1024 * 4}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "area": (["top-left", "top-center", "top-right",
                          "center-left", "center", "center-right",
                          "bottom-left", "bottom-center", "bottom-right"],)
            },
        }

    CATEGORY = NodeCategories.IMAGE_COLORS
    RETURN_TYPES = (RGBPalette.ID,)
    RETURN_NAMES = ("palette",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def _get_pixel_area(self, img: DreamImage, area):
        w = img.width
        h = img.height
        wpart = round(w / 3)
        hpart = round(h / 3)
        x0 = 0
        x1 = wpart - 1
        x2 = wpart
        x3 = wpart + wpart - 1
        x4 = wpart + wpart
        x5 = w - 1
        y0 = 0
        y1 = hpart - 1
        y2 = hpart
        y3 = hpart + hpart - 1
        y4 = hpart + hpart
        y5 = h - 1
        if area == "center":
            return (x2, y2, x3, y3)
        elif area == "top-center":
            return (x2, y0, x3, y1)
        elif area == "bottom-center":
            return (x2, y4, x3, y5)
        elif area == "center-left":
            return (x0, y2, x1, y3)
        elif area == "top-left":
            return (x0, y0, x1, y1)
        elif area == "bottom-left":
            return (x0, y4, x1, y5)
        elif area == "center-right":
            return (x4, y2, x5, y3)
        elif area == "top-right":
            return (x4, y0, x5, y1)
        elif area == "bottom-right":
            return (x4, y4, x5, y5)

    def result(self, image, samples, seed, area):
        result = list()
        r = random.Random()
        r.seed(seed)
        for data in image:
            di = DreamImage(tensor_image=data)
            area = self._get_pixel_area(di, area)

            pixels = list()
            for i in range(samples):
                x = r.randint(area[0], area[2])
                y = r.randint(area[1], area[3])
                pixels.append(di.get_pixel(x, y))
            result.append(RGBPalette(colors=pixels))

        return (tuple(result),)


class DreamImageSampler:
    NODE_NAME = "Sample Image as Palette"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "samples": ("INT", {"default": 1024, "min": 1, "max": 1024 * 4}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})
            },
        }

    CATEGORY = NodeCategories.IMAGE_COLORS
    RETURN_TYPES = (RGBPalette.ID,)
    RETURN_NAMES = ("palette",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, image, samples, seed):
        result = list()
        r = random.Random()
        r.seed(seed)
        for data in image:
            di = DreamImage(tensor_image=data)
            pixels = list()
            for i in range(samples):
                x = r.randint(0, di.width - 1)
                y = r.randint(0, di.height - 1)
                pixels.append(di.get_pixel(x, y))
            result.append(RGBPalette(colors=pixels))

        return (tuple(result),)


class DreamColorAlign:
    NODE_NAME = "Palette Color Align"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.palette | {
                "target_align": (RGBPalette.ID, ),
                "alignment_factor": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 10.0, "step": 0.1}),
            }
        }

    CATEGORY = NodeCategories.IMAGE_COLORS
    RETURN_TYPES = (RGBPalette.ID,)
    RETURN_NAMES = ("palette",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, palette: Tuple[RGBPalette], target_align: Tuple[RGBPalette], alignment_factor: float):
        results = list()

        def _limit(c):
            return max(min(c, 255), 0)

        for i in range(len(palette)):
            p = palette[i]
            t = target_align[i]
            (_, r1, g1, b1) = p.analyze()
            (_, r2, g2, b2) = t.analyze()

            dr = (r2 - r1) * alignment_factor
            dg = (g2 - g1) * alignment_factor
            db = (b2 - b1) * alignment_factor
            new_pixels = list()
            for pixel in p:
                r = _limit(round(pixel[0] + (255 * dr)))
                g = _limit(round(pixel[1] + (255 * dg)))
                b = _limit(round(pixel[1] + (255 * db)))
                new_pixels.append((r, g, b))
            results.append(RGBPalette(colors=new_pixels))
        return (tuple(results),)


class DreamColorShift:
    NODE_NAME = "Palette Color Shift"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.palette | {
                "red_multiplier": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 100.0, "step": 0.1}),
                "green_multiplier": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 100.0, "step": 0.1}),
                "blue_multiplier": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 100.0, "step": 0.1}),
                "fixed_brightness": (["yes", "no"],),
            }
        }

    CATEGORY = NodeCategories.IMAGE_COLORS
    RETURN_TYPES = (RGBPalette.ID,)
    RETURN_NAMES = ("palette",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, palette, red_multiplier, green_multiplier, blue_multiplier, fixed_brightness):
        results = list()

        def _limit(c):
            return max(min(c, 255), 0)

        for p in palette:
            new_pixels = list()
            for pixel in p:
                s = pixel[0] + pixel[1] + pixel[2]
                r = _limit(round(pixel[0] * red_multiplier))
                g = _limit(round(pixel[1] * green_multiplier))
                b = _limit(round(pixel[2] * blue_multiplier))
                if fixed_brightness == "yes":
                    brightness_factor = max(s, 1) / float(max(r + g + b, 1))
                    r = _limit(round(r * brightness_factor))
                    g = _limit(round(g * brightness_factor))
                    b = _limit(round(b * brightness_factor))

                new_pixels.append((r, g, b))
            results.append(RGBPalette(colors=new_pixels))
        return (tuple(results),)


class DreamAnalyzePalette:
    NODE_NAME = "Analyze Palette"
    NODE = "📊"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.palette
            ,
        }

    CATEGORY = NodeCategories.IMAGE_COLORS
    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT", "FLOAT")
    RETURN_NAMES = ("brightness", "redness", "greenness", "blueness")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, palette):
        f = 1.0 / len(palette)
        (w, r, g, b) = (0, 0, 0, 0)
        for p in palette:
            (brightness, red, green, blue) = p.analyze()
            w += brightness
            r += red
            g += green
            b += blue

        return w * f, r * f, g * f, b * f
