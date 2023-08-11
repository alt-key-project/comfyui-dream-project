import json
from PIL.PngImagePlugin import PngInfo
from .categories import NodeCategories

from .types import SharedTypes, FrameCounter
from .shared import hashed_as_strings, convertToPIL
import os


class AKPImageSequenceOutput:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.frame_counter | {
                "image": ("IMAGE",),
                "directory_path": ("STRING", {"default": '', "multiline": False}),
                "prefix": ("STRING", {"default": 'frame', "multiline": False}),
                "digits": ("INT", {"default": 5}),
                "filetype": (['png with embedded workflow', "png", 'jpg small size', 'jpg high quality'],),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    CATEGORY = NodeCategories.IMAGE_ANIMATION
    RETURN_TYPES = ()
    FUNCTION = "was_save_images"
    OUTPUT_NODE = True
    RETURN_NAMES = ()
    FUNCTION = "save"

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(*values)

    def get_new_filename(self, current_frame, prefix, digits, filetype):
        return prefix + "_" + str(current_frame).zfill(digits) + "." + filetype.split(" ")[0]

    def save_png(self, pil_image, filepath, embed_info, prompt, extra_pnginfo):
        info = PngInfo()
        if extra_pnginfo is not None:
            for item in extra_pnginfo:
                info.add_text(item, json.dumps(extra_pnginfo[item]))
        if prompt is not None:
            info.add_text("prompt", json.dumps(prompt))
        if embed_info:
            pil_image.save(filepath, pnginfo=info, optimize=True)
        else:
            pil_image.save(filepath, optimize=True)

    def save_jpg(self, pil_image, filepath, quality):
        pil_image.save(filepath, quality=quality, optimize=True)

    def save(self, frame_counter: FrameCounter, image, directory_path, prefix, digits, filetype, prompt, extra_pnginfo):
        filename = self.get_new_filename(frame_counter.current_frame, prefix, digits, filetype)
        filepath = os.path.join(directory_path, filename)
        if len(image) != 1:
            print("Warning - batch output not supported for animation nodes. Only saving first result!")
        pil_image = convertToPIL(image[0])
        if not os.path.isdir(directory_path):
            os.makedirs(directory_path)
        if filetype.startswith("png"):
            self.save_png(pil_image, filepath, filetype == 'png with embedded workflow', prompt, extra_pnginfo)
        elif filetype == "jpg small size":
            self.save_jpg(pil_image, filepath, 70)
        elif filetype == "jpg high quality":
            self.save_jpg(pil_image, filepath, 98)
        print("Saved {} in {}".format(filename, os.path.abspath(directory_path)))
        return ()
