from .shared import *
from .types import *
from .categories import NodeCategories


class DreamNoiseFromPalette:
    NODE_NAME = "Noise from Palette"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.palette | {
                "width": ("INT", {"default": 512, "min": 1, "max": 8192}),
                "height": ("INT", {"default": 512, "min": 1, "max": 8192}),
                "blur_amount": ("FLOAT", {"default": 0.1, "min": 0, "max": 1.0, "step": 0.05}),
                "iterations": ("INT", {"default": 4, "min": 1, "max": 64}),
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

    def generate_noise(self, image: DreamImage, color_function, rng: random.Random, i: int, blur_amount) -> DreamImage:
        w = image.width >> i
        h = image.height >> i
        blur_radius = round(max(image.width, image.height) * blur_amount * 0.25)
        if w <= 1 or h <= 1:
            return image
        for i in range(1 << (i*2)):
            x = rng.randint(-w+1, image.width - 1)
            y = rng.randint(-h+1, image.height - 1)
            image.color_area(x, y, w, h, color_function())
        image = image.blur(blur_radius)
        return self.generate_noise(image, color_function, rng, i + 1, blur_amount)

    def result(self, palette: Tuple[RGBPalette], width, height, seed, blur_amount, iterations):
        outputs = list()
        rng = random.Random()
        for p in palette:
            seed += 1
            color_iterator = p.random_iteration(seed)
            image = DreamImage(pil_image=Image.new("RGB", (width, height), color=next(color_iterator)))
            for n in range(iterations):
                image = self.generate_noise(image, lambda: next(color_iterator), rng, 1, blur_amount)
            outputs.append(image)

        return (DreamImage.join_to_tensor_data(outputs),)
